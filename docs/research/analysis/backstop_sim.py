"""Daily-bar simulation of the S1 ETF trend bot with the K1 governor, to count how often the E9
broker-side backstop (epoch drawdown -13.5%) would be touched and in which scenario.

Input: CSV with date, open, high, low, close (any case; extra columns ignored). The index series is
used both as the signal and as the proxy for the held ETF price.

Conventions (PRD v1.11):
- signal: close > SMA(ma_days) -> target 1 else 0; decision at close T, fill at T+1 open, 5 bps slippage
- governor on NAV vs reference peak: halve at -6 (release above -3), REDUCING at -10, HALT+flatten at -12
- governor checked at the session low (live: every minute at LTP); flatten fills at the close of the
  halt session (proxy for the intraday fill; usually a little better than the low)
- epoch: one epoch until a HALT; resumption after >=20 sessions at the next entry signal starts a new
  epoch (models the owner running new-epoch), ref peak and epoch peak reset to NAV
- backstop touch: an invested session whose low takes epoch drawdown to <= -13.5%
  classified as GAP (open already <= -13.5%, previous close > -12%), INTRADAY (open > -12%, low <= -13.5%),
  or SPIKE (low <= -13.5% but close > -12%: the only case where point 3 decides anything)
"""
import sys, pandas as pd, numpy as np

HALVE, HALVE_REL, REDUCE, HALT, BACKSTOP = -0.06, -0.03, -0.10, -0.12, -0.135
SLIP = 0.0005
COOLOFF = 20

