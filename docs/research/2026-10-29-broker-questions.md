# Questions sent to the brokers (drafted 29 Oct 2026)

Two emails, prepared as Gmail drafts for the owner to send. The Zerodha mail goes to kiteconnect@zerodha.com (the address Zerodha's forum staff gave for automation questions). The Dhan mail goes to apihelp@dhan.co (the address on the DhanHQ site). Replies are to be filed under `docs/research/` and the PRD's §16.2 and Appendix B updated from them. Background and sources: `2026-10-09-zerodha-verification.md`.

## To Zerodha (Kite Connect)

Subject: Kite Connect personal app: automation scope, data storage, DDPI, TTL and GTT questions (Client ID [XXXXXX])

Hello Kite Connect team,

I am an individual Zerodha client (Client ID [XXXXXX]) building a personal trading application on Kite Connect for my own account and my own capital only. Before I place the first live order through it, I need written confirmation on six points.

Facts about the application:
- One account, one API key, one registered static IP, no third-party users.
- Instruments: NSE ETFs only (for example NIFTYBEES and a liquid ETF), product CNC.
- Frequency: about one entry or exit per week, and never more than 5 orders per second, well under the 10 orders/second registration threshold, so orders would carry the generic algo ID.
- Each new position is confirmed by me manually (a tap on a Telegram message) before the order is sent. Exits, however, are rule-based: stop-loss sells, a drawdown-based flatten and a broker-side GTT sell can be placed by the application without my intervention at that moment.

Questions:

1. Automation. The Kite Connect API terms, clause 2(e), say the APIs "are not meant for placing fully automated trades (without manual intervention)" and that full automation needs exchange approval. For a personal application as described above (own account, below 10 orders per second, static IP registered), are rule-based exit orders sent without a manual confirmation permitted under the SEBI retail algo framework of 4 February 2025 and the generic algo ID, or do they require registration of the algo through Zerodha with the exchange? If registration is required, what is the procedure and the timeline?

2. Storing historical data. Clause 4(b) says the user will not "scrape, build databases, or otherwise create permanent copies of such content". May I keep a local copy of day and minute candles fetched through the historical data API, solely for my own backtesting and for cross-checking my own trades, never redistributed or shared? If not, is there a subscription or written permission that allows it?

3. DDPI. I have activated DDPI. Is meta.demat_consent = "consent" in the /user/profile response the reliable indicator that DDPI is active, so that CNC sell orders and GTT sell orders placed through the API need no CDSL TPIN authorisation? In the /portfolio/holdings response, which field gives the quantity that can be sold today without TPIN, and is authorised_quantity populated when DDPI is active?

4. TTL validity. The orders documentation lists validity TTL with validity_ttl in minutes, and the order-book sample shows a CNC order with TTL.
   (a) Is TTL validity accepted on CNC limit orders for NSE ETFs?
   (b) When such an order is modified (price change) with validity=TTL and validity_ttl sent again, does the TTL clock restart from the modification time or continue from the original placement time?
   (c) If a modify request omits validity and validity_ttl, does the order keep its TTL or revert to DAY?

5. GTT on T1 holdings. Can a single-leg GTT sell be created against holdings bought on the previous day (T1 quantity) under DDPI? If the GTT triggers before the shares are credited to the demat account, is the resulting sell order placed and executed, or rejected? Separately, the GTT documentation shows a triggered order rejected because the limit price was outside the day's circuit range. Is there any way to have the GTT re-arm after such a rejection, or must the client create a new GTT?

6. Static IP and identification of GTT orders.
   (a) Do GTT create, modify and delete calls have to come from the registered static IP in the same way as order placement, modification and cancellation?
   (b) A GTT has no tag field. When a GTT triggers, does the resulting order carry any reference to the trigger_id (or a tag) in the order book or in the postback, so that the application can match the order to the GTT?

Thank you for your help. A written reply to this email would be ideal, as I intend to keep it on file as the basis for the application's design.

Kind regards,
[Name]
Client ID [XXXXXX]

## To Dhan (DhanHQ)

Subject: DhanHQ API personal trading app: automation scope, data storage, Forever Orders and holdings questions (Client ID [XXXXXX])

Hello DhanHQ team,

I am an individual Dhan client (Client ID [XXXXXX]) building a personal trading application on the DhanHQ v2 API for my own account and my own capital only. Before I place the first live order through it, I need written confirmation on five points.

Facts about the application:
- One account, one API key, one registered static IP, no third-party users.
- Instruments: NSE ETFs only (for example NIFTYBEES and a liquid ETF), product CNC.
- Frequency: about one entry or exit per week, and never more than 5 orders per second, well under the 10 orders/second registration threshold, so orders would carry the generic algo ID.
- Each new position is confirmed by me manually before the order is sent. Exits, however, are rule-based: stop-loss sells, a drawdown-based flatten and a broker-side Forever Order sell can be placed by the application without my intervention at that moment.

Questions:

1. Automation. Does Dhan permit an individual client to place rule-based orders without a manual confirmation from a personal application as described above, under the SEBI retail algo framework of 4 February 2025 and the generic algo ID? Is any registration of the application or the strategy required, and if so, what is the procedure and the timeline?

2. Storing historical data. May I keep a local copy of day and minute candles fetched through the Historical Data API, solely for my own backtesting and for cross-checking my own trades, never redistributed or shared? Does the Data APIs plan listed at Rs 499 cover this, and is that price per month?

3. Forever Orders on T1 holdings. With DDPI active, can a SINGLE Forever Order (sell, CNC) be created on shares bought on the previous day? If it triggers before the shares are credited to the demat account, is the resulting sell order placed and executed, or rejected? If a triggered Forever Order's limit price falls outside the day's circuit range, what happens to the order and to the Forever Order?

4. Holdings. When DDPI is active (givenPowerOfAttorney = true in the token response), which field in the holdings response gives the quantity that can be sold today without a CDSL TPIN authorisation?

5. Order validity. The order API accepts validity DAY or IOC. Is there any broker-side time-limited validity for CNC limit orders (for example a validity in minutes), or must the application cancel a resting order itself?

Thank you for your help. A written reply to this email would be ideal, as I intend to keep it on file as the basis for the application's design.

Kind regards,
[Name]
Client ID [XXXXXX]

## What each answer changes in the PRD

| Question | PRD item | If the answer is no |
|---|---|---|
| Zerodha 1 / Dhan 1 | A3, A5, K1 flatten, E9; OD-3 (primary broker) | Automatic exits need a manual tap at Zerodha: either every exit becomes an APPROVE-style confirmation, or Dhan becomes the primary broker before the first live order. |
| Zerodha 2 / Dhan 2 | D1, D3, D4 | Stored history stays NSE bhavcopies and niftyindices.com only; broker candles are a transient cross-check; the D4 minute archive stays deferred. |
| Zerodha 3 / Dhan 4 | C9, §16.2 #3 | The DDPI check falls back to the A6 smoke test (a one-share sell) before live trading. |
| Zerodha 4 / Dhan 5 | R8a, §16.2 #18 | The R8a fallback applies: no risk-increasing order rests; cancel after each 60 s reprice attempt (at Dhan, always). |
| Zerodha 5 / Dhan 3 | E9, §16.2 #16 | The backstop is armed only on settled quantity; the first day after an entry is covered by the governor alone, and a triggered-but-rejected backstop is re-issued under A5. |
| Zerodha 6 | E9, §16.2 #19, manual runbook | GTT calls go only through the gateway on the whitelisted IP; GTT-born orders are matched by trigger_id and the absence of a tag. |
