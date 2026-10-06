# Governor, backstop and gap analysis for the S1 ETF trend bot

Date: 2026-10-06. Inputs: `data/research/` (Nifty 50 price index 2007-09 to 2026-10; NIFTYBEES 2009-01 to 2026-10, split-adjusted). Scripts and exact outputs: `docs/research/analysis/`. Purpose: evidence for PRD decisions 3, 9 and 10 (Appendix B) and for the owner's question on opening gaps.

Method in one line: replay the S1 bot as PRD v1.11 specifies it (close-of-T decision, T+1 open fill with 5 bps slippage, governor halve at −6% released above −3%, REDUCING at −10%, HALT and flatten at −12%, epoch breach at −12% on the epoch peak, backstop level −13.5%), with the governor checked at each session's low because live it runs every minute. No charges, no tax, price index without dividends. Caveats are in the data README.

## 1. The governor on the index (what a sanitised price looks like)

Buy-and-hold on the price index over the same span: 8.8% a year, maximum drawdown −59.9%.

| SMA | Exposure | CAGR | Time invested | Halvings | Halts (all epoch breaches) | Halt dates |
|---|---|---|---|---|---|---|
| 50 | 1.0 | 5.6% | 60% | 24 | 5 | 2008-08-28, 2009-10-27, 2012-10-05, 2015-08-12, 2022-04-25 |
| 50 | 0.7 | 4.0% | 62% | 12 | 1 | 2009-02-02 |
| 50 | 0.5 | 2.7% | 62% | 7 | 0 | |
| 100 | 1.0 | 7.0% | 63% | 20 | 4 | 2011-11-02, 2012-10-05, 2013-11-11, 2015-10-28 |
| 100 | 0.7 | 4.6% | 64% | 9 | 1 | 2012-08-31 |
| 100 | 0.5 | 2.8% | 64% | 10 | 0 | |
| 150 | 1.0 | 6.2% | 65% | 23 | 6 | 2011-07-08, 2012-07-23, 2012-10-05, 2013-11-13, 2016-04-05, 2022-09-28 |
| 150 | 0.7 | 3.9% | 67% | 11 | 1 | 2012-03-29 |
| 150 | 0.5 | 2.8% | 67% | 10 | 1 | 2012-10-05 (index flash crash; the ETF did not print it) |
| 200 | 1.0 | 5.4% | 67% | 24 | 6 | 2012-07-23, 2012-10-05, 2013-10-07, 2015-06-29, 2022-09-26, 2025-06-13 |
| 200 | 0.7 | 3.4% | 71% | 13 | 1 | 2016-04-28 |
| 200 | 0.5 | 2.7% | 71% | 6 | 0 | |

Readings:
- At full exposure the governor halts 4 to 6 times in 19 years; at 70% once; only 50% never halts (except the 150-day filter on the 2012 flash crash).
- The §10.2 Backtest → Paper criterion (2), "the governor never reaches HALTED", is therefore satisfied only at 50% exposure, where the return is about 2.7% a year on the price index, roughly 4% with dividends, which cannot beat the RM benchmark. Decision 10 in Appendix B.
- Halvings run at about one a year at full exposure, each a trim sale plus a top-up buy needing approval.
- The backstop level (−13.5% epoch drawdown) was touched on at most one day per configuration: 5 October 2012, the index flash crash caused by erroneous orders, which NIFTYBEES itself did not print (exchange low that day −1.3%). No opening gap ever jumped through both −12% and −13.5% at once.

## 2. The governor on raw ETF prices (unsanitised last traded price)

The same replay on NIFTYBEES's own highs and lows, 2009 to 2026: 13 to 19 halts at full exposure and 44 halvings, most of them caused by prints far below fair value rather than by the market. From 2023 onward the same replay shows 0 to 1 halts. Marking portfolio value at the raw last traded price is therefore unsafe; decision 9 in Appendix B proposes marking at the ETF's published fair value, or at the last traded price only when it lies inside the fair-value band.

## 3. ETF prints that would trigger a stop on last traded price

Days when the NIFTYBEES low crossed a level X% below its previous close while the Nifty's own low stayed within 3%:

