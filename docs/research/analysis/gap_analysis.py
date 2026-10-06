import pandas as pd, numpy as np
import sys
n = pd.read_csv(sys.argv[1], parse_dates=["date"]).sort_values("date").reset_index(drop=True)
n = n[(n[["open","high","low","close"]]>0).all(axis=1)].reset_index(drop=True)
n["prev_close"] = n.close.shift(1); n["prev_date"] = n.date.shift(1)
n["gap"] = n.open/n.prev_close - 1
n["day_ret"] = n.close/n.prev_close - 1
n["cal_gap_days"] = (n.date - n.prev_date).dt.days
n["weekday"] = n.date.dt.day_name()
n["after_long_break"] = n.cal_gap_days >= 4   # long weekend or holiday
n = n.dropna(subset=["gap"]).reset_index(drop=True)
yrs = (n.date.iloc[-1]-n.date.iloc[0]).days/365.25
print(f"Nifty 50, {len(n)} sessions over {yrs:.1f} years\n")

def dist(x, label):
    q = x.quantile([0.001,0.01,0.05,0.5,0.95,0.99,0.999])*100
    print(f"{label:<34} n={len(x):5d}  p0.1={q.iloc[0]:6.2f}%  p1={q.iloc[1]:6.2f}%  p5={q.iloc[2]:5.2f}%  median={q.iloc[3]:5.2f}%  p95={q.iloc[4]:5.2f}%  p99={q.iloc[5]:5.2f}%  p99.9={q.iloc[6]:5.2f}%   |gap|>=1%: {(x.abs()>=0.01).mean()*100:4.1f}% of days")
print("Opening gap vs previous close (open/prev_close - 1):")
dist(n.gap, "all sessions")
dist(n[n.weekday=="Monday"].gap, "Mondays")
dist(n[n.weekday!="Monday"].gap, "Tuesday to Friday")
dist(n[n.after_long_break].gap, "after a 4+ day break")
dist(n[~n.after_long_break].gap, "after a 1-3 day break")
print()
print("Worst 10 gap-downs:"); print(n.nsmallest(10,"gap")[["date","weekday","cal_gap_days","gap","day_ret"]].assign(gap=lambda d:(d.gap*100).round(2), day_ret=lambda d:(d.day_ret*100).round(2)).to_string(index=False))
print("\nLargest 8 gap-ups:"); print(n.nlargest(8,"gap")[["date","weekday","cal_gap_days","gap","day_ret"]].assign(gap=lambda d:(d.gap*100).round(2), day_ret=lambda d:(d.day_ret*100).round(2)).to_string(index=False))
# streaks of consecutive sessions with gap <= -1%
streak = 0; streaks = []
for i, g in enumerate(n.gap):
    if g <= -0.01: streak += 1
    else:
        if streak >= 2: streaks.append((n.date[i-1].date(), streak))
        streak = 0
print(f"\nStreaks of 2+ consecutive sessions each opening down 1% or more: {len(streaks)}  ->", streaks[:15])
# cumulative gap-only loss over worst 5-session windows (sum of negative gaps)
n["neg_gap"] = n.gap.clip(upper=0)
n["gap5"] = n.neg_gap.rolling(5).sum()
print("Worst 5 five-session windows by accumulated opening gaps:", n.nsmallest(5,"gap5")[["date","gap5"]].assign(gap5=lambda d:(d.gap5*100).round(2)).to_string(index=False, header=False).replace("\n","; "))

# ---- what the bot would have faced: replay the signal and record gaps while invested
def replay(ma, drift=0.02):
    d = n.copy(); d["sma"] = d.close.rolling(ma).mean(); d = d.dropna().reset_index(drop=True)
    pos = 0; rows = []; dropped = []; whip = []
    pend = None; last_exit_i = None
    for i in range(len(d)):
        o, c, g = d.open[i], d.close[i], d.gap[i]
        if pend == "BUY":
            if abs(g) > drift: dropped.append((d.date[i].date(), round(g*100,2), round((d.close[min(i+5,len(d)-1)]/o-1)*100,2)))
            else: pos = 1
            pend = None
        elif pend == "SELL":
            pos = 0; pend = None; last_exit_i = i
            if g >= 0.01: whip.append((d.date[i].date(), round(g*100,2)))
        rows.append((d.date[i], pos, g, d.day_ret[i], d.weekday[i], d.after_long_break[i]))
        on = c > d.sma[i]
        if on and pos == 0: pend = "BUY"
        elif not on and pos == 1: pend = "SELL"
    r = pd.DataFrame(rows, columns=["date","pos","gap","day_ret","weekday","long_break"])
    inv = r[r.pos==1]
    return r, inv, dropped, whip
for ma in (100, 200):
    r, inv, dropped, whip = replay(ma)
    print(f"\n=== Signal SMA{ma}: invested {inv.pos.sum()} of {len(r)} sessions ({inv.pos.sum()/len(r)*100:.0f}%) ===")
    print(f"Gap-downs faced while invested: <= -1%: {(inv.gap<=-0.01).sum()} days, <= -2%: {(inv.gap<=-0.02).sum()}, <= -3%: {(inv.gap<=-0.03).sum()}, <= -5%: {(inv.gap<=-0.05).sum()}; worst: {inv.gap.min()*100:.2f}% on {inv.loc[inv.gap.idxmin(),'date'].date()}")
    print(f"Gap-downs faced while in cash (missed):  <= -2%: {(r[r.pos==0].gap<=-0.02).sum()}, <= -3%: {(r[r.pos==0].gap<=-0.03).sum()}, <= -5%: {(r[r.pos==0].gap<=-0.05).sum()}")
    print(f"Mondays vs other days while invested: mean gap Mon {inv[inv.weekday=='Monday'].gap.mean()*100:.3f}% (n={len(inv[inv.weekday=='Monday'])}), others {inv[inv.weekday!='Monday'].gap.mean()*100:.3f}%; after 4+ day break {inv[inv.long_break].gap.mean()*100:.3f}% (n={inv.long_break.sum()}), worst after break {inv[inv.long_break].gap.min()*100:.2f}%")
    print(f"Entries dropped by the 2% drift check: {len(dropped)}; of those, index 5 sessions later vs the dropped open: higher in {sum(1 for _,_,x in dropped if x>0)}, lower in {sum(1 for _,_,x in dropped if x<=0)}  -> {dropped[:8]}")
    print(f"Exits executed into a gap-UP of 1%+ at the open (likely whipsaw): {len(whip)} of all exits -> {whip[:8]}")
