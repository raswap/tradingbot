# PRD hardening log

Target: `docs/PRD.md`, Tradebot PRD. Baseline v1.9 (commit `712d156`) → v1.10.
Method: repeated review passes, each with one lens, each applied and committed separately so every change is a reviewable diff. Open owner decisions were never decided; where a pass needed a default it added one, marked it, and listed it in Appendix B of the PRD.

| Pass | Lens | Commit | Edits |
|---|---|---|---|
| 1 | Internal consistency | `76e8127` | 10 |
| 2 | Specification gaps | `769d16b` | 25 |
| 3 | Failure-scenario walkthrough | `a432dd0` | 19 |
| 4 | Testability of MUSTs and gates | `40d4ef8` | 13 |
| 5 | Plan realism | `1b32ae2` | 8 |
| 6 | Fact verification | none | 0 (blocked, see below) |
| 7 | Coherence re-read of the whole diff | this commit | 17 + Appendix B |

## Pass 1: internal consistency

Checked every cross-reference (§ numbers, requirement IDs, §16.2 item numbers, OD numbers), the slice columns in §8 against §14, the numeric thresholds against the config example, and the state machine against the prose that describes it.

Found and fixed:
- Principle 8 said risk-reducing exits never wait for a human, but K5 pauses strategy exits under an E4 or `/halt` HALTED. Principle 8 and A5 now say only flattens never wait.
- B5 enforced instrument disjointness at config load, but the stage is not in the YAML, and an L4 challenger must trade the champion's ISIN on paper. Moved the check to promotion and scoped it to live bots.
- K1 never said what "reached" means, and the reference-peak halt at −12% is dominated by the epoch breach at −12% with default thresholds; that, and the K7(4) consequence (any governor HALTED demotes every bot to PAPER), are now stated.
- The backtest governor's auto-resumption rule is a modelling assumption about the owner's behaviour, not platform behaviour; it is now labelled as such, and a backtest is defined as one epoch.
- K7 did not say whether the paper clock restarts after a demotion. It does.
- E9's known-limits sentence on T1 units contradicted its own covered-quantity definition.
- The Approve → Auto gate cited a `/halt` drill that A6 never defined; added it, and noted that the `/flatten` drill sets HALTED.

Checked and found consistent: slice assignments (§8 vs §14), governor constraint against config values, rate-limit numbers (E1, C1), approval-expiry and order-window times across R8, A2, §13.3 and §13.5, the DROPPED_* states in §13.4 against K4(k).

## Pass 2: specification gaps

Read each requirement asking "what would an implementer have to guess?".

Added: cash-movement accounting and initial unit value (K0); reference-peak and bot-drawdown definitions (K0); UDiFF backfill and missed-session backfill (D1); T+1 as a calendar session and the special-session rule (D2); a two-source check on the index close, which is the only signal input and had none (D3, D10); order-tag format, terminal replies and GTT identification (E5, B1); restart semantics (§13.4); trial-count definition (R10); halving hysteresis (K1, OD-5); Telegram identity config and example external-holdings, tax-profile and cost files (§13.5); rejected-approval behaviour (A2(d)); time handling (§9, M3); broker-cash cap on buys (K4(b)); per-ISIN backstop trigger from S2 (E9); §16.2 items 19–21.

## Pass 3: failure-scenario walkthrough

Walked concrete sequences through the text: GTT reduction followed by a platform sell that is cancelled and re-placed; host death between GTT reduction and fill; a cancel racing the broker-side TTL; session revoked mid-window; late bhavcopy; broker cash below platform capital; GTT fill while the platform is alive; a holiday between T and T+1; a corporate action on a held ISIN; a failed reconciliation sync; stale quotes at a NAV mark; `new-epoch` with open positions; the annual walk-forward re-selection changing live parameters.

The one substantive correction: E9's covered quantity used "settled by the next session's open", but T+1 settlement happens during the next session, so units bought on T were never covered on the evening of T, contradicting A6 step 2 and §16.2 #17. Now "on or before the next session".

Added: atomic cancel-and-re-place for the GTT; re-arm on settlement and before corporate actions; a `backstop_fired` HALTED cause; a `storage` fail-closed cause (E1); session-lost handling (E6); sync-failure handling (E4); stale-mark rule (K1); preconditions for `new-epoch` and withdrawals (K0); the re-selection rule (§11.1); a dead-host runbook (§13.6); new invariants and failure injections (§13.7); §16.2 #22.

