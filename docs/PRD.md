# Tradebot: Product Requirements Document

| | |
|---|---|
| Version | v1.9 |
| Date | 2026-09-30 |
| Owner / sole user | Platform owner: a salaried staff software engineer in India, working solo |
| Status | For owner review, then handoff to the implementing system |
| Self-contained | Yes. Every fact the design depends on is in this document, with sources in Appendix A. "§N" refers to a section of this PRD. |

---

## 0. How to read this document (for the implementing system)

- **§1–§12** cover *what* to build and *why*. **§13** covers *how*, at an architectural level. **§14** is the build order. **§16** lists decisions still open and facts still unverified.
- **Requirement IDs** (D1, K4, …) are stable; use them in plans and commits. The **Slice** column says when each is built. **"Parked"** means not scheduled until its named trigger fires.
- **MUST / MUST NOT** mark hard requirements. Everything else is default behaviour unless the owner decides otherwise in §16.
- **"(unverified)"** marks a fact that has not been confirmed from a primary source. Verify it before relying on it (§16.2).
- **Dates** are estimates assuming 10–12 owner-hours a week (OD-1).
- **Units:** ₹1 lakh (L) = ₹100,000. ₹1 crore (cr) = ₹10 million. 1 bps = 0.01%.

## 1. Summary

Tradebot is a **personal, owner-operated platform** for researching, backtesting, paper-trading and live-trading configurable trading bots with the owner's own capital. The owner's accounts are Zerodha (Kite Connect) and Dhan. Sensibull is used for manual options analysis only.

- **Build order:** NSE ETFs and equities first. Options and intraday stay as research and paper tracks. Crypto is a possible year-2 addition. Forex is out.
- **Capital:** starts at ₹2 lakh and scales only through an explicit gate (§10).
- **Bots:** each bot is a declarative config (instruments, horizon, strategy, parameters, capital, risk limits). Many bots run side by side, and every order goes through one compliant order gateway.
- **Autonomy is staged per bot:** BACKTEST → PAPER → APPROVE → AUTO. In APPROVE, the owner approves entries on Telegram and exits happen automatically.
- **Learning:** the platform learns from its own record through an append-only journal and statistically gated challengers. It never reacts to recent losses.
- **First deliverable (slice S1):** one daily-bar ETF trend bot, working end to end. Paper trading from about late Nov 2026. **First approved live order about Feb–Mar 2027**, which starts the 12-month proof clock.

## 2. Problem, goal, reality check

**Goal:** grow the owner's capital with a systematic, low-maintenance process. It should beat a risk-matched benchmark after costs and tax (§4), keep peak-to-trough **drawdown under 15%**, and improve over time without overfitting.

**The reality check that shapes every requirement** (sources in Appendix A.3):
- **F&O losses are near-universal.** 87.7% of individual equity-derivatives traders lost money in FY26, and only **0.5% were profitable in every year FY22–FY26**. The median options buyer's return on capital in FY26 was **-114%**.
- **Intraday is not much better.** 71% of intraday cash traders lost money in FY23, and 80% of those making 500+ trades a year lost.
- **Algos don't help individuals.** There is **no evidence that algo use improves individual outcomes**. SEBI tags a client as an algo user after a single algo trade.
- **The winners are institutions.** In FY26, 99% of prop-desk and FPI gross derivatives profit came from algo entities, mostly co-located market makers. The top 10 prop firms took 74.5%.

So the platform optimises for **avoiding the known failure modes**: high turnover, ignoring costs, leverage, overfitting, and overriding the system by hand. "Consistent returns" means the measurable targets in §4, not a promise.

## 3. User and usage

- **One user: the owner.** Year 1 uses only the owner's own accounts. Family accounts are possible later under C6. There is never any third party.
- **Unattended by design.** The owner has a full-time job, so the platform MUST run unattended during market hours. On a normal day it should take **at most about 15 minutes**: the morning login, approvals, and reading the daily summary.
- **When the owner is unreachable:**
  - With a valid broker session, risk-reducing actions MUST still happen automatically (A5).
  - With **no session** (no login that day), the only automatic protection is the broker-side **E9 GTT backstop**, which lives at the broker and triggers without any login.
  - For planned absences, the runbook (§13.6) is to set bots to REDUCING or hold cash before leaving.

## 4. Goals and success metrics

### 4.1 Benchmarks (named, used by every gate)

| Name | Definition | Use |
|---|---|---|
| **RM** (risk-matched) | 50% Nifty 50 TRI + 50% the NAV of one direct-plan liquid fund. The fund's AMFI scheme code is chosen at S1 start and stored in `portfolio.yaml: benchmarks.rm_liquid_amfi_code`. Rebalanced to 50/50 on the first session of each month. | **Primary** pass/fail benchmark |
| **BH** | Nifty 50 TRI buy-and-hold (proxy for holding NIFTYBEES) | Always reported, never gated |
| **PF** | The TRI of the passive factor index matching a factor bot (e.g., Nifty200 Momentum 30, Nifty100 Low Vol 30) | **Pass/fail for factor bots**, in addition to RM |

**Benchmark rules:**
- Benchmarks use the same evaluation window and the same X5 tax profile as the bot.
- Interim rebalances are notionally tax-free. Tax is applied once, at liquidation on the last day of the window: equity legs at STCG/LTCG, the liquid-fund leg at the X5 slab rate (including surcharge and cess).
- A strategy cannot be its own benchmark.

### 4.2 Platform goals

| ID | Goal | Metric / target |
|---|---|---|
| P1 | One strategy code path | A bot moves between BACKTEST, PAPER and live by stage change only. From S2, research (vectorbt) and bar-replay must produce identical trade lists (timestamp, side, qty), with an absolute difference in cumulative net return of 0.1 pp or less. |
| P2 | Low operating burden | 15 min/day or less on normal days. Login takes 1 minute or less. No manual steps in data ingestion. |
| P3 | State integrity | A reconciliation mismatch sets HALTED within 60 s of detection (E4). Zero duplicate orders (E5). |
| P4 | Compliance by construction | Zero broker or exchange rejections caused by platform behaviour (market orders, rate limits, wrong IP, product type). |
| P5 | Cost | ₹5,000/month or less; target about ₹2,050 in S1 (§13.8). |

### 4.3 Trading goals (live portfolio)

| ID | Goal | Metric / target |
|---|---|---|
| T1 | Beat the benchmark | Portfolio return after costs and tax beats **RM** over the evaluation window, and factor bots also beat their **PF**. BH is reported. The S1 ETF trend bot is a drawdown-control strategy and is **expected to lag BH on return** (Appendix A.5). It is judged on RM and on the drawdown it saves. |
| T2 | Drawdown | **Hard limit: 15% epoch drawdown from peak NAV** (K0). The governor halts at −12% on both the reference peak and the epoch peak (K1), leaving a 3 pp buffer for price gaps. |
| T3 | Live matches expectation | **Execution:** slippage_bps = signed (fill − mid at first placement) / mid × 10⁴, positive when adverse. Median ≤ R4 model + 2 bps, and no single fill above 3× the model. **Returns:** rolling 60-session Sharpe and 60-session return stay within the 5th–95th percentile band of the expectation model (§10.1). |

## 5. Non-goals

- **Selling, sharing or publishing bots, signals or advice.** That needs exchange empanelment as an algo provider, plus SEBI Research Analyst registration for black-box algos.
- **Forex.**
  - Offshore forex is illegal under FEMA.
  - INR pairs on Indian exchanges require a real underlying exposure (RBI Master Direction, 5 Apr 2024).
  - Cross pairs are unrestricted but thinly traded (unverified).
- **Live intraday and live F&O in year 1.** Research and paper only (§11, §12).
- **Leveraged products in year 1:** MIS, MTF and NRML. Delivery (CNC) only (K4).
- **HFT, co-location,** or anything needing more than 5 orders/second.
- **LLM agents that place or size orders.** Deep learning or reinforcement learning on raw prices.
- **Multi-user features, a public web app, or a rich dashboard.** Telegram, CLI and reports only.
- **Crypto before the NSE portfolio has 12 months live** (OD-11).
- **Abstractions without a second implementation** (principle 9).

## 6. Constraints

