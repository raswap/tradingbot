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

See section 6.

## 6. Event attribution

Sources: Wikipedia Portal:Current events pages (business and economy, politics and elections sections) for the event day and the two days before; GDELT 2.0 DOC API headlines matching Sensex or Nifty on the event day (coverage from 2017). Raw output: `docs/research/analysis/event_attribution.json`.

| Date | Event in the analysis | Recorded context (Wikipedia current events, business and politics sections, up to two days before) | Indian market headlines that day (GDELT, available from 2017) |
|---|---|---|---|
| 2008-10-29 | gap-up +6.4% | no economic entry found | before GDELT coverage |
| 2011-08-09 | gap-down streak (3 days) | 2011-08-08: Stock markets in Asia, Australia, and the United States fall further after the credit rating of the United States is downgraded with the D; 2011-08-09: August 2011 stock markets fall | before GDELT coverage |
| 2011-09-23 | gap-down streak | 2011-09-21: United Technologies Corporation announced that it reached an agreement to purchase Goodrich Corporation, manufacturer of spacecraft attitu; 2011-09-22: World stock markets plunge amid growing global fears of recession. (Sky News) | before GDELT coverage |
| 2011-11-02 | governor halt, SMA100 | 2011-10-31: The Government of Japan intervenes to reduce the exchange rate of the Japanese yen with the United States dollar after the yen reached rec; 2011-10-31: US brokerage firm MF Global files for Chapter 11 bankruptcy after declaring £4bn of Eurozone debt exposure. (BBC) | before GDELT coverage |
| 2012-07-23 | governor halt, SMA200 | 2012-07-23: Syria Foreign Ministry spokesman Jihad Makdissi declares that Syria has stockpiles of chemical and biological weapons and that it plans to | before GDELT coverage |
| 2012-10-05 | index flash crash -16% intraday | 2012-10-04: Jordan's official news agency announces that King Abdullah dissolves parliament, paving the way for early elections. (BBC) | before GDELT coverage |
| 2013-07-11 | exit into gap-up | no economic entry found | before GDELT coverage |
| 2013-10-07 | governor halt, SMA200 | no economic entry found | before GDELT coverage |
| 2013-11-11 | governor halt, SMA100 | no economic entry found | before GDELT coverage |
| 2014-12-18 | exit into gap-up | no economic entry found | before GDELT coverage |
| 2015-01-08 | exit into gap-up | no economic entry found | before GDELT coverage |
| 2015-06-29 | governor halt, SMA200 | 2015-06-29: Puerto Rico government-debt crisis; 2015-06-29: Governor Alejandro García Padilla said the region has failed attempts and is unable to pay off the $72 billion debt. (USA Today) | before GDELT coverage |
| 2015-08-12 | governor halt, SMA50 | 2015-08-11: The People's Bank of China devalues the Chinese yuan by two percent in an attempt to boost its economy, a move which could spark a currenc | before GDELT coverage |
| 2015-10-28 | governor halt, SMA100 | 2015-10-26: USAA, one of the largest financial services companies in the U.S., announced the ending of its long-term relationship with MasterCard. The | before GDELT coverage |
| 2016-11-09 | gap-down -5.6% | no economic entry found | before GDELT coverage |
| 2016-11-16 | exit into gap-up | 2016-11-14: Aftermath of the Bulgarian presidential election, 2016; 2016-11-14: Bulgarian Prime Minister Boyko Borissov resigns as a result of Socialist-backed Rumen Radev winning the presidential election. (Reuters) | before GDELT coverage |
| 2018-02-06 | gap-down -3.5% (worst while invested, SMA100) | 2018-02-05: The Wall Street stock market sheds 4.6% of its value, with the Dow Jones Industrial Average dropping a record 1,175 points at close. At on | Closing bell : After massacre at D - street , Sensex falls 561 pts , Nifty ends below 10 , 500 mark ; Sensex continues freefall , plunges by 1200 points Latest News - NewsNow . in |
| 2018-06-20 | NIFTYBEES print -19% | no economic entry found | Tata Steel dispatches Ferro chrome from Gopalpur Industrial park Latest News - NewsNow . in; Sensex surges 261 points on global rebound ; RIL ends at record high Latest News - NewsNow . in |
| 2018-12-11 | gap-down streak | 2018-12-10: The Governor of the Reserve Bank of India, Urjit Patel, resigns abruptly. (Reuters); 2018-12-09: 2018 Armenian parliamentary election | Market overlooks BJP poll defeat : Sensex , Nifty see a dip , but not a crash; Sensex down by over 500 points , rupee crashes 1 . 5 % following RBI governor resignation |
| 2020-03-12 | gap-down -4.0% | 2020-03-12: Black Thursday, economic impact of the COVID-19 pandemic; 2020-03-12: All three major United States trading indexes fall 7% during early trading, leading to a 15-minute trading halt. They all closed over 9% d | no headline matched |
| 2020-03-13 | gap-down -5.0%, then +3.8% close | no economic entry found | Market trading halted for 45 minutes after Nifty slides 10 %; BSE , NSE stop trading as panic grips stock markets |
| 2020-03-16 | gap-down -3.7%, start of 6-day streak | 2020-03-14: Economic impact of the COVID-19 pandemic; 2020-03-14: Apple Inc. says it will close all of its stores outside China for two weeks in response to the coronavirus pandemic, according to its CEO  | no headline matched |
| 2020-03-19 | gap-down -4.8% | 2020-03-17: Economic impact of the COVID-19 pandemic; 2020-03-18: Economic impact of the COVID-19 pandemic | Share Market Today LIVE / Sensex , Nifty , BSE , NSE , Share Prices , Stock Market News Updates Marc; Sensex , Nifty off 33 % from record high levels , key factors that pulled down Dalal Street |
| 2020-03-23 | gap-down -9.1%, worst day -13% | no economic entry found | Sensex records worst day in history , crashes 3 , 934 points; Coronavirus wipes out Rs 14 lakh crore wealth as Sensex , Nifty log biggest session loss |
| 2020-03-27 | gap-up +3.6% | no economic entry found | no headline matched |
| 2020-04-07 | gap-up +4.5% after long weekend | no economic entry found | Sensex surges 1 , 500 points : Top stocks leading the bull charge today; These 87 stocks hit 52 - week lows on NSE even as Sensex , Nifty continue with bull run on D - Stree |
| 2020-05-13 | gap-up +4.2% | no economic entry found | Share Market LIVE : Sensex climbs 1 , 400 points at pre - open , Nifty at 9 , 585 , Jubilant Life Sc; Closing Bell : Sensex , Nifty rise 2 % after PM Modi announces economic stimulus ; banks , autos gai |
| 2020-05-26 | NIFTYBEES print -12% | no economic entry found | HDFC Bank , ITC lift Sensex over 400 points , Nifty tops 9 , 150 ; check what moving D - Street toda; Share Market LIVE : Sensex rises 350 points , Nifty at 9 , 125 ; JSW Steel , ITC , HDFC Bank top per |
| 2020-06-12 | gap-down -3.6% | no economic entry found | Share Market Today LIVE / Sensex , Nifty , BSE , NSE , Share Prices , Stock Market News Updates June; Sensex , Nifty bounce back as US markets make a U - turn - The Hindu BusinessLine |
| 2020-09-04 | NIFTYBEES print -15.6% | no economic entry found | no headline matched |
| 2020-10-27 | NIFTYBEES opening print -13.6% | no economic entry found | no headline matched |
| 2021-04-20 | NIFTYBEES opening print -14.3% | no economic entry found | Sensex and Nifty close with losses of around half a per cent; Share Market Updates : Sensex , Nifty Fall For Second Straight Session Dragged By IT Shares |
| 2021-07-30 | NIFTYBEES print -20% | no economic entry found | Sensex Rockets 125 Points In Early Trade ; Nifty Tops 15 , 800; Share Market Updates : Sensex , Nifty End Flat ; Sun Pharma Surges Over 10 % On Strong Q1 Earnings |
| 2022-02-25 | exit into gap-up | no economic entry found | Sensex gains over 1 , 100 points , Nifty rises more than 350 points to trade above 16 , 500; Sensex , Nifty regain losses after opening in green zone |
| 2022-03-02 | gap-down streak | no economic entry found | no headline matched |
| 2022-04-25 | governor halt, SMA50 | no economic entry found | Share Market LIVE : Sensex , Nifty likely to open lower today; Sensex tumbles 617 points , Nifty ends below 17 , 000 |
| 2022-05-09 | gap-down streak | no economic entry found | no headline matched |
| 2022-06-13 | gap-down streak | no economic entry found | no headline matched |
| 2022-09-26 | governor halt, SMA200 | no economic entry found | no headline matched |
| 2022-10-04 | exit into gap-up | no economic entry found | Sensex gains over 1000 points in early trade ; Nifty gains over 255 points; Share Market News Today Live : Sensex jumps over 800 points amid positive global cues , Nifty trades |
| 2024-06-03 | gap-up +3.6% (Monday) | no economic entry found | Lok Sabha election result tomorrow : A look back at stock market performance on last 4 vote counting; Share Market Today LIVE Updates : Stock Market To Break Record ? GIFT Nifty Futures Rises Record Hig |
| 2024-06-05 | exit into gap-up | no economic entry found | no headline matched |
| 2025-04-07 | gap-down -5.0% (Monday) | no economic entry found | Sensex Today / Stock Market LIVE Updates : Sensex nosedives over 2 , 600 pts , Nifty below 22 , 000 ; Market Opening Bell : Sensex tanks over 3 , 900 points , Nifty down 5 per cent , all sectoral indice |
| 2025-05-12 | exit into gap-up | no economic entry found | Market Opening Bell : Bulls roar on Dalal Street , Sensex surges 1 , 350 points , Nifty above 24 , 4; Weekly Musings – Index performance for week ended May 09 , 2025 |
| 2025-06-13 | governor halt, SMA200 | no economic entry found | no headline matched |
| 2026-02-03 | gap-up +4.9%, exit into gap-up | no economic entry found | no headline matched |
| 2026-03-04 | gap-down streak | no economic entry found | no headline matched |
| 2026-04-08 | gap-up +3.2% | 2026-04-07: Iran threatens to launch massive retaliatory strikes against the energy infrastructure of Saudi Arabia and the UAE in the event of a U.S. ; 2026-04-08: Tariffs in the second Trump administration | Market cheers ceasefire in biggest rally this year so far , Sensex jumps nearly 2 , 950 points; Nifty 50 , Sensex prediction today : Check how Indian stock market is expected to trade on 8 April a |

