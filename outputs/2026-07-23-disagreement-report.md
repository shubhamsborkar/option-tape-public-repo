# Disagreement report — 2026-07-23 close (DEFINITIVE; supersedes the intraday run of the same trading date)

**Run type:** post-close (fetched 2026-07-24 morning IST). **Snapshots:** 2
definitive closes (07-22, 07-23). Streak-based scoring (+2, needs 3 consecutive
snapshots) activates with the 07-24 close.

**Market context that colors everything below:** 07-23 was a broad red day —
GOOGL -7.1% on its earnings reaction, ORCL -4.6%, MCO -3.8%, ISRG -2.7%, MSFT
-2.2%, most of the universe down. Universe-wide put demand on a day like this
is partly market repricing (exclusion #5), and scores are read conservatively.

**Standing data limits:** delayed EOD data — no trade direction, no sweeps;
put accumulation = someone paying for downside exposure, investigate, don't
conclude. Congress is House-only, up to 45-day lag. Scores are an untested
hypothesis pending backtest. Nothing here is a recommendation.

**Two pipeline notes from this run (kept honest):**
1. *Date bug fixed:* the CBOE API timestamp is UTC and rolls past midnight
   while the US market is closed; early-IST runs mislabeled yesterday's close
   as today. Snapshots are now stamped by latest actual trade time.
2. *New DEEP_ITM flag:* 07-23 tape was flooded across LULU/ORCL/GOOGL/ISRG/
   COST/MSFT with deep-ITM prints at ~intrinsic prices (e.g. LULU Dec 300P
   with the stock at 110.63; COST 650C with the stock at 926). That is
   synthetic-stock/conversion mechanics, not directional information — the
   scanner now flags it automatically.

---

## The headline of this run: every flagged position was KEPT

Yesterday's intraday candidates faced the volume→OI test overnight. All of
them converted to standing open interest (snapshot 07-23 vs 07-22):

| Contract | Prior OI | Now | Verdict |
|---|---|---|---|
| ORCL Aug-7 114P | 101 | 1,631 | kept (full-day vol 1,625) |
| GOOGL Aug-28 285P | 63 | 6,314 | kept |
| GOOGL Feb-27 260P | 3 | 1,370 | kept |
| GOOGL Feb-27 280P | 9 | 768 | kept |
| GOOGL Sep-27 275P | 79 | 499 | kept |
| TSM Aug-21 465C | 146 | 3,868 | kept (full-day vol 5,100) |
| ISRG Jun-27 240P | 24 | 224 | ~200 of 299 kept |
| MSFT Sep-18 425C | 853 | 4,640 | kept |

None of yesterday's flags were day trades. The adjudication mechanism works.

---

## Tier 1

### ACN — WATCH NOTE (score 1, but the single most unusual print on the tape today).
One paired structure, Aug-21 expiry, near-equal legs:

| Leg | Vol | OI before | Ratio | Premium proxy |
|---|---|---|---|---|
| Aug-21 130C (slightly ITM; close 138.74) | 21,202 | 1,173 | 18.1x | $27.8M |
| Aug-21 120P (~13% OTM) | 22,741 | 1,564 | 14.5x | $3.4M |

~22k contracts per leg ≈ 2.2M shares ≈ ~$300M notional on a chain whose entire
open interest is ~207k contracts. Matched size + same expiry reads as ONE
institutional structure — collar-shaped (protection on a large stock position)
or an equivalent package; it is not a clean directional bet, which is why the
score stays low (+2 size, −1 paired/two-sided). Congressional context, no
points scored: Rep. Allen's spouse SOLD ACN May 8 ($15k-50k, filed 6/8, DocID
20034740 — 77 days back, outside the 60-day window); Rep. Newhouse's spouse
BOUGHT ACN July 10 ($1k-15k, filed 7/17, DocID 20034998).
**Monday's test:** if ~22k appears in both legs' OI, someone genuinely
structured $300M of ACN exposure. That is worth knowing about a real holding.

