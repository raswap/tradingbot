import json, sys, subprocess, datetime as dt, zoneinfo
sym, out = sys.argv[1], sys.argv[2]
url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=946684800&period2=1791500000&interval=1d&events=div%2Csplit"
raw = subprocess.run(["curl","-sS","--max-time","60","-A","Mozilla/5.0",url], capture_output=True, text=True, check=True).stdout
j = json.loads(raw)["chart"]["result"][0]
ts = j["timestamp"]; q = j["indicators"]["quote"][0]; adj = j["indicators"].get("adjclose",[{}])[0].get("adjclose",[None]*len(ts))
ist = zoneinfo.ZoneInfo("Asia/Kolkata")
rows = []
for i,t in enumerate(ts):
    if q["close"][i] is None or q["open"][i] is None: continue
    d = dt.datetime.fromtimestamp(t, ist).date()
    rows.append((d, q["open"][i], q["high"][i], q["low"][i], q["close"][i], adj[i], q["volume"][i]))
with open(out,"w") as f:
    f.write("date,open,high,low,close,adjclose,volume\n")
    for r in rows: f.write(",".join(str(x) for x in r)+"\n")
ev = j.get("events",{})
print(f"{sym}: {len(rows)} rows, {rows[0][0]} to {rows[-1][0]}; splits: {[(dt.datetime.fromtimestamp(int(k),ist).date(), v.get('splitRatio')) for k,v in ev.get('splits',{}).items()]}; dividends: {len(ev.get('dividends',{}))}")
print("first rows:", rows[:2]); print("last rows:", rows[-2:])