def load(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    cols = {c: c for c in df.columns}
    for want, alts in {"date": ["date", "timestamp", "time"], "open": ["open"], "high": ["high"], "low": ["low"], "close": ["close", "adj close", "price"]}.items():
        for a in alts:
            if a in df.columns: cols[want] = a; break
    out = pd.DataFrame({k: df[cols[k]] for k in ["date", "open", "high", "low", "close"]})
    raw = out["date"].astype(str).str.strip()
    iso = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
    out["date"] = iso if iso.notna().mean() > 0.9 else pd.to_datetime(raw, dayfirst=True, errors="coerce")
    for c in ["open", "high", "low", "close"]:
        out[c] = pd.to_numeric(out[c].astype(str).str.replace(",", ""), errors="coerce")
    out = out.dropna()
    out = out[(out[["open","high","low","close"]] > 0).all(axis=1) & (out.high >= out.low)]
    out = out.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    return out

def simulate(df, ma_days, max_exp, capital=200000.0, start=None):
    d = df.copy()
    d["sma"] = d["close"].rolling(ma_days).mean()
    if start is not None: d = d[d["date"] >= pd.Timestamp(start)].reset_index(drop=True)
    d = d.dropna().reset_index(drop=True)
    cash, qty = capital, 0
    ref_peak = epoch_peak = capital
    halved = False; state = "ACTIVE"; halted_at = None; reduced_at = None
    pending = None  # ('BUY'|'SELL', fraction_target) to execute at today's open
    ev = {"halve": 0, "reduce": 0, "halt": 0, "touch": 0, "gap": 0, "intraday": 0, "spike": 0, "epochs": 1, "sessions_invested": 0, "epoch_breach": 0}
    touches = []; halts = []
    nav_series = []
    for i in range(len(d)):
        o, h, l, c, dt = d.open[i], d.high[i], d.low[i], d.close[i], d.date[i]
        prev_close_nav = cash + qty * (d.close[i-1] if i > 0 else o)
        # 1) execute yesterday's decision at today's open
        if pending is not None:
            side, target_frac = pending; pending = None
            target_val = target_frac * max_exp * (0.5 if halved else 1.0) * (cash + qty * o)
            if side == "BUY":
                price = o * (1 + SLIP); q = int(max(0, (target_val - qty * o)) // price)
                q = min(q, int(cash // price)); cash -= q * price; qty += q
            else:
                price = o * (1 - SLIP); want_qty = int(target_val // o) if target_frac > 0 else 0
                q = max(0, qty - want_qty); cash += q * price; qty -= q
        invested = qty > 0
        if invested: ev["sessions_invested"] += 1
        # 2) governor at the session low (live: every minute); epoch drawdown at the low for the backstop
        nav_low = cash + qty * l; nav_open = cash + qty * o; nav_close = cash + qty * c
        dd_ref_low = nav_low / ref_peak - 1; dd_ep_low = nav_low / epoch_peak - 1
        dd_ep_open = nav_open / epoch_peak - 1; dd_ep_close = nav_close / epoch_peak - 1
        dd_ep_prev = prev_close_nav / epoch_peak - 1
        if invested and dd_ep_low <= BACKSTOP:
            ev["touch"] += 1
            if dd_ep_open <= BACKSTOP and dd_ep_prev > HALT: kind = "gap"
            elif dd_ep_close > HALT: kind = "spike"
            else: kind = "intraday"
            ev[kind] += 1; touches.append((dt.date(), kind, round(dd_ep_low*100, 1), round(dd_ep_close*100, 1)))
        if state != "HALTED":
            if dd_ep_low <= HALT or dd_ref_low <= HALT:
                kind_h = "epoch" if dd_ep_low <= HALT else "ref"
                if kind_h == "epoch": ev["epoch_breach"] += 1
                state = "HALTED"; ev["halt"] += 1; halted_at = i; halts.append((dt.date(), kind_h, round(min(dd_ep_low, dd_ref_low)*100,1)))
                price = c * (1 - SLIP); cash += qty * price; qty = 0; pending = None
            elif dd_ref_low <= REDUCE and state == "ACTIVE":
                state = "REDUCING"; ev["reduce"] += 1; reduced_at = i
            if dd_ref_low <= HALVE and not halved:
                halved = True; ev["halve"] += 1
                if qty > 0: pending = ("SELL", 1.0)   # trim to half at next open (strategy-exit window)
            elif halved and (nav_close / ref_peak - 1) > HALVE_REL:
                halved = False
        # 3) peaks at the close
        nav_close = cash + qty * c
        ref_peak = max(ref_peak, nav_close); epoch_peak = max(epoch_peak, nav_close)
        nav_series.append((dt, nav_close))
        # 4) evening decision
        signal_on = c > d.sma[i]
        if state == "HALTED":
            if i - halted_at >= COOLOFF and signal_on:
                state = "ACTIVE"; halved = False; ref_peak = epoch_peak = nav_close; ev["epochs"] += 1
                pending = ("BUY", 1.0)
            continue
        if state == "REDUCING":
            if i - reduced_at >= COOLOFF and signal_on:
                state = "ACTIVE"; ref_peak = nav_close   # simulated CLI reset (K1 backtest mapping); epoch continues
                if qty == 0: pending = ("BUY", 1.0)
            elif not signal_on and qty > 0: pending = ("SELL", 0.0)
            if state == "REDUCING": continue
        if signal_on and qty == 0 and pending is None: pending = ("BUY", 1.0)
        elif signal_on and qty > 0 and not halved:
            # top-up after halving release if gap > 5% of capital
            target_val = max_exp * nav_close; 
            if target_val - qty * c > 0.05 * nav_close: pending = ("BUY", 1.0)
        elif not signal_on and qty > 0: pending = ("SELL", 0.0)
    nav = pd.Series([v for _, v in nav_series], index=[t for t, _ in nav_series])
    return ev, touches, halts, nav

if __name__ == "__main__":
    path = sys.argv[1]; start = sys.argv[2] if len(sys.argv) > 2 else None
    df = load(path)
    print(f"rows {len(df)} from {df.date.min().date()} to {df.date.max().date()}")
    rows = []
    for ma in (50, 100, 150, 200):
        for mx in (1.0, 0.7, 0.5):
            ev, touches, halts, nav = simulate(df, ma, mx, start=start)
            yrs = (nav.index[-1] - nav.index[0]).days / 365.25
            cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/yrs) - 1
            rows.append({"ma": ma, "max_exp": mx, "cagr%": round(cagr*100,1), "invested%": round(100*ev["sessions_invested"]/len(nav),0), "halve": ev["halve"], "reduce": ev["reduce"], "halt": ev["halt"], "epochs": ev["epochs"],
                         "backstop_touch": ev["touch"], "gap": ev["gap"], "intraday": ev["intraday"], "spike": ev["spike"],
                         "touch_dates": "; ".join(f"{t} {k} low {lo}% close {cl}%" for t,k,lo,cl in touches)[:200],
                         "epoch_breach": ev["epoch_breach"], "halt_dates": "; ".join(f"{t} {k} {x}%" for t,k,x in halts)[:230]})
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200)
    print(out.to_string(index=False))