### SOLS — quiet. Green day (+1.3%, 60.88) on a red tape. Nothing met thresholds.

### LULU — quiet once mechanics are stripped.
The scary-looking $241M put premium aggregate is entirely deep-ITM prints
(strikes 185-350 vs stock 110.63) — synthetic-stock mechanics, all DEEP_ITM
flagged, discarded. No genuine directional anomaly.

### ORCL — WATCH NOTE, score 4. One shy of a disagreement item. Strongest signal in the book.
Two-day slide 125.85 → 120.04 (-4.6%). Evidence, mechanics stripped:

| Item | Detail |
|---|---|
| Yesterday's 114P | CONVERTED (101→1,631 OI) — position standing |
| Jul-31 124P | standing at 9,063 OI (was 95 two days ago) |
| NEW: Aug-21 118P (~1.7% OTM) | 3,201 vol vs 515 OI (6.2x), $2.48M premium proxy |
| Other side | Aug-21 125C built 3,859→12,931; Sept 145C/155C still building |

Score: +2 repeat flag, +2 new position >= $1M, +1 same-direction cluster,
−1 two-sided tape = **4**. Insiders: nothing discretionary (Henley June sale
was 10b5-1, accession 0001341439-26-000064). Congress: no ORCL matches.
Read: someone is paying real money for near-dated ORCL downside while someone
else accumulates September upside — a genuine argument in the tape, on a
broad-red day, on a name in my coverage.
**Friday's test:** 118P conversion; 124P/114P persistence (streak rule arms
with the third snapshot).

---

## Tier 2

### GOOGL — WATCH NOTE, score 3 (upgraded from 2).
The post-earnings put ladder all converted (table above) and September OTM put
builds extended: 310P 4,690→14,689, 300P 7,195→11,113 (2-day streak; third
day arms the +2). Congress now shows TWO same-direction filers: Kean partial
sales June 2/24 (DocID 20035003) and Newhouse spouse partial sale July 10
(DocID 20034998) — capped at +1 by rubric. Score: +2 repeat, +1 standing
converted positions, +1 cluster, +1 congress, −2 earnings window (reported
07-22) = **3**. The −2 expires as the event recedes; if the September builds
hit a 3-day streak Friday, this is the leading candidate for the project's
first disagreement item.

### TSM — logged, score 2.
The Aug 465C bullish position confirmed standing (146→3,868). Allen spouse
TSM purchase was May 8 — outside the 60-day window (77 days), context only.
Today's 450P/457.5P prints: deep-ITM expiry mechanics, discarded.

### ISRG — logged. Jun-27 240P kept (~200 contracts). Today's put-premium
headline ($101M!) is entirely deep-ITM mechanics (strikes 460-560 vs stock
332) — the DEEP_ITM flag now catches this class automatically.

### MSFT / AAPL — earnings window (expected next week; verify exact dates
before public use), logged: MSFT Sept 425C converted and Jul-31 435C built
2,598→12,024 (bullish-lean); AAPL October call builds inching on (345C at
17,194). NVDA: the Oct 180C block is stable at 91,050 — real standing OI,
origin still unexplained, stays on the investigate list. V, MA, COST, ASML,
MCO, SPGI: quiet or mechanics only.

---

## Next-run checklist (Friday close, run Saturday morning)
1. Third snapshot arms all streak scoring. Key arms: GOOGL Sept 310P/300P,
   ORCL 124P, MSFT 435C.
2. Conversion tests: ACN's paired 22k legs (the big one), ORCL 118P.
3. GOOGL earnings −2 penalty: keep while within 10 days of 07-22.
4. Still open: MSFT/AAPL/GOOGL earnings dates verified from IR pages; NVDA
   Oct 180C origin.

*Research note only — not for publication. Anything drafted from this goes
through COMPLIANCE_FRAMEWORK.md in full.*
