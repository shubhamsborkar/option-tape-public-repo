# Methodology: an options tape for long-term investors

Designed 2026-07-23 around what free end-of-day data can honestly support. Revised to v2 on 2026-09-23 (see "What changed in v2" at the end).

## What the output is

The tool surfaces **persistent series-level positioning anomalies**: specific option contracts where activity or open interest looks unusual against that contract's own history, on names you own or follow. That is a research prompt, not evidence that "the options market disagrees with you". Free end-of-day data cannot tell you who traded, which side they took, or why.

## What end-of-day data can and cannot say

- **Volume is gross activity. Open interest is a net count.** Volume counts every contract that changed hands during the day. Open interest counts the contracts still open after the day settles.
- **Unchanged open interest does not prove day trading.** If one participant closes 5,000 contracts while another opens 5,000, volume is 10,000 and open interest does not move, even though a new position now exists.
- **Rising open interest confirms more contracts are outstanding, and nothing more.** It does not say who initiated the position or whether the informed side is long or short.
- **Put volume is not automatically bearish, and call volume is not automatically bullish.** Sold puts, covered calls, vertical spreads, calendars, collars, rolls and conversions can all leave very similar end-of-day footprints.
- Classifying direction properly needs trade-level timestamps, execution prices against the national best bid and offer at the time of the trade, condition codes and multi-leg reconstruction. Even then it is inference. This tool has none of those, so it never assigns direction.

## Signals (deterministic layer, scripts/scan.py)

1. **Unusual volume** (contract level, one day): volume >= 2.5x max(open interest, 1), volume >= 250 and estimated premium >= $200,000. Thin chains (total open interest under 50,000): volume >= 50 and premium >= $50,000. This marks activity that is large against the contracts already open. It does not mean positions were opened.
2. **Open interest builds** (across snapshots): open interest on one contract rising over at least two consecutive snapshots, growing by >= 1,000 contracts (>= 100 on thin chains). Logged to the flag ledger once, on the day the build reaches three consecutive rises.
3. **Activity ratios** (ticker level): put/call ratios by volume and by open interest, and put and call premium estimates, tracked against the name's own history. These describe activity, not sentiment.

## Premium estimates and data-quality flags

There is no VWAP and no trade tape in free end-of-day data, so every premium figure is an estimate.

- `prem_mid` = volume x closing bid-ask midpoint x 100. Used for the thresholds when a quote exists.
- `prem_last` = volume x last trade price x 100. Kept for reference only, because the last trade can be stale or unrelated to most of the day's volume.
- Flags on every candidate: `STALE_LAST` (last trade not from the snapshot day), `LAST_OUTSIDE_QUOTE` (last trade outside the closing bid and ask), `WIDE_MARKET` (spread above 25% of the midpoint, or no bid), `NO_QUOTE`.

## Context tags (tag, never discard)

v1 threw candidates away when they looked like mechanics. v2 keeps everything and tags it, so tagged and untagged flags can be evaluated separately.

| Tag | Source | Why it matters |
|---|---|---|
| `EARNINGS(±Nd)` | data/events.csv | Hedging and event trades cluster around results |
| `EX_DIVIDEND(+Nd)` | data/events.csv | Dividend capture and early exercise of calls |
| `CORPORATE_ACTION`, `ADJUSTED_CONTRACT` | events.csv; non-standard contract root | Adjusted contracts trade on different terms |
| `INDEX_REBALANCE` | data/events.csv | Index-driven hedging flows |
| `HARD_TO_BORROW` | data/events.csv | Conversions and synthetic shorts show up in options when stock is hard to borrow |
| `NEAR_EXPIRY`, `OPEX_WEEK`, `WEEKLY/MONTHLY/QUARTERLY_EXPIRY` | contract symbol, calendar | Rolls and expiry mechanics |
| `DEEP_ITM` | strike vs close | Conversions, dividend and exercise mechanics |
| `PROBABLE_MULTI_LEG(n)` | other series on the same name with near-identical volume that day | Spreads, calendars and collars look like separate trades in end-of-day data |
| `EARNINGS_DATE_UNCHECKED` | events.csv has no earnings date for the name | The flag cannot be placed in the earnings or non-earnings bucket yet |

Dated events in `data/events.csv` are added by the judgment layer from a named source (the company's investor relations page for earnings, the exchange or index provider for rebalances). They are never guessed.

## Cross-references (judgment layer)

- **Insiders (EDGAR Form 4):** direction, size and the 10b5-1 checkbox. Every citation carries the accession number.
- **Congress (House PTRs):** actual transaction rows, with the transaction-to-filing lag stated (up to 45 days). House only; the Senate site blocks scripted access.

These are context for a flagged name, never confirmation of a direction.

## Evaluation

Every flag is appended to `data/flag-ledger.csv` with its bucket fields (days to expiry, moneyness, tags, quality flags). What counts as a flag that "paid" is defined in `process/evaluation-plan.md`, written before any outcome was measured, and scored by `scripts/evaluate.py` against matched controls. Until the plan's minimum sample is reached the script prints INSUFFICIENT DATA, and no claim about the signal is made.

## Known limitations

| Limitation | Consequence |
|---|---|
| Delayed end-of-day data, no trade tape | No buyer or seller side, no sweeps, no direction |
| Closing quotes only | Premium estimates are proxies; flags mark when they are weak |
| Open interest settles overnight | Today's open interest reflects yesterday's settled positions |
| Congressional lag up to 45 days | Context only, never real-time |
| House-only congress coverage | Senate missing |
| Snapshot filter (volume >= 25 or open interest >= 100) | Small contracts are not on file |

## What changed in v2 (2026-09-23)

v1 said that if unusual volume did not appear in the next day's open interest it was day trading and the candidate died, and if it did appear someone had kept the position. That was wrong for the reasons in "What end-of-day data can and cannot say" above, and v1 reports use that framing ("killed", "converted", "paid flag"). The v1 reports and scan log are left as they were written, as a record.

v2: the output is described as a positioning anomaly rather than disagreement; direction is never assigned from puts or calls; premium thresholds use the bid-ask midpoint with data-quality flags; mechanics are tagged instead of discarded; every flag goes to a ledger; and "paid" is defined in advance with matched controls.
