> Generated 2026-09-30 by research workflow wf_4f373234-c5d (10 topic researchers + adversarial fact-checkers + synthesis + critic).
> Caveats: the fact-check pass for **strategy-evidence** (section 5) failed (API error), so section 5 figures are researcher-only. The critic ran after the WebSearch session cap and checked via direct fetches. **Read the Critique appendix first: it corrects the timeline, ITR form, TOTP claim and approve-stage algo status.**

# Personal NSE Multi-Bot Trading Platform: Research Brief

**As of 30 Sep 2026.** Every fact is as of that date unless another date is given. "(unverified)" means it could not be confirmed from a primary or reliable source in this research round. All effort and return estimates are engineering or research judgement, not sourced facts.

---

## 0. Your question: how much time will it take?

There are three separate timelines. Only the first one gets shorter if you work harder.

### A. Build time
Assumes you work solo at about 10-12 hours a week alongside your job. These are researcher estimates, not sourced.

| Piece | Effort | Notes |
|---|---|---|
| Compliance/admin: API app, static-IP VM, IP whitelisting, daily login | 1-2 days (unverified) | Registering the wrong IP costs you a week, because IPs can change only once per calendar week ([Zerodha](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip), [Dhan](https://dhanhq.co/docs/v2/authentication/)) |
| Data layer: NSE bhavcopies in two formats, corporate-action parsing, point-in-time universe, minute history, news archive | 40-60 h (4-6 weekends). A rough daily-bar pipeline takes about 2 weekends. | Fact-check raised this from 3-5 weekends because of hidden gotchas (see §8) |
| Broker adapter, token handling, global rate limiter, paper-fill simulator | 1-2 weeks, plus about 1 week for Kite login and IP work | |
| Risk engine, kill switches, reconciliation, Telegram approvals, monitoring | 6-10 weeks for the whole infra/risk layer. 3-5 weeks if OpenAlgo supplies the adapter and approval queue. | |
| Research harness: Indian cost model, vectorbt, walk-forward testing | 3-4 weeks | |
| Learn-from-mistakes loop: journal, CPCV/DSR/PBO gate, champion/challenger | 4-7 weekends, after the core exists | |

These pieces overlap. The combined estimate is **about 3-4 months to your first approve-each-trade live order and about 6-8 months to full auto**. Working full-time roughly halves the coding time, but not the soak periods below.

### B. Soak time (can't be compressed)
- **Paper trading:** at least 2-3 months per bot (50+ trades for higher-frequency bots). Its job is to check that live execution matches the backtest, not to prove the strategy has an edge.
- **Approve-each-trade:** another 4-8 weeks before full auto.
- **Static IP timing:** you don't need one until the approve stage. Market data works from any IP ([Zerodha](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip)).

### C. Proof time (the one that actually limits you)
The Minimum Track Record Length (MinTRL) is the number of daily returns needed to confirm a real edge at 95% confidence ([Bailey & Lopez de Prado](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643), recomputed):

| True annual Sharpe | Normal returns | Fat tails (skew -0.5, kurtosis 6) |
|---|---|---|
| 0.5 | ~2,730 days (10.8 yrs) | ~2,775 days |
| 1.0 | ~684 days (2.7 yrs) | ~708 days |
| 1.5 | ~305 days (~14-15 months) | ~322 days |
| 2.0 | ~173 days (0.7 yrs) | ~186 days |

**Your 12-month live window can only confirm a strategy with a true Sharpe of about 1.65-1.7 or higher.** Running many bots raises that bar further. Realistic positional strategies (Sharpe 0.5-1.0) need 3-11 years. So make scale-up a gradual ramp tied to statistics, not a single decision at month 12.

### Calendar if you start in Oct 2026
| When | Milestone |
|---|---|
| Oct 2026, week 1 | Start archiving NSE announcements and news RSS. No free historical Indian news archive exists. |
| Oct-Nov 2026 | Data layer, cost model, research harness. Backtest ETF trend and momentum strategies. |
| Dec 2026 | First bots in paper trading |
| Jan-Feb 2027 | First approve-each-trade live orders with small capital |
| Apr-Jun 2027 | Full auto for bots that passed the gates |
| Jan-Feb 2028 | 12 months of live data. First scale-up step, taken as a ramp. |
| 2027-28 | F&O on paper. Crypto maybe in year 2 (adapter about 1-2 weeks plus about 1 week for the tax ledger). |

**Fastest path (my estimate):** one daily-bar ETF trend bot, one broker, end-of-day data and Telegram approval would take about 4-6 part-time weeks to a first approved live order. The evidence favours exactly this kind of bot, so the full multi-bot, intraday machinery is not needed to start trading in year 1.

---

## 1. TL;DR

1. **Time:** about 3-4 months part-time to your first approved live trade and 6-8 months to full auto. Statistical proof takes years. Twelve months live only confirms a Sharpe of about 1.65 or higher (§0).
2. **Compliance is light if you stay under 10 orders/second across all bots** (a limit per exchange). You need a static IP, a daily OAuth/2FA login, limit or market-protection orders only, and all bots on one API key. No exchange registration is needed. "Approve each trade" through the API still counts as algo trading.
3. **Start with daily-bar positional ETF and equity bots. Keep intraday and F&O off live money in year 1.** 87.7% of individual F&O traders lost money in FY26, and 71% of intraday cash traders lost money in FY23. Costs and tax fall hardest on high turnover.
4. **Round-trip costs at Rs 50k per trade:** intraday 10.6 bps, delivery 25.3 bps, equity ETF about 5.4 bps. Derivatives STT rose on 1 Apr 2026. Swing profits are taxed at 20% STCG (about 20.8-23.9% effective). Intraday and F&O profits are taxed at your slab rate (about 31-39%), and those losses can't be set off against salary.
5. **No long-only equity strategy has historically stayed inside a 10-15% drawdown.** Nifty fell about 60% in 2008 and momentum indices fell 68-73%. A portfolio-level drawdown governor is mandatory. The benchmark is NIFTYBEES buy-and-hold, and for factor bots, the matching passive factor fund.
6. **Brokers:** Zerodha Kite Connect as primary (Rs 500/month, most mature API). Dhan as backup: it has the only official TOTP token API (for unattended daily login), zero delivery brokerage, and 5 years of expired-options data for later F&O research. Upstox has become less attractive: expired data needs a paid plan, and its Rs 10/order promo ends today.
7. **Monthly cost:** about Rs 2,000-2,500 for Kite Connect plus a static-IP AWS Lightsail VM in Mumbai plus a second IP. Free NSE archives and RSS feeds cover data and news.
8. **Stack:** a thin custom Python core on the official broker SDKs, with vectorbt (open source) for research. OpenAlgo is an optional shortcut; pin its version. Revisit NautilusTrader when v2 is stable.
9. **ML only as a filter or sizer on rule-based bots,** gated by the Deflated Sharpe Ratio, backtest-overfitting probability and shadow trading. LLMs only turn news into features. Every LLM-trader benchmark from 2025-26 failed to beat buy-and-hold reliably.
10. **Crypto:** maybe in year 2, one low-frequency BTC/ETH bot on Delta Exchange India. The tax rules (30% plus surcharge, no loss set-off) kill high-turnover strategies. **Forex:** skip. INR pairs are legally restricted to hedging a real exposure.

---

## 2. Rules the bot must follow

### 2.1 SEBI/NSE retail algo framework

| Rule | What it means for your bot | Source |
|---|---|---|
| The SEBI circular of 4 Feb 2025 is mandatory for all brokers from 1 Apr 2026. Go-live slipped from 1 Aug 2025 to 1 Oct 2025, then became a glide path (circular of 30 Sep 2025). | It applies to you now. No newer algo circular was found through Sep 2026. | [SEBI](https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html), [30 Sep 2025 circular](https://nsearchives.nseindia.com/content/circulars/INVG70541.zip) |
| Registration threshold: 10 orders/second per exchange, measured on the broker server's clock second. The threshold comes from the NSE standards, not the SEBI text. | Below it: no registration. Orders get the generic Algo ID 99999. Above it: registration through the broker, an auditor certificate, and write-ups of the strategy and risk checks. | [NSE/INVG/67858](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf), [NSE/INVG/69255](https://nsearchives.nseindia.com/content/circulars/INVG69255.zip) |
| Unregistered algos may run on only one predefined API key (A.4). The broker may set a lower per-client limit. | All bots must go through one order gateway with one global rate limiter. Zerodha's 10/s limit is per trading account, not per app. | [NSE/INVG/67858](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf), [Kite FAQ](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs) |
| Static IP: a primary plus an optional secondary, changeable at most once per calendar week, shareable only with family (self, spouse, dependent children and parents). | Applies only to order placement, modification and cancellation. Data, order book and positions calls work from any IP. Brokers differ: Zerodha allows family sharing by declaration, Dhan requires a unique IP per individual, Upstox forbids sharing across accounts. | [NSE A.1-A.7](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf), [Zerodha](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip) |
| Where the algo is hosted | The circular text says retail algos are hosted on broker servers (I.h, para 14). In practice, brokers require self-built algos to run on your own static-IP machine. Treat the broker docs as the rule that applies. | [NSE/INVG/69255](https://nsearchives.nseindia.com/content/circulars/INVG69255.zip) |
| OAuth or 2FA only. Every API session is logged out before the next trading day (A.8). | Plan a re-login every morning. Kite tokens expire at 6 AM ([Kite](https://kite.trade/docs/connect/v3/user/)). SEBI says "OAuth only", so broker TOTP endpoints could be withdrawn. | [NSE A.8](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf) |
| Plain market orders from algos are rejected upfront: currency derivatives from 28 Apr 2025, cash from 30 Jun 2025, F&O from 24 Jul 2025. Mismatched NNF ID/Algo ID is also rejected. | Send limit orders or market orders with protection. On Kite, market_protection must be above 0 and up to 100, or -1 for automatic; 0 is rejected. | [NSE/FAOP/69296](https://nsearchives.nseindia.com/content/circulars/FAOP69296.pdf), [Kite orders](https://kite.trade/docs/connect/v3/orders/) |
| The broker is liable, the exchange can kill a rogue algo, the client is responsible for strategy logic and risk checks, and brokers keep a 5-year audit trail. | Keep your own order audit log. It also feeds the learning loop. | [NSE I.a, I.f, J.3](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf) |
| "Approve each trade" via the API is still an algo order. | Static IP and the 10/s limit apply from the approve stage onward. | [Kite FAQ](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs) |
| Running bots for anyone outside your family makes you an algo provider. That needs exchange empanelment, plus Research Analyst registration for black-box algos. | Keep it strictly personal. | [SEBI](https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html) |

### 2.2 Exchange market-structure rules that affect execution
- **Closing Auction Session** (live 3 Aug 2026, [NSE/FAOP/74467](https://nsearchives.nseindia.com/content/circulars/FAOP74467.zip)): F&O trades until 15:40. Market orders can't be modified or cancelled between 15:25 and 15:30. There are no MOC/LOC order types and no IOC during the auction. Stock-futures orders outside the reset ±3% band are cancelled by the exchange, so expect unsolicited cancellations.
- **New ETF norms** covering base price, price bands, a pre-open call auction and close-out apply from 7 Sep 2026 (the start was moved from 1 Sep). An ETF-first bot must follow them ([SEBI 28 Aug 2026](https://www.sebi.gov.in/legal/circulars/aug-2026/extension-of-timeline-for-implementation-of-provisions-of-sebi-circular-dated-june-15-2026-on-norms-for-base-price-price-bands-call-auction-in-pre-open-session-and-close-out-procedure-for-exchange-_104094.html)).
- **Order-to-trade ratio framework revised** 4 Feb 2026, effective 6 Apr 2026. Equity-option orders within ±40% of LTP or ±Rs 20 (whichever is higher) are exempt ([NSE/SURV/72668](https://nsearchives.nseindia.com/content/circulars/SURV72668.zip)).
- **Rules may change again:** SEBI's consultation of 12 Sep 2026 on the closing auction, market timings and derivative settlement ([SEBI](https://www.sebi.gov.in/reports-and-statistics/reports/sep-2026/consultation-paper-on-review-of-certain-aspects-of-the-closing-auction-session-market-timings-and-settlement-methodologies-for-derivative-contracts-_104464.html)).

### 2.3 F&O curbs (why F&O stays on paper in year 1)
- **SEBI circular of 1 Oct 2024:** minimum index contract Rs 15 lakh, one weekly benchmark expiry per exchange, +2% extreme-loss margin on short options on expiry day, upfront premium collection, and no calendar-spread margin benefit on expiry day ([SEBI](https://www.sebi.gov.in/legal/circulars/oct-2024/measures-to-strengthen-equity-index-derivatives-framework-for-increased-investor-protection-and-market-stability_87208.html)).
- **Lot sizes from Jan 2026, still current for Oct-Dec 2026:** NIFTY 65, BANKNIFTY 30, FINNIFTY 60, MIDCPNIFTY 120, NIFTYNXT50 25 ([NSE lot file](https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv), [NSE/FAOP/70616](https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf)).
- **Expiry days:** NSE moved to Tuesday after 28 Aug 2025 EOD, with the first Tuesday weekly on 9 Sep 2025. BSE uses Thursday. There are no BANKNIFTY or FINNIFTY weeklies ([NSE/FAOP/68685](https://nsearchives.nseindia.com/content/circulars/FAOP68685.pdf)).
- **STT from 1 Apr 2026:** futures 0.05% on the sell side (was 0.02%). Options 0.15% of premium on the sell side (was 0.1%), and 0.15% of intrinsic value on exercise (was 0.125%) ([Budget memo](https://www.indiabudget.gov.in/doc/memo.pdf)).
- **Scale at Rs 2 lakh:** one NIFTY lot is about Rs 16 lakh notional. Naked short margin is roughly Rs 1.5-2.5 lakh per lot, and the extra 2% expiry-day margin alone is about Rs 32k (unverified; check a live margin calculator). Your whole drawdown budget is Rs 20-30k, so even a 1-lot defined-risk spread uses most of it.

---

## 3. Costs and taxes

### 3.1 Rate card (Zerodha, [charges page](https://zerodha.com/charges/))
- **Brokerage:** delivery 0; intraday and futures min(0.03%, Rs 20) per order; options Rs 20 per order.
- **STT:** delivery 0.1% on both buy and sell; intraday 0.025% on the sell side; futures 0.05% on the sell side; options 0.15% of premium on the sell side. Equity-oriented ETF sales pay 0.001% on the sell side (statutory schedule per [ClearTax](https://cleartax.in/s/securities-transaction-tax-stt); some broker summaries show 0.1%, so check one real contract note). Gold, liquid and gilt ETFs pay no STT ([Dhan](https://dhan.co/pricing/)).
- **NSE transaction charges from 1 Mar 2026:** cash 0.00307%, futures 0.00183%, options 0.03553% of premium ([Upstox](https://upstox.com/brokerage-charges/)).
- **Other charges:**
  - SEBI fee: Rs 10/crore.
  - GST: 18% on brokerage, exchange and SEBI charges.
  - Stamp duty, buy side only: delivery 0.015%, intraday 0.003%, futures 0.002%, options 0.003%.
  - DP charge: Rs 15.34 per scrip per sell day.
  - Auto square-off: Rs 50 + GST per order.

### 3.2 Round trips (buy and sell at the same price, no slippage)

| Segment, size | Brokerage | STT | Exchange | Stamp | GST | DP | **Total** | **bps** |
|---|---|---|---|---|---|---|---|---|
| Intraday equity, Rs 50k | 30.00 | 12.50 | 3.07 | 1.50 | 5.97 | – | **53.14** | **10.6** |
| Intraday equity, Rs 2L | 40.00 | 50.00 | 12.28 | 6.00 | 9.48 | – | **118.16** | **5.9** |
| Delivery equity, Rs 50k | 0 | 100.00 | 3.07 | 7.50 | 0.57 | 15.34 | **126.58** | **25.3** |
| Equity ETF delivery, Rs 50k | 0 | 0.50 | 3.07 | 7.50 | 0.57 | 15.34 | **27.08** | **5.4** |
| Equity ETF delivery, Rs 2L (my calc) | 0 | 2.00 | 12.28 | 30.00 | 2.28 | 15.34 | **62.30** | **3.1** |
| Stock futures, Rs 10L notional | 40.00 | 500.00 | 36.60 | 20.00 | 14.15 | – | **612.75** | **6.1** |
| Index options, Rs 50k premium | 40.00 | 75.00 | 35.53 | 1.50 | 13.61 | – | **165.74** | **33.1 of premium** |
| Index options, Rs 5k premium | 40.00 | 7.50 | 3.55 | 0.15 | 7.84 | – | **59.05** | **118 of premium** |

SEBI fees (Rs 0.01-2) are included in the totals. STT is 79% of the delivery cost, so the choice of broker barely matters for delivery. The fixed DP charge makes small delivery sells expensive: it is 15 bps on a Rs 10k sale.

### 3.3 Tax treatment
| Bucket | What falls in it | Rate | Rules |
|---|---|---|---|
| STCG (held 12 months or less) | Swing and positional delivery, equity ETFs | 20% + 4% cess, surcharge capped at 15%: about 20.8-23.9% | [ClearTax](https://cleartax.in/s/capital-gains-income) |
| LTCG (held over 12 months) | Same | 12.5% above Rs 1.25 lakh a year, no indexation | |
| Speculative business (code 21009) | Intraday equity | Slab rate: 31.2% (30% + cess) up to about 39% with 25% surcharge (surcharge figures from the standard schedule, not fetched) | Losses offset only speculative gains, carry forward 4 years, never against salary ([Varsity](https://zerodha.com/varsity/chapter/taxation-for-traders/)) |
| Non-speculative business (code 21010) | F&O | Slab rate | Carry forward 8 years. Speculative gains can absorb these losses, not the reverse. |
| VDA | Crypto | 30% + cess + surcharge (not capped at 15%) | No set-off, no carry-forward, 1% TDS (§11) |

**Other points:**
- **Filing:** returns go on ITR-3. The non-audit due date is now 31 Aug (moved from 31 Jul by Budget 2026). Losses carry forward only if you file on time ([ClearTax](https://cleartax.in/s/budget-2026-highlights)).
- **Tax audit:** applies only if turnover exceeds Rs 10 crore (cash 5% or less). For intraday and F&O, "turnover" is the sum of absolute P&L per trade, so this is unlikely at your size ([Varsity](https://zerodha.com/varsity/chapter/turnover-balance-sheet-and-pl/)).
- **Advance tax:** 15%/45%/75%/100% by 15 Jun/15 Sep/15 Dec/15 Mar once uncovered tax is Rs 10k or more. Salary TDS doesn't cover trading income. The bot should produce a P&L estimate before each date.
- **New law:** the Income-tax Act 2025 took effect 1 Apr 2026. It introduces a single "tax year" and new section numbers, with no change to rates. FY2025-26 returns still use the 1961 Act ([PRS](https://prsindia.org/billtrack/the-income-tax-bill-2025)). Label everything by concept (STCG, speculative), not by section number.
- **Delivery trades as business income:** very frequent delivery trading can be treated as business income. Choose one treatment with a CA and apply it consistently (CBDT Circular 6/2016; primary not fetched).
- **Budget 2026 changes:** buyback proceeds are now taxed as capital gains, and the interest-expense deduction against dividends is gone.

### 3.4 Break-even edge per trade, by horizon

| Horizon | Size | Cost | Slippage (assumed; calibrate from paper fills) | **Gross edge needed per round trip** | Annual cost drag example |
|---|---|---|---|---|---|
| Intraday | Rs 50k | 10.6 bps | 3-8 bps | **~15-20 bps** | 250 round trips/yr = Rs 13.3k (27% of Rs 50k deployed) |
| Intraday | Rs 2L | 5.9 bps | 3-8 bps | **~9-14 bps** | Order Rs 67k or more to hit the Rs 20 brokerage cap |
| Swing, equity delivery | Rs 50k | 25.3 bps | ~5 bps | **~30-35 bps** | 50 round trips/yr = Rs 6.3k (3.2% of Rs 2L) |
| Positional ETF | Rs 50k-2L | 3.1-5.4 bps | ~3-5 bps (trade near iNAV) | **~8-12 bps** | 10 switches/yr on Rs 2L = about Rs 620 (0.3%) |
| Options buying | Rs 5k-50k premium | 33-118 bps of premium | spread | **0.5-1.5%+ of premium** | Plus the base rate of ~91% of F&O traders losing |

After tax, you keep about 61-69% of intraday profit and about 76-79% of swing profit. Lower turnover wins twice.

**Implementation:** keep costs in a versioned table where every rate has an effective-from date (STT changed 1 Oct 2024 and 1 Apr 2026, NSE charges 1 Mar 2026). Otherwise backtests covering 2023-25 will look better than trading today would. Tag every fill with its tax bucket.

---

## 4. What the evidence says about retail outcomes

| Metric | Value | Source |
|---|---|---|
| Individuals losing money in equity derivatives | **87.7% FY26**; 90.9% FY25 (revised); 92.7% FY22-24 | [SEBI PR 50/2026, 20 Aug 2026](https://www.sebi.gov.in/media-and-notifications/press-releases/aug-2026/sebi-studies-indicate-key-trends-in-retail-participation-trading-behaviour-and-profitability-in-the-equity-derivatives_103838.html) |
| Individual net losses | Rs 91,685 cr FY26; Rs 1.12 lakh cr FY25; **Rs 2.03 lakh cr FY25-26, more than the Rs 1.81 lakh cr lost over FY22-24** | [SEBI profitability study](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233506209.pdf) |
| Average loss per trader, FY26 | Rs 1.17 lakh | same |
| Loss rate: options vs futures | 87.7% vs 66.0%; options caused 92% of losses | same |
| "Only options buyers" (93% of traders) | Median return on capital -187% (FY25), -114% (FY26) | [SEBI behaviour study](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233601328.pdf) (sample of ~5,050, indicative) |
| "Majorly options sellers" (~2%) | Median +1%, 44% loss rate, but a losing seller lost **Rs 51.7 lakh** on average | same |
| Profitable in all five years, FY22-26 | **0.5%**; 65.6% lost every year; 90-92% of two-year losers lost again | same |
| Traders active more than 100 days a year | 42% of traders, 87% of losses | same |
| Who wins | FY26 gross profit: prop desks about Rs 44k cr, FPIs about Rs 14k cr; 99% of it from algo entities; top 10 prop firms took 74.5% | [profitability study](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233506209.pdf) |
| Intraday cash, FY23 | 71% lost; 80% of those making 500+ trades a year; costs deepened losers' losses by 57% | [SEBI Jul 2024](https://www.sebi.gov.in/sebi_data/attachdocs/jul-2024/1721818140715.pdf) |

- **Algo use gives individuals no visible advantage.** SEBI flags a client as an algo user after a single algo trade, and broker auto square-off counts. The published figures also mix FY26 headcounts with FY25-26 losses. The only defensible conclusion is that there is no evidence algo use improves individual outcomes.
- **The Nov 2024 curbs** pushed out small and occasional traders. Premium turnover recovered to about Rs 82k cr a day by H2 FY26, and 97% of index-options turnover is still within 7 days of expiry.
- **No SEBI data covers retail delivery-based swing or positional cash trading**, which is your actual first market. The only related hint: F&O traders who did relatively more cash-market trading had lower loss rates.

**What the profitable minority does differently** (correlation, not causation):
- More capital and bigger portfolios: the loss rate falls from 93% (no holdings) to 58% (portfolios above Rs 10 cr).
- Older traders: 81% of those over 60 lose, against 89% of those under 30.
- Trades less: 83% loss rate for those active under 10 days a year, against 89% for over 100 days.
- More cash-market activity.
- Sells options rather than buys, which comes with large tail losses.

The winning institutions are market makers with colocation. None of this is a retail edge.

**For your bots:**
- Cap turnover per bot, not just drawdown.
- Treat loss asymmetry (median losing quarter -Rs 10.5k vs median winning quarter +Rs 4.4k), trading more after losses, and losses that persist as automatic kill-switch metrics.
- With small capital, losses tend to be frequent but small as long as leverage is capped: traders using under Rs 1 lakh of margin lost Rs 0.44 lakh on average.

---

## 5. Strategy archetypes, ranked for Rs 2L now and scaling up later

Sources:
- Index figures: [NSE Indices factsheets, 31 Aug 2026](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf) and the [Apr 2026 momentum whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf).
- Factor data: the [IIMA factor library](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/) (Dec 2025 release).
- The researcher's own backtests were **not independently fact-checked**, and the stock-level ones use current index members, which inflates returns (survivorship bias). Treat them as directional only.

| # | Archetype (horizon) | Edge source and evidence | Expected after costs (estimate) | Drawdown | Trades/yr | Capacity | Main risk | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **Index ETF trend or exposure overlay** (NIFTYBEES/JUNIORBEES vs liquid ETF, positional) | Drawdown control, not extra return. 100-day moving-average filter on the Nifty 50 price index, 2007-26: 9.7% CAGR, **-16.2% max drawdown**, vs buy-and-hold 9.1% and -59.9%. Since 2015 it lagged buy-and-hold by about 1 pp/yr. | ~8-11% CAGR | ~15-25% | ~8-10 switches | Unlimited at your scale | Whipsaw; lags V-shaped recoveries | **First live bot** |
| 2 | **Cross-sectional momentum** (Nifty 200/500, monthly or semi-annual) with trend overlay or 50-70% exposure cap | Strongest Indian anomaly. IIMA winners-minus-losers 10.65%/yr since 1994 (long-short, gross; worst drawdown -62%). Nifty200 Momentum 30 TRI 19.19% vs Nifty 200 15.08% (Apr 2005-Feb 2026). Semi-annual rebalancing beat quarterly. | +1-4 pp/yr over the parent index after costs and tax | 25-70% unhedged (index max 67.7%; lagged its parent by 14.1 pp in 2025) | 2-12 rebalances; 100-140% churn a year | Fine to Rs 25L+. At Rs 2L the minimum Rs 25k delivery trade means 8 names or fewer. | Momentum crashes, multi-year lag, 1-3 pp STCG drag | **Second.** At Rs 2L, consider timing a momentum index fund with your overlay rather than picking stocks. |
| 3 | **Low-vol / alpha-low-vol sleeve** (quarterly) | Nifty100 Low Vol 30, 5 yrs: 10.47% (SD 11.94%, beta 0.79). Alpha Low-Vol 30: 10.62% (beta 0.85). Nifty 50: 8.32%. | About the index return with lower beta | Lower than the market, but still falls in crashes | 4 | Fine | Hard to beat the passive fund | Defensive sleeve, probably via an ETF |
| 4 | **Swing pullback-in-uptrend / breakout** (days to weeks) | Small edge. Pullback: +0.55% per trade net, only about 0.2-0.3% above drift (low confidence, survivorship-biased) | Unknown; likely thin | Varies | ~250 across 100 stocks | Fine | 30-35 bps cost per trade eats the edge | Paper only until it passes walk-forward on survivorship-free data |
| 5 | Sector rotation | Not tested | – | – | – | – | – | Research only |
| 6 | Post-earnings drift / news-event | No Indian net-of-cost evidence | – | – | – | – | Data cost, look-ahead | Research only; archive news now |
| 7 | Weekly short-term reversal | +5.5 pp/yr gross, but net lagged equal-weight by about 10 pp after 0.30% round-trip cost | Negative | -51% | ~44x turnover | – | Delivery STT | **Skip** |
| 8 | Intraday opening-range breakout / VWAP / gap trades | No credible Indian evidence. Opening-range breakout failed out-of-sample after costs on US futures ([arXiv 2605.04004](http://arxiv.org/abs/2605.04004v3)). Nifty gap fades of about 15 bps vs 15-20 bps round-trip cost. | ~0 or negative | – | High | Fine | Costs; 71-80% of intraday traders lose | **Skip live in year 1** |
| 9 | Options buying / selling | Buying: median -114%. Selling: out of reach at Rs 2L, with large tail losses | Negative / n.a. | Ruin-level tails | – | – | – | **Skip; paper only** |

**Benchmark to beat (after costs and tax):**
- **NIFTYBEES buy-and-hold** (Nifty 50 TRI: 1 yr -0.35%, 5 yrs 8.32%, since 1995 12.38%; max drawdown about 60% in 2008) ([factsheet](https://www.niftyindices.com/Factsheet/ind_nifty50.pdf)).
- **Risk-matched version for your 10-15% drawdown limit:** 40-50% NIFTYBEES plus a liquid fund, or the moving-average-filtered NIFTYBEES.
- **Factor bots** must beat the matching passive fund (Nifty200 Momentum 30 or Low Vol 30 index funds). If they don't, the bot adds nothing.

**Drawdown reality:** every fully invested long-only equity strategy fell far beyond 15% in 2008-09 and 2020. Your drawdown limit therefore forces exposure scaling on every bot, and a portfolio governor (§10).

---

## 6. Learning loop

### What works
- **Gradient-boosted trees on engineered features** (momentum, liquidity, volatility) have the strongest support ([Gu-Kelly-Xiu, RFS 2020](https://www.nber.org/papers/w25398)). The gains are smaller after costs and in liquid names.
- **LLMs as feature extractors only.** US evidence shows real but decaying news predictability, concentrated in small caps and negative news ([Lopez-Lira & Tang](https://arxiv.org/abs/2304.07619)). Replacing company names with placeholders improves the signal ([Glasserman & Lin](https://arxiv.org/abs/2309.17322)), and the effect is strongest for large companies, which is your universe.
- **Batch retraining on a fixed schedule.** River's own README says batch learning usually suffices ([River](https://github.com/online-ml/river)).

### What overfits or fails
- **LLM trading agents:** StockBench, LiveTradeBench and FINSABER find most fail to beat buy-and-hold ([2510.02209](https://arxiv.org/abs/2510.02209), [2511.03628](https://arxiv.org/abs/2511.03628), [2505.07078](https://arxiv.org/abs/2505.07078)). Backtest profits "evaporate once the model's knowledge window ends" ([Profit Mirage](https://arxiv.org/abs/2510.07920)).
- **Staged testing drops sharply** (crypto preprint, Sep 2026): 23 of 24 ML methods were profitable in backtest, 2 of 8 in paper trading, and 1 of 4 live, all with negative alpha. Slippage rose about 6x from paper to live. Non-ML methods were all profitable in paper trading during a rising market, so **absolute paper profit proves nothing; gate on alpha versus buy-and-hold** ([2609.34510](https://arxiv.org/html/2609.34510v1)).
- **Deep learning or foundation models on raw prices:** poor evidence ([M6](https://arxiv.org/abs/2310.13357)). Skip. Skip reinforcement learning too.
- **Indian news sentiment:** only classification-accuracy papers exist, with no net-of-cost backtests ([2512.20082](https://arxiv.org/abs/2512.20082)). RBI-communication sentiment depends on the topic: dovish on rates means a bearish equity signal, dovish on FX reserves means bullish ([2411.04808](https://arxiv.org/abs/2411.04808)).
- **Statistics alone don't catch look-ahead bias.** A deliberately leaky Sharpe-35 oracle passed both the Deflated Sharpe and overfitting-probability tests ([2608.27734](https://arxiv.org/abs/2608.27734), preprint).
- **Too many parameter trials.** With 5 years of daily data, trying more than about 45 independent parameter sets makes an in-sample Sharpe of 1 expected by chance alone (minimum backtest length, computed from [Bailey et al.](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)). The Deflated Sharpe paper's own example rejects a 5-year, Sharpe-2.5 backtest ([DSR](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)).
- **Meta-labeling:** no peer-reviewed Sharpe evidence could be retrieved. Treat it as an untested pattern that must pass the same gate.

### Recommended safe design
1. **Journal:** append-only, one row per decision and per fill. Fields:
   - bot_id, strategy git SHA, config hash, model alias/version, feature-snapshot hash;
   - point-in-time data timestamp, news IDs with first-seen time, LLM model/prompt/response hash;
   - intended vs filled price, slippage, full charges, tax bucket, risk state;
   - outcome label (profit-take / stop / time-limit, whichever hit first);
   - **mistake class**: signal / execution / risk breach / data / regime / operator override.
2. **Two kinds of "learning":**
   - Safe, and doesn't count as a trial: recalibrating the slippage and fill model from live fills, and fixing data or execution bugs.
   - Dangerous, and counts as a trial: any change to strategy parameters or rules. These are logged in the trial registry.
3. **Retraining cadence:** fixed calendar: monthly for intraday (if you ever run it), quarterly for swing and positional. **Never triggered by losses.** Drift detectors only demote a model or flag it for review.
4. **Validation:**
   - Point-in-time, survivorship-free data, and costs versioned by effective date.
   - Purged walk-forward or combinatorial purged CV. [skfolio CombinatorialPurgedCV](https://skfolio.org/generated/skfolio.model_selection.CombinatorialPurgedCV.html) defaults to **purged_size=0 and embargo_size=0**, so set both to at least the label horizon.
   - vectorbt 1.1.1 changed its Deflated Sharpe calculation, so recompute any earlier gate results ([release](https://github.com/polakowo/vectorbt/releases/tag/v1.1.1)).
5. **Champion/challenger gate** (a challenger must pass all of these):
   - (a) probability of backtest overfitting below 0.05 (up to 0.2 at most);
   - (b) Deflated Sharpe of 0.95 or more, using the trial count from the registry;
   - (c) beats both the rule-only baseline and buy-and-hold out-of-sample, after costs **and tax**;
   - (d) at least 2-3 months of shadow paper trading alongside the champion, with slippage within the model and drawdown at most half the bot's budget;
   - (e) your manual approval;
   - (f) capital ramped 25%, then 50%, then 100% of the bot's allocation;
   - (g) automatic demotion if drawdown exceeds the bot's limit or live Sharpe falls more than 2 sigma below expectation.

   Use MLflow aliases ("champion") for promotion ([MLflow](https://mlflow.org/docs/latest/ml/model-registry/)).
6. **Paper duration:** 2-3 months minimum per bot. For positional bots with about 10 trades a year, paper trading only checks execution. The evidence of edge has to come from 2005-2026 walk-forward tests.
7. **LLM news features:** replace entity names with placeholders, pin the model version, store the exact prompt and response, and test only on news dated **after** the model's knowledge cutoff.

---

## 7. Broker pick

| | Zerodha Kite Connect | Dhan (DhanHQ) | Upstox | ICICI Breeze | Groww |
|---|---|---|---|---|---|
| API cost | Rs 500/mo with data; the free Personal plan covers orders and GTT only ([pricing](https://zerodha.com/products/api/)) | Trading free; data "extra" (price unverified) | Free | Free | Rs 499 + GST (early-bird price) |
| Delivery brokerage | 0 | 0 | Rs 20/order (Rs 10 promo **ends 30 Sep 2026**) ([charges](https://upstox.com/brokerage-charges/)) | High | – |
| Order limits | 10/s, 400/min, 5,000/day, 25 modifications per order ([docs](https://kite.trade/docs/connect/v3/exceptions/)) | 10/s, 250/min, 1,000/hr, 7,000/day | 10/s, 500/min, 2,000/30 min | 100 calls/min, 5,000/day | 10/s, 250/min |
| Live data | 3 WebSockets x 3,000 instruments | 5 x 5,000, 200-level depth | 2 connections (5 with the paid Plus plan) | – | 1,000 subscriptions |
| History | Minute to day, continuous futures, **no expired options** (depth per request unverified) | 5 yrs intraday (90 days per call); **5 yrs of expired options** (ATM ±10 strikes, IV, OI) ([docs](https://dhanhq.co/docs/v2/expired-options-data/)) | 1-min from Jan 2022, daily from 2000; expired contracts **need Plus, about 6 months only** ([docs](https://upstox.com/developer/api-documentation/get-expiries/)) | Free (1-second data claim unverified) | 3 months only |
| Daily login | Browser redirect; **no official headless or TOTP login** ([docs](https://kite.trade/docs/connect/v3/user/)) | **Official TOTP token API** (v2.5, 9 Feb 2026), 24-hour token ([releases](https://dhanhq.co/docs/v2/releases/)) | Semi-automated, needs your approval ([docs](https://upstox.com/developer/api-documentation/authentication/)) | – | 150 token calls/day |
| Static IP | 2 IPs, weekly change, family sharing; IPv6 egress that differs from the whitelisted IPv4 gets rejected | Primary + secondary, IPv4 or IPv6, 7-day lock, unique per person | Changing it invalidates tokens; no sharing | Mandatory | – |
| Python SDK | kiteconnect 5.2.2 (15 Sep 2026) | dhanhq 2.2.0 (Apr 2026), repo active Aug 2026 | 2.30.0 (Sep 2026); order sandbox | NSE only, no market orders | growwapi 1.5.0 |

Not recommended: Fyers (limits and pricing unverified). Angel SmartAPI, Shoonya and AliceBlue have stale SDKs.

**Pick:**
- **Primary: Zerodha Kite Connect.** Most mature API and docs, zero delivery brokerage, broker-side GTT stops. Plan on a 30-second manual login from your phone each morning. Community TOTP-scraping scripts are unofficial and may breach Zerodha's terms; ask kiteconnect@zerodha.com in writing if you want automation.
- **Backup and F&O research: Dhan.** Official unattended login, zero delivery brokerage, and the best expired-options data. If the daily manual login becomes a real burden at the full-auto stage, promote Dhan to primary.
- **Optional:** Upstox's free order sandbox for continuous-integration tests of the order path.
- **Before you rely on one VM for both brokers:** reusing one static IP at two brokers for the same person is **unverified**. OpenAlgo explicitly warns against assuming it ([OpenAlgo](https://docs.openalgo.in/installation-guidelines/static-ip.md)). Confirm with both brokers, or budget a second IP.

---

## 8. Data and news stack within Rs 2-5k/month

| Source | Cost/month | What you get | Gotchas | Use |
|---|---|---|---|---|
| Kite Connect | Rs 500 + GST, about Rs 590 | Live ticks, minute history, continuous futures | No expired options | **Live feed and minute history** |
| NSE archives | Free | Bhavcopies (daily price files) back to **Jan 1995**. Old format until 05-Jul-2024, new UDiFF format from 08-Jul-2024 ([example](https://nsearchives.nseindia.com/content/historical/EQUITIES/1995/JAN/cm02JAN1995bhav.csv.zip)) | Two formats to handle; send a browser User-Agent and cache locally | **Daily history including delisted names** |
| NSE corporate-actions API | Free | Splits, bonuses, dividends back to at least 2010 ([API](https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date=01-01-2010&to_date=31-12-2010)) | Ratios come as free text you must parse; demergers need hand-set adjustment factors | Your own price adjustment |
| NSE delisted.csv | Free | 329 rows | **Stale since Nov 2020**; misses merger exits | Use a symbol or ISIN disappearing from bhavcopies as the exit signal |
| nsepit, nse-index-history | Free | Historical NIFTY index membership | Hobby projects with 0-1 stars; spot-check them | Point-in-time universe ([nsepit](https://github.com/NegativeZone/nsepit)) |
| jugaad-data | Free | Maintained downloader (v0.35.9, 23 Sep 2026) | **On holidays it silently returns the previous day's file**; check the date inside every file | Downloader ([repo](https://github.com/jugaad-py/jugaad-data)) |
| yfinance | Free | – | Mis-adjusted the RAYMOND demerger (May 2025); renamed symbols fail | Cross-check only |
| Dhan Data API | Price unverified | 5-yr expired options | – | Later F&O research |
| Accelpix | Rs 1,599-3,499 + GST | Live feed | Only 45-120 days of minute history | Not needed |
| TrueData, Global Datafeeds | Quote only | – | TrueData API access needs an application and compliance review | Not needed |
| NSE announcements RSS and JSON APIs | Free | Feed refreshed every 5 min, board-meeting calendar, quarterly results ([RSS](https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml)); BSE notices.xml | Session quirks | **Event feed; archive from day 1** |
| News RSS | Free | [ET Markets](https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms), [Business Standard](https://www.business-standard.com/rss/markets-106.rss), [Mint](https://www.livemint.com/rss/markets) | **Moneycontrol feeds return HTTP 200 but have been frozen since 23 Apr 2024**; add a freshness check | Headlines scored locally with FinBERT |
| EODHD / Marketaux | $19.99 (about Rs 1,920) / $29 (about Rs 2,786) at Rs 96.06/$, plus GST and card forex markup | News with sentiment | India coverage unknown; test the free tiers first | Optional later |
| NewsAPI Business | $449 | – | Far over budget | No |

**Pick:**
- Kite Connect (Rs 590).
- NSE archives through jugaad-data or your own downloader.
- Your own corporate-action parser.
- nsepit for historical index membership.
- The NSE announcements feed plus three RSS feeds, scored locally with FinBERT.

Store everything as Parquet keyed by **ISIN**, not symbol (for example, ZOMATO became ETERNAL). Download minute history incrementally from day one, because every broker caps how far back one request goes.

---

## 9. Framework options

| Framework | Licence | Status (Sep 2026) | Indian brokers | Live trading | Fit |
|---|---|---|---|---|---|
| NautilusTrader | LGPL-3.0 | Strongest engine; **v2.0.0 release candidates with breaking changes** (rc3-rc5, Aug-Sep 2026) ([releases](https://github.com/nautechsystems/nautilus_trader/releases)) | **None.** The only Zerodha repo is a 1-star notebook | Yes | Later, once v2 is stable and you need tick-level simulation. Adapter effort is unknown (the "10-12 weeks" figure is not in its docs). |
| OpenAlgo | AGPL-3.0 server (fine for personal use) | 36 plugins / 34 brokers, weekly releases; Python 3.12+ ([repo](https://github.com/marketcalls/openalgo)) | Yes | Gateway; sandbox with Rs 1 cr virtual capital; **Action Center semi-auto approval plus Telegram** | Optional shortcut. v2.0.2.2 fixed an order-hang bug and a Dhan bug where 8,642 security IDs mapped to two contracts each, so pin the version and smoke-test every upgrade. |
| vectorbt (open source) | Apache 2.0 + Commons Clause | v1.1.1, 26 Sep 2026 | n/a | No | **Research and parameter sweeps** |
| vectorbt PRO | Paid, $25/mo | Active | n/a | No | Only if limit-order simulation becomes a blocker |
| QuantConnect Lean | Apache 2.0 | Active; official Zerodha plugin | Zerodha, Samco | Yes, but needs a **paid organisation tier**; C# core | Poor fit |
| backtrader | GPL-3.0 | **Dormant** (last push Aug 2024) | Unmaintained | IB/Oanda only | Avoid |
| zipline-reloaded | Apache 2.0 | No release since Jul 2025 | Custom work | No | Avoid |
| Backtesting.py | AGPL-3.0 | v0.6.6 | n/a | No; one instrument per run | Quick single-strategy checks only |
| freqtrade / hummingbot / jesse | Various | Active | Crypto only | Yes (jesse live needs a paid licence) | freqtrade if crypto comes later |

**Recommendation: build a thin custom core** with these parts:
- **Strategies as pure signal functions**, called by both the vectorbt research code and the live loop.
- **A broker adapter over the official SDKs** (kiteconnect, dhanhq), about 300-500 lines. Two brokers don't justify a 36-broker gateway with a Flask hop.
- **One shared cost and risk module.**
- **A small bar-replay backtester** that drives the live code path. Every strategy must match its vectorbt result within tolerance before it goes to paper trading.

If you want to be trading sooner, use OpenAlgo in the first few months for its sandbox and semi-auto approval queue (saves about 2-4 weeks), pinned to one version. Replace it once your gateway is ready.

---

## 10. Infra, ops and risk controls

### Hosting
| Option | Cost (at Rs 96.06/$, plus 18% GST) | Static IP | Notes |
|---|---|---|---|
| **AWS Lightsail Mumbai, 2 GB** | $12, about Rs 1,360 | Included | **Recommended** ([pricing](https://aws.amazon.com/lightsail/pricing/)) |
| Lightsail Mumbai, 1 GB | $7, about Rs 790 | Included | Enough for daily-bar bots |
| Secondary IP | about Rs 570+ | – | Options: a second $5 Lightsail instance in another Mumbai zone, EC2 plus Elastic IP in Hyderabad (ap-south-2), or DigitalOcean Bangalore. **Lightsail has no Hyderabad region** ([AWS](https://docs.aws.amazon.com/lightsail/latest/userguide/understanding-regions-and-availability-zones-in-amazon-lightsail.html)). |
| EC2 t4g.small + Elastic IP | about $16-18 | $0.005/hr for IPv4 | Mumbai instance price unverified |
| DigitalOcean Bangalore | $6-12 | Reserved IP free while assigned, $5/mo if unassigned | Alternative |
| Hetzner | – | – | No India location (Singapore is nearest) |
| Home connection | ISP static IP (cost unverified) | – | Only for research: outages leave positions unmanaged |

- **Force IPv4 egress** on the order host. On Kite, an IPv6 source address that differs from the whitelisted IPv4 gets orders rejected.
- **Monthly total:** Kite Rs 590 + Lightsail Rs 1,360 + secondary IP about Rs 570 = **about Rs 2,500**. There is room within budget for EODHD news later.

### Process layout and storage
- **One order-gateway process** owns the broker token, the single API key, the global rate limiter (set it at about 5 orders/second, half the legal cap, plus the daily caps), the risk checks and the static-IP egress. Bots are separate systemd services that submit order *intents* to it.
- **Scheduling and secrets:** systemd timers for login, ingestion and reconciliation. API secrets and TOTP seeds in a root-only environment file or AWS SSM, never in git. SSH keys only, no inbound ports.
- **Research data:** Parquet files queried with DuckDB. DuckDB allows either one read-write process *or* many read-only processes, never both at once, so write Parquet and read it with DuckDB ([DuckDB](https://duckdb.org/docs/current/connect/concurrency.html)).
- **Live order/fill ledger:** SQLite or Postgres.
- **Later options:** QuestDB only if you start storing ticks. Avoid ArcticDB, whose licence requires payment for production use ([ArcticDB](https://github.com/man-group/ArcticDB)).

### Telegram approval flow
1. The bot emits an intent. The gateway runs pre-trade risk checks and stores the intent with a short ID and an expiry time (60-120 s for intraday, longer for end-of-day bots).
2. You get a Telegram message with inline Approve/Reject buttons. The button payload (callback_data, 64 bytes max) carries only the short ID. The message shows bot, symbol, side, quantity, limit price, notional, reason and risk state.
3. Use **long polling**, so no inbound port is needed. Webhooks and polling can't run together ([Bot API](https://core.telegram.org/bots/api)). **Accept callbacks only from your own Telegram user ID.**
4. On approval, **re-check** price drift versus LTP, risk limits and token validity, then send a limit or protected order. On expiry, auto-cancel.
5. Report the fill or rejection back. Commands: `/halt`, `/status`, `/flatten`. Stay under about 1 message per second per chat ([FAQ](https://core.telegram.org/bots/faq)).

### Kill-switch set
Thresholds are my recommendations for Rs 2L with a 10-15% drawdown tolerance.

| Control | Setting |
|---|---|
| Portfolio drawdown governor | -6% from peak: halve new risk. -10%: REDUCING mode (exits only). **-12%: HALTED**, flatten to cash or liquid ETF, manual review. This leaves a buffer for gaps before -15%. |
| Global daily loss (realised + mark-to-market) | -2% of capital (Rs 4k): halt for the day |
| Per-bot limits | Capital allocation; drawdown above about 20% of its allocation demotes it to paper; turnover cap versus plan; alarm if it trades more often after losses |
| Fat-finger checks | Notional per order at most 20-25% of capital, a maximum quantity, limit price within 1-2% of LTP and inside the exchange band |
| Stale-data guard | Intraday: no new entries if the last tick is more than N seconds old or the WebSocket is down. End-of-day: the file date must equal the expected trading day (the jugaad-data holiday bug). |
| Reconciliation | On startup and every minute. Any mismatch between broker positions/orders and internal state means HALTED. |
| Duplicate protection | Idempotent client tags or IDs where the broker supports them |
| Dead-man switch | External heartbeat monitor, plus **broker-side GTT/stop-loss on every position**, so a dead VM never leaves naked risk |
| Square-off | Close intraday positions yourself before the broker's auto square-off (Rs 50 + GST per order). Respect the 15:25-15:30 closing-auction freeze. |
| Trading states | ACTIVE / REDUCING / HALTED, modelled on NautilusTrader ([docs](https://nautilustrader.io/docs/latest/concepts/execution/)). Per-bot circuit breakers modelled on freqtrade's StoplossGuard and MaxDrawdown ([docs](https://www.freqtrade.io/en/stable/plugins/)). |

**Deploy rules, from Knight Capital** (1 Aug 2012, [SEC order](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf)): Knight lost more than $460M in about 45 minutes and got over 4 million executions, because one of 8 servers missed a deploy, an old flag was reused for new code, 97 warning emails went unread, and **the rollback made it worse**. For you:
- Deploy only outside market hours, and verify a checksum or version on the host.
- Never reuse config flags.
- The in-market runbook is **halt and cancel**, never redeploy or roll back.

**Daily runbook:**
- 08:30: login (Dhan automatic, Kite manual).
- 08:45: alert if no valid token.
- 09:00: reconcile.
- Close: reconcile, write the journal, back up.
- Evening: ingest bhavcopies and archive news.

---

## 11. Crypto and forex later: verdicts

| | Verdict | Why |
|---|---|---|
| **Crypto** | **Maybe in year 2**, after 12 months of NSE live results. One low-frequency BTC/ETH trend bot on perpetuals. | Tax is 30% + cess + **surcharge not capped at 15%**, so 31.2% to about 39% effective. Losses can't be set off or carried forward, and 1% TDS applies on transfers ([ClearTax](https://cleartax.in/s/cryptocurrency-taxation-guide)). After-tax profit = (1-t) x gross gains - gross losses, so a bot needs a **profit factor of about 1.45-1.56 just to break even**, and about 2.7-3.5 to keep half its pre-tax profit. Grid, scalping and market-making strategies are ruled out. |
| Venue | **Delta Exchange India** | FIU-registered, INR-settled, testnet available, official Python client v1.0.14 (Apr 2026). Fees 0.02% maker / 0.05% taker; check whether GST is included. Settlement is charged at the taker rate. The option fee cap appears to be 10% of premium ([fees](https://www.delta.exchange/fees), [docs](https://docs.delta.exchange/)). |
| Open points | – | Whether TDS applies to INR-settled crypto derivatives is unsettled (unverified): get a CA opinion. Exchange reporting to CBDT from 1 Apr 2026 (unverified). CoinDCX hack of July 2025 (unverified). Offshore exchanges add FEMA/LRS grey areas. |
| **Forex** | **Skip.** At most, a paper-only EURUSD/USDJPY bot through Kite's currency segment (2-3 days of work). | Under the RBI Master Direction effective 5 Apr 2024, INR pairs are only for hedging a real contracted exposure. The USD 100M allowance only waives the paperwork; the exposure must still exist ([RBI](https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12594)). Cross pairs carry no purpose restriction but are thinly traded (unverified). Offshore forex is illegal under FEMA. |

**Now:** keep the venue and tax-regime layers pluggable, with only the NSE implementation built. Don't build the crypto path yet.

---

## 12. Key risks and failure modes

| Risk | What it looks like | Mitigation |
|---|---|---|
| Overfitting across many bots | A great backtest that is flat or negative live | Trial registry, Deflated Sharpe with the true trial count, overfitting-probability test, champion/challenger gate |
| Look-ahead and survivorship bias | Current index members used in history; LLM "knows" the future | Point-in-time universe from bhavcopies, ISIN keys, post-cutoff LLM tests |
| Cost understatement | 2023-25 backtests priced at old STT | Versioned cost table; slippage calibrated from paper fills |
| Breaking the drawdown limit | A long-only bot falls 20-60% in a crash | Portfolio governor, trend and exposure overlay, hard halt at -12% |
| Momentum and factor regime risk | Momentum lagged its parent by 14 pp in 2025 | Diversify across sleeves; judge over years, not months |
| Execution rejections | Market orders, closing-auction cancellations, price bands, the new ETF norms | Limit or protected orders only; treat rejections as normal events |
| Login and IP lockout | Missed morning login; IP changes locked for a week | Morning alert, secondary IP, broker-side stops |
| Gateway software bugs | OpenAlgo order-hang and Dhan symbol-mapping bugs | Pin versions, smoke-test every upgrade, reconcile every minute |
| Data errors | Holiday duplicate files, the stale delisting list, dead RSS feeds, yfinance adjustments | Date checks, freshness checks, multiple sources |
| Operational (Knight-style) | A bad deploy or reused flag | Deploy outside hours, verify checksums, halt-and-cancel runbook |
| Regulatory change | Consultation on the closing auction and settlement; SEBI's "OAuth only" could withdraw TOTP endpoints; weekly-expiry changes | Keep the login step pluggable; review the SEBI and NSE circulars list monthly |
| Tax mistakes | Missed advance tax; surcharge; delivery trades reclassified as business income | Per-fill tax bucket, quarterly estimates, choose one treatment with a CA |
| Behaviour | Overriding bots, chasing losses, scaling too early | Journal operator overrides as a mistake class; scale-up only through the statistical ramp |
| Small-capital friction | DP charges, positions that can't be sized finely | Minimum Rs 25k per delivery trade; prefer ETFs |
| Security | API secret or TOTP seed on the VM; spoofed Telegram approvals | Root-only secrets, Telegram user-ID check, SSH keys only |
| Proof horizon | 12 months looks good by luck | MinTRL-based ramp; compare against buy-and-hold and passive factor funds after tax |

---

## 13. Open decisions for you

1. **Hours per week.** Every timeline here assumes 10-12. Tell me the real figure and I'll re-plan.
2. **Primary broker:** Zerodha (most mature, but a manual login every morning) or Dhan (official unattended login, less mature SDK)?
3. **Build or borrow:** your own gateway from the start, or OpenAlgo for the first few months to trade sooner?
4. **Year-1 scope:** agree to no live intraday and no live F&O? (Recommended.)
5. **Drawdown governor:** moving-average trend filter, volatility targeting, or a fixed exposure cap? And do the -6/-10/-12% thresholds suit you?
6. **Momentum implementation at Rs 2L:** pick stocks (at most 8 names with Rs 25k minimum trades) or time a momentum index fund?
7. **Tax treatment of delivery trades** (capital gains or business income): decide with a CA before the first live trade, then keep it consistent.
8. **Scale-up rule:** replace "after 12 months" with a statistical ramp (for example 1.5-2x steps when out-of-sample plus live Deflated Sharpe clears the bar)?
9. **Static IPs:** confirm with both brokers whether one IP can be registered at both, or budget a second instance (about Rs 570/month).
10. **News budget:** free only (NSE feeds + RSS + FinBERT) or add EODHD (about Rs 1,920/month) after a free-tier test?
11. **F&O entry criteria:** what capital level and what paper record would justify it? (Probably well above Rs 2L; my view.)
12. **Crypto in year 2:** yes or no, given 31-39% tax with no loss set-off?

---

# Appendix: Critique (corrections and gaps)


WebSearch had already hit its 200-call session limit, so I checked claims by fetching primary sources and downloading PDFs directly. About 20 calls. Some sources were unreachable: Zerodha charges (HTTP 429), Kite docs (socket hang-up), the Budget memo (403) and the SEBI and Income-tax sites (403).

## (c) Spot-checks of the most decision-critical claims

1. **Algo framework timeline: CONFIRMED.** NSE/INVG/70541 (30 Sep 2025) records the go-live moving from 1 Aug 2025 to 1 Oct 2025 (SEBI circular of 29 Jul 2025). It adds a glide path for brokers that weren't ready (SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/132). Zerodha says a static IP is needed for API order placement from 1 Apr 2026. WebSocket, order book and positions calls work from any IP. It allows 2 IPs, one change per calendar week, and family sharing by declaration.
   - https://nsearchives.nseindia.com/content/circulars/INVG70541.zip (fetched 30 Sep 2026)
   - https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip (30 Sep 2026)
   - Not checked: the exact 1 Apr 2026 end date of the glide path (it's in the annexure).
2. **"Approve each trade via the API is still algo": PARTLY WRONG / INCOMPLETE.** The Kite FAQ says orders placed through **Kite Publisher**, where the user places them manually, fall outside SEBI's algo framework.
   - So the approve stage could use a Publisher or basket link from the Telegram message. That would push back the static-IP and algo-rule requirements.
   - Orders sent from your own code through the API are still algo orders.
   - https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs (30 Sep 2026)
3. **STT from 1 Apr 2026: CONFIRMED.** Futures 0.05% and options 0.15% on the sell side. Delivery 0.1% on both sides, intraday 0.025% on the sell side, and 0.001% on sales of equity-oriented fund or ETF units. The brief's 0.001% ETF STT is right.
   - https://cleartax.in/s/securities-transaction-tax-stt (30 Sep 2026)
4. **SEBI FY26 study: CONFIRMED.** 87.7% of individuals lost money in FY26, against 90.9% in FY25. Net losses were Rs 91,685 cr, against a revised Rs 1.12 lakh cr. The average loss was Rs 1.17 lakh. Options loss rate 87.7%, futures 66.0%.
   - https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233506209.pdf (PDF parsed 30 Sep 2026)
5. **ITR due date of 31 Aug: CONFIRMED, but it applies only to ITR-3 and ITR-4.** ITR-1 and ITR-2 are still due 31 Jul.
   - If year 1 is positional-only (capital gains plus salary, no intraday or F&O), the user files **ITR-2, due 31 Jul**, not 31 Aug.
   - The brief's "returns go on ITR-3, 31 Aug" is wrong for the recommended year-1 scope.
   - https://cleartax.in/s/budget-2026-highlights (30 Sep 2026). The buyback change to capital-gains treatment is also confirmed there.
6. **"Dhan has the only official TOTP token API": WRONG.** Angel One's official smartapi-python SDK logs in with `generateSession(username, pwd, pyotp.TOTP(token).now())`.
   - Dhan's TOTP endpoint (`auth.dhan.co/app/generateAccessToken?...&totp=`), its 24-hour token, the 7-day IP lock and the unique-IP-per-person rule are all confirmed.
   - https://github.com/angel-one/smartapi-python, https://dhanhq.co/docs/v2/authentication/ (30 Sep 2026)
7. **Kite pricing: CONFIRMED.** The Personal plan is free (orders and GTT, no market data). The paid plan is Rs 500/month per API key and includes WebSockets and historical candles. The limit is 10 orders/second per trading account.
   - Kite FAQ above (30 Sep 2026)
8. **MinTRL table: arithmetic re-derived and OK.** With a benchmark Sharpe of 0 and a one-sided z of 1.645, an annual Sharpe of 1.0 needs about 683 days. Twelve months (252 days) confirms only a Sharpe of about 1.65 or higher.

## (b) Contradictions and stale or unsourced claims

- **The headline timeline contradicts the brief's own build table and paper rule.**
  - Adding the table serially at 10-12 h/week gives about 1 wk (admin) + 4-6 (data) + 2-3 (broker) + 6-10 (risk/infra) + 3-4 (research) = **about 16-24 weeks of build** (about 12-19 with OpenAlgo).
  - That is before any paper trading. "These pieces overlap" doesn't hold for one person working alone.
  - Adding the 2-3 month paper minimum gives a **first approve-each-trade live order around May-Aug 2027**, not Jan-Feb 2027.
  - The calendar allows only 1 month of paper (Dec, then live in Jan-Feb), which breaks its own "at least 2-3 months" rule.
- **The "fastest path" of 4-6 weeks to a first live order ignores the paper soak.** Consistently applied, it means about 4-6 weeks of build plus at least 2 months of paper, so about Feb-Mar 2027. That is the only route that actually meets the Jan-Feb 2027 milestone.
  - Suggested headline: one ETF bot live (approve stage) around Feb-Mar 2027. Full multi-bot platform around 9-12 months.
- **Effort is given in mixed units** (hours, weekends, weeks, days). Normalise everything to hours at the stated weekly capacity.
- **§3.4 says "~91% of F&O traders losing"** while §1 and §4 say 87.7% (FY26). Use 87.7%.
- **Trend-filter evidence (§5 #1) compares unlike series.** The moving-average filter was tested on the Nifty 50 *price* index, while buy-and-hold is quoted from the TRI. There is no stated return on the cash leg, and the comparison is pre-tax.
  - With 8-10 switches a year, all gains become STCG at 20% instead of deferred LTCG at 12.5%. The 0.6 pp/yr pre-tax edge likely disappears after tax.
  - Retest on TRI, with a liquid-fund return on the cash leg, after tax.
- **Tax treatment of the "liquid ETF" parking asset is missing.** Liquid, debt and gold-in-cash sleeves are specified mutual funds, taxed at slab rate regardless of holding period. LIQUIDBEES pays daily dividends as units, which are also taxed at slab rate. (Standard rule, not fetched this round.)
- **Kite claims I couldn't reach in this round:** tokens expiring at 6 AM, no official TOTP login, and market_protection = -1. All three still rest on the brief's own citations.
- **Claims marked "unverified" that the design depends on:** Dhan data API price, Lightsail Mumbai pricing parity, whether one static IP can be registered at two brokers, and CoinDCX / CBDT crypto reporting. These should become explicit to-dos, not footnotes.

## (a) Important gaps for the design

- **DDPI / e-DIS for automated sells.** Selling delivery holdings, and GTT stops on holdings, needs DDPI or a daily CDSL TPIN authorisation. Without DDPI, full auto and "broker-side GTT on every position" fail. Add "sign DDPI" to the admin steps. (Standard broker practice, not fetched.)
- **Several bots on one account.**
  - The broker nets positions per account, so each bot needs its own internal sub-ledger for positions and P&L.
  - Cross-bot netting is needed, plus **self-trade prevention**. Two bots crossing the same symbol can create self-trades that surveillance flags.
  - A portfolio allocator is missing.
- **Surveillance lists.** ASM/GSM, trade-to-trade (BE series) and circuit-band stocks affect a Nifty 200/500 momentum universe: 100% margin, no intraday, one-sided circuits. The universe filter must pull NSE's daily ASM/GSM lists.
- **Execution timing for daily-bar bots.** Nothing covers when an end-of-day signal becomes an order: after-market orders via the API, the 09:00-09:15 pre-open session, the new ETF pre-open call auction, or the closing auction. This should drive backtest fill assumptions.
- **Exchange calendar.** Holidays, special sessions (Muhurat, Budget-day Saturday) and T+1 settlement, including selling shares bought the previous day and short-delivery auction risk.
- **Statistical bar for beating the benchmark.** MinTRL is computed against a Sharpe of 0. The gate says "beat buy-and-hold and the passive factor fund", which needs MinTRL on the *excess* return and makes the bar much higher. State this explicitly for the scale-up ramp.
- **Paper trading for low-frequency bots.** A 2-3 month paper run of a bot trading 8-10 times a year yields about 2 trades. Define the paper gate as a checklist of execution events (orders, rejections, reconciliation, GTT behaviour), not a duration.
- **GTT limits.** GTT triggers on the last traded price, isn't guaranteed at the exchange, expires after 1 year, and needs DDPI on holdings. So it's a weak dead-man switch. Add an external monitor plus a documented manual flatten path from the phone.
- **Backup and outage plan** for a broker, exchange or cloud outage, beyond "secondary IP": which broker takes over, and how positions are held across two brokers.
- **Tax-regime choice.** The effective-rate and surcharge figures assume the new regime. Say so, and note that salary plus trading gains above Rs 50 lakh triggers surcharge.

## Bottom line on "how much time will it take?"

- **Minimum single ETF bot:** about 1-1.5 months to build, plus at least 2 months of paper, gives a first approved live order around Feb-Mar 2027.
- **Full multi-bot platform with the risk and learning loop:** about 9-12 months part-time.
- **Statistical proof:** years, unless the true Sharpe is 1.65 or higher. Twelve months of live data can't prove a typical positional edge.