# Evaluation plan

Written 2026-09-23, before any v2 outcome was measured. This rule does not change after results come in. If it ever needs to change, the new version gets a new date and the old results are reported under the old rule.

## The question

Do clean positioning anomalies come before larger moves in the underlying stock than comparable days without one?

Direction is deliberately not part of the primary question, because end-of-day data cannot say which side opened a position.

## What is evaluated

- **Unit:** one flagged ticker-day. Several flagged contracts on the same name on the same day share one outcome and count once.
- **Evaluated set:** clean flags only. A flag is clean when it has no data-quality flag (`STALE_LAST`, `LAST_OUTSIDE_QUOTE`, `WIDE_MARKET`, `NO_QUOTE`), more than 7 days to expiry, and none of `NEAR_EXPIRY`, `DEEP_ITM`, `PROBABLE_MULTI_LEG`, `ADJUSTED_CONTRACT`. Other flags stay in the ledger for reading but are not scored.
- **Non-overlapping:** for each name, a flag counts only if its outcome window starts after the previous counted flag's window has ended.

## Outcome

- **Primary:** the absolute move in the underlying from the flag-day close to the close 20 trading days later.
- **Secondary:** the same at 5 and 60 trading days.

## Control

For each flag, the controls are days on the same name with no clean flag, in the same earnings bucket and the same volatility regime:

- **Earnings bucket:** within 10 calendar days of a dated earnings release in `data/events.csv`, or not. Names without earnings dates on file are not evaluated.
- **Volatility regime:** tercile (low, mid, high) of the name's own trailing 20-day realised volatility.

Days to expiry and moneyness are recorded on every ledger row, so results can also be broken down by those buckets once there is enough data.

## When a result counts

- Earnings and non-earnings flags are reported separately and never pooled.
- No verdict in a bucket until it has at least 100 resolved, non-overlapping clean flagged ticker-days.
- Above that, the flag "paid" at a horizon if the median absolute move after flags is larger than the median absolute move on matched control days. Anything else is reported as no difference.

## Where things stand on 2026-09-23

44 daily snapshots (22 July to 22 September 2026) across 16 names. That is enough to test that the pipeline works, and not enough to test the idea. No result has been claimed.
