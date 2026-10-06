"""Refined Wikipedia lookup: only the 'Business and economy' and 'Politics and elections' sections of the
current-events pages for the two previous days and the event day, ranked by market relevance."""
import json, re, subprocess, time, datetime as dt, html
UA = "tradebot-research/0.1 (owner research; contact via github raswap/tradingbot)"
res = json.load(open("event_attribution.json"))
ECON = re.compile(r"stock|market|Sensex|Nifty|index|indices|econom|bank|Fed\b|Federal Reserve|RBI|Reserve Bank|oil|crude|tariff|trade war|currency|rupee|yuan|dollar|default|downgrade|GDP|inflation|recession|rate|bailout|Lehman|debt|budget|demonet|lockdown|coronavirus|COVID|election|exit poll|ceasefire|invasion|strikes? on|missile", re.I)
def clean(w):
    w = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", w, flags=re.S); w = re.sub(r"\{\{[^{}]*\}\}", "", w)
    w = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", w); w = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", w)
    w = re.sub(r"'{2,}", "", w); w = re.sub(r"\s+", " ", w); return html.unescape(w).strip()
def sections(d):
    page = f"Portal:Current_events/{d.year}_{d.strftime('%B')}_{d.day}"
    url = f"https://en.wikipedia.org/w/api.php?action=parse&page={page}&prop=wikitext&format=json&formatversion=2"
    try:
        raw = subprocess.run(["curl","-sS","--max-time","30","-A",UA,url], capture_output=True, text=True, timeout=40).stdout
        wt = json.loads(raw)["parse"]["wikitext"]
    except Exception: return []
    out = []; sec = ""
    for l in wt.splitlines():
        if l.startswith(";"): sec = l.lstrip(";").strip().lower(); continue
        if l.startswith("*"):
            txt = clean(l.lstrip("*").strip())
            if not txt or len(txt) < 25: continue
            econ = "business" in sec or "econom" in sec
            pol = "politic" in sec or "election" in sec
            if econ or (pol and ECON.search(txt)) or (ECON.search(txt) and re.search(r"stock|market|Sensex|Nifty|rupee|RBI|tariff|lockdown", txt, re.I)):
                out.append((2 if econ else 1, f"{d.isoformat()}: {txt}"))
    return out
for r in res:
    d = dt.date.fromisoformat(r["date"])
    lines = []
    for k in (2, 1, 0):
        lines += sections(d - dt.timedelta(days=k)); time.sleep(0.25)
    lines.sort(key=lambda x: -x[0])
    r["wiki_business"] = [t for _, t in lines][:5]
    print(r["date"], "|", r["label"]); [print("   B:", t[:170]) for t in r["wiki_business"][:4]]
json.dump(res, open("event_attribution.json","w"), indent=1, ensure_ascii=False)
print("\nsaved")
