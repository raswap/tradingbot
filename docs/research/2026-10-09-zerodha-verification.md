# Zerodha verification from documentation and community sources (2026-10-09)

Purpose: settle as much of PRD §16.2 and the four owner questions (Appendix B, decision 5) as public sources allow, before anything is asked of Zerodha directly. Sources were fetched on 2026-10-09; quotes are verbatim.

## The four questions

### 1. Does DDPI let the platform sell holdings and run GTT sells without a daily TPIN? Which API field shows sellable quantity?

- Support article "What is the validity of the CDSL authorisation?": "You can activate DDPI for your Zerodha account to skip placing CDSL TPIN authorisation requests every time you place long-standing orders like GTT. Your CDSL TPIN authorisations are valid for a single day ... Starting from 7:00 AM ... until 5:00 PM."
- Support article "What is the CDSL TPIN and how to use it to sell the stock holdings?": "If you have enabled DDPI for your Zerodha account, you can sell shares without entering CDSL TPIN and OTP, and the Authorise option will not be visible to you."
- Support article "What is DDPI": "DDPI is a document that allows your broker to debit securities from your demat account and deliver them to the exchange. You do not have to enter the CDSL TPIN and OTP to sell shares once you submit the DDPI." Charge ₹100 + GST; activated within 24 working hours; DDPI replaced POA on 19 Nov 2022.
- TradingQnA "CDSL TPIN on GTT Order" (2020): a GTT sell triggered and was rejected because the day's TPIN authorisation was missing. This is the failure DDPI removes.
- Kite Connect user API: the profile's `meta.demat_consent` is documented as "empty, consent or physical". `consent` is the DDPI state, `physical` the old POA. This is the C9 mechanism the PRD left unverified.
- Holdings API fields: `authorised_quantity` "Quantity authorised at the depository for sale", `authorised_date` "Date on which user can sell required holding stock", `t1_quantity` "Quantity on T+1 day after order execution", `realised_quantity` "Quantity delivered to Demat", `used_quantity` "Quantity sold from the net holding quantity".

**Verdict:** DDPI covers sells and GTT without a daily TPIN, and the authorisation is at the demat level, not per channel, so API sells are covered too. The one thing still worth a written confirmation from Zerodha: that `demat_consent = consent` is the reliable DDPI indicator and whether `authorised_quantity` is populated under DDPI. §16.2 #3 moves from unverified to verified-by-documentation; the A6 smoke test confirms it on the live account.

### 2. Does Kite accept TTL validity on CNC limit orders, and does a modification keep or reset the TTL?

- Orders documentation: `validity` "Order validity (DAY, IOC and TTL)", `validity_ttl` "Order life span in minutes for TTL validity orders". The documented order-book sample includes a CNC order with `"validity": "TTL", "validity_ttl": 2`.
- Modify-order parameters list `validity`; the official Python SDK (kiteconnect 5.2.2) passes `validity` and `validity_ttl` on modify as well.
- `tag`: "An optional tag to apply to an order to identify it (alphanumeric, max 20 chars)".

**Verdict:** TTL on CNC is documented. Whether a modification without `validity_ttl` keeps or resets the clock is not documented; the gateway re-sends `validity_ttl` on every modification (R8a already requires this), and A6 step 1 confirms it. §16.2 #18 moves to verified-by-documentation with the modification behaviour left to A6.

### 3. Can a single-leg GTT sell be placed on T1 holdings, and does it execute if triggered before settlement?

- TradingQnA "GTT for T1 Holdings" (2021), question whether GTT OCO sells can be placed for T1 and T2 holdings; answer from Zerodha's siva-reddy: "You can."
- Kite Connect forum (28 Sep 2026, Zerodha staff nagavenij) on holdings after a same-day CNC sale with T1 quantity present: settled quantity is consumed first, `t1_quantity` stays, `used_quantity` rises, and `positions()["net"]` shows the CNC sale as a negative quantity. Worked example: quantity 60, t1 40, sell 50 → quantity 10, t1 40, used 50.

**Verdict:** placement on T1 units is confirmed by Zerodha staff in the community; execution before settlement is consistent with Zerodha allowing sales of T1 holdings, but no source states it for a triggered GTT. §16.2 #17 stays on the A6 list. The forum examples also settle §16.2 #16: broker quantity = `quantity` + `t1_quantity` where `quantity` already excludes today's sales, and today's CNC sale appears as a negative CNC position.

### 4. Must GTT calls come from the static IP, and does a GTT carry a client tag?

