# Disagreement report — 2026-07-24 close (Friday; run Saturday evening IST)

**Snapshots:** 3 definitive closes (07-22, 07-23, 07-24).
**Run limitation discovered (structural, honest):** this fetch shows Friday's
VOLUME with THURSDAY's open interest — the post-Friday OI update had not
posted to the CBOE delayed feed by fetch time (verified: multiple contracts
carry OI identical to Thursday's file; MCO's entire chain was served stale —
MCO has no Friday data this run). Consequences: no streak signals could fire
today, Friday's conversion tests (ACN structure, ORCL 118P) roll to Monday,
and the right Monday run is ~5:30 PM IST (after the OI update posts US
Monday pre-market, before the US open).

**Standing data limits:** delayed EOD, no trade direction; congress
House-only, up to 45-day lag; scores untested pending backtest. Friday was
July monthly-adjacent weekly expiry — enormous 0-DTE volume on AAPL/NVDA/
GOOGL/MSFT is expiry-day mechanics, ROLL_RISK-flagged and discarded wholesale.

---

## Tier 1

### ACN — the sequence of the week. Structure Thursday, +5.95% Friday.
Friday: 138.74 → 146.815 (+5.95%, intraday high 147.52). Verified externally:
no single same-day announcement; coverage attributes the move to sentiment
rebound on a name down ~44% YTD (GuruFocus 8978676; Quiver Quantitative,
2026-07-24). Sequence on the tape:
- Thursday: paired Aug-21 structure, ~22k contracts per leg (130C / 120P),
  ~$300M notional (07-23 report).
- Friday: +5.95%, and the 130 calls are now ~17 points ITM.
What the data CANNOT say: whether the structure was collar-shaped (long puts,
short calls — Friday blew through the capped strike) or a bullish
risk-reversal (long those calls — remarkably well-timed). EOD data has no
trade direction; both readings fit the same prints. **Monday's OI is the
adjudicator:** if ~22k stands in both legs, the structure is real and its
composition becomes partially inferable from how the legs behave vs. spot.
No new ACN candidates Friday; aggregates normalized (P/C vol 0.54).

### SOLS — first genuine SOLS item: WATCH NOTE, score 2 (thin-chain language).
Aug-21 80C (32% OTM): OI path 5,440 → 6,218 → 6,447 across the three
snapshots — a rising path on a chain where 6,447 contracts is ~7% of total
OI. Caveat: per-ticker cache freshness varied this run; treat the third point
as provisional until Monday. +2 rising OTM directional build (provisional).
No insider or congressional matches. Small absolute numbers; someone is
quietly long upside exposure in a thin chain. Verify path Monday.

### LULU — quiet. Deep-ITM mechanics only (all DEEP_ITM-flagged), aggregates
normalizing (P/C vol 1.14 vs 1.57 Thursday). Stock +3.3% Friday to 114.28.

### ORCL — WATCH NOTE, score 4. Third consecutive down day; the argument in
the tape is resolving toward the put side, and the fundamental tape caught up.
125.85 → 120.04 → 114.99 (-8.6% over three sessions). Verified externally:
S&P downgraded Oracle to BBB- citing OpenAI exposure (the $300B/5-yr compute
deal), FCF at negative $23.7B, stock down >50% since June 2 (TradingKey
07-24; Yahoo Finance; 24/7 Wall St 07-22). Friday's fresh prints, mechanics
stripped:

| Item | Detail |
|---|---|
| Dec-2027 100P | 4,052 vol vs 1,095 OI (3.7x), $9.68M premium proxy — LEAPS downside |
| Jul-31 110P (~4% OTM) | 14,580 vol vs 2,651 OI (5.5x), $3.19M |
| Dec-2028 105P / Dec-2027 90P / Dec-2026 75P | $2.7M / $2.35M / $2.24M, all high vol/OI |
| Other side | Jul-31 120C/125C/117C active ($1.0-1.4M each) — still two-sided, but put premium now dominates ($199.7M vs $88.6M daily proxy) |

Score: +2 repeat (third consecutive flagged run), +2 new position >= $1M,
+1 same-direction cluster (five non-mechanic put candidates across four
expiries), −1 two-sided = **4**. Streak points unavailable (OI stale).
Honesty required in any future write-up: Wednesday's and Thursday's put flags
preceded Friday's downgrade-driven leg — that part is the tool working.
Friday's put buying, after -8.6% and a public downgrade, is reactive/hedging
flow, not foresight. The early flags are the finding; today's are follow-through.
Insiders: still nothing discretionary (June cluster was grants/10b5-1).
Congress: no ORCL matches. **Monday: 118P + 110P conversions, streak checks.**

---

## Tier 2 (compressed — expiry-day noise dominated)

- **GOOGL:** stabilized (+0.6% to 319.74). All Friday candidates are 0-DTE /
  Monday-expiry mechanics. Sept 310P/300P build checks blocked by stale OI —
  Monday. Earnings −2 window has ~1 week left. Holding at watch, score 3
  (unchanged pending OI).
- **AAPL:** +3.5% to 333.02 on colossal 0-DTE call volume (330C traded
  225,305 contracts) — expiry-day momentum, excluded. Non-expiry residue:
  Sept 330P $7.5M (4.1x OI) — single print, logged; earnings window applies.
- **TSM:** -2.9% to 403.41. Deep-ITM call flood (DEEP_ITM-flagged, mechanics).
  Real residue: long-dated OTM LEAPS on BOTH sides — Sep-27 280P ($2.5M),
  Jun-28 300P ($1.6M) vs Jan-28 630C/640C ($2.5M/$1.2M). Someone is pricing
  wide long-term outcomes; two-sided, logged.
- **MSFT:** flat; expiry mechanics plus modest Aug 385C/387.5C prints
  ($0.9-2.2M); earnings window −2; logged. **NVDA:** all mechanics or
  DEEP_ITM; Oct 180C block unchanged at ~91k (investigate list). **MA:** two
  small call prints ($0.6M) — first MA activity, logged. **V, COST, ASML,
  SPGI:** quiet or sub-threshold. **MCO:** NO FRIDAY DATA (stale cache) —
  gap recorded, not hidden.

---

## Next-run checklist (MONDAY ~5:30 PM IST — timing matters this once)
1. Post-Friday OI lands US Monday pre-market: adjudicate ACN's 22k legs
   (the big one), ORCL Jul-31 110P and Aug 118P, SOLS 80C third point,
   GOOGL Sept 310P/300P streaks, AAPL Sept 330P.
2. MCO: confirm fresh chain returns.
3. GOOGL earnings −2 expires 08-01; MSFT/AAPL earnings expected this coming
   week — get exact dates from IR pages before any public use.
4. Edition outline is due ~Monday per plan — this week's material: the
   conversion mechanism validated, the date bug, the DEEP_ITM flood, the ACN
   sequence, the ORCL early-flags-then-follow-through distinction.

*Research note only — not for publication. Anything drafted from this goes
through COMPLIANCE_FRAMEWORK.md in full.*