## Pass 4: testability

Listed every MUST and every gate criterion and asked how a test or a gate record would evaluate it.

Fixed: K1 "not disableable" is now a checkable statement; T3, §10.1 and K7(1) share one Sharpe computation and one action rule (below the 5th percentile demotes, anything else alerts); each §10.2 criterion names its window, comparison and evidence; A1 gate records are one row per criterion with an evidence reference; P4 has a counting rule; M1(f) lost its "about"; strategy purity is a unit test.

## Pass 5: plan realism

S1 in v1.9 carried 54 requirement IDs on a 60–75 hour budget. That figure was the research brief's "fastest path" for a minimal bot, not for the risk, state-machine, backstop and tax scope the PRD assigns to S1. Split S1 into S1a (paper-ready, 110–160 h) and S1b (live-ready, 60–85 h, built during the two-month paper period so the calendar cost is small). First approved live order moves from Feb–Mar 2027 to Mar–Apr 2027; S2, S3, S5 and S6 follow. OD-15 records the decision and ranks what could be cut from S1a to hold the earlier date. The hour ranges are engineering estimates; the owner's real weekly hours (OD-1) move every date.

## Pass 6: fact verification (blocked)

Tried to verify the §16.2 items that primary sources could settle (Kite order validity and tag limits, GTT fields, token expiry, static-IP rules, DDPI). The session's egress proxy denies kite.trade, support.zerodha.com and nseindia.com for both curl and the web-fetch tool, so nothing was verified and nothing in §16.2 changed status. The four items that matter most before code is written: #3 (DDPI covering API sells and GTT on holdings, which can invalidate the unattended-exit design), #18 (TTL validity on CNC limit orders), #17 (GTT on T1 units) and #19 (GTT tag support). All four can be asked of Zerodha support now.

## Pass 7: coherence re-read

Re-read the complete v1.9 → v1.10 diff in context. Found and fixed: two leftovers of the old covered-quantity wording (E9 known limits, a §13.7 invariant); the GTT-coverage invariant needed the cancel-and-re-place exception; `backstop_fired` was worded as if it applied only when the platform was alive; "HALTED by E4 or `/halt`" appeared in four places, now one defined term (pausing cause) used everywhere; the `storage` cause needed to say what happens to cancels; D2's special-session rule needed "backtests apply the same rule"; the §13.4 restart rule needed "with K4 re-run"; `cash-move` and `new-epoch` were missing from the CLI component list; §0 needed the S1/S1a note; OD-12 gained the cash-leg handicap note; the R8a TTL row lacked its closing table cells (a v1.9 defect); header bumped to v1.10; Appendix B added.

A further pass on the same lenses found nothing material, so the loop stops here.

## Deliberately not changed

- OD-12 (0% cash leg). Flagged as a handicap against the RM benchmark, not changed: it is an owner decision with tax consequences.
- The −6/−10/−12 thresholds, the 15% hard limit, the 5 orders/s cap, the 2-month paper minimum and the 12-month proof clock. All are owner choices with stated rationale.
- The redundancy between the reference-peak halt and the epoch breach at −12%. Harmless with defaults, useful if `halt` is ever set less negative; documented instead of removed.
- Appendix A. Evidence figures were not re-verified (network), so none were altered.
- The research brief under `docs/research/` is unchanged and kept only for traceability.

## Next lenses, if the loop continues

1. A formal state-transition table for K5, K7, A5 and K1 as an appendix, generated from the prose and then treated as the source of truth for the §13.7 property tests.
2. A worked numeric example of one R7 after-tax evaluation against RM over one walk-forward window, to pin down the liquidation and set-off order.
3. Tie-breaking in the §11.1 selection rule when several grid points have equal after-tax return.
4. R8a pricing when the order book is one-sided (no best ask or bid) or the quote is inside the iNAV band but outside the exchange band.
5. Telegram message formats (approval card, daily summary, alerts) as fixtures, so M1 and M2 are testable.
6. Primary-source verification of §16.2 from a network that can reach Zerodha and NSE.
