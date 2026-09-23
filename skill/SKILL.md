---
name: options-tape
description: >-
  Run the options tape: surface persistent series-level positioning anomalies
  in US options on names you own or cover. Takes a daily chain snapshot (free
  Cboe delayed data), scans for unusual volume and open-interest builds with
  data-quality flags and context tags, logs every flag to a ledger,
  cross-references EDGAR Form 4 insider filings and House congressional PTRs,
  and writes a dated positioning report. Use when the user says "run the
  tape," "options tape," "tape scan," "positioning report," "options
  screener," or asks whether anything unusual is happening in the options on
  their names. Also for snapshot-only runs ("take today's snapshot") and for
  "evaluate the tape." NOT for: trade recommendations, single-stock selloff
  triage (stock-selloff-triage), or post-earnings behavior reads
  (calendar-tell).
---

# Options tape

## What this is and is not

A research prompt for a long-term investor. It surfaces **persistent series-level positioning anomalies**: contracts where activity or open interest is unusual against their own history. It is never a trade-idea generator, and it never says what "the options market thinks". No output may recommend buying, selling or holding anything.

## What the data cannot say (applies to every sentence written)

- Volume is gross activity; open interest is a net count. Unchanged open interest does not prove day trading, because one participant can close while another opens. Rising open interest confirms more contracts are open, and says nothing about who opened them or which side they hold.
- Put volume is not bearish and call volume is not bullish by default. Sold puts, covered calls, verticals, calendars, collars, rolls and conversions leave similar end-of-day footprints.
- Never write "someone kept the position", "the volume converted", "the candidate died", "bearish bet", "bullish bet", "smart money" or "the options market disagrees". Describe what the numbers show: "open interest in the October 170 put rose from 14 to 2,168 contracts over three sessions."

## Vocabulary

- Say "positioning anomaly", "positioning report", "flagged for research".
- Never: "plays", "conviction", "golden sweep", ranked buy lists, or any directive to act.
- Insider and congressional data are public disclosures, used as context, never as confirmation of a direction.

## Step 1: run the deterministic layer

```bash
python3 scripts/take_snapshot.py
python3 scripts/scan.py
python3 scripts/fetch_form4.py
python3 scripts/fetch_ptrs.py
```

The snapshot is stamped with the trading date of the data. A run while the US market is open captures partial volume and is overwritten by a later run; the definitive snapshot is after the close. Say in the report which kind it is.

Outputs: `workspace/scan_candidates.md`, `workspace/form4_recent.md`, `workspace/ptr_matches.md`, and new rows in `data/flag-ledger.csv`.

## Step 2: keep data/events.csv current

For every name with a candidate, check that `data/events.csv` has its next earnings date, any ex-dividend date in the next two weeks, and any corporate action, index rebalance or hard-to-borrow condition. Add missing rows as `ticker,date,event,source`, with `event` one of `earnings`, `ex_dividend`, `corporate_action`, `index_rebalance`, `hard_to_borrow`, and `source` naming where the date came from (the company's investor relations page, the exchange, the index provider). Never guess a date. If you added rows, re-run `scan.py` so the tags pick them up.

## Step 3: read the tags, do not discard

Every candidate carries data-quality flags and context tags (full list in `process/methodology.md`). Read them before writing anything:

- A candidate with `STALE_LAST`, `LAST_OUTSIDE_QUOTE`, `WIDE_MARKET` or `NO_QUOTE` has an unreliable premium estimate. Say so.
- `NEAR_EXPIRY`, `OPEX_WEEK`, `DEEP_ITM`, `PROBABLE_MULTI_LEG`, `ADJUSTED_CONTRACT`, `EX_DIVIDEND` and `HARD_TO_BORROW` point to mechanics that often explain the footprint. Name the likely mechanic.
- `EARNINGS(±Nd)` is context, not a reason to drop the flag.
- A candidate is **clean** when it has no quality flag, more than 7 days to expiry, and none of the mechanics tags above. Clean candidates get the fuller write-up.

## Step 4: cross-reference clean candidates

- **Insiders:** open the Form 4s for that name (`form4_recent.md`). Read direction, size, price and the 10b5-1 checkbox. Note the accession number for every filing cited.
- **Congress:** check `ptr_matches.md`; read the PTR for ticker, buy or sell, size band, and transaction date against filing date. State the lag (up to 45 days) and that coverage is House only.

## Step 5: write the positioning report

Path: `outputs/YYYY-MM-DD-positioning-report.md` (trading date).

1. Header: scan date, close or intraday, snapshot count, and the standing limits block (delayed end-of-day data; no trade direction; premium figures are estimates; House-only congress with lag).
2. Tier 1 names first, each with a status line even when nothing is flagged.
3. Clean candidates: the numbers, the tags, the likely explanations including mechanics, cross-references with accession numbers or PTR IDs, and what to check next. No score, no direction.
4. Tagged candidates: one line each, with the tag that most likely explains them.
5. Every figure traces to a snapshot file, an EDGAR accession number or a PTR ID.

Write it so a new investor can follow it: the plain description first ("a put on Oracle at 115 expiring 31 July"), the contract shorthand after. Gloss open interest, premium and similar terms at first use.

Then append one line to `data/scan-log.md`: `| date | close-or-intraday | snapshots | clean candidates | notes |`. Log every run, quiet ones included.

## Evaluate (on request: "evaluate the tape")

Run `python3 scripts/evaluate.py` and report its table as printed. The rule is in `process/evaluation-plan.md` and is never changed after results are seen. Below the minimum sample it says INSUFFICIENT DATA, and nothing more may be claimed.

## Standing honesty rules

- Never cherry-pick: the ledger and the scan log record everything.
- Thin chains make anomalies stand out, but the absolute numbers are small; size the language to match.
- Outputs are research notes for your own process, not advice to anyone.