**Reading the table** (interpretation, with the source of each claim):

- **Global shocks explain most large gaps and most governor halts.** The August 2011 streak followed the downgrade of the United States' credit rating; September 2011 was a global recession scare; the August 2015 halt followed China's devaluation of the yuan; the February 2018 gap followed the record 1,175-point fall of the Dow the previous night; March 2020 was the pandemic crash, with the 13 March circuit-breaker halt and the 23 March lockdown session, the worst day in the index's history; the 2022 streaks sit on the invasion of Ukraine and the Federal Reserve's hikes; 7 April 2025 was the tariff crash; 8 April 2026 was the rally on a United States–Iran ceasefire. All of these are in the fetched records.
- **Domestic shocks are rarer but real.** The 10 December 2018 resignation of the RBI governor is in the records. The −5.6% gap of 9 November 2016 and the June 2024 election days are known from the author's knowledge, not from the fetched records: demonetisation announced on the evening of 8 November 2016 together with the United States election result, and the exit polls and results of the Lok Sabha election on 3 and 4 June 2024 (GDELT confirms the exit-poll framing on 3 June).
- **The ETF prints had no news behind them.** On 26 May 2020, 4 September 2020, 27 October 2020, 20 April 2021 and 30 July 2021 the same-day headlines describe ordinary or rising sessions. The prints were not reactions to events, which is what makes them false triggers for a stop on the last traded price.
- **Governor halts on slow declines have no headline.** 23 July 2012, 7 October and 11 November 2013, 29 June and 28 October 2015, 25 April and 26 September 2022 are days when a long slide crossed the 12% line, not days with a single cause. A news feed would not have warned of them; the drawdown rules exist precisely for that.
- **Unexplained in the records:** the +4.9% gap-up of 3 February 2026 and the March 2026 streak. The author's knowledge does not cover them reliably either.
- **5 October 2012** was a flash crash caused by erroneous orders from one broker, from the author's knowledge; the records fetched do not mention it, and NIFTYBEES itself did not print the move.

