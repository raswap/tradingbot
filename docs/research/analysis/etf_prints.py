"""Count NIFTYBEES prints far below the previous close on days when the Nifty itself barely moved.
Usage: python3 etf_prints.py niftybees_daily_ohlc_splitadj.csv nifty50_daily_ohlc.csv"""
import sys, pandas as pd
b = pd.read_csv(sys.argv[1], parse_dates=["date"]).sort_values("date")
n = pd.read_csv(sys.argv[2], parse_dates=["date"]).sort_values("date")
b["prev"] = b.close.shift(1); n["prev"] = n.close.shift(1)
m = b.merge(n[["date","low","open","prev"]], on="date", suffixes=("","_idx")).dropna()
m["etf_dip"] = m.low/m.prev - 1; m["idx_dip"] = m.low_idx/m.prev_idx - 1; m["etf_open_dip"] = m.open/m.prev - 1; m["year"] = m.date.dt.year
print("Days when the ETF low crossed X% below its previous close while the Nifty low stayed above -3%:")
for X in (3,5,8,10,12):
    f = m[(m.etf_dip <= -X/100) & (m.idx_dip > -0.03)]
    print(f"  X={X:>2}%: {len(f):3d} days since {m.year.min()}; since 2015: {len(f[f.year>=2015]):3d}; since 2020: {len(f[f.year>=2020]):3d}; since 2023: {len(f[f.year>=2023]):3d}")
f8 = m[(m.etf_dip <= -0.08) & (m.idx_dip > -0.03)]
print("Of the 8% cases, opening prints:", int((f8.etf_open_dip <= -0.08).sum()), "intraday:", int((f8.etf_open_dip > -0.08).sum()))
post = m[m.date >= "2026-09-07"]
print(f"Since the ETF price-band norms of 7 Sep 2026: {len(post)} sessions, worst ETF dip {post.etf_dip.min()*100:.1f}%, worst index dip {post.idx_dip.min()*100:.1f}%")
print("\nWorst 12 ETF-only prints since 2021:")
w = m[(m.date >= "2021-01-01") & (m.idx_dip > -0.03)].nsmallest(12, "etf_dip")
print(w[["date","prev","open","low","close","etf_dip","idx_dip"]].assign(etf_dip=lambda d:(d.etf_dip*100).round(1), idx_dip=lambda d:(d.idx_dip*100).round(1)).to_string(index=False))
