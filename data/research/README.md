# Research data (not platform data)

These files exist for PRD evidence and design decisions only. The platform itself never reads them: its sources are the ones in PRD §8.1 (NSE bhavcopies, Kite candles, niftyindices.com), and Yahoo Finance is never a platform source (PRD §15).

| File | Content | Rows | Span | Source |
|---|---|---|---|---|
| `nifty50_daily_ohlc.csv` | Nifty 50 price index, daily open, high, low, close | 4,672 | 2007-09-17 to 2026-10-01 | Yahoo Finance chart API, symbol `^NSEI`, fetched 2026-10-05 |
| `niftybees_daily_ohlc_splitadj.csv` | NIFTYBEES ETF, daily open, high, low, close, on the post-split price scale | 4,379 | 2009-01-02 to 2026-10-02 | Yahoo Finance chart API, symbol `NIFTYBEES.NS`, fetched 2026-10-05 |

## Normalisation applied

1. ISO dates (`YYYY-MM-DD`), one row per session, sorted ascending, duplicates dropped.
2. Rows with a non-positive price or high below low dropped (none in the index series; a handful in the ETF series).
3. Prices rounded to 2 decimals. Volume dropped (meaningless for the index; unreliable for the ETF around the split).
4. NIFTYBEES: prices before 2019-12-19 divided by 10. The exchange bhavcopy for 19 Dec 2019 shows the previous close as 1292.54 and the open as 129.20, a 1:10 split; Yahoo's series was not adjusted for it.

## Verification against primary records

- Nifty 50 closes checked on 2008-01-08, 2008-10-24 (low 2,525.05), 2020-03-23 (close 7,610.25) and 2024-09-27 (high 26,277.35): all match the published values.
- NIFTYBEES lows checked against NSE bhavcopies (`cm<DD><MON><YYYY>bhav.csv`) for 2020-01-13, 2020-05-26 (low 84.60), 2020-09-04 (low 102.26), 2020-10-27 (open and low 109.50), 2021-04-20 (open and low 132.00), 2021-07-30 (low 135.51), 2012-10-05 (low 575.00 on the pre-split scale) and 2019-12-19: all match. The deep ETF lows are real exchange prints, not data errors.
- The official niftyindices.com history API could not be used from the research environment (it returned a web page), so the index series is Yahoo's, validated by the spot checks above.

## Known limitations

- The index series is the **price** index, not the total-return index: dividends are excluded, which understates buy-and-hold and the bot alike by roughly 1.2 to 1.5 points a year.
- The series starts in September 2007, so the January 2008 top and the first leg of the 2008 crash are only partly inside the moving-average warm-up.
- Daily highs and lows stand in for the intraday path; the governor's one-minute marks are approximated by the session low.

## Terms

Yahoo Finance and NSE restrict redistribution of their data. These copies are kept in the owner's private repository for the owner's own research; do not publish or redistribute them.

## Checksums (sha256, first 16 hex)

- `nifty50_daily_ohlc.csv`: `91af9574238f93c2`
- `niftybees_daily_ohlc_splitadj.csv`: `f5151b8c5a3cc5bb`