## 7. Implications for the PRD

1. **K1 mark price** (decision 9): mark NAV at the iNAV when it is fresh, else at the last traded price only when it lies within the iNAV band of the previous mark; otherwise the mark is stale. Protects the governor from prints; does not protect the broker-side GTT, which triggers at the exchange.
2. **Gate criterion (2)** (decision 10): "never HALTED over the whole backtest" admits only 50% exposure. Options: keep it and accept the likely OD-14 outcome; count halts per epoch and allow at most one epoch breach per N years; or evaluate the criterion over the last ten years only. Owner's call, since it sets the risk the owner is taking.
3. **E9 GTT limit offset**: a false trigger can fill as far as 3% below the trigger into a thin book. A tighter offset limits false-trigger damage but fills less reliably in a real gap. Owner's call; propose 1% as the new default for discussion.
4. **Exit into a gap-up**: a re-check of the signal at the open before a strategy exit would have avoided 4 to 7 whipsaws in 19 years. A strategy change, so the first L4 challenger, not a v1 change.
5. **Corporate actions**: the 1:10 NIFTYBEES split of 19 December 2019 is real and visible in Yahoo's unadjusted series; D6 and §16.2 #12 stand.
6. **Weekends and holidays**: no change; the evening arming of the GTT before every break is the right design.