| Area | Constraint |
|---|---|
| Capital | ₹2 lakh to start; scale only through the §10 gate |
| Risk | Hard drawdown limit 15% (owner's stated tolerance: 10–15%) |
| Budget | ₹2–5k/month for data and infra |
| Time | Owner hours/week not yet fixed (OD-1); plans assume 10–12 |
| Regulation | SEBI retail algo framework, mandatory for all brokers since 1 Apr 2026 (per Zerodha; exact glide-path end date unverified, §16.2 #1). NSE execution rules; income-tax law (Appendix A.1, A.2). |
| Stack | Python, a thin custom core, and official broker SDKs (§13) |
| Brokers | Zerodha Kite Connect for S1 (APPROVE stage). Dhan is the candidate for AUTO and for options data (both parked). |

## 7. Product principles

1. **Rules first; ML earns its place.** A model ships only if it beats the rule-only baseline out-of-sample (OOS) after costs and tax.
2. **One code path.** The same strategy functions run in backtest, paper and live.
3. **Costs and taxes are first-class and dated.** Every rate has an effective-from date, and every fill has a tax lot.
4. **One order path.** Exactly one component can call a broker order API. It owns the session, API key, rate limiter, pre-trade checks and audit log.
5. **Gates up, automatic demotion down.** Promotion needs recorded evidence (A1). A breach demotes automatically (K7).
6. **Never learn from pain.** Retraining runs on a calendar and is never triggered by losses. Every parameter or rule change counts as a trial.
7. **Point-in-time truth.** Data is keyed by ISIN and free of survivorship and look-ahead bias.
8. **Fail safe.** When in doubt, halt and cancel. Never deploy or roll back during market hours. Flattens (K1, `/flatten`, K7) never wait for a human, with two exceptions. (a) An E8 halt: placing orders from an unregistered IP is never allowed, so the owner flattens manually. (b) No valid broker session: the E9 GTT at the broker is the backstop. Strategy exits are also automatic, but they pause while the portfolio is HALTED by E4 or `/halt` (K5), because a reconciliation mismatch puts the ledger itself in doubt; the owner clears that halt from the CLI.
9. **No seams before the second implementation.** An abstraction is extracted only when a second implementation exists. The broker interface is justified from S1, because the paper broker and Kite are its two implementations.

## 8. Functional requirements

### 8.1 Data (D)

| ID | Requirement | Slice |
|---|---|---|
| D1 | **Daily bhavcopies:** ingest NSE UDiFF bhavcopies into Parquet, keyed by **ISIN**: a one-off backfill of every UDiFF file from 8 Jul 2024, then incrementally. Each run fetches every session since the last stored one (D2), so a late or failed day is backfilled at the next run rather than skipped. Reject any file whose internal trade date differs from the expected session (third-party downloaders silently return the previous day's file on holidays). **S1 instrument history:** NIFTYBEES daily OHLCV back to listing, from Kite historical day candles. Legacy (pre-8 Jul 2024) bhavcopies are parsed for the S1 ISINs only, as the D3 secondary source. The full-market 1995+ legacy backfill is S2, and only if OD-6 = stock-picking. | S1 / S2 |
| D2 | **Exchange calendar:** trading holidays, special sessions (Muhurat, Budget-day Saturday), session windows (pre-open, normal market, closing auction; exact times §16.2 #13), and the **settlement date of each trade (T+1)**. K4, A6 and X1 use it. **T+1** and **next session** always mean the next trading session in this calendar, never the next calendar day. Special sessions (Muhurat, Budget-day Saturday) count as sessions for signals and moving averages, because their closes are published, but are never order windows: the platform places no orders in them, the evening pipeline of a special session emits no intent, and the special session's close enters the moving average at the next regular session's pipeline. | S1 |
| D3 | **Data-quality checks:** missing sessions, duplicates, stale sources, OHLC sanity. For S1 instruments, cross-check Kite day candles against the bhavcopy. If the close differs by more than 0.1% or volume by more than 5%, alert and compute no signal for that session. The Nifty 50 price-index close for session T, which is the only signal input, MUST also come from two sources and agree within 0.05%: the niftyindices.com daily report and the Kite day candle for the index instrument (`NSE:NIFTY 50`, §16.2 #20). If they disagree, or either is missing by the §9 cutoff, no signal is computed for T. | S1 |
| D4 | **Minute bars:** a one-off 30-minute check in S1 of Kite's total look-back for minute candles. If it is under 2 years, an incremental archive job starts in S1 as a side job. Otherwise minute bars are fetched on demand in S5. | S1 (check, archive if needed) / S5 |
| D5 | **News/announcements raw archiver.** A side job, timeboxed to 4 h, that never blocks trading and is not an exit criterion. One cron script appends the NSE corporate-announcements RSS plus the ET Markets, Business Standard and Mint markets RSS as raw items with a first-seen timestamp, deduped by GUID. Alert if a feed hasn't changed for 48 h (Moneycontrol feeds return HTTP 200 but have been frozen since Apr 2024). Start immediately: there is no free historical Indian news archive. | S1 (side) |
| D6 | **Corporate actions** from the NSE corporate-actions API, parsed into adjustment factors, plus a manual override file (demergers need hand-set factors). S1 covers the S1 instruments only (NIFTYBEES splits and IDCW). API coverage is verified only from 2010; if earlier years are missing, stock-level tests start in 2010. | S1 (S1 instruments) / S2 (equities, if OD-6 = stock-picking) |
| D7 | **Point-in-time index membership** (NIFTY 50/200/500). Delisting is inferred from an ISIN disappearing from bhavcopies, because NSE's delisted list has been stale since Nov 2020. Candidate sources are the nsepit / nse-index-history hobby projects (0–1 stars); spot-check them against NSE index factsheets. | S2, if OD-6 = stock-picking |
| D8 | Daily ASM/GSM/trade-to-trade surveillance lists as a universe filter. | S2, if OD-6 = stock-picking |
| D9 | Dhan expired-options history: 5 years, ATM ±10 strikes, with IV and OI. Price unverified (OD-13). | S5 |
| D10 | **Benchmark, signal and ETF series:** | S1 |
| | Nifty 50 price index and TRI daily history from the niftyindices.com historical downloads, from 2007-01-01 or earlier. The daily price-index close is appended each evening from the niftyindices.com daily report and cross-checked per D3; the TRI is appended on its own schedule (§13.3 step 3). | |
| | The RM liquid fund's daily NAV from AMFI, from 2007-01-01. Direct plans only exist from 1 Jan 2013. Before that date, use the same scheme's regular-plan NAV, grossed up daily by the published expense-ratio difference (0.2%/yr if unknown), and flag it as a proxy. | |
| | Live ETF **iNAV**; source unverified (§16.2 #5). Fallback: if no iNAV quote 60 s old or newer exists, K4(d) uses the LTP band only, sets the `inav_unavailable` flag and alerts once per day. | |
| | 20-day median traded value per ETF, computed from the D1 bhavcopy traded-value column. | |
| | PF series are added with the S2 bots. | |
| | All series are stored point-in-time with source and date checks. | |

### 8.2 Research and backtest (R)

| ID | Requirement | Slice |
|---|---|---|
| R1 | Strategies are **pure signal functions**: point-in-time data up to the decision time goes in, and `target_exposure ∈ [0, 1]` comes out. The same function runs in backtest, paper and live. The S1 strategy is specified in §11.1. | S1 |
| R2 | **S1:** one bar-replay backtester that drives the live code path (strategy → risk → paper-fill model). **S2:** vectorbt for parameter sweeps, plus the P1 parity check before any vectorbt-researched bot enters PAPER. | S1 → S2 |
| R3 | **Versioned cost model** per broker, segment and product, with effective-from dates. It covers brokerage, STT, exchange transaction charges, SEBI fee, stamp duty, GST, DP charges and the auto square-off fee (Appendix A.2). S1 needs only the Zerodha ETF/equity delivery rows. Until dated historical rows are added, backtests apply the **current** rate card to all history, which is conservative. Validated against contract notes (X6). | S1 |
| R4 | **Slippage model.** S1 static default: **5 bps per side** for liquid ETFs. S3: calibrated from measured slippage (T3) and from the open-vs-fill gap (R8). | S1 → S3 |
| R5 | **Walk-forward** plus a **trial registry**. Anchored walk-forward (defaults: 5-year train, 1-year test, 1-year step; configurable). Each bot's research config declares a parameter grid. The pass rule is on the chained OOS result. **Every grid point evaluated is logged** as a trial (strategy, params, data window, result); the trial count feeds R10. The S1 specifics are in §11.1. | S1 |
| R6 | Combinatorial purged cross-validation, with purge and embargo each at least the label horizon (skfolio defaults both to 0), and the probability of backtest overfitting (PBO). | Parked (with L7) |
| R7 | **After-tax reporting** per tax year and bucket (X1), against RM and BH (and PF for factor bots), using the X5 profile. | S1 |
| | Set-off rules: short-term capital losses offset STCG first, then LTCG; long-term capital losses offset only LTCG; carry-forward for 8 years. | |
| | Positions still open at the end of the window are liquidated on the last day. | |
| | Current tax rates apply to all history (conservative). | |
| R8 | **Execution timing,** the same for all modes. | S1 |
| | The decision uses session-T close data. The intent and approval request go out on the evening of T. Placement happens in the bot's order window on T+1, the next trading session per D2 (default 09:20–10:30 IST), following R8a. AMOs are disabled. | |
| | Backtest fill = T+1 open + R4 slippage, as a proxy for the order window (no minute bars in S1). | |
| | The gap between the T+1 open and the actual fill is journaled (L1) and folded into R4 in S3. | |
| R8a | **Order placement algorithm.** | S1 |
| | **Drift check at placement:** drift = abs(LTP − T close) / T close. If drift > `risk.drift_pct` (default 2%), a risk-increasing intent is dropped, journaled and alerted. Risk-reducing intents proceed. | |
| | **Limit price:** buy = min(best ask, iNAV × (1 + band)); sell = max(best bid, iNAV × (1 − band)), where band = `risk.inav_band_bps`. Without iNAV, use the LTP band (K4(d)). | |
| | **Premium check (risk-increasing orders):** if abs(LTP / iNAV − 1) exceeds `inav_band_bps`, skip the order, journal it and alert (K4(d)). | |
| | **Exit pricing (risk-reducing orders):** use the sell formula above. Switch to the best bid, clamped to the exchange price band, only when (d) would block the order or the order is a K1 flatten or `/flatten`. Raise one alert per order, not one per reprice. | |
| | **Repricing:** every 60 s, up to 10 modifications per order. When a **risk-increasing** order hits the cap, it stops being modified and rests at its last limit until `order_expiry`. When a **risk-reducing** order hits the cap, it is cancelled and re-placed as a new order with a new E5 tag, again with at most 10 modifications. The E1 rate limits and the broker's 25-modification cap are never exceeded. | |
| | **Broker-side expiry (MUST):** every risk-increasing and drill order is placed with Kite `validity=TTL` and `validity_ttl` = whole minutes left until its `order_expiry` (rounded down, minimum 1), re-set on every modification. The broker then expires the order even if the platform is dead, logged out or E8-halted. Verified in A6 (§16.2 #18). If TTL is not accepted, the fallback is that a risk-increasing order never rests: any unfilled remainder is cancelled after each 60 s reprice attempt.
| | **Expiry:** at `order_expiry` the unfilled remainder of a risk-increasing order is cancelled and the order ends EXPIRED. Risk-reducing remainders are re-issued under A5. | |
| | **Flatten expiry:** for K1 flattens, `/flatten` and K7 flattens, `order_expiry` is the end of the normal market session on the day of issue, never the bot order window. Until then any unfilled remainder keeps repricing and re-placing under R8a. Anything still unfilled is re-issued at the start of the next normal session. Strategy exits keep `order_expiry` at the end of the bot order window and are re-issued in the next session's window. | |
| | The limit shown at approval is indicative; placement may differ within the K4 bands. | |
| | **Re-emission:** an entry intent is re-emitted each evening only while the regime is unchanged and abs(governed target ₹ − current ₹) > 5% of capital (§11.1). Each re-emission needs fresh approval. Backtests apply the same rule. | |
| R9 | **Capacity report:** results at ₹2L, ₹10L and ₹25L, covering liquidity, minimum trade size and lot size. | S2 |
| R10 | **Deflated Sharpe Ratio (DSR):** computed on the backtest with the R5 trial count at every Backtest → Paper gate. The **trial count** is the number of distinct (strategy, parameter point) rows in the trial registry for that strategy family, across all its versions and challengers; walk-forward windows re-evaluate the same point and do not multiply it, and L3 safe-learning runs are excluded. Live DSR on excess return over RM is computed for the §10 scale-up criterion (5). On delivery, S3 recomputes DSR for existing gate records. | S3 |

### 8.3 Bots and configuration (B)

| ID | Requirement | Slice |
|---|---|---|
| B1 | A bot is a declarative YAML config validated against the §13.5 schema. Invalid configs are rejected at load. Each bot has a unique 2-character `code` used in order tags (E5); `dr` is reserved for drills. **The stage is not part of the YAML.** It lives only in the gate-record table (A1) and changes only through CLI `promote`/`demote` or K7. A YAML that contains `stage` is rejected. | S1 (one bot) |
| B2 | Every decision records the strategy's git SHA and the config hash. | S1 |
| B3 | Multiple bots can be spawned and stopped. Each runs isolated and submits intents to the gateway. | S2 |
| B4 | Per-bot sub-ledger of positions, allocated cash and P&L, reconciled as in E4. | S2 |
| B5 | By default, **live** bots hold **disjoint instruments**. Because the stage is not in the YAML (B1), the check runs at promotion: Paper → Approve is refused while another bot in APPROVE or AUTO holds any of the candidate's ISINs. BACKTEST and PAPER bots may share instruments with anything, which is what lets an L4 challenger paper-trade the champion's ISIN. Cross-bot netting and self-trade prevention are built only when two live bots are allowed to share an instrument. | S2 (check only) |
| B6 | Capital allocator across bots, with fixed weights first. | S2 |

### 8.4 Portfolio risk (K)

| ID | Requirement | Slice |
|---|---|---|
| K0 | **Definitions.** | S1 |
| | **Capital** = `portfolio.starting_capital` (₹2L) + net platform cash movements + cumulative platform P&L after charges (tax not deducted), marked at the latest close. It never uses the broker's funds balance. Cash movements (a §10 scale-up deposit, a withdrawal to pay tax) are recorded only through the CLI `cash-move` command, which journals them as `operator`, adjusts capital, and issues or redeems NAV units at the last marked NAV. Money in the broker account that is not journaled this way is invisible to the platform. | |
| | **NAV** = unitised, time-weighted portfolio value: deposits and withdrawals change units, not NAV. Units start at NAV 100.00 per unit when the first epoch starts; a cash movement issues or redeems units at the last marked NAV and takes effect at the next mark. Marked at every reconciliation while live and at session close in backtests. | |
| | **Drawdown** = NAV / reference peak − 1, where the **reference peak** is the running maximum NAV since the later of the epoch start and the last CLI reset (K1). | |
| | **Bot drawdown** (K3, K7) = bot sub-ledger NAV / its running maximum since the bot last entered its current live stage − 1. In S1 it coincides with epoch drawdown, because the one bot's live stage and the epoch start together. | |
| | **Epoch drawdown** = NAV / running maximum NAV since the current epoch began − 1. T2 and §10 use it, and it never resets within an epoch. | |
| | **Epoch:** the first epoch starts at the first live order. A new epoch starts only through the CLI `new-epoch` command (after a K1 epoch breach), which is journaled, restarts the §10 12-month clock, and permanently keeps the failed epoch's result in reports. | |
| K1 | **Portfolio drawdown governor** (MUST NOT be disableable), measured on NAV against the reference peak. Evaluated at every NAV mark: each live reconciliation at LTP, and the close in backtests. That timing difference is accepted and documented. A level is reached when drawdown ≤ its threshold (at or beyond it); thresholds are in percentage points of the reference peak, and each level's release rule is stated with it below. | S1 |
| | At −6% (`governor.halve`): the bot's effective `max_exposure` is multiplied by 0.5, both in the target ₹ formula (§11.1) and in the K4(b) cap. It is released only when drawdown recovers above `governor.halve_release` (default −3%), not at −6%, so that NAV oscillating around the threshold cannot produce a trim, a top-up and another trim in successive sessions (OD-5). The halving applies to the target, not to individual orders. | |
| | At −10%: **REDUCING**. | |
| | At **−12%: HALTED plus an automatic flatten to cash** (A5). | |
| | Thresholds live in `portfolio.yaml: governor`. Config load MUST reject any set that breaks halve_release > halve > reduce > halt ≥ −(hard limit − 3 pp) > backstop_dd > −hard limit. | |
| | **Epoch breach:** independently of the reference peak, epoch drawdown ≤ −(`hard_drawdown_limit` − 3) pp sets HALTED, triggers an automatic flatten (A5), and demotes all bots to PAPER. The CLI refuses to clear it, and only `new-epoch` (K0) restarts live trading. Because the reference peak is never above the epoch peak, epoch drawdown is always at least as deep as reference drawdown, so with the defaults (`halt` = −12 = epoch-breach level) every −12% halt is an epoch breach; the reference-peak halt can fire first only if `halt` is set less negative than −(`hard_drawdown_limit` − 3). Either kind of governor HALTED demotes all bots to PAPER (K7(4)), so clearing a reference-peak HALTED from the CLI restores the ACTIVE state but not live trading: the bots must re-pass Paper → Approve. | |
| | Clearing REDUCING or HALTED (short of an epoch breach) is CLI-only: the owner confirms a new reference peak equal to the current NAV, and the reset is journaled. Epoch drawdown is untouched. | |
| | Backtests MUST include the governor. A backtest is a single epoch: the epoch peak is never reset, so the gate's epoch max drawdown is the deepest trough of the whole run. After REDUCING or HALTED, the simulator resumes ACTIVE at the next strategy entry signal that comes at least `governor.backtest_cooloff_sessions` sessions later (default 20), with the reference peak reset to NAV at that point. That resumption stands in for the owner's CLI reset: it is a modelling assumption about owner behaviour, not platform behaviour, and, together with the NAV-mark timing above, it is the only place the backtest path deliberately differs from live. A backtest that reaches the epoch-breach level fails gate criterion (2) in §10.2 whatever the simulator does afterwards, because live it would have ended the epoch and demoted every bot. | |
| K2 | **Global daily loss limit:** −2% of capital (realised + mark-to-market) sets REDUCING. Exits are still allowed. | S5 (first intraday bot) |
| K3 | **Per-bot guards.** | S2 |
| | Drawdown above `risk.max_drawdown_pct` demotes the bot one stage (K7). | |
| | Turnover alarm: switches in the trailing 20 sessions exceed 1.5 × `planned_turnover` × 20/252. | |
| | Chasing alarm: orders in the 5 sessions after a losing week exceed 1.5 × the 5-session average over the trailing 60 sessions. | |
| K4 | **Pre-trade checks in the gateway** (every order, every stage). | S1 |
| | **(a) Scope:** ISIN allowlist from the bot config; product **CNC only**; segment NSE cash only. | |
| | **(b) Size:** buy notional ≤ (capital × `allocation` × `max_exposure` − current bot exposure in ₹) × 1.02, and buy qty ≤ what broker-reported available cash (Kite margins API, §16.2 #21) can pay for at the limit price; if that is lower, the order is placed for the affordable quantity, journaled and alerted, and capital is never adjusted automatically. Sell qty ≤ the bot's **settled** holdings. Selling unsettled units (T1/BTST) is blocked unless `risk.allow_unsettled_sell` is true (default false). Flatten sells are capped per K5(v). | |
| | **(c) Order limits:** at most `risk.max_orders_per_day` new orders per bot (default 2) and at most 10 modifications per order (the broker allows 25). What happens at the modification cap is defined in R8a. | |
| | **(d) Price band:** limit within `risk.ltp_band_pct` of LTP (default 1.5; config accepts 1–2). ETFs also need the limit within `risk.inav_band_bps` of iNAV (default 25) and inside the exchange band set by the ETF norms in force since 7 Sep 2026. If the ETF's premium or discount to iNAV exceeds the band, skip and alert. iNAV fallback per D10. | |
| | **(e) Liquidity:** order size ≤ `risk.adv_cap_pct` (default 5%) of the ETF's 20-day median traded value. | |
| | **(f) Freshness:** EOD data must carry the expected session date, and the quote used for pricing must be 10 s old or less. | |
| | **(g) Session:** place only inside the normal market session and the bot's order window, never in pre-open or the closing auction. No market orders (C3). | |
| | **(h) Switches:** sell first. The buy is sized to broker-reported available funds after the sell fills, not to expected proceeds. The paper broker assumes 100% of delivery-sale proceeds, net of charges, are available the same day (unverified, §16.2 #14). | |
| | **(i) AMOs:** disabled by default. If ever enabled, the R8a drift check re-runs at placement and cancels on breach. | |
| | **(j) Exit exemptions.** Risk-reducing orders (strategy exits, K1 flatten, `/flatten`, K7 demotion flatten) are exempt from the per-day count in (c), and from (d), (e) and the EOD-date clause of (f). Pricing follows R8a exit pricing. The K1 flatten, `/flatten` and the K7 flatten are also exempt from the bot order-window clause of (g): they are placed at any time in the normal market session, never in pre-open or the closing auction. Strategy exits keep the bot order window. K1 flattens, `/flatten` and K7 flattens may also sell **T1 quantity** (bought on an earlier session, not yet settled), whatever `risk.allow_unsettled_sell` says. This means accepting the short-delivery/auction risk in an emergency. Units bought in the same session are never sold (no same-day round trip); they are flattened at the next session's open. Strategy exits keep the settled-quantity rule. Still enforced for all exits: (a), quote freshness in (f), no market orders, the per-order modification cap, and the E1 rate limits. | |
| | **(k) State and flags:** a risk-increasing order is placed only if the portfolio (and, from S2, the bot) is ACTIVE and no blocking flag (K5) is set at placement time. Otherwise the intent ends DROPPED_STATE and is journaled and alerted. An intent from a bot with a pending K7 demotion always ends DROPPED_STATE. Every modification of a risk_increasing order counts as a placement for this check. | |
| K5 | **Trading states.** Portfolio level in S1; bot level in S2. Leaving REDUCING or HALTED is CLI-only (K1). | S1 → S2 |
| | **ACTIVE:** normal operation. | |
| | **REDUCING:** exits only, no new risk. | |
| | **Cancel on entry:** when the portfolio (or, from S2, the bot) enters REDUCING or HALTED from any cause, or `UNPROTECTED`/`NOT_FLATTENABLE` becomes set, the gateway immediately cancels every open risk_increasing order, after an E5 order-book check. The unfilled remainder ends DROPPED_STATE and is journaled and alerted. | |
| | **HALTED:** no new orders, and all open bot orders are cancelled. HALTED set by E4 or `/halt` pauses all orders, including strategy exits, and alerts every 30 min until the owner decides via the CLI. Exceptions: | |
| | (i) `/flatten` is accepted in every state, including HALTED. | |
| | (ii) Flattens issued by K1 (reference or epoch threshold), `/flatten` or K7 continue under A5 until filled. | |
| | (iii) If a K1 threshold is breached while already HALTED by E4 or `/halt`, the K1 flatten is still issued. | |
| | (iv) Under an **E8** halt no API orders are sent at all. Alerts go out every 5 min with the manual Kite-app runbook (§13.6: cancel open tradebot orders, delete the GTT, then flatten). Each alert lists every open tradebot-tagged order (id, side, qty) and every live GTT id and qty from the last successful E4(0) sync. | |
| | (v) **Flatten sizing:** every flatten (K1 reference or epoch, `/flatten`, K7) sizes each ISIN at min(ledger qty, broker (settled + T1) qty − `external_holdings` qty) − the quantity in open sell orders, including any E9 GTT-triggered order (which the flatten adopts per K5(vi)). It is recomputed after the E4(0) sync before every placement and re-placement. The E9 GTT is reduced or deleted first, per E9 Coordination. A flatten therefore never sells the owner's external units. | |
| | (vi) **E9 is exempt from states:** the E9 GTT and any order it has triggered are never cancelled by a state change. E9 place, modify and re-arm are not "new orders" for K4(k) or K5. They continue in every state and flag, and stop only under an E8 halt or with no valid session. The only reductions or deletions are the ones E9 Coordination makes just before a platform sell is placed, and the deletion when the sub-ledger is flat. **Adoption:** with a valid session and no E8 halt, an open, not-fully-filled GTT-triggered order is adopted at the next E4(0) sync as a risk-reducing platform order. It is repriced under R8a exit pricing (best bid clamped to the exchange band when a K1, `/flatten` or K7 flatten is pending), its modifications count against the per-order cap, and at the cap it is cancelled and re-placed with a new E5 tag, sized per K5(v). State changes still never cancel it. | |
| | **Precedence:** each state cause (K1 reference, K1 epoch, K7, E4, E8, `/halt`, `/flatten`) is recorded and journaled separately. The effective state is the most restrictive active cause: HALTED > REDUCING > ACTIVE. A cause never lowers the state set by another. Each cause is cleared separately from the CLI, and an epoch-breach HALTED clears only via `new-epoch`. | |
| | **Status flags** (not states): | |
| | `UNPROTECTED`: no valid broker token between 09:05 IST and the close on a trading day. Blocks placement of risk-increasing orders (K4(k)). | |
| | `NOT_FLATTENABLE`: the C9 check failed. Blocks placement of risk-increasing orders (K4(k)). | |
| | `NO_BACKSTOP`: bot units in the covered qty (E9) are covered neither by an armed E9 GTT nor by an open platform sell order. Blocks placement of risk-increasing orders (K4(k)) and alerts every 30 min. | |
| | `inav_unavailable`: informational only. It switches K4(d) to the LTP band (D10) and does not block. | |
| | All flags show in `/status` and the daily summary, and clear automatically when the condition clears. | |
| K6 | **Kill switch.** `/halt` sets HALTED with no flatten. `/flatten` needs a second confirmation tap within 30 s, then flattens every bot position (A5) and sets HALTED. `/status` shows state. The CLI has the same commands. | S1 |
| K7 | **Automatic demotion** (immediate, journaled). Each rule demotes one stage down (AUTO→APPROVE, APPROVE→PAPER): | S1 |
| | (1) rolling 60-session live Sharpe below the 5th percentile of the expectation model (§10.1). The test is skipped for windows with zero return variance, e.g. fully in cash; | |
| | (2) 3 or more reconciliation HALTs within 20 sessions; | |
| | (3) bot drawdown above `risk.max_drawdown_pct`. | |
| | (4) A governor HALTED demotes **all** bots to PAPER. | |
| | **Demotion from APPROVE or AUTO has two steps.** First, the bot immediately goes to bot-level REDUCING on the live broker. In S1, where the portfolio holds one bot, this is **portfolio-level REDUCING**, added as a K7 cause under the K5 precedence rule, so it never lowers HALTED; bot-level REDUCING replaces it in S2. Leaving it follows K5 (CLI-only). An A5 flatten of its live position is issued at the same time (K4(j)). A flatten already running from K1 or `/flatten` counts as this one. Second, the stage switches to PAPER only once the live sub-ledger is flat, and the PAPER run then starts flat. The Paper → Approve clock (§10.2) restarts at that switch, and the demotion cause is written on the bot's next gate record. Until that switch, E4 real-account reconciliation, the governor and A5 re-issue all stay active. | |

### 8.5 Execution and gateway (E)

| ID | Requirement | Slice |
|---|---|---|
| E1 | **One order path.** | S1 → S2 |
| | **Gateway service:** in S1, one long-running service runs the in-session scheduler, the Telegram poller and the gateway module. Only it can call a broker order API. It owns the broker session, **one API key per broker account**, the rate limiter, the K4 checks and the audit log. | |
| | **Rate limits:** at most **5 orders/s**, plus the broker's per-minute and per-day caps (Kite: 10/s, 400/min, 5,000/day). | |
| | **Writers:** it is the only writer of `live.sqlite` (orders, fills, ledger, tax lots, journal, gate records). | |
| | **Batch jobs:** ingest, the D5 archiver, backtests and reports run as systemd timers or CLI jobs. They write Parquet or `research.sqlite` (trial registry, backtest results) and never call broker order APIs. | |
| | **Commands:** the CLI and Telegram send commands to the service. | |
| | **S2:** the gateway moves into its own process once B3 adds bot processes. | |
| E2 | Kite adapter over the official `kiteconnect` SDK. Limit orders only. Kite rejects `market_protection=0`; valid values are 1–100, or −1 for automatic. | S1 |
| E3 | **Paper broker** implementing the same interface as E2. | S1 |
| | **Fill rule:** at placement and at each reprice, the order fills in full if its limit crosses the live Kite quote (buy limit ≥ best ask, sell limit ≤ best bid), at the touch price. No modelled slippage is added; slippage is *measured* as in T3. PAPER therefore needs the E6 login for quotes. | |
| | **Rejections reproduced:** price-band and ETF-norm rejections, holidays, the T+1 sell block (lifted for T1 quantity on K1, `/flatten` and K7 flattens, per K4(j)), and the K4(h) sale-credit assumption. | |
| E4 | **Reconciliation** runs at startup, at 09:00 IST, every minute during market hours while any bot is live, and after close. In PAPER, the ledger is compared with the paper broker. Real-account checks start with the first live order (including A6 drills). Scope: every instrument in any bot's config. | S1 |
| | **(0) Sync first:** before each comparison, fetch the broker order book, trades and GTT list. Book every fill on tagged orders, including E9 GTT-triggered orders matched by GTT id. | |
| | (a) Broker quantity − `external_holdings.yaml` quantity MUST equal the sum of the sub-ledgers of bots in APPROVE or AUTO (including demotion run-off) plus the drill sub-ledger. Broker quantity = holdings (settled + T1 quantity) + today's CNC day-buy quantity. This formula must be confirmed during the A6 smoke test across the buy → T1 → settled days (§16.2 #16). PAPER sub-ledgers reconcile only against the paper broker. | |
| | (b) Every open order in scope MUST carry a bot or drill tag. | |
| | (c) Expected non-order events (IDCW, splits and bonuses from D6) are booked before comparing. If the event matches, book it and alert; don't halt. | |
| | (d) A difference that persists across 2 consecutive post-sync checks is unexplained, and sets HALTED within 60 s of the second check. | |
| | (e) An untagged fill in an in-scope instrument (a manual owner trade) is journaled as `operator` and also sets HALTED, until the ledger is reconciled from the CLI. | |
| | (f) `config/external_holdings.yaml` holds the owner's own holdings, which are excluded from bot sums. For any ISIN in a bot config it MUST hold **lot rows** (acquisition date, qty, cost per unit); the CLI refuses a quantity-only entry for such an ISIN. X1 loads these lots into the account-level FIFO queue. Changes are CLI-only and are journaled as `operator`. | |
| E5 | Every order carries a unique client tag: `tb`, the bot's 2-character `code` (B1), and a base-36 sequence, alphanumeric and at most 20 characters to fit Kite's `tag` field, unique across re-placements and process restarts because the sequence lives in `live.sqlite`. Before any retry, the gateway queries the broker order book for that tag and retries only if the original is absent. Broker-side idempotency is **not** assumed. A cancel or modify that the broker answers with "already cancelled, complete or expired" is a success: the order book is re-read and the reply is never retried. GTTs are assumed to carry no client tag (§16.2 #19): the gateway identifies its GTT by the GTT id stored in `live.sqlite`. Any other GTT on a bot ISIN is journaled as `operator` and alerted once; if it triggers, E4(e) applies. | S1 |
| E6 | **Kite daily login.** | S1 |
| | **Flow:** the registered redirect URL is a static page hosted off the VM (or `127.0.0.1`) that shows the `request_token`. The owner sends `/login <request_token>` on Telegram (M1 checks apply), and the gateway exchanges it using the api_secret. | |
| | **Token storage:** gateway memory plus a file with mode 0600 owned by the gateway's Unix user. **Never logged.** Invalidated via the logout API after the evening pipeline (§13.3 step 6), before 23:59 IST. | |
| | **Alerts:** no valid token by 08:45 IST; the `UNPROTECTED` flag at 09:05; an "unmanaged positions" alert after 3 consecutive missed logins. | |
| E7 | Dhan adapter with Dhan's official TOTP token login (unattended, 24-hour token). | Parked (S4) |
| E8 | **Static-IP order host.** | S1 (primary) / S4 (secondary) |
| | **Host:** AWS Lightsail Mumbai with a static IPv4 address. IPv6 is disabled at the OS level, because Kite rejects orders whose IPv6 source differs from the whitelisted IPv4. | |
| | **Egress check:** at startup the gateway checks its egress IP and HALTs if it isn't the whitelisted one. | |
| | **Registration:** at least **2 weeks before the first live order**, because the IP can change only once per calendar week. S1 registers the primary IP; the secondary IP comes with S4. | |
| E9 | **Broker-side GTT backstop (MUST).** Protects positions when the platform cannot act, such as no login or a dead host. | S1 |
| | **What:** while a live (non-drill) bot sub-ledger holds units, the gateway keeps exactly one tagged GTT single-leg CNC SELL LIMIT per ISIN. **GTT qty = covered qty − qty in open platform sell orders for that ISIN** (strategy exits, K1 trims and flattens, `/flatten`, K7), capped by the K5(v) bound. **Covered qty** = settled units + T1 units whose D2 settlement date is on or before the next session's open. If GTT qty is 0, no GTT is held. | |
| | **Coordination:** before placing or re-placing **any** platform sell of these units, the gateway first modifies the untriggered GTT down to the new GTT qty (or deletes it at 0), confirms it in an E4(0) sync, and only then sends the sell. When that sell is cancelled or expires, or its window or session ends with an unfilled remainder, the gateway re-arms or raises the GTT for the remainder immediately. | |
| | **Trigger:** min(the price at which portfolio epoch drawdown would reach `governor.backstop_dd` (from S2: computed per ISIN with every other position held at its LTP), LTP × (1 − `risk.gtt_min_gap_pct`/100)). `backstop_dd` defaults to −13.5%, beyond the −12% platform halt, so the two don't race. `gtt_min_gap_pct` defaults to 1; confirm Kite's minimum trigger-to-LTP gap in A6. The min() always applies, including when the backstop level has already been passed or a K1, `/flatten` or K7 flatten is pending. In that case the GTT is what carries out the pending flatten without a session. | |
| | **Limit:** trigger × (1 − `risk.gtt_limit_offset_pct`/100) (default 3), clamped to the exchange band. | |
| | **Maintenance:** placed or modified through the gateway (E1/E8, audit-logged) after every fill, and **in the evening pipeline while the token is still valid** (§13.3 step 6), for the covered qty at the next open. Arming MUST NOT depend on the next morning's `/login`; step 7 only verifies and re-arms. Deleted when the sub-ledger is flat. If Kite rejects a GTT on T1 units (§16.2 #17), set `NO_BACKSTOP` that evening and alert: "no backstop tomorrow unless you log in". | |
| | **Booking:** E4(0) books fills from GTT-triggered orders as tagged bot fills, matched by GTT id, not as `operator`. | |
| | **Known limits:** GTT triggers on LTP and isn't guaranteed at the exchange. A limit sell may not fill on a gap below the limit. GTTs expire after 1 year, so re-arm yearly. T1 units settling after the next session's open aren't covered until they settle, and if Kite rejects a GTT on T1 units (§16.2 #17) no T1 units are covered before settlement (`NO_BACKSTOP`). It needs DDPI (C9). Whether GTT API calls need the whitelisted IP is §16.2 #2, verified in A6. | |
| | **Manual path:** a documented manual flatten path from the phone (§13.6). | |

### 8.6 Autonomy stages (A)

| ID | Requirement | Slice |
|---|---|---|
| A1 | **Stages per bot:** BACKTEST → PAPER → APPROVE → AUTO. | S1 (up to APPROVE) |
| | The platform MUST refuse a promotion unless a **gate-evidence record** exists in `live.sqlite` for that bot and transition, holding the §10 criteria and their values, signed off by the owner in the CLI. | |
| | Demotions need no record. | |
| | **Exception:** CLI `promote --research <bot>` may create a Backtest → Paper record flagged `research_only`. The record shows the failed criteria values and is signed off by the owner. It allows the PAPER stage only. Paper → Approve MUST be refused for any bot whose current Backtest → Paper record is `research_only`. | |
| A2 | **APPROVE flow** for risk-increasing intents. | S1 |
| | **(a)** A Telegram message shows bot, instrument, side, qty, indicative limit, notional, reason, risk state and `approval_expiry`, with Approve/Reject buttons. | |
| | **(b)** Approve moves the intent to APPROVED. In the order window, the gateway runs the R8a drift check, K4 and a token check, then places the API order. | |
| | **(c)** If `approval_expiry` passes (default 09:15 IST on T+1), the intent becomes APPROVAL_EXPIRED and is journaled. | |
| | **(d)** A rejected or expired entry is not retried that day. It is re-emitted the next evening only under the R8a re-emission rule, each time as a fresh intent needing fresh approval, and every rejection is journaled as `operator` (A4). | |
| | OD-2 is decided: API order after Approve (§16.1). | |
| A3 | AUTO: risk-increasing intents are placed without approval, inside all limits. | Parked (S4) |
| A4 | **Operator overrides** are journaled with mistake class `operator`: manual trades in bot instruments, rejected approvals, config edits submitted during market hours, and `external_holdings.yaml` changes. | S1 |
| A5 | **Exit policy, every live stage.** | S1 |
| | **What goes out without approval:** strategy exits, the K1 flattens (reference or epoch threshold), `/flatten` and the K7 demotion flatten, as API orders under K4(j). They are algo orders, so E8 and C9 are prerequisites of the first live order. | |
| | **Never dropped:** a failed or expired exit is re-issued every session, with a repeat alert every 30 min, until it fills or is cancelled from the CLI. While the portfolio is HALTED by E4 or `/halt`, strategy exits are held (K5) and resume at the next placement opportunity after the CLI clears that halt; flattens continue regardless. | |
| A6 | **Drills and smoke test.** The CLI `drill` command creates intents for a pseudo-bot `drill`: 1 unit of the S1 risk ISIN, its own sub-ledger (counted in E4 sums), and its own order caps. They pass through the gateway and K4 without approval, are journaled as `drill`, and MUST end flat. | S1 |
| | **Paper drills** trigger checklist events that a low-frequency bot may not produce naturally (§10). | |
| | **Live smoke test,** run after C9 and E8: | |
| | 1. Day 1: a non-marketable limit buy of 1 unit at iNAV × (1 − `inav_band_bps`/2/10⁴), or LTP × (1 − `ltp_band_pct`/2/100) when iNAV is unavailable, rounded **up** to the tick. It must sit below the best bid; if it doesn't, retry later. Place it with TTL validity (R8a) and confirm the broker shows the TTL. Modify it one tick lower, which stays inside K4(d), confirm the TTL is kept, then cancel it. Then place a marketable limit buy of 1 unit. | |
| | 2. **Drill GTT (one GTT throughout).** On the evening before the unit settles, place a GTT single-leg CNC SELL LIMIT on it through the API, with trigger = LTP × 0.90 and limit = trigger × (1 − `gtt_limit_offset_pct`/100), clamped to the exchange band. This is drill-only: the E9 drawdown formula doesn't apply to the drill sub-ledger. Confirm it is still armed at the next open; this tests the T1 case (§16.2 #17). Once the unit shows as settled holdings (usually the second session after purchase; §16.2 #15), modify the trigger by one tick, delete the GTT, then place the API sell of 1 unit. This also settles §16.2 #2. | |
| | 3. Buy 1 unit, and once it settles, run the `/flatten` drill. `/flatten` sets HALTED (K6); clear it from the CLI afterwards. | |
| | 4. `/halt` drill: place a non-marketable drill limit buy of 1 unit as in step 1, send `/halt`, and confirm that the order is cancelled and HALTED is set. Clear it from the CLI. Steps 3 and 4 produce the journaled `/halt` and `/flatten` drill records; the Approve → Auto gate (§10.2) accepts them, so a repeat during APPROVE is not required. | |
| | The drill sub-ledger is excluded from automatic E9 maintenance and from `NO_BACKSTOP`. | |
| | Never a same-day round trip: that would be speculative income. | |

### 8.7 Learning loop (L): "learn from mistakes"

| ID | Requirement | Slice |
|---|---|---|
| L1 | **Append-only journal:** one row per decision, approval and fill. | S1 |
| | Fields: bot_id, git SHA, config hash, data as-of date, signal value, risk state, approval outcome and latency, intended vs filled price, slippage (T3), open-vs-fill gap (R8), full charges, tax lot, outcome label, mistake class. | |
| | Added (nullable) with L7/L8: model version, feature-snapshot hash, news IDs, LLM prompt/response hash. | |
| L2 | **Mistake class** on every losing or anomalous trade. Anomalous means slippage above 3× the model, a rejection, or a reconciliation mismatch. | S1 (auto) → S3 (owner tagging) |
| | Classes: `signal`, `execution`, `risk_breach`, `data`, `regime`, `operator`, `drill`. | |
| | Automatic: `execution`, `data`, `operator` and `drill`. The owner tags the rest from the CLI in S3. | |
| L3 | **Safe learning,** not counted as a trial: recalibrating slippage/fill models (R4), cost-model fixes from contract notes (X6), and data or execution bug fixes. | S3 |
| L4 | **Counted learning.** Any parameter or rule change is a *challenger*. It is recorded in the trial registry (R5) and increases the trial count used by R10. Until L6 is active, a challenger is a **new bot version** (new id or version suffix) and must pass every §10 gate from Backtest → Paper onward. | S1 |
| L5 | **Retraining calendar:** quarterly for swing and positional bots, monthly for intraday. **Never triggered by losses.** Drift is handled by K7; it never triggers retraining. | Parked (with L7) |
| L6 | **Champion/challenger gate.** A challenger must pass all of: | Parked (with L7) |
| | (a) PBO < 0.05. Values from 0.05 to 0.2 are allowed only with a journaled owner override. | |
| | (b) DSR ≥ 0.95, using the trial count from the registry. | |
| | (c) OOS after costs and tax, it beats the current champion (or the rule-only baseline, for ML overlays) and RM. | |
| | (d) At least 2 months of shadow paper, with median slippage ≤ model + 2 bps and drawdown ≤ 50% of `risk.max_drawdown_pct`. | |
| | (e) Owner sign-off. | |
| | (f) Capital ramps 25% → 50% → 100%, at least 1 month per step, with (d) re-checked at each step. | |
| | (g) Automatic demotion on any breach. | |
| | Promotion uses model-registry aliases (e.g., MLflow "champion"). | |
| L7 | ML only as gradient-boosted filters or position sizers **on top of rule-based bots**. | Parked (trigger: at least 1 bot with 6 months live and a hypothesis with OOS evidence) |
| L8 | **News features:** FinBERT or LLM scoring with entity names masked, a pinned model version and stored prompt/response hashes. Evaluated only on news published **after the model's knowledge cutoff**. Uses the D5 archive. | Parked (with L7) |
| L9 | **Quarterly mistakes review:** a journal query grouping losses by mistake class. Proposed fixes are queued as challengers (L4). | S3 |

### 8.8 Monitoring and reporting (M)

| ID | Requirement | Slice |
|---|---|---|
| M1 | **Telegram bot over long polling** (no inbound ports). | S1 |
| | **(a) Identity:** accept updates only where `from.id` equals the owner's ID **and** `chat.id` equals the owner's private chat. | |
| | **(b) Callbacks:** callback data (max 64 bytes) carries a single-use nonce bound to one intent. It is rejected after `approval_expiry` or on reuse. | |
| | **(c) Token:** the bot token is a secret. HTTP 409 conflicts or unexpected `getUpdates` gaps raise an alert, because they suggest another poller has the token. | |
| | **(d) 2-step:** the owner's Telegram account MUST have 2-step verification. | |
| | **(e) CLI-only:** leaving REDUCING or HALTED, raising limits, promotions and config changes can only be done from the CLI over SSH. | |
| | **(f) Rate:** stay under about 1 message per second per chat. | |
| M2 | **Reports.** Daily Telegram summary: positions, P&L after costs, drawdown, state and flags, and tomorrow's pending intents. The monthly report arrives in S2: per bot and portfolio, after costs and after tax, against RM/BH/PF, with tracking against the expectation model. | S1 → S2 |
| M3 | **Health checks:** token validity, data freshness, missed scheduled jobs, egress IP, clock synchronisation (NTP offset 1 s or less). An **external dead-man heartbeat** (e.g., healthchecks.io free tier) alerts by Telegram or email if the daily pipeline or the poller stops checking in. Disk and error-rate checks come in S2. | S1 → S2 |
| M4 | Web dashboard. | Parked (trigger: owner request only) |

### 8.9 Tax and accounting (X)

| ID | Requirement | Slice |
|---|---|---|
| X1 | **Tax lots** per demat account per ISIN, matched FIFO. Each dividend-reinvestment unit is its own lot, with its own date and cost. Holding period and bucket come from the account-level lot; per-bot tax P&L is an allocation used for reporting only. | S1 |
| | **Buckets:** equity STCG (held ≤12 months); equity LTCG; specified-MF/debt-ETF gains (slab rate whatever the holding period; unverified standard rule); dividend income (slab rate, TDS tracked); speculative (intraday); non-speculative (F&O); later VDA (crypto). | |
| | **Labels** are concepts, not section numbers, because sections changed under the Income-tax Act 2025. | |
| X2 | **Advance-tax estimate** for each instalment: 15 Jun, 15 Sep, 15 Dec and 15 Mar at 15/45/75/100%, plus 31 Mar for gains realised after 15 Mar. Uses X5, and shows the shortfall and estimated interest. | S2 |
| X3 | **Export for the CA and ITR filing.** ITR-2 (due 31 Jul) if there are only capital gains. ITR-3 (due 31 Aug) if there is any business income: intraday, F&O, or delivery trading treated as business income under OD-7. Reminders go out 30 and 7 days before the due date. Losses carry forward only when the return is filed on time. | S2 |
| X4 | Crypto (VDA) tax regime. | S6, if OD-11 = yes |
| X5 | **Tax profile config,** dated per tax year: regime (new or old), expected non-trading income band (sets surcharge), LTCG exemption already used outside the platform, and available loss carry-forwards. | S1 |
| | Defaults: new regime; slab rate 30%; surcharge tier 15% on capital gains and 25% on slab income; 4% cess on tax plus surcharge; no LTCG exemption available to the bots. | |
| X6 | **Contract-note reconciliation.** | S1 (import) / S2 (AIS) |
| | **Sources:** contract notes from the Zerodha Console download or the emailed PDF; the tradebook from the Kite trades API or Console. | |
| | **Per fill:** charges are compared against R3. If the difference exceeds max(₹1, 1%), alert and fix the cost model (L3). | |
| | **Monthly** against the broker's tax P&L; **yearly** against AIS/26AS before filing (S2). | |
| | **Golden tests:** seeded from the owner's existing ETF contract notes, or from fixtures hand-computed from the Appendix A.2 rate card until live notes exist. | |

### 8.10 Compliance (C)

| ID | Requirement | Slice |
|---|---|---|
| C1 | Stay under 10 orders/second per exchange across all bots (the registration threshold). The gateway hard-caps at 5/s. | S1 |
| C2 | One API key per broker account, used by all (unregistered) algos. | S1 |
| C3 | No plain market orders. Exchanges reject them from algos. | S1 |
| C4 | OAuth/2FA login only. The session is invalidated daily and never reused across days. | S1 |
| C5 | A static IP is registered with the broker, and all API order placement, modification and cancellation uses IPv4 egress from it (E8). If the IP is lost, the runbook is a manual place or flatten in the Kite app, which is not an algo order. | S1 (primary) / S4 (secondary) |
| C6 | **Accounts:** only the owner's own in year 1. A later family account (spouse, dependent children, parents) needs its own API key, a daily login by the account holder, a broker IP-sharing declaration (Zerodha) or its own IP (Dhan), and its own tax ledger and X5 profile. Never any third party. | Always |
| C7 | **Audit log and journal:** append-only with a **hash chain**. Nightly encrypted off-host backup to versioned object storage with a deletion lock. Restore drilled before Paper → Approve and quarterly after that. Kept **8 years** after the end of the tax year, together with the broker contract notes. | S1 |
| C8 | A monthly Telegram reminder to review new SEBI/NSE circulars (e.g., SEBI's 12 Sep 2026 consultation on the closing auction, market timings and derivative settlement). | S1 |
| C9 | **DDPI signed and active** with the broker before the first live order. Without DDPI, each API sell of holdings needs a same-day CDSL e-DIS/TPIN authorisation, which unattended exits can't provide (unverified; confirm with Zerodha). A pre-open **sellability check** looks at the Kite holdings API authorised quantity against settled quantity, or a DDPI flag (mechanism unverified, §16.2 #3). On failure it sets the `NOT_FLATTENABLE` flag and alerts. | S1 (before first live order) |

### 8.11 Options (O) and intraday (I) research tracks

| ID | Requirement | Slice |
|---|---|---|
| O1 | Options pricing and Greeks (IV, delta, gamma, theta, vega) from D9 data. | S5 |
| O2 | **Defined-risk options templates** (vertical spreads, iron condors), with max loss computed before entry. Backtests use current costs: options STT 0.15% of premium on sale and 0.15% of intrinsic value on exercise (both from 1 Apr 2026), and exchange charges of 0.03553% of premium (from 1 Mar 2026). Plus current lot sizes and expiry rules (Appendix A.1). | S5 |
| I1 | **Intraday paper bots:** minute-bar replay (D4), square-off before the broker's auto square-off (₹50 + GST per order), closing-auction constraints, and K2. | S5 |

## 9. Non-functional requirements

| Area | Requirement |
|---|---|
| Reliability | Every scheduled job is idempotent and restart-safe, and missed runs are detected (M3). State survives restarts. No live position changes without a prior reconciliation. All schedules are IST; timestamps are stored in UTC with the IST session date alongside, and the host keeps NTP time (M3). |
| Security | Broker and Telegram secrets are readable only by the gateway's Unix user (mode 0600 files or AWS SSM), never in git and never logged. From S2, bot processes hold no broker credentials. SSH keys only; no inbound ports except SSH. Telegram as in M1. |
| Auditability | Any past decision can be reproduced from (git SHA, config hash, data snapshot). The audit log is tamper-evident (C7). |
| Deployment | Deploy outside market hours only, and verify the version on the host. Never reuse config flags. Bot config changes take effect at the next session start; edits submitted during market hours are queued and journaled as `operator`. Risk-reducing commands and demotions apply immediately. The in-market incident runbook is **halt and cancel**: never redeploy or roll back mid-session (Knight Capital, Appendix A.9). |
| Timeliness | The daily pipeline (ingest, signals, intents, approval requests) finishes by 21:00 IST on T. Only the signal and K4 inputs gate it; benchmark series (TRI, AMFI NAV) never block it (§13.3 step 3). If the signal inputs aren't published, retry every 10 min until 20:30. After that, no new signal for T and an alert; pending A5 exits are unaffected. |
| Cost | ₹5,000/month or less (§13.8). |
| Testability | Unit tests for every pure function. Cost-model golden tests (X6). Paper end-to-end runs on replayed sessions. Failure-injection tests (§13.7). The paper gate is an execution-event checklist, not just a duration. |

## 10. Lifecycle gates

### 10.1 Expectation model

For each bot, take the daily OOS returns from its R5 walk-forward (risk-free rate 0). Compute the distribution of rolling 60-session Sharpe ratios and of 60-session cumulative returns.

- **Expected** = the median of each distribution.
- **Band** = the 5th to 95th percentiles.

T3 and K7 use this model. For a bot that is often in cash, the distribution naturally includes flat periods.

### 10.2 Gates

A1 enforces every promotion through a recorded gate-evidence record.

| Transition | Entry criteria (all required) |
|---|---|
| **Backtest → Paper** | (1) R5 chained OOS return after costs and tax (R7) beats **RM**; factor bots must also beat **PF**. (2) The governed backtest's **epoch max drawdown** (K0, over the whole backtest) is ≤ `risk.max_drawdown_pct`, and the governor never reaches HALTED. (3) All trials are logged in R5; DSR is reported from S3 (R10). (4) From S2, parity per P1. |
| **Paper → Approve** | (1) At least 2 months of paper; bots with `planned_turnover` above 50/yr also need at least 50 paper trades. (2) Execution checklist completed, naturally or through A6 paper drills: order placed and filled; a rejection handled; clean reconciliation; a process restart survived; a holiday handled; a corporate action booked (if relevant). (3) Paper slippage within T3, measured at real quotes (E3). (4) Prerequisites: DDPI active (C9); static IP registered and egress check passing (E8); E9 GTT place/modify/delete and Kite TTL validity verified in A6; backup restore drilled (C7); **OD-7 decision recorded with the CA's name and date**. (5) A6 live smoke test completed, ending flat, with fills within T3. |
| **Approve → Auto** | At least 4 weeks and at least 5 approved live orders. Zero unexplained reconciliation mismatches. `/halt` and `/flatten` each executed at least once on the live account (the A6 smoke-test drills count), with a journaled drill record. AUTO itself is parked (S4). |
| **Capital scale-up** | (1) **At least 12 months live in the current epoch,** counted from the latest date the portfolio entered APPROVE or AUTO. Any all-bots demotion to PAPER, or a new epoch, restarts the clock. The window MUST contain a **full cycle**: at least one Nifty 50 drawdown of 8% or more from peak; if not, extend until it does. (2) Return after costs and tax above **RM** (factor bots also above PF; BH reported). (3) **Epoch max drawdown under 15%** (K0). (4) Live results inside the §10.1 band. (5) **Live DSR on excess return over RM ≥ 0.95,** with the registry trial count (R10). Then ramp capital in 1.5–2× steps, re-gating each step. Caveat: 12 months of daily data confirms only a true Sharpe of about 1.65 or higher *against zero* (Appendix A.4). Against a benchmark, the excess-return bar is higher, and more bots raise it further, so criterion (5) can take longer than 12 months. |
| **Demotion** | Automatic per K7. |

## 11. Strategy roadmap

The figures below are secondary-source numbers that have not been independently verified. Treat them as directional (Appendix A.5).

| # | Bot | Market | Horizon | Evidence | Slice / stage |
|---|---|---|---|---|---|
| 1 | **ETF trend filter** (spec in §11.1) | NSE ETF | Positional (~8–10 switches/yr) | **Drawdown control, not extra return.** 2007–26 on the price index: 9.7% CAGR and −16.2% max drawdown, vs buy-and-hold 9.1% and −59.9%. It has lagged buy-and-hold by about 1 pp/yr since 2015, and the pre-tax edge likely disappears after STCG. It MUST be re-tested on TRI with a real cash leg, after tax (§11.1). | S1 → live (APPROVE) |
| 2 | **Cross-sectional momentum** (point-in-time Nifty 200, semi-annual rebalance) with a trend overlay or exposure cap. Default at ₹2L: **time a momentum index fund/ETF** (OD-6). | NSE equity / ETF | Positional | The strongest Indian anomaly. IIMA winners-minus-losers 10.65%/yr gross long-short since 1994 (worst drawdown −62%). Nifty200 Momentum 30 TRI 19.19% vs Nifty 200 15.08% (Apr 2005–Feb 2026). Estimated +1–4 pp/yr over the index after costs and tax. Unhedged drawdowns of 25–70%; lagged its parent by 14.1 pp in 2025. | S2 |
| 3 | **Low-volatility sleeve** (ETF or index fund) | NSE ETF | Positional (quarterly) | Nifty100 Low Vol 30, 5 years: 10.47% (beta 0.79), vs Nifty 50 8.32% | S2 |
| 4 | **Swing pullback / breakout** | NSE equity | Swing | Thin edge: about +0.2–0.3% per trade above drift, low confidence, survivorship-biased. The ~30–35 bps break-even edge for delivery (Appendix A.2) consumes it. | Paper only, until it passes walk-forward on survivorship-free data |
| 5 | **News / event** (post-earnings drift) | NSE equity | Swing | No Indian net-of-cost evidence | Research only (D5 archive; L8 parked) |
| 6 | **Options, defined-risk** | NSE F&O | Weekly / monthly | Median options buyer −114% in FY26; selling needs large capital | S5 research and paper (§12) |
| 7 | **Intraday** (opening-range breakout, VWAP) | NSE equity | Intraday | No credible Indian evidence. Opening-range breakout failed OOS after costs on US futures. Nifty gap fades are about 15 bps against a 15–20 bps break-even edge (Appendix A.2). | S5, paper only |
| 8 | **BTC/ETH trend** | Crypto (Delta Exchange India) | Positional | Needs a profit factor of about 1.45–1.56 just to break even under crypto tax | Year 2 at the earliest (OD-11) |
| – | **Skip:** weekly short-term reversal (net about 10 pp/yr behind equal-weight after costs), options buying, grid/scalping/market-making | | | | |

### 11.1 S1 bot specification (`etf-trend-v1`)

- **Signal:**
  - Compare the Nifty 50 **price index** close on session T with the simple moving average (SMA) of the last `ma_days` session closes, including T.
  - Close > SMA → `target_exposure = 1`; otherwise 0.
  - No hysteresis in v1. A hysteresis band is a later challenger (L4).
- **Instrument:** NIFTYBEES (the risk leg). The cash leg is **cash**, earning 0% (OD-12).
- **Returns in backtest:** NIFTYBEES prices plus distributions from its listing. Before listing, the Nifty 50 TRI is the proxy.
- **Backtest window:** from 2007-01-01 (using the D10 pre-2013 liquid-fund proxy) to the latest session. It MUST include 2008.
- **Position:**
  - target ₹ = `target_exposure` × `max_exposure` × `allocation` × capital (K0).
  - qty = floor(target ₹ / NIFTYBEES close on T).
  - Trade only if abs(target ₹ − current ₹) > 5% of capital.
  - **No rebalancing within a regime:** a price move in the held position never triggers a trade.
  - **Exception, K1 halving:** governor-driven target changes are not rebalancing. When the −6% halving engages and abs(governed target ₹ − current ₹) > 5% of capital, a **trim** sell is emitted as a risk_reducing intent (A5, no approval, strategy-exit window). When the halving lifts, the **top-up** buy is a risk_increasing intent under A2 and the R8a re-emission rule. The bar-replay backtest applies the same rule.
- **Walk-forward (R5):**
  - Anchored: 5-year train, 1-year test, 1-year step.
  - Grid: `ma_days` ∈ {50, 100, 150, 200} × `max_exposure` ∈ {0.5, 0.6, 0.7, 0.8, 0.9, 1.0}, which is 24 points per window, all logged.
  - **Selection** per train window: the highest after-tax return where the governed **epoch** max drawdown is ≤ 12% **and** the governor never reached HALTED. If no point qualifies, `max_exposure` = 0.5 at `ma_days` 200, flagged.
  - **Pass:** the chained OOS after-tax return beats RM over the same span.
  - Live parameters = the selection from the most recent train window.
- **Risk:** `risk.max_drawdown_pct` = 12, which equals the K1 halt, because this bot is the whole portfolio in S1.

## 12. Position on options strategies

**Options are in scope as a research and paper track, but not live at ₹2L.**

- **Why not live now:**
  - **Size:** one NIFTY lot (65) is about ₹16L notional.
  - **Margin:** naked short margin is roughly ₹1.5–2.5L per lot, plus an extra 2% (about ₹32k) on expiry day (unverified; §16.2 #11).
  - **Drawdown budget:** a single defined-risk spread uses up most of the ₹20–30k budget.
  - **Hedging doesn't fit either:** one lot of index puts hedges about 8× the whole portfolio.
  - **Track record:** retail outcomes are the worst of any segment (§2).
- **What S5 builds:**
  - D9 data.
  - O1 pricing and Greeks.
  - O2 defined-risk templates with current costs.
  - Paper trading.
  - Expiry rules: NSE weekly expiry is Tuesday (NIFTY only), BSE is Thursday, and there are no BANKNIFTY/FINNIFTY weeklies.
- **Going live** needs about **₹10L+ capital** (OD-10), the same §10 gates, defined risk only, and a per-position max loss inside the bot's `risk.max_drawdown_pct` budget.
- **Tax:** F&O is non-speculative business income at the slab rate, filed on ITR-3.
- **Sensibull** is a manual cross-check tool, not a dependency.

## 13. Technical direction

### 13.1 Stack

| Concern | Choice | Why |
|---|---|---|
| Language | Python 3.12 or 3.13, managed with `uv` | Quant/ML ecosystem. Check numba/vectorbt support before moving to a newer Python. |
| Broker SDK | Official `kiteconnect` (S1); `dhanhq` (parked) | Maintained and compliant. Community TOTP-scraping logins for Kite are unofficial and may breach Zerodha's terms, so they MUST NOT be used. |
| Research | Own bar-replay backtester (S1); vectorbt open source (S2) | One code path in S1. Sweeps later. |
| Market data | Parquet files keyed by ISIN, queried with DuckDB | DuckDB allows either one read-write process or many read-only ones, never both. So batch jobs write Parquet, and readers use DuckDB. |
| State | `live.sqlite` (WAL mode), with the gateway as its only writer: orders, fills, ledger, tax lots, journal, gate records. `research.sqlite`: trial registry and backtest results. | One host, one writer. Move to Postgres only if S2 multi-process needs it. |
| Messaging | Telegram Bot API, long polling (any maintained client) | No inbound ports |
| Scheduling | systemd service (gateway, with in-session scheduler) plus systemd timers (ingest, archiver, backups, reports) | Boring and supervised |
| Host | AWS Lightsail Mumbai, 2 GB, static IPv4 | About $12/month with static IP included (price unverified; §16.2 #7) |
| Backup | Encrypted nightly copy to versioned object storage with object lock (e.g., S3) | C7 |
| Heartbeat | healthchecks.io free tier or equivalent | M3 |
| Rejected (Appendix A.8) | NautilusTrader (v2 still in release candidates; no Indian adapter), OpenAlgo (AGPL; recent order-hang and symbol-mapping bugs), Lean (paid tier; C# core), backtrader (dormant) | Revisit NautilusTrader once v2 is stable. |

### 13.2 Components (S1)

```
tradebot/
  data/        ingest (bhavcopy, Kite day candles, niftyindices, AMFI, iNAV), calendar (D2),
               quality (D3), corporate actions (D6), news archiver (D5)
  strategy/    pure signal functions (R1): etf_trend(view_as_of_t, params) -> target_exposure
  backtest/    bar-replay engine: strategy -> risk (incl. governor) -> fill model (R2, R5, R8)
  costs/       dated cost table + calculator (R3), slippage model (R4)
  risk/        definitions (K0), governor (K1), pre-trade checks (K4), states/flags (K5), demotion (K7)
  gateway/     order path (E1): placement algo (R8a), rate limiter, audit log (C7),
               reconciliation (E4), retry (E5), login (E6), egress check (E8)
    brokers/   Broker interface + paper (E3) + kite (E2)
  approvals/   intents, Telegram flow (A2, A5, M1), nonces, drills (A6)
  ledger/      positions, fills, FIFO tax lots (X1), tax profile (X5), contract-note import (X6)
  journal/     decision journal (L1), mistake classes (L2), trial registry (R5), gate records (A1)
  reports/     daily summary (M2), after-tax vs RM/BH (R7)
  ops/         health + heartbeat (M3), backup (C7)
  cli/         the only path for un-halting, config changes, promotions, drills, external holdings
config/        portfolio.yaml, bots/*.yaml, costs/*.yaml (dated), tax_profile.yaml, external_holdings.yaml
```

**Interfaces other code depends on:**
- `Broker`: place, modify, cancel, orders, trades, positions, holdings, funds, quote. Implementations: paper and Kite.
- `strategy(view_as_of_t, params) -> target_exposure ∈ [0, 1]`: pure, no I/O.
- `Intent`: intent_id, bot_id, kind (`risk_increasing` | `risk_reducing` | `drill`), isin, side, qty, indicative_limit, reason, risk_state, `approval_expiry`, `order_expiry`. Bots emit intents; the gateway consumes them.

### 13.3 Daily flow (S1 bot)

The cycle below runs from the close of session T to the close of session T+1, then repeats.

1. **After the close of T (~15:45 IST). Wrap up.** Reconcile (E4), import contract notes and tradebook (X6), write the journal. The Kite session stays valid for the evening pipeline.
2. **19:00. Ingest signal inputs.** Bhavcopy, Kite day candle (needs the still-valid token), Nifty 50 price close, corporate actions. Retry per §9, then run the D3 checks. A failure means no signal for T and an alert.
3. **Ingest benchmark series separately.** Nifty 50 TRI and AMFI NAV run on their own schedule, retrying until 09:00 on T+1 and alerting if still missing. They **never** block or delay a signal or intent.
4. **Decide** (no earlier than `schedule.signal`, 20:00). Gated **only** on signal and K4 inputs for session T: the NIFTYBEES bhavcopy (D1), the Nifty 50 price-index close, the D3 Kite day-candle cross-check, and D6 corporate actions for the S1 ISIN. If they haven't passed by 20:30, no signal is computed for T (§9). The strategy view MUST assert that its latest bar is session T (from D2); otherwise no intent is emitted, and the run is journaled as `data` and alerted. Then: strategy target (§11.1), compared with the ledger position, then the K1 governor, then an intent. A risk-increasing intent goes to Telegram (`approval_expiry` 09:15 on T+1). A risk-reducing intent is queued automatically (A5).
5. **After Decide. Summary.** Send the daily summary (M2), including pending intents for T+1.
6. **Evening close-out.** Arm or modify the E9 GTT for the covered qty at the next open (settled units plus T1 units settling by then). Then log out through the Kite logout API (C4, E6) once steps 4–5 finish, never later than 23:59 IST. Back up (C7). The heartbeat pings after every step (M3).
7. **08:30 on T+1. Pre-open checks.** Kite login via `/login` (E6), egress-IP check (E8), sellability check (C9), E9 GTT check and re-arm (units that settled overnight). **09:00:** reconcile (E4).
8. **09:20–10:30 on T+1. Place orders.** This window applies to approved entries and strategy exits. The K1, `/flatten` and K7 flattens are placed immediately whenever they are issued during the normal session (K4(j)). Intents run R8a: drift check, K4(k) state check, sells first (K4(h)), limit pricing, repricing. At `order_expiry` the remainder is cancelled and the order ends EXPIRED. That is 10:30 for entries and strategy exits; for K1, `/flatten` and K7 flattens it is the session close, and until then they keep re-placing (R8a). Exits are re-issued in the next session under A5.
9. **Every minute while live. Reconcile.**

### 13.4 Order lifecycle

```
INTENT -> APPROVAL_PENDING -> APPROVED | APPROVAL_REJECTED | APPROVAL_EXPIRED
APPROVED (or risk_reducing / drill, which skip approval)
  -> RISK_CHECKED | DROPPED_DRIFT | DROPPED_CHECK (K4 failure) | DROPPED_STATE (K4(k)) | DROPPED_NO_TOKEN
RISK_CHECKED -> PLACED -> (PARTIAL ->)* FILLED | CANCELLED | BROKER_REJECTED | EXPIRED
```

- Every transition is written to the audit log with a timestamp and a hash-chain link. Retries follow E5.
- **Restart:** on startup the gateway rebuilds every in-flight order from the broker order book by tag (E5) before it resumes R8a repricing or places anything. An approved intent whose order is not at the broker is placed only if its `order_expiry` has not passed. Approvals survive restarts because they live in `live.sqlite`.
- **DROPPED_NO_TOKEN** is the terminal state when the broker session is invalid at placement, whatever the flags say; **DROPPED_STATE** covers every other K4(k) failure.
- A **risk_reducing** intent that ends in any non-FILLED terminal state triggers an A5 re-issue at the next placement opportunity.
- A **risk_increasing** intent that ends that way is journaled and alerted.

### 13.5 Config schema and example

```yaml
# config/portfolio.yaml
starting_capital: 200000
governor: { halve: -6, halve_release: -3, reduce: -10, halt: -12, backstop_dd: -13.5, backtest_cooloff_sessions: 20 }
hard_drawdown_limit: 15
benchmarks: { rm_liquid_amfi_code: "<AMFI scheme code>" }   # chosen at S1 start
brokers: { kite: { api_key_env: KITE_API_KEY } }
telegram: { bot_token_env: TG_BOT_TOKEN, owner_user_id: <owner's Telegram user id>, chat_id: <owner's private chat id> }   # M1(a)

# config/bots/etf-trend-v1.yaml
id: etf-trend-v1
code: et                   # 2-character code used in order tags (E5); unique across bots, `dr` is reserved for drills
strategy: etf_trend
params: { signal_index: NIFTY50, ma_days: 100 }       # ma_days from latest walk-forward selection
venue: nse                                              # allowed: nse
instruments: { risk: "<NIFTYBEES ISIN>", cash: null }   # ISIN from the NSE master (§16.2 #6); cash leg = cash
horizon: positional                                     # allowed: intraday | swing | positional
schedule: { signal: "20:00", order_window: ["09:20", "10:30"], approval_expiry: "09:15" }
allocation: 1.0            # fraction of capital (K0)
max_exposure: 1.0          # placeholder; set from walk-forward selection (§11.1)
planned_turnover: 10       # switches per year
risk:
  max_drawdown_pct: 12
  max_orders_per_day: 2
  ltp_band_pct: 1.5        # accepted range 1–2
  inav_band_bps: 25
  drift_pct: 2
  adv_cap_pct: 5
  allow_unsettled_sell: false
  gtt_limit_offset_pct: 3   # E9 backstop limit below trigger
  gtt_min_gap_pct: 1        # E9 trigger at least this far below LTP
# no `stage` key: stage lives only in the gate-record table (A1, B1)
research:
  walk_forward: { anchored: true, train_years: 5, test_years: 1, step_years: 1 }
  grid: { ma_days: [50, 100, 150, 200], max_exposure: [0.5, 0.6, 0.7, 0.8, 0.9, 1.0] }

# config/external_holdings.yaml   (E4(f): lot rows are mandatory for any ISIN that appears in a bot config)
- isin: "<NIFTYBEES ISIN>"
  lots:
    - { acquired: 2024-03-12, qty: 150, cost_per_unit: 241.30 }

# config/tax_profile.yaml   (X5: one entry per tax year)
- tax_year: 2026-27
  regime: new
  slab_rate_pct: 30
  surcharge_pct: { capital_gains: 15, slab_income: 25 }
  cess_pct: 4
  ltcg_exemption_available_inr: 0
  loss_carry_forward_inr: { stcl: 0, ltcl: 0 }

# config/costs/zerodha.yaml   (R3: one row per charge with an effective-from date; S1 needs the NSE cash CNC rows only)
# effective_from 1900-01-01 means "current rate applied to all history" until dated rows exist (R3)
- { broker: zerodha, segment: nse_cash, product: cnc, charge: brokerage,    side: both, rate_pct: 0,       effective_from: 1900-01-01 }
- { broker: zerodha, segment: nse_cash, product: cnc, charge: stt,          side: sell, rate_pct: 0.001,   applies_to: equity_etf, effective_from: 1900-01-01 }   # verify on a contract note (§16.2 #4)
- { broker: zerodha, segment: nse_cash, product: cnc, charge: stt,          side: both, rate_pct: 0.1,     applies_to: equity,     effective_from: 1900-01-01 }
- { broker: zerodha, segment: nse_cash, product: cnc, charge: exchange_txn, side: both, rate_pct: 0.00307, effective_from: 2026-03-01 }
- { broker: zerodha, segment: nse_cash, product: cnc, charge: sebi_fee,     side: both, rate_per_crore_inr: 10, effective_from: 1900-01-01 }
- { broker: zerodha, segment: nse_cash, product: cnc, charge: stamp_duty,   side: buy,  rate_pct: 0.015,   effective_from: 1900-01-01 }
- { broker: zerodha, segment: nse_cash, product: cnc, charge: gst,          side: both, rate_pct: 18, on: [brokerage, exchange_txn, sebi_fee], effective_from: 1900-01-01 }
- { broker: zerodha, segment: nse_cash, product: cnc, charge: dp,           side: sell, flat_inr: 15.34, per: scrip_per_day, effective_from: 1900-01-01 }
```

### 13.6 Deployment and runbooks

- **Deploy:** by git tag to the host. The service checks its tag against the expected version at startup. Deploys run only outside 08:30–16:00 IST on trading days.
- **In-market incident:** `/halt` (sets HALTED and cancels open orders). Investigate after the close. Use `/flatten` only if the exposure itself must go.
- **Lost IP or host:** in the Kite app, in this order:
  0. **Cancel every open tradebot-tagged order** (listed in the alert).
  1. **Delete the tradebot GTT** for each bot ISIN (listed in the alert).
  2. Flatten manually (not an algo order). Take the quantity from the Kite holdings and positions screens, not from the alert.
  3. Fix the host. E4(e) books the manual fill as `operator`.
- **Planned absence:** before leaving, set bots to REDUCING from the CLI, or hold cash.
- **Missed login:** without a token the platform can't place orders, and the `UNPROTECTED` flag is set. The E9 GTT at the broker stays armed as the backstop. A5 exits wait for the next valid session, so log in, or flatten manually in the app.

### 13.7 Testing strategy

- **Unit tests** for every pure function:
  - strategy; cost calculator;
  - governor: backtest re-entry, a second −12% leg after a reference-peak reset triggering the epoch breach, and the −6% halving applied to the target;
  - K4 checks: the (j) exemptions including intraday flatten outside the order window, and (k);
  - FIFO lots including external lots; calendar and settlement dates; NAV/units.
- **State-machine invariants** (MUST). K5/K7/A5/K1 are implemented as one explicit transition table, with property-based tests over random event sequences (breaches, E4 mismatches, E8, `/halt`, `/flatten`, demotions, fills, restarts). The tests assert:
  - a cause never lowers the state set by another;
  - risk-increasing orders are placed only in ACTIVE with no blocking flag;
  - a flatten is never blocked except under E8 or when there's no valid session;
  - outside E8 and no-session periods: for every live (non-drill) ISIN, armed GTT qty + open platform sell qty ≥ covered qty (E9). `NO_BACKSTOP` may stand in only after the broker has rejected the GTT, never because of a HALTED or REDUCING cause;
  - at every evening logout, an armed GTT covers every bot unit that will be settled at the next open, unless the broker rejected it and `NO_BACKSTOP` is set;
  - a platform sell is never sent while the untriggered GTT qty + that sell's qty exceeds the covered qty;
  - total open sell quantity per ISIN (platform plus GTT-triggered) never exceeds the K5(v) bound, so there's no double sell;
  - flatten qty ≤ the K5(v) bound, and external units are never sold;
  - no same-session buy is sold;
  - an epoch breach clears only via `new-epoch`;
  - a demoted bot reaches PAPER only when flat;
  - outside E8 and no-session periods, no risk_increasing order is open at the broker while the effective state isn't ACTIVE or a blocking flag is set. At all times, every open risk_increasing order carries a broker-side TTL ending no later than its `order_expiry`;
  - with a valid session and no E8 halt, no GTT-triggered sell rests with its limit above the best bid for longer than one R8a reprice interval (60 s);
  - a fully invested position crossing −6% produces a trim to 0.5× the target.
- **Golden tests** for the cost model against contract notes (X6).
- **Replay end-to-end:** historical sessions through the full S1 pipeline with the paper-fill model, asserting journal, ledger and tax-lot outcomes.
- **Failure injection:**
  - data and session: stale or holiday-duplicate file, token expiry, IPv6 egress;
  - execution: reconciliation mismatch, untagged manual fill, broker rejection, modification cap;
  - approvals: Telegram nonce reuse or late tap, iNAV unavailable;
  - settlement: the T1 sell block.

### 13.8 Recurring cost (S1)

| Item | ₹/month |
|---|---|
| Kite Connect (market data + historical; ₹500 + GST) | ~590 |
| Lightsail Mumbai 2 GB with static IP ($12 incl. GST at ₹96/$; price unverified) | ~1,360 |
| Backup storage, heartbeat | <100 |
| **Total** | **~2,050** |

Parked additions: a secondary IP (about ₹570) with S4, and EODHD news (about ₹1,920 before GST and card forex markup) only if OD-9 says so.

## 14. Release plan (vertical slices)

The full multi-bot platform with the learning loop takes about **9–12 months part-time**. The first live trade comes much earlier.

| Slice | Scope (requirement IDs) | Exit criteria | Target |
|---|---|---|---|
| **S1: first bot end to end** | Bot #1 (§11.1). **Data:** D1 (incremental + S1 history), D2, D3, D4 (check, archive if needed), D5 (side), D6 (S1 instruments), D10. **Research:** R1, R2 (bar-replay), R3 (Zerodha delivery), R4 (static), R5, R7, R8, R8a. **Bots:** B1, B2. **Risk:** K0, K1, K4, K5 (portfolio), K6, K7. **Execution:** E1–E6, E8 (primary), E9. **Autonomy:** A1, A2, A4, A5, A6. **Learning:** L1, L2 (auto), L4. **Monitoring:** M1, M2 (daily), M3. **Tax:** X1, X5, X6 (import). **Compliance:** C1–C9 (C5 primary). | Bot #1 passes Backtest → Paper and runs on paper daily, then passes Paper → Approve (§10.2). **If bot #1 fails Backtest → Paper,** S1 still exits with the pipeline running on paper: bot #1 is promoted with `promote --research` (A1) and held at PAPER, and the owner decides OD-14. | Build Oct – mid-Nov 2026 (~60–75 h). Paper from about late Nov 2026. **First approved live order about Feb–Mar 2027**, which starts the 12-month clock. |
| S2: multi-bot | B3–B6, E1 (separate process), K3, K5 (bot level), M2 (monthly), M3 (disk, error rate), R2 (vectorbt + parity), R9, X2, X3, X6 (AIS). Bots #2 and #3. D1 backfill and D6–D8 only if OD-6 = stock-picking. | Three bots with clean sub-ledger reconciliation; bots #2 and #3 through their own paper period | Mar – Jun 2027 |
| S3: gate hygiene | R4 (calibrated), R10, L2 (owner tagging), L3, L9 | DSR and trial count recomputed and attached to every existing gate-evidence record | Jun – Aug 2027 |
| S4: full auto | E7, E8 (secondary IP), A3, C5 (secondary) | One bot promoted to AUTO | **Parked.** Trigger: approvals exceed about 10/week, or the owner can't respond within approval expiries; plus a bot with Approve → Auto evidence. |
| S5: options and intraday research | D4 (on-demand), D9, O1, O2, I1, K2 | Options and intraday bots on paper with full reports | After S3 (H2 2027 on); live only per §12 and §10 |
| ML | R6, L5–L8 | First challenger through L6 | **Parked.** Trigger: at least 1 bot with 6 months live, and a hypothesis with OOS evidence. |
| S6: scale and expand | §10 capital ramp; crypto decision (OD-11); X4 if yes | Gate decision | Earliest about Feb–Mar 2028 |
| – | M4 | – | Parked (owner request only) |

## 15. Risks

| Risk | Mitigation |
|---|---|
| Overfitting across many bots | Trial registry (R5), DSR (R10), PBO (R6), new-version rule (L4), L6 |
| Look-ahead and survivorship bias | Point-in-time, ISIN-keyed data (D1, D7); post-cutoff LLM tests (L8). Statistics alone can miss a leaky backtest (Appendix A.6), so data-timing code gets reviewed as well. |
| Understated costs | Dated cost model (R3), current rates applied to all history, contract-note checks (X6), calibrated slippage (R4) |
| Drawdown breach in a crash | Governor K1 inside backtests; `max_exposure` selection (§11.1); hard halt at −12% with flatten |
| Exits fail when needed | A5 auto-exits with the K4(j) exemptions; E9 GTT backstop; C9 DDPI plus sellability check; E8 static IP; M3 dead-man; E6 login alerts |
| Owner unreachable or no login | A5 (with a session); the E9 GTT backstop (without one); the `UNPROTECTED`/`NO_BACKSTOP` flags; runbooks in §13.6 |
| Factor regime risk (momentum lagged 14 pp in 2025) | Multiple sleeves; judge over years; RM/PF gates |
| Execution rejections (price bands, ETF norms since 7 Sep 2026, closing auction, market-order ban) | K4, R8a limit pricing, E3 models rejections |
| T+1 and settlement | K4(b), K4(h); D2 settlement dates; E3 |
| Data errors (holiday duplicates, stale delisting list, frozen RSS, yfinance mis-adjustments) | D1 date check, D3 cross-source check, D5 freshness alerts. yfinance is never a source. |
| Operational (Knight-style) incident | §9 deployment rules; halt-and-cancel runbook |
| Security (secrets, spoofed or replayed approvals, account takeover) | §9; M1 nonces, chat check, 2-step verification, CLI-only un-halt |
| Regulatory change (e.g., "OAuth only", closing auction and settlement consultation) | Kite OAuth flow; C8 monthly review |
| Tax mistakes | X1 FIFO lots; X5; X6; OD-7 recorded at the gate |
| Behavioural (overrides, scaling too early) | A4 journaling; A1 gate records; §10 |
| Proof horizon (a lucky 12 months) | §10 scale-up criteria (1) and (5) |

## 16. Open decisions and verification to-dos

### 16.1 Open decisions

| ID | Decision | Default until decided |
|---|---|---|
| OD-1 | Owner's real hours per week | 10–12 |
| OD-2 | APPROVE mechanism | **Decided: API order after Approve.** The Kite Publisher alternative (owner places each order manually) was rejected: A5 needs API exits and a static IP in S1 anyway, and Publisher can't enforce expiry, re-checks or idempotency. |
| OD-3 | AUTO-stage broker | Kite for APPROVE; AUTO not planned in year 1 (S4 parked). If AUTO later moves to Dhan, the bot first needs at least 4 weeks of APPROVE on Dhan. Kite holdings run off at Kite, or move by off-market transfer (not sold). |
| OD-4 | Can one static IP be registered at both brokers? | Not needed until S4 (Dhan requires a unique IP per person). |
| OD-5 | Governor mechanism; keep −6/−10/−12? Keep the −3 release level for the halving? | `max_exposure` plus bot #1's trend filter; −6/−10/−12; halving released at −3 (K1) |
| OD-6 | Momentum at ₹2L: pick stocks (≤8 names at ₹25k minimum each) or time a momentum index fund? | Time the index fund, which keeps stock-universe work out of S2. |
| OD-7 | Tax treatment of delivery trades (capital gains or business income), agreed with a CA before the first live trade | Capital gains. Recorded at the Paper → Approve gate. |
| OD-8 | Scale-up rule | As in §10.2. Owner to confirm. |
| OD-9 | News data: free only, or add EODHD after a free-tier test? | Free only |
| OD-10 | Live options threshold | ₹10L+ plus the §10 gates |
| OD-11 | Crypto in year 2? | Decide at S6 |
| OD-12 | Cash leg for bot #1 | **Cash (0%).** Conservative and creates no slab-rate tax items. LIQUIDBEES and liquid/overnight funds are later challengers (L4), priced after tax at the owner's marginal slab rate. They are taxed at slab rate (unverified standard rule; confirm with the CA). |
| OD-13 | Dhan data API price; Lightsail Mumbai price | Treat as unknown until quoted |
| OD-14 | What to do if bot #1 fails Backtest → Paper | Decide when it happens. Options: a hysteresis or volatility-target challenger, bot #3 (low-vol ETF) as the first live bot, or staying on paper. |

### 16.2 Facts to verify before relying on them

1. The exact end date of the SEBI algo-framework glide path (in the circular annexure).
2. That Kite access tokens expire at 6 AM, and whether GTT API calls need the whitelisted IP.
3. That DDPI covers API sells and GTT on holdings at Zerodha, and the exact sellability-check field (C9).
4. That ETF STT is 0.001% on sale, on a real contract note (some broker summaries show 0.1%).
5. The source and timeliness of ETF iNAV (D10).
6. The NIFTYBEES ISIN (the config holds a placeholder).
7. The Lightsail Mumbai price.
8. Slab-rate treatment of liquid, debt and specified funds and of ETF dividends.
9. Whether NSE corporate-action coverage goes back before 2010.
10. nsepit data accuracy (only if OD-6 = stock-picking).
11. NIFTY naked-short and expiry-day margin figures (§12).
12. Kite historical day-candle depth for NIFTYBEES back to listing (D1).
13. Exact NSE cash-segment session windows: pre-open, normal market, and closing auction after 3 Aug 2026 (D2, K4(g)).
14. The share of same-day delivery-sale proceeds usable for buys at Zerodha (K4(h)).
15. When units bought on T appear as settled holdings in Kite (A6, K4(b)).
16. The E4(a) broker-quantity formula: how Kite reports a CNC buy across the positions, holdings T1 and settled views on each day. Confirm during the A6 smoke test.
17. Whether Kite accepts a GTT CNC sell on T1 (not yet settled) units, and whether a triggered GTT sell of T1 units executes. Confirm in A6 step 2.
18. Kite `validity=TTL` support for CNC equity limit orders through the API, and whether a modification keeps or re-sets the TTL. Confirm in A6 step 1.
19. Whether Kite GTTs accept a client tag. If not, the gateway identifies its GTT by id (E5, E9).
20. That Kite serves day candles for the `NSE:NIFTY 50` index instrument and that its close matches the niftyindices.com daily report (D3).
21. Which Kite margins API field reports cash usable for a CNC buy (K4(b)).

---

# Appendix A: Evidence base (as of 30 Sep 2026)

### A.1 Regulation and market rules

| Rule | Detail | Source |
|---|---|---|
| SEBI retail algo framework | Circular of 4 Feb 2025. Go-live moved from 1 Aug 2025 to 1 Oct 2025. A glide path was announced 30 Sep 2025. Mandatory for all brokers from 1 Apr 2026 (per Zerodha; glide-path end date unverified, §16.2 #1). | [SEBI circular](https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html), [NSE/INVG/70541](https://nsearchives.nseindia.com/content/circulars/INVG70541.zip), [Zerodha static IP](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip) |
| Registration threshold | 10 orders/second per exchange. Below it: no registration, and orders carry the generic Algo ID 99999. Above it: registration through the broker. | [NSE/INVG/67858](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf), [NSE/INVG/69255](https://nsearchives.nseindia.com/content/circulars/INVG69255.zip) |
| API key and IP | Unregistered algos use one predefined API key. Static IP: a primary plus an optional secondary, changeable at most once per calendar week, shareable with family only. It applies to order place/modify/cancel; data calls work from any IP. Zerodha allows family sharing by declaration; Dhan requires a unique IP per person. | NSE/INVG/67858 A.1–A.7; Zerodha static IP page |
| Sessions | OAuth/2FA only; sessions logged out before the next trading day | NSE/INVG/67858 A.8 |
| Market orders | Plain market orders from algos are rejected (cash segment from 30 Jun 2025). On Kite, `market_protection` must be 1–100 or −1. | [NSE/FAOP/69296](https://nsearchives.nseindia.com/content/circulars/FAOP69296.pdf), [Kite orders](https://kite.trade/docs/connect/v3/orders/) |
| Manual orders | Kite Publisher orders placed manually by the user fall outside the algo framework | [Kite FAQ](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs) |
| Kite limits | 10 orders/s per account, 400/min, 5,000/day, 25 modifications per order | [Kite exceptions](https://kite.trade/docs/connect/v3/exceptions/) |
| Algo provider | Serving non-family users needs exchange empanelment, plus RA registration for black-box algos | SEBI circular above |
| Closing auction | Live 3 Aug 2026. Market orders can't be modified or cancelled 15:25–15:30. | [NSE/FAOP/74467](https://nsearchives.nseindia.com/content/circulars/FAOP74467.zip) |
| ETF norms | Base price, price bands, pre-open call auction and close-out, from 7 Sep 2026 | [SEBI 28 Aug 2026](https://www.sebi.gov.in/legal/circulars/aug-2026/extension-of-timeline-for-implementation-of-provisions-of-sebi-circular-dated-june-15-2026-on-norms-for-base-price-price-bands-call-auction-in-pre-open-session-and-close-out-procedure-for-exchange-_104094.html) |
| Order-to-trade ratio | Revised 4 Feb 2026, effective 6 Apr 2026 | [NSE/SURV/72668](https://nsearchives.nseindia.com/content/circulars/SURV72668.zip) |
| Pending | SEBI consultation of 12 Sep 2026 on the closing auction, market timings and derivative settlement | [SEBI consultation](https://www.sebi.gov.in/reports-and-statistics/reports/sep-2026/consultation-paper-on-review-of-certain-aspects-of-the-closing-auction-session-market-timings-and-settlement-methodologies-for-derivative-contracts-_104464.html) |
| F&O curbs | Minimum index contract ₹15L. One weekly benchmark expiry per exchange. +2% extreme-loss margin on short options on expiry day. Upfront premium. No calendar-spread benefit on expiry day. Lot sizes (Jan 2026): NIFTY 65, BANKNIFTY 30, FINNIFTY 60, MIDCPNIFTY 120, NIFTYNXT50 25. NSE expiry Tuesday, BSE Thursday; no BANKNIFTY/FINNIFTY weeklies. | [SEBI 1 Oct 2024](https://www.sebi.gov.in/legal/circulars/oct-2024/measures-to-strengthen-equity-index-derivatives-framework-for-increased-investor-protection-and-market-stability_87208.html), [NSE lots](https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv), [NSE/FAOP/68685](https://nsearchives.nseindia.com/content/circulars/FAOP68685.pdf) |
| Forex | INR pairs only for hedging a contracted exposure (RBI Master Direction, 5 Apr 2024). Offshore forex is illegal under FEMA. | [RBI](https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12594) |
| Crypto | 30% + cess + surcharge (not capped at 15%). No set-off or carry-forward. 1% TDS. Delta Exchange India: FIU-registered, INR-settled, 0.02% maker / 0.05% taker. | [ClearTax crypto](https://cleartax.in/s/cryptocurrency-taxation-guide), [Delta fees](https://www.delta.exchange/fees) |

### A.2 Costs and taxes

**Zerodha rate card** ([charges](https://zerodha.com/charges/))

| Charge | Rate |
|---|---|
| Brokerage | Delivery ₹0. Intraday/futures min(0.03%, ₹20) per order. Options ₹20 per order. |
| STT | Delivery 0.1% on buy and sell. Intraday 0.025% on sell. Futures 0.05% on sell (from 1 Apr 2026). Options 0.15% of premium on sell (from 1 Apr 2026). **Equity ETF 0.001% on sell** ([ClearTax STT](https://cleartax.in/s/securities-transaction-tax-stt)). |
| NSE transaction charges (from 1 Mar 2026) | Cash 0.00307%, futures 0.00183%, options 0.03553% of premium |
| SEBI fee | ₹10/crore |
| GST | 18% on brokerage, exchange and SEBI charges |
| Stamp duty (buy side) | Delivery 0.015%, intraday 0.003%, futures 0.002%, options 0.003% |
| DP charge | ₹15.34 per scrip per sell day |
| Auto square-off | ₹50 + GST |

**Round trips** (same price, no slippage)

| Segment, size | Total | bps |
|---|---|---|
| Intraday equity, ₹50k | ₹53.14 | 10.6 |
| Delivery equity, ₹50k | ₹126.58 | 25.3 |
| Equity ETF delivery, ₹50k | ₹27.08 | 5.4 |
| Equity ETF delivery, ₹2L | ₹62.30 | 3.1 |
| Index options, ₹50k premium | ₹165.74 | 33.1 of premium |

**Break-even edge per round trip, including slippage:** intraday about 15–20 bps at ₹50k; swing delivery about 30–35 bps; positional ETF about 8–12 bps.

**Tax rules** ([ClearTax capital gains](https://cleartax.in/s/capital-gains-income), [Zerodha Varsity](https://zerodha.com/varsity/chapter/taxation-for-traders/), [Budget 2026](https://cleartax.in/s/budget-2026-highlights))

| Item | Rule |
|---|---|
| Equity STCG (held ≤12 months) | 20% |
| Equity LTCG | 12.5% above ₹1.25L a year. Surcharge on capital gains is capped at 15%, so the effective rate on these gains is about 20.8–23.9%. |
| Intraday | Speculative business income at slab rate. Losses offset only speculative gains, carry forward 4 years, and are never set off against salary. |
| F&O | Non-speculative business income at slab rate; losses carry forward 8 years |
| Returns | ITR-2 due 31 Jul; ITR-3 due 31 Aug (Budget 2026) |
| Tax audit | Only above ₹10 crore turnover (with cash transactions ≤5%) |
| Advance tax | 15/45/75/100% by 15 Jun/Sep/Dec/Mar, once uncovered tax is ₹10k or more |
| Income-tax Act 2025 | In force from 1 Apr 2026: introduces the "tax year" and new section numbers; rates unchanged |
| Budget 2026 | Buybacks are now taxed as capital gains |
| Share kept after tax | About 61–69% of intraday profit; about 76–79% of swing profit |

### A.3 Retail outcomes (SEBI)

Sources: [SEBI PR 50/2026](https://www.sebi.gov.in/media-and-notifications/press-releases/aug-2026/sebi-studies-indicate-key-trends-in-retail-participation-trading-behaviour-and-profitability-in-the-equity-derivatives_103838.html), [profitability study](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233506209.pdf), [behaviour study](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233601328.pdf), [intraday study Jul 2024](https://www.sebi.gov.in/sebi_data/attachdocs/jul-2024/1721818140715.pdf).

**Individual F&O traders**

| Measure | Figure |
|---|---|
| Share who lost money | 87.7% (FY26), 90.9% (FY25), 92.7% (FY22–24) |
| Net losses, FY26 | ₹91,685 cr; average loss ₹1.17L |
| Loss rate by product | Options 87.7%, futures 66.0%; options caused 92% of losses |
| Median ROC, options buyers (FY26) | −114% |
| Consistency, FY22–26 | 0.5% profitable every year; 65.6% lost every year |
| Frequent traders | Those active more than 100 days a year were 42% of traders and caused 87% of losses |

**Who wins:** prop desks (about ₹44k cr gross profit) and FPIs (about ₹14k cr), 99% of it from algo entities.

**Intraday cash, FY23:** 71% lost. Among those making 500+ trades a year, 80% lost. Costs deepened losers' losses by 57%.

### A.4 Proof horizon

Minimum Track Record Length at 95% confidence against a Sharpe of 0 ([Bailey & López de Prado](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643)):

| True annual Sharpe | Days of live data needed |
|---|---|
| 0.5 | ~2,730 (10.8 years) |
| 1.0 | ~684 (2.7 years) |
| 1.5 | ~305 (14–15 months) |
| 2.0 | ~173 (0.7 years) |

Measured against a benchmark (excess return), the requirement is higher.

### A.5 Strategy evidence

These are unverified secondary-source figures and researcher backtests. Treat them as directional.

- **Index trend filter** (100-DMA on the Nifty 50 price index, 2007–26): 9.7% CAGR and −16.2% max drawdown, vs buy-and-hold 9.1% and −59.9%.
  - It has lagged buy-and-hold by about 1 pp/yr since 2015.
  - The comparison mixes the price index with the TRI.
  - 8–10 switches a year turn deferred LTCG into STCG.
- **Momentum:**
  - [IIMA factor library](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/): winners-minus-losers 10.65%/yr gross, worst drawdown −62%.
  - [Nifty200 Momentum 30](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf): TRI 19.19% vs 15.08% (Apr 2005–Feb 2026). Max drawdown 67.7%. Lagged its parent by 14.1 pp in 2025.
  - Semi-annual rebalancing beat quarterly.
- **Low volatility:** Nifty100 Low Vol 30 returned 10.47% over 5 years (SD 11.94%, beta 0.79), vs 8.32% for the Nifty 50.
- **Nifty 50 TRI** ([factsheet](https://www.niftyindices.com/Factsheet/ind_nifty50.pdf)): 8.32% over 5 years, 12.38% since 1995. Max drawdown about 60% (2008).
- **Weekly reversal:** +5.5 pp/yr gross, but net it lagged equal-weight by about 10 pp at a 0.30% round-trip cost.
- **Opening-range breakout:** failed OOS after costs on US futures ([arXiv 2605.04004](http://arxiv.org/abs/2605.04004v3)).
- **Drawdown reality:** no fully invested long-only equity strategy stayed within 15% through 2008–09 or 2020.

### A.6 Learning-loop evidence

**What works**
- Gradient-boosted trees on engineered features have the strongest support ([Gu, Kelly & Xiu, RFS 2020](https://www.nber.org/papers/w25398)).
- News predictability is real but decaying, concentrated in small caps and negative news ([Lopez-Lira & Tang](https://arxiv.org/abs/2304.07619)).
- Masking entity names improves the signal ([Glasserman & Lin](https://arxiv.org/abs/2309.17322)).
- Batch retraining usually suffices ([River](https://github.com/online-ml/river)).

**What fails**
- LLM trading agents mostly fail to beat buy-and-hold ([StockBench](https://arxiv.org/abs/2510.02209), [LiveTradeBench](https://arxiv.org/abs/2511.03628), [FINSABER](https://arxiv.org/abs/2505.07078)).
- Backtest profits vanish after the model's knowledge window ([Profit Mirage](https://arxiv.org/abs/2510.07920)).
- In a staged crypto test, 23 of 24 ML methods were profitable in backtest, 2 of 8 on paper, and 1 of 4 live, all with negative alpha. Live slippage was about 6× paper ([2609.34510](https://arxiv.org/html/2609.34510v1)).
- Deep learning on raw prices has poor evidence ([M6](https://arxiv.org/abs/2310.13357)).
- Indian news sentiment has classification-accuracy papers only, with no net-of-cost results ([2512.20082](https://arxiv.org/abs/2512.20082)).

**Validation cautions**
- A deliberately leaky backtest passed both DSR and PBO ([2608.27734](https://arxiv.org/abs/2608.27734)).
- With 5 years of daily data, more than about 45 independent trials make an in-sample Sharpe of 1 expected by chance ([Bailey et al.](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)).
- skfolio's CombinatorialPurgedCV defaults purge and embargo to 0 ([skfolio](https://skfolio.org/generated/skfolio.model_selection.CombinatorialPurgedCV.html)).
- vectorbt 1.1.1 changed its DSR calculation ([release](https://github.com/polakowo/vectorbt/releases/tag/v1.1.1)).

### A.7 Brokers

| | Zerodha Kite Connect | Dhan | Upstox | Angel One SmartAPI |
|---|---|---|---|---|
| API cost | ₹500/month with data; free Personal plan covers orders + GTT only ([pricing](https://zerodha.com/products/api/)) | Trading free; data price unverified | Free | Free |
| Delivery brokerage | 0 | 0 | ₹20/order | – |
| Order limits | 10/s, 400/min, 5,000/day | 10/s, 250/min, 1,000/hr, 7,000/day | 10/s, 500/min | – |
| History | Minute to day; no expired options | 5 years intraday; 5 years expired options ([docs](https://dhanhq.co/docs/v2/expired-options-data/)) | 1-min from 2022; expired contracts need a paid plan | – |
| Daily login | Browser redirect; no official TOTP ([docs](https://kite.trade/docs/connect/v3/user/)) | Official TOTP token API, 24-hour token ([auth](https://dhanhq.co/docs/v2/authentication/)) | Semi-automated | Official SDK login with TOTP ([smartapi-python](https://github.com/angel-one/smartapi-python)) |
| SDK | kiteconnect 5.2.2 (Sep 2026) | dhanhq 2.2.0 | 2.30.0, with an order sandbox | Infrequent releases (unverified) |

### A.8 Data sources and frameworks

**Data sources**
- **NSE bhavcopies:** free, back to 1995; legacy format until 5 Jul 2024, UDiFF from 8 Jul 2024; delisted names included.
- **NSE corporate-actions API:** free, verified back to 2010; ratios are free text.
- **Announcements feed:** NSE announcements [RSS](https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml).
- **News RSS:** [ET Markets](https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms), [Business Standard](https://www.business-standard.com/rss/markets-106.rss), [Mint](https://www.livemint.com/rss/markets).
- **jugaad-data:** silently returns the previous day's file on holidays.
- **yfinance:** mis-adjusted the RAYMOND demerger.
- **Paid vendors** (Accelpix, TrueData, GDFL): not needed at this stage.

**Frameworks**
- **NautilusTrader** (LGPL): v2.0.0 release candidates with breaking changes (Aug–Sep 2026); no Indian adapter.
- **OpenAlgo** (AGPL): 34 brokers; recent order-hang and Dhan symbol-mapping bugs.
- **vectorbt:** Apache 2.0 + Commons Clause; v1.1.1.
- **Lean:** needs a paid tier for live trading with Zerodha.
- **backtrader:** dormant since Aug 2024.
- **ArcticDB:** production use needs a paid licence.

### A.9 Infra and operations

- **Lightsail:** Mumbai 2 GB is $12 with a static IP included ([pricing](https://aws.amazon.com/lightsail/pricing/)). No Lightsail in Hyderabad.
- **Other hosts:** DigitalOcean Bangalore is an alternative. Hetzner has no India region.
- **DuckDB:** one writer or many readers ([docs](https://duckdb.org/docs/current/connect/concurrency.html)).
- **Telegram:** callback data max 64 bytes; webhooks and long polling are mutually exclusive ([Bot API](https://core.telegram.org/bots/api)).
- **Knight Capital** (1 Aug 2012): lost more than $460M in about 45 minutes. One of 8 servers missed a deploy, an old flag was reused, 97 warning emails went unread, and the rollback made things worse ([SEC order](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf)).

### A.10 Glossary

**Market and data**

| Term | Meaning |
|---|---|
| AMFI | Association of Mutual Funds in India; publishes daily fund NAVs |
| AMO | After-market order (queued outside market hours) |
| ASM / GSM | Exchange surveillance lists (additional / graded surveillance measures) |
| Bhavcopy / UDiFF | NSE daily end-of-day price files; UDiFF is the newer format |
| iNAV | Indicative intraday NAV of an ETF |
| ISIN | Permanent security identifier; symbols can change (e.g., ZOMATO → ETERNAL) |
| LTP | Last traded price |
| NAV | Net asset value. Tradebot NAV is unitised (K0). |
| Epoch | A live-trading period with its own drawdown peak. It ends only on a K1 epoch breach; the next starts via CLI `new-epoch` (K0). |
| SMA | Simple moving average |
| TRI | Total return index (includes dividends) |
| Muhurat | Special evening trading session on Diwali |

**Orders, settlement and accounts**

| Term | Meaning |
|---|---|
| CNC / MIS / MTF / NRML | Delivery / intraday / margin-funded / F&O carry-forward products |
| DDPI | Demat Debit and Pledge Instruction: lets the broker debit holdings for sells without a daily TPIN |
| e-DIS / TPIN | CDSL per-day authorisation for selling holdings |
| GTT | Good-till-triggered broker-side order |
| IDCW | Income distribution cum capital withdrawal (a fund or ETF payout) |
| T+1 | Settlement on the next trading day |
| T1 | Zerodha's label for units bought but not yet settled into the demat |
| BTST | Buy today, sell tomorrow (before settlement) |

**Tax**

| Term | Meaning |
|---|---|
| AIS / 26AS | Income-tax department statements of reported income and TDS |
| CA | Chartered accountant |
| Cess | 4% health and education cess on tax plus surcharge |
| FIFO | First in, first out (lot matching) |
| ITR | Income tax return |
| Slab rate | The owner's marginal income-tax rate |
| STCG / LTCG | Short- / long-term capital gains |
| STT | Securities Transaction Tax |
| TDS | Tax deducted at source |
| VDA | Virtual digital asset (crypto) |

**Research and statistics**

| Term | Meaning |
|---|---|
| bps | Basis points; 1 bps = 0.01% |
| OOS | Out-of-sample |
| Walk-forward | Repeated fit-on-past, test-on-next-window evaluation |
| DSR | Deflated Sharpe Ratio: Sharpe adjusted for the number of trials and for non-normal returns |
| PBO | Probability of backtest overfitting |
| CPCV | Combinatorial purged cross-validation |
| MinTRL | Minimum track record length |
| Champion / challenger | The live strategy or model vs a candidate replacement |
| RM / BH / PF | Benchmarks defined in §4.1 |
