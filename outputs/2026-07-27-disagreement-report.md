# Disagreement report — 2026-07-27 close (Monday; run Tuesday IST)

**Snapshots:** 4 definitive closes (07-22, 07-23, 07-24, 07-27). Post-Friday
OI is now in the data — this run adjudicates everything that queued up over
the weekend.
**Data quirks carried honestly:** (1) the 07-24 file's OI column is known-stale
(Thursday's values), so automatic streak counts undercount by one this run —
judged per-item below instead. (2) MCO's chain came back stale a second time
(feed lags ~a day on this thin name) — MCO is read with a one-day delay from
here on. (3) Macro overlay: Fed meeting Jul 28-29; MSFT reports Wed 7/29 AMC
(verified, Microsoft IR), AAPL Thu 7/30, V today AMC, SPGI this morning —
event windows are live across a third of the universe; reads conservative.

**Standing data limits:** delayed EOD, no trade direction; congress
House-only, lagged; scores untested pending backtest. Not recommendations.

---

## Adjudications — the weekend's open questions, answered

**KILLED (flagged, tested, dead):**

| Candidate | Test result |
|---|---|
| ACN paired Aug 130C/120P, ~22k per leg (~$300M notional) | **Did NOT convert.** 130C OI 1,173 → 1,163; 120P 1,564 → 1,653. ~22,000 contracts traded per leg and left essentially zero standing position: closing/rolling flow or same-day round-trips, NOT a new position. The week's most dramatic candidate is dead, and the tool killed it itself. |
| ORCL Aug-21 118P ($2.48M flag from Thursday) | Not converted: OI 515 → 508. Dead. |

**CONFIRMED STANDING:**

| Position | Now |
|---|---|
| ORCL Jul-31 110P | 2,651 → **12,711** OI (Friday's 14,580 vol mostly kept) |
| ORCL Dec-2027 100P (LEAPS) | 1,095 → **5,101** ($9.7M flag was real) |
| AAPL Sep 330P | 1,483 → **6,503** |
| TSM Sep-2027 280P | 87 → **2,048** (Friday's $2.5M print kept) |
| SOLS Aug 80C | **6,449** (Friday's provisional point was real; growth now stalled: +2 in two sessions) |
| GOOGL put ladder | Intact, inching: Aug-28 285P 6,457; Sep 310P 15,180 (+491); Sep 300P 11,774 (+661) |

**REDUCED:** ORCL Jul-31 124P cut 9,063 → 5,603 — ~3,500 contracts taken off
into Monday's +4.3% bounce. Consistent with profit-harvesting after the slide.

---

## Tier 1

### ACN — the structure is dead; the stock is +11% in two sessions.
138.74 → 146.815 → 154.06. The 22k-per-leg structure left no OI (table above),
so Thursday's prints get reclassified: roll/close mechanics, not new money.
What remains real on the tape: a small add of Mar-2027 240C (+1,000 contracts,
~56% OTM LEAPS) on Monday. Logged, score 1. For the edition: this is the
flagship kill — the most cinematic-looking print of the week failed the
overnight test, and a tool that cannot kill its own candidates is a
tout sheet.

### SOLS — holding, not growing. Aug 80C stands at 6,449; the build stalled
after Friday. Downgraded to logged (score 1-2, thin-chain language). Still the
first real SOLS accumulation on record; watching for resumption.

### LULU — quiet. +3.1% to 117.83, mechanics only. Third quiet run of four.

### ORCL — WATCH NOTE, score 3. The picture matured into a barbell.
Monday +4.3% bounce to 119.90. Mechanics stripped, the standing structure is
now unambiguous:
- **Long-dated crash protection GREW on the bounce:** Jan-27 60P +5,015 to
  11,091; Dec-26 75P +4,684 to 6,453; Dec-26 90P to 5,929; Dec-27 100P at
  5,101; Jul-31 110P at 12,711. All far-OTM, all long-dated, all growing.
- **Near-dated upside converted and added:** Jul-31 125C at 8,542, 130C at
  9,280, Aug 125C at 13,096, Sep 145C at 11,584; fresh Jul-31 124C Monday
  (7,137 vol, 3.0x, $1.59M).
- **Near-dated puts harvested:** 124P cut ~3,500.
Read: positioning for a tradeable bounce while paying carry on deep
disaster insurance out to 2027-2028. Score: +2 repeat (4th consecutive run),
+1 new position, +1 LEAPS-put cluster, −1 two-sided = **3**.
Insiders: still nothing discretionary. Congress: still no ORCL matches.

---

## Tier 2 (event windows dominate)

- **NVDA** -5.0% to 196.51 on a semis-specific red day (ASML -5.8%, TSM -1.1%,
  while megacap software rose). The huge Jul-31 call OI jumps (+60-70k per
  strike: 215C to 89,423, 222.5C to 77,884, 220C to 67,279) are rolls from
  the expired 7/24 weeklies — mechanics at scale, discarded. Real residue:
  Sep 255C fresh $2.65M (3.1x); Oct 180C block stable at 91,451 (investigate
  list, unexplained since day 2). Earnings ~Aug 27, outside window. Logged.
- **ASML** — first ASML candidate: Aug-21 1575P (~5% OTM), 892 vol vs 275 OI
  (3.2x), $6.09M, printed ON a -5.8% day (-8.2% over three sessions) —
  reactive-flavored, watch 1.
- **MSFT** — reports tomorrow (Wed 7/29 AMC, verified). Pre-earnings call
  accumulation is enormous and CONVERTED: Sep 430C +12,334 to 19,813; Jul-31
  430C 15,174; Aug 420C 18,381; Aug-7 460C 8,252; Dec 670C 3,695. Event
  window −2 → logged, size flagged; Thursday's run adjudicates against the
  print.
- **AAPL** — reports Thursday. Nov 400C +11,343 to 46,214 (standing), Oct
  calls holding, but two-sided put builds too (Jul-31 320P 11,547, Sep 275P
  11,791). Event −2, logged.
- **GOOGL** — watch, score 2-3 held. Recovery: +2.1% to 326.56, big Jul-31
  call builds (400C to 12,282, 335C to 10,365) AGAINST the standing Sept put
  ladder. The argument continues; earnings −2 expires 08-01.
- **V** reports today AMC — Oct 370C +2,522 sits in the event window, logged.
  **SPGI** reported this morning — Monday's thin prints were pre-earnings,
  logged. **COST** — first items: Feb-27 950P/900P LEAPS puts ($2.39M/$1.57M,
  ~5x) plus Aug 785P builds (~1,100 each) as the stock makes highs at 951.58
  — hedging-into-strength flavor, watch 1-2. **TSM** — protective long-dated
  put family broadening (Jul-31 270P +4,105; Sep 260P +2,946; Oct 280P/350P
  up) while the bullish Aug 465C holds at 4,078 — watch 2. **ISRG** +5.7% to
  356.83, tape quiet; the Jun-27 240P holder is now 33% OTM. **MA** quiet.
  **MCO** stale (noted above).

---

## Running kill list vs. confirmed book (for the edition)
- **Kills:** ACN 22k structure (the big one), ORCL Aug 118P.
- **Confirmed standing:** ORCL crash-protection LEAPS ladder + 110P; GOOGL
  Sept put ladder + Aug-28 285P; AAPL Sep 330P + Nov 400C; TSM 465C + Sep-27
  280P; MSFT Sept/Jul-31 call block; SOLS Aug 80C; NVDA Oct 180C (unexplained).

## Next-run checklist (Wednesday or Thursday morning IST)
1. Wednesday run = pre-MSFT baseline; Thursday morning run = MSFT reaction +
   Fed. Post-AAPL adjudication lands Friday morning IST.
2. ORCL: does the LEAPS put ladder keep growing on strength?
3. ASML 1575P and COST LEAPS puts conversion checks.
4. GOOGL earnings −2 expires 08-01 — rescore then.
5. Edition outline: due now (per plan). Material is ample — five days,
   two kills, a validated adjudication loop, three build fixes, one barbell.

*Research note only — not for publication. Anything drafted from this goes
through COMPLIANCE_FRAMEWORK.md in full.*