| X | Since 2009 | Since 2015 | Since 2020 | Since 2023 |
|---|---|---|---|---|
| 3% | 119 | 93 | 75 | 8 |
| 5% | 68 | 56 | 46 | 0 |
| 8% | 35 | 27 | 24 | 0 |
| 10% | 23 | 17 | 15 | 0 |
| 12% | 21 | 15 | 13 | 0 |

Of the 35 cases at 8%, 16 were the opening print itself and 19 were intraday. The worst since 2021: 30 July 2021, low 20.3% below the previous close on a day the index moved 0.2%. The exchange bhavcopies confirm these prints (see the data README). Since the ETF price-band norms of 7 September 2026, 18 sessions, the worst ETF dip is −1.7% against an index dip of −1.8%.

Consequence: a GTT that triggers on last traded price would have fired on a false print several times a year in 2020 to 2022 and never since 2023. The bands make a recurrence unlikely but not impossible, which is why a GTT fill halts live trading until the owner reviews it (decision 3, agreed) and why the GTT limit offset deserves a decision of its own.

## 4. Opening gaps

| Opening gap, Nifty 50, 4,671 sessions | All days | Mondays | After a 4+ day break |
|---|---|---|---|
| Days with a gap of 1% or more either way | 5.9% | 8.7% | 10.2% |
| 1-in-100 worst gap-down | −1.6% | −2.3% | −1.4% |
| 1-in-1000 worst gap-down | −4.3% | −5.3% | −3.1% |

Worst gap-downs: −9.1% (2020-03-23), −5.6% (2016-11-09), −5.0% (2020-03-13), −5.0% (2025-04-07), −4.8% (2020-03-19). Streaks of two or more consecutive gap-down days of 1% or more: 9 in 19 years, the longest six days in March 2020 with the gaps alone summing to −16% over five sessions.

What the bot faced while invested (100-day filter, invested 65% of the time): gap-downs of 2% or more on 5 days, of 3% or more on 1 day, of 5% or more on none; worst −3.5% on 2018-02-06. The 200-day filter, slower to exit, met one gap of 5% or more (−5.6% on 2016-11-09). The 2% drift check on entries bit 0 to 1 times in 19 years. Exits executed into an opening gap-up of 1% or more: 4 of the 100-day filter's exits and 7 of the 200-day filter's, including the +4.9% open of 2026-02-03.

Mondays and post-holiday sessions carry wider tails but no negative average gap while invested, so no weekday rule is warranted.

## 5. What was happening on those days

See section 6, filled from recorded sources (Wikipedia current-events pages for every date; GDELT headlines for dates from 2017). The attribution output is `docs/research/analysis/event_attribution.json`.

## 6. Event attribution

(pending: the event attribution job is running; this section is filled in the next commit)

## 7. Implications for the PRD

1. **K1 mark price** (decision 9): mark NAV at the iNAV when it is fresh, else at the last traded price only when it lies within the iNAV band of the previous mark; otherwise the mark is stale. Protects the governor from prints; does not protect the broker-side GTT, which triggers at the exchange.
2. **Gate criterion (2)** (decision 10): "never HALTED over the whole backtest" admits only 50% exposure. Options: keep it and accept the likely OD-14 outcome; count halts per epoch and allow at most one epoch breach per N years; or evaluate the criterion over the last ten years only. Owner's call, since it sets the risk the owner is taking.
3. **E9 GTT limit offset**: a false trigger can fill as far as 3% below the trigger into a thin book. A tighter offset limits false-trigger damage but fills less reliably in a real gap. Owner's call; propose 1% as the new default for discussion.
4. **Exit into a gap-up**: a re-check of the signal at the open before a strategy exit would have avoided 4 to 7 whipsaws in 19 years. A strategy change, so the first L4 challenger, not a v1 change.
5. **Corporate actions**: the 1:10 NIFTYBEES split of 19 December 2019 is real and visible in Yahoo's unadjusted series; D6 and §16.2 #12 stand.
6. **Weekends and holidays**: no change; the evening arming of the GTT before every break is the right design.