- GTT documentation: a GTT order carries exchange, tradingsymbol, transaction_type, quantity, order_type (LIMIT), product, price. No tag. Triggers are identified by `trigger_id`; `expires_at` is one year after creation; statuses are active, triggered, disabled, expired, cancelled, rejected, deleted.
- Static-IP article: "effective 1 April 2026, you must have a static IP for API-based order placement ... The WebSocket market data stream and other APIs, such as orderbook and positions, can continue to be accessed from any IP address." One IP change per calendar week; up to two IPs; family sharing by declaration. GTT is not mentioned either way. A forum user asked on 28 Sep 2026 whether GTT create, modify and delete calls are IP-checked; no public answer.

**Verdict:** no client tag on GTTs (§16.2 #19 verified); identify by `trigger_id`. Whether GTT calls are IP-checked remains open, but the gateway runs on the whitelisted IP, so it only matters for the manual runbook. Ask Zerodha alongside the automation question below.

## Other facts settled on the way

- Access token: "it'll expire at 6 AM on the next day (regulatory requirement)" unless invalidated via the API or a master logout (§16.2 #2, first half, verified). Forum, 11 Sep 2026, Zerodha staff: generating a new access token for the same API key invalidates the previous one; logging into Kite web or app does not. The E6 design must never run the login flow from a second process.
- GTT product types: CNC, MTF and NRML only (Zerodha, TradingQnA, May 2026). A trailing-stop-loss GTT exists on the Kite beta since May 2026; API availability unknown.
- **GTT-triggered orders can fail at trigger time.** The GTT documentation's own sample shows a triggered order with `order_result.status = failed` and `rejection_reason`: "Your order price is lower than the current lower circuit limit of 70.65. Place an order within the daily range." A limit set 3% below the trigger can fall outside the day's circuit range on the day it triggers. E9 must keep the limit inside the band of the current day (re-arm in the evening pipeline) and must treat a `triggered` GTT with a failed `order_result` as an unfilled exit to re-issue under A5.

## Two findings that need Zerodha's written answer before the first live order

1. **Automation.** Kite Connect API terms, clause 2(e): "The APIs are not meant for placing fully automated trades (without manual intervention). If you wish to use the APIs for full automation, you should seek necessary approvals from the exchange. Zerodha may provide the necessary assistance in obtaining approvals." The support article "What is algo trading" says: "you must manually place orders, as full automation is not permitted for retail traders." Against that, the static-IP article describes "API-based order placement as per NSE/SEBI algorithmic trading regulations" as something retail clients do from 1 April 2026, which is the SEBI framework the PRD is built on. Two forum users asked for clarification in September 2026 (threads 16278 and 16304); Zerodha's forum staff replied only "You may write above concern to kiteconnect@zerodha.com." The APPROVE stage keeps a human tap on every entry, but the PRD's automatic exits (A5), the governor flattens and the AUTO stage (A3) are order placement without manual intervention. Nothing goes live until Zerodha confirms in writing which of these is permitted on a personal app below 10 orders per second from a registered static IP, and whether the generic algo ID covers it.
2. **Storing API data.** Terms clause 4(b): "Unless expressly permitted by Zerodha or by the applicable laws, you will not ... Scrape, build databases, or otherwise create permanent copies of such content, or keep cached copies with the intent of redistributing." The PRD stores Kite day candles (D1 S1 history, D3 cross-check) and possibly minute candles (D4) in Parquet. A forum user asked the same question on 28 Sep 2026; no public answer. Until Zerodha permits it in writing, the platform should treat NSE bhavcopies and niftyindices.com as its only stored history, keep Kite candles as a transient cross-check that is not persisted, and defer the D4 minute archive.

## Sources

- https://kite.trade/docs/connect/v3/orders/ , https://kite.trade/docs/connect/v3/gtt/ , https://kite.trade/docs/connect/v3/portfolio/ , https://kite.trade/docs/connect/v3/user/ , https://kite.trade/terms/
- https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip
- https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/what-is-algo-trading
- https://support.zerodha.com/category/your-zerodha-account/your-profile/ddpi/articles/activate-ddpi
- https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/tpin-preauthorisation
- https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/validity-of-cdsl-tpin-authorisation
- https://kite.trade/forum/discussion/16278 , /16304 , /16275 , /16259 , /16244
- https://tradingqna.com/t/gtt-for-t1-holdings/119408 , https://tradingqna.com/t/cdsl-tpin-on-gtt-order/80973 , https://tradingqna.com/t/introducing-trailing-stop-loss-in-gtt-orders-on-kite-beta/194095
- Official SDK source: kiteconnect 5.2.2 from PyPI (`VALIDITY_TTL`, `validity_ttl` on place and modify, GTT payload fields).
