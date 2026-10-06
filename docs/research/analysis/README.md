# Analysis scripts and captured outputs (2026-10-05/06)

Inputs are the normalised series in `data/research/`. Each `out_*.txt` file is the exact output of the script named in it, so the numbers quoted in the research notes and the PRD can be regenerated.

| Script | Purpose | Output |
|---|---|---|
| `yahoo_fetch.py SYMBOL out.csv` | Fetches a raw daily series from the Yahoo chart API (research only). | raw CSV, not committed |
| `backstop_sim.py series.csv [start]` | Replays the S1 ETF trend bot with the K1 governor (halve at −6, release above −3, REDUCING at −10, HALT and flatten at −12, epoch breach at −12 on the epoch peak) and counts touches of the E9 backstop level (−13.5% epoch drawdown) by scenario: gap, intraday, spike. | `out_backstop_sim_nifty50.txt`, `out_backstop_sim_niftybees.txt`, `out_backstop_sim_niftybees_2023on.txt` |
| `gap_analysis.py series.csv` | Opening-gap distribution by weekday and after long breaks, streaks, the gaps the bot faced while invested, drift-check drops, exits into gap-ups. | `out_gap_analysis_nifty50.txt` |
| `etf_prints.py etf.csv index.csv` | ETF prints far below the previous close on days the index barely moved (false-trigger risk for a GTT on last traded price). | `out_etf_prints.txt` |

Conventions follow PRD v1.11: decision at close T, fill at the T+1 open with 5 bps slippage, no charges or tax, governor evaluated at the session low, backtest resumption after a cool-off of 20 sessions with the reference peak reset, one epoch per resumption.

| `attribute_events.py` | For each event date, fetches the Wikipedia current-events page (event day and the day before) and GDELT headlines matching Sensex or Nifty (from 2017), spaced to GDELT's one-request-per-5-seconds limit. | `event_attribution.json` |
| `wiki_business.py` | Refines the Wikipedia context to the business and politics sections over the two previous days and the event day, ranked by market relevance. | adds `wiki_business` to `event_attribution.json` |
