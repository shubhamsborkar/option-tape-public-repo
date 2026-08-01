# Methodology — the disagreement detector

Designed 2026-07-23 from first principles around what free end-of-day data can
honestly support. No thresholds, criteria, or scoring borrowed from anyone.

## Design principle

The instrument answers one question for a long-term quality investor: **is the
options market disagreeing with me about a business I own or cover?** Every
design choice follows from that. We do not chase intraday flow; we look for
*persistent, paid-for positioning* that contradicts (or corroborates) a
long-term thesis, then check whether people with disclosure obligations
(insiders, members of Congress) are leaning the same way in the public record.

## Signals (deterministic layer, scripts)

1. **New-position anomaly** (contract level, latest day):
   volume >= 2.5x max(OI, 1) AND volume >= 250 AND premium proxy
   (volume x last x 100) >= $200,000. Thin chains (total OI < 50k): vol >= 50,
   premium >= $50,000. Rationale: volume far above existing OI means positions
   are being OPENED, not managed; the premium floor removes retail-lottery
   noise; thin-chain scaling keeps SOLS-class names visible.
2. **OI persistence** (across snapshots): open interest rising over
   consecutive snapshots with growth >= 1,000 contracts (>= 100 thin).
   Rationale: day-traded volume disappears overnight; positions that persist
   and GROW are conviction someone is paying carry on. This is the signal the
   whole snapshot discipline exists for, and it strengthens mechanically as
   the archive deepens.
3. **Skew shift** (ticker level): put/call ratios by volume and OI, and put vs
   call premium proxies, tracked daily against the name's own history — each
   name is compared to its own normal, never to another name's.

## Cross-references (judgment layer)

- **Insiders (EDGAR Form 4):** direction, size, and the 10b5-1 checkbox.
  Scheduled-plan sales are near-noise; discretionary trades matter. Every
  citation carries the accession number.
- **Congress (House PTRs):** actual transaction rows read from the PDF, with
  the transaction-vs-filing lag stated every time (up to 45 days). v1 is
  House-only — the Senate site blocks scripted access. Never framed as
  real-time corroboration.

## Exclusion ladder (run before anything is called a signal)

Near-expiry mechanics (DTE <= 3) → earnings-window hedging (~10 days, dates
verified externally) → two-sided volume (vol trades) → deep-ITM volume ≈ OI
(rolls/dividend mechanics) → universe-wide same-direction days (macro
repricing, not name-specific information).

## Divergence score

Itemized 0-10 rubric in SKILL.md; bands: >= 5 disagreement item, 3-4 watch
note, < 3 logged. **The scoring is an untested hypothesis** until the scan log
(data/scan-log.md) is deep enough to backtest. Every scan is logged including
quiet ones — the log is append-only and never cherry-picked.

## Known limitations (stated, not worked around)

| Limitation | Consequence |
|---|---|
| Delayed EOD data, no trade tape | Cannot see buyer- vs seller-initiated trades or sweeps; direction inferred weakly from put/call structure |
| Intraday runs capture partial volume | Definitive snapshot is post-US-close; intraday runs labeled as such |
| OI updates overnight (OCC) | Today's OI reflects yesterday's settled positions; volume→OI conversion checked next day |
| Congressional lag up to 45 days | Corroboration only, capped at +1, never "real-time" |
| House-only congress coverage | Senate missing in v1; said in every report |
| ~10% of PTR PDFs unparseable (scanned) | Counted and listed honestly; read visually when material |

The volume→OI conversion check deserves emphasis: free data's one clean trick.
If today's anomalous volume does NOT appear in tomorrow's OI, it was day
trading and the candidate dies. If it does, someone kept the position. The
next snapshot always adjudicates today's candidates.
