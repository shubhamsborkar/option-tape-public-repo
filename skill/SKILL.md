---
name: options-tape
description: >-
  Run the options-tape disagreement detector: does the US options market
  disagree with the long-term thesis on names you own or cover? Takes a
  daily chain snapshot (free CBOE delayed data), scans for positioning
  anomalies (new-position volume, multi-day OI builds, put/call skew shifts),
  cross-references EDGAR Form 4 insider filings and House congressional PTRs,
  scores divergence, and writes a dated disagreement report. Use when the user says "run the tape," "options tape," "tape scan," "disagreement report,"
  "options screener," or asks whether the options market is saying something
  about his names. Also for snapshot-only runs ("take today's snapshot"). NOT
  for: trade recommendations, single-stock selloff triage (stock-selloff-triage),
  or post-earnings behavior reads (calendar-tell).
---

# Options Tape — the disagreement detector

## What this is (and is not)

A thesis-surveillance instrument for a long-term quality investor. The question
is always: **"is the options market disagreeing with me about a business I own
or cover?"** It is NEVER a trade-idea generator. No output may recommend
buying, selling, or holding anything — flagged names are presented as what the
machine surfaced and what to investigate, full stop.

## Vocabulary law (house rules — applies to every output)

- Say "divergence score," "disagreement report," "flagged for investigation."
- NEVER: "plays," "conviction score," "golden sweep," ranked buy lists,
  "smart money says buy," or any directive to act.
- Frame insider/congressional data as "public disclosure data as a positioning
  signal" — never as profiting from non-public information.

## Step 1 — Run the deterministic layer (all four scripts)

```bash
python3 scripts/take_snapshot.py
python3 scripts/scan.py
python3 scripts/fetch_form4.py
python3 scripts/fetch_ptrs.py
```

Timing rule: the snapshot is stamped with the TRADING date from the CBOE API
timestamp. A run while the US market is open captures partial-day volume and
will be overwritten by a later run the same day — the definitive snapshot is
after the US close. Intraday runs are fine for a look, but say in the report
which kind it is.

Outputs land in `workspace/`:
`scan_candidates.md`, `form4_recent.md`, `ptr_matches.md`.

## Step 2 — Judgment layer: exclusions first

For each NEW-POSITION candidate and OI BUILD in `scan_candidates.md`, work
through the false-positive ladder before treating it as signal:

1. **Near-expiry mechanics:** DTE <= 3 (ROLL_RISK flag) — almost always rolls
   or expiry gamma, discard unless extraordinary.
2. **Earnings hedging:** check the name's next earnings date (web search;
   verify on the company's IR page). Anomalous volume within ~10 days of
   earnings at near-dated expiries is presumptively hedging, not information.
3. **Two-sided volume:** matching call AND put volume at the same expiry ≈
   straddle/volatility trade, not directional.
4. **Deep-ITM volume ≈ OI:** likely rolls or dividend/assignment mechanics.
5. **Index/macro days:** if the whole universe lights up the same direction on
   the same day, that is market-wide repricing, not a name-specific signal.

Known EOD data limits (state them in every report, never work around them by
guessing): delayed EOD data cannot show buyer- vs seller-initiated trades or
sweeps; direction is inferred only weakly (put OI accumulating = someone
paying for downside exposure — investigate, don't conclude).

## Step 3 — Cross-reference survivors

Only for names that survive exclusions:

- **Insiders:** open the Form 4 doc URLs for that name (`form4_recent.md`).
  Read direction (P/S), size, price, and the 10b5-1 checkbox
  (`aff10b5One`). Discretionary (non-10b5-1) trades matter; scheduled-plan
  sales are near-noise. Note the accession number for every filing cited.
- **Congress:** check `ptr_matches.md` for the name; read the PTR PDF for the
  actual transaction (ticker, buy/sell, size band, TRANSACTION date vs filing
  date). Always caveat the lag (up to 45 days) and that v1 is House-only.
- If an unparseable (scanned) PTR could matter for a flagged name, Read the
  PDF visually.

## Step 4 — Divergence score (0-10, evidence itemized every time)

- +2 persistent OI build, >= 3 consecutive snapshots, on directional
  (OTM) strikes
- +1 any surviving new-position candidate (premium proxy >= $200k, >= $50k
  thin); +2 instead if premium proxy >= $1M (>= $250k on thin chains)
- +1 cluster: multiple same-direction candidates on the name the same day
- +2 discretionary insider Form 4 in the same direction within 30 days
- +1 insider cluster (>= 2 distinct insiders, same direction, 30 days)
- +1 congressional trade same direction within 60 days (max 1 point — lagged,
  coarse data)
- +2 repeat: name was flagged on a prior scan (check `data/scan-log.md`)
- −2 earnings within 10 calendar days
- −1 near-expiry candidate carrying the signal
- −1 two-sided volume signature

Bands: **>= 5 disagreement item** (full write-up), **3-4 watch note**,
**< 3 logged only**. Never present the score without its component breakdown.

## Report language law (keep every report readable)

Write every report so a newbie investor could follow it. The rigor stays in the
numbers; the sentences get plain:
- Describe positions as what they are: "a bet that Oracle falls below 115 by
  July 31" beats "Jul-31 115P". Give the plain description first, the contract
  shorthand after it in parentheses.
- Gloss any term of art at first use in each report (open interest = contracts
  still held; conversion = the volume became positions somebody kept; premium
  proxy = rough dollars at stake).
- Short sentences. One idea per sentence. No desk shorthand ("two-sided tape",
  "harvested", "prints") without a plain-English companion.
- Keep the tables precise and dense; let the prose around them be the simple
  layer. The report is a note to a smart friend who has never traded options.

## Step 5 — Write the disagreement report

Path: `outputs/YYYY-MM-DD-disagreement-report.md` (trading date). Structure:

1. Header: scan date, intraday-or-close, snapshot count, standing data-limits
   block (delayed EOD; no trade-direction; House-only congress with lag).
2. **Tier 1 names first (ACN, SOLS, LULU, ORCL) — every one gets a status
   line even when quiet.** Quiet is a finding: the tape agrees with the
   thesis today.
3. Disagreement items and watch notes: evidence tables, cross-references with
   accession numbers / PTR DocIDs, itemized score, and "what to verify next."
4. Every figure in the report traces to the snapshot file, an EDGAR accession
   number, or a PTR DocID. No figure from memory.

Then append one line to `data/scan-log.md`:
`| date | close-or-intraday | snapshots | flagged (score) | watch notes |`
— this log is the backtest dataset; never skip it, even for quiet scans.

## Standing honesty rules

- Scoring is an untested hypothesis until backtested against the scan log.
  Say so whenever a score appears in anything public-facing.
- Never cherry-pick: the scan log records every run, including the boring ones.
- Thin chains make anomalies stand out more, but the absolute numbers are
  small; size the language accordingly.
- This skill's outputs are research notes for your own process, not
  publishable advice. Nothing it writes is a recommendation to anyone.
