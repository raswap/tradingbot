import json, re, subprocess, time, datetime as dt, html
UA = "tradebot-research/0.1 (owner research; contact via github raswap/tradingbot)"
EVENTS = [
 ("2008-10-29","gap-up +6.4%"),("2011-08-09","gap-down streak (3 days)"),("2011-09-23","gap-down streak"),("2011-11-02","governor halt, SMA100"),
 ("2012-07-23","governor halt, SMA200"),("2012-10-05","index flash crash -16% intraday"),("2013-07-11","exit into gap-up"),("2013-10-07","governor halt, SMA200"),
 ("2013-11-11","governor halt, SMA100"),("2014-12-18","exit into gap-up"),("2015-01-08","exit into gap-up"),("2015-06-29","governor halt, SMA200"),
 ("2015-08-12","governor halt, SMA50"),("2015-10-28","governor halt, SMA100"),("2016-11-09","gap-down -5.6%"),("2016-11-16","exit into gap-up"),
 ("2018-02-06","gap-down -3.5% (worst while invested, SMA100)"),("2018-06-20","NIFTYBEES print -19%"),("2018-12-11","gap-down streak"),
 ("2020-03-12","gap-down -4.0%"),("2020-03-13","gap-down -5.0%, then +3.8% close"),("2020-03-16","gap-down -3.7%, start of 6-day streak"),("2020-03-19","gap-down -4.8%"),
 ("2020-03-23","gap-down -9.1%, worst day -13%"),("2020-03-27","gap-up +3.6%"),("2020-04-07","gap-up +4.5% after long weekend"),("2020-05-13","gap-up +4.2%"),
 ("2020-05-26","NIFTYBEES print -12%"),("2020-06-12","gap-down -3.6%"),("2020-09-04","NIFTYBEES print -15.6%"),("2020-10-27","NIFTYBEES opening print -13.6%"),
 ("2021-04-20","NIFTYBEES opening print -14.3%"),("2021-07-30","NIFTYBEES print -20%"),("2022-02-25","exit into gap-up"),("2022-03-02","gap-down streak"),
 ("2022-04-25","governor halt, SMA50"),("2022-05-09","gap-down streak"),("2022-06-13","gap-down streak"),("2022-09-26","governor halt, SMA200"),("2022-10-04","exit into gap-up"),
 ("2024-06-03","gap-up +3.6% (Monday)"),("2024-06-05","exit into gap-up"),("2025-04-07","gap-down -5.0% (Monday)"),("2025-05-12","exit into gap-up"),
 ("2025-06-13","governor halt, SMA200"),("2026-02-03","gap-up +4.9%, exit into gap-up"),("2026-03-04","gap-down streak"),("2026-04-08","gap-up +3.2%"),
]
KEYS = re.compile(r"market|stock|share|index|econom|bank|rate|Fed|Federal Reserve|RBI|Reserve Bank|oil|crude|tariff|trade|election|poll|budget|war|invasion|invade|attack|missile|strike|COVID|coronavirus|lockdown|pandemic|demonet|currency|rupee|default|downgrade|GDP|inflation|recession|Sensex|Nifty|India|Pakistan|China|Ukraine|Russia|Iran|Israel|United States|U\.S\.|Trump|Modi|crisis|bailout|Lehman|debt", re.I)

def clean(w):
    w = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", w, flags=re.S)
    w = re.sub(r"\{\{[^{}]*\}\}", "", w)
    w = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", w)
    w = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", w)
    w = re.sub(r"'{2,}", "", w)
    return html.unescape(w).strip()

def wiki_day(d):
    page = f"Portal:Current_events/{d.year}_{d.strftime('%B')}_{d.day}"
    url = f"https://en.wikipedia.org/w/api.php?action=parse&page={page}&prop=wikitext&format=json&formatversion=2"
    try:
        raw = subprocess.run(["curl","-sS","--max-time","30","-A",UA,url], capture_output=True, text=True, timeout=40).stdout
        wt = json.loads(raw)["parse"]["wikitext"]
    except Exception as e:
        return []
    lines = [clean(l.lstrip("*").strip()) for l in wt.splitlines() if l.startswith("*")]
    lines = [l for l in lines if l and KEYS.search(l)]
    return lines

def gdelt(d):
    s = d.strftime("%Y%m%d") + "030000"; e = (d + dt.timedelta(days=1)).strftime("%Y%m%d") + "030000"
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?query=(Sensex%20OR%20Nifty)%20sourcelang:eng&mode=artlist&startdatetime={s}&enddatetime={e}&format=json&maxrecords=8&sort=hybridrel"
    for attempt in range(3):
        raw = subprocess.run(["curl","-sS","--max-time","30","-A","Mozilla/5.0",url], capture_output=True, text=True, timeout=40).stdout
        if raw.startswith("Please limit"): time.sleep(6); continue
        try:
            arts = json.loads(raw).get("articles", [])
            seen = set(); out = []
            for a in arts:
                t = re.sub(r"\s+"," ",a.get("title","")).strip()
                if t and t.lower() not in seen: seen.add(t.lower()); out.append((t, a.get("domain","")))
            return out[:5]
        except Exception: return []
    return []

results = []
for ds, label in EVENTS:
    d = dt.date.fromisoformat(ds)
    wiki = wiki_day(d - dt.timedelta(days=1))[:4] + wiki_day(d)[:4]
    gd = gdelt(d) if d >= dt.date(2017,1,1) else []
    time.sleep(5.2)
    results.append({"date": ds, "label": label, "wiki": wiki, "gdelt": gd})
    print(f"{ds} | {label}")
    for w in wiki[:5]: print("   W:", w[:170])
    for t, dom in gd[:4]: print("   G:", t[:150], f"({dom})")
json.dump(results, open("event_attribution.json","w"), indent=1, ensure_ascii=False)
print("\nsaved event_attribution.json")
