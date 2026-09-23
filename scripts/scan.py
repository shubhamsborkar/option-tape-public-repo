"""Scan the snapshot history for persistent series-level positioning anomalies.

Deterministic layer only: computes candidates, data-quality flags and context
tags. The judgment layer (reading the tags, cross-referencing, the report) is
Claude's job, see SKILL.md.

What end-of-day data can and cannot say (read process/methodology.md):
- Volume is gross activity. Open interest is a net count of contracts still
  open. Unchanged OI does not prove the volume was day trading (one trader can
  close while another opens), and rising OI does not say who opened the
  position or which side they are on.
- Put volume is not automatically bearish and call volume is not automatically
  bullish: sold puts, covered calls, spreads, calendars, collars, rolls and
  conversions leave similar end-of-day footprints.
So the output is a list of anomalies to research, never a verdict on direction.

Usage:
  python3 scan.py          scan the latest snapshot, append its flags to the ledger
  python3 scan.py --all    rebuild the flag ledger from every snapshot on file

Outputs: workspace/scan_candidates.md, data/flag-ledger.csv
"""
import csv
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from config import (EARNINGS_WINDOW_DAYS, MULTI_LEG_VOL_TOLERANCE,
                    NEAR_EXPIRY_DTE, NEWPOS_MIN_PREMIUM, NEWPOS_MIN_VOL,
                    NEWPOS_VOLOI_RATIO, THIN_CHAIN_TOTAL_OI, THIN_MIN_PREMIUM,
                    THIN_MIN_VOL, UNIVERSE, VAULT_REPO, WIDE_SPREAD_PCT,
                    WORKSPACE, parse_contract)

SNAP_DIR = os.path.join(VAULT_REPO, "data", "snapshots")
EVENTS_FILE = os.path.join(VAULT_REPO, "data", "events.csv")
LEDGER_FILE = os.path.join(VAULT_REPO, "data", "flag-ledger.csv")
LEDGER_COLS = ["flag_date", "ticker", "contract", "kind", "type", "strike",
               "expiry", "dte", "dte_bucket", "moneyness", "moneyness_bucket",
               "vol", "oi", "prem_last", "prem_mid", "close", "quality_flags",
               "tags"]


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_snapshots():
    """{date: {ticker: {'close': float|None, 'contracts': {sym: row}}}}"""
    snaps = {}
    for fn in sorted(os.listdir(SNAP_DIR)):
        m = re.match(r"(\d{4}-\d{2}-\d{2})\.md$", fn)
        if not m:
            continue
        date = m.group(1)
        snaps[date] = {}
        ticker, in_csv = None, False
        for line in open(os.path.join(SNAP_DIR, fn)):
            line = line.rstrip("\n")
            h = re.match(r"## (\w+)\s+\(close: ([\d.]*)", line)
            if h:
                ticker = h.group(1)
                snaps[date][ticker] = {"close": fnum(h.group(2)), "contracts": {}}
                continue
            if line.startswith("```csv"):
                in_csv = True
                continue
            if line.startswith("```"):
                in_csv = False
                continue
            if in_csv and ticker and not line.startswith("contract,"):
                p = line.split(",")
                if len(p) < 7:
                    continue
                try:
                    snaps[date][ticker]["contracts"][p[0]] = {
                        "vol": int(p[1]), "oi": int(p[2]),
                        "last": fnum(p[3]) or 0.0,
                        "bid": fnum(p[4]), "ask": fnum(p[5]),
                        "last_time": p[6],
                    }
                except ValueError:
                    continue
    return snaps


def load_events():
    """data/events.csv: ticker,date,event,source. Filled in by the judgment
    layer from a named source (earnings, ex_dividend, corporate_action,
    index_rebalance, hard_to_borrow). Never guessed."""
    events = []
    if os.path.exists(EVENTS_FILE):
        for r in csv.DictReader(open(EVENTS_FILE)):
            try:
                d = datetime.date(*map(int, r["date"].split("-")))
            except (KeyError, ValueError):
                continue
            events.append((r["ticker"].strip().upper(), d, r["event"].strip()))
    return events


def third_friday(y, m):
    d = datetime.date(y, m, 15)
    return d + datetime.timedelta(days=(4 - d.weekday()) % 7)


def expiry_cycle(exp):
    if exp == third_friday(exp.year, exp.month):
        return "QUARTERLY_EXPIRY" if exp.month in (3, 6, 9, 12) else "MONTHLY_EXPIRY"
    return "WEEKLY_EXPIRY"


def dte_bucket(dte):
    return "0-7" if dte <= 7 else "8-30" if dte <= 30 else "31-90" if dte <= 90 else "91+"


def moneyness(cp, strike, close):
    """Signed distance out of the money: + means OTM, - means ITM."""
    if not close:
        return None
    return round((strike / close - 1) if cp == "C" else (1 - strike / close), 3)


def moneyness_bucket(m):
    if m is None:
        return "unknown"
    if abs(m) < 0.05:
        return "ATM"
    if m > 0:
        return "OTM_5-15" if m < 0.15 else "OTM_15+"
    return "ITM_5-15" if m > -0.15 else "ITM_15+"


def premium_and_quality(row, snap_date):
    """Two premium estimates plus flags on how far to trust them.

    Free end-of-day data has no VWAP and no trade tape, so both numbers are
    proxies. prem_last uses the last trade, which can be stale or unrelated to
    most of the day's volume. prem_mid uses the closing bid-ask midpoint, which
    is also not the price the volume traded at. The flags say when either is
    weak."""
    vol, last, bid, ask = row["vol"], row["last"], row["bid"], row["ask"]
    prem_last = vol * last * 100
    flags = []
    mid = None
    if bid is None or ask is None or ask <= 0:
        flags.append("NO_QUOTE")
    else:
        mid = (bid + ask) / 2
        if bid <= 0 or (mid > 0 and (ask - bid) / mid > WIDE_SPREAD_PCT):
            flags.append("WIDE_MARKET")
        if last and (last < bid - 0.01 or last > ask + 0.01):
            flags.append("LAST_OUTSIDE_QUOTE")
    if not row["last_time"].startswith(snap_date):
        flags.append("STALE_LAST")
    prem_mid = vol * mid * 100 if mid else None
    return prem_last, prem_mid, flags


def context_tags(t, sym, cp, strike, exp, dte, close, today, contracts, row, events):
    tags = []
    underlying = sym[:-15]
    if underlying != t:
        tags.append("ADJUSTED_CONTRACT")        # non-standard root after a corporate action
    if dte <= NEAR_EXPIRY_DTE:
        tags.append("NEAR_EXPIRY")
    tags.append(expiry_cycle(exp))
    if third_friday(today.year, today.month) - today in [datetime.timedelta(days=i) for i in range(0, 5)]:
        tags.append("OPEX_WEEK")
    if close and ((cp == "C" and strike < close * 0.93) or (cp == "P" and strike > close * 1.07)):
        tags.append("DEEP_ITM")                 # conversions, dividend and early-exercise mechanics
    # Probable multi-leg: other series on the same name, same day, with
    # near-identical volume at a different strike or expiry.
    legs = 0
    for s2, r2 in contracts.items():
        if s2 == sym or r2["vol"] < 50:
            continue
        if abs(r2["vol"] - row["vol"]) <= MULTI_LEG_VOL_TOLERANCE * row["vol"]:
            legs += 1
    if legs:
        tags.append(f"PROBABLE_MULTI_LEG({legs + 1})")
    # Dated events from data/events.csv (sourced by the judgment layer).
    for et, ed, ev in events:
        if et != t:
            continue
        gap = (ed - today).days
        if ev == "earnings" and -EARNINGS_WINDOW_DAYS <= gap <= EARNINGS_WINDOW_DAYS:
            tags.append(f"EARNINGS({gap:+d}d)")
        elif ev == "ex_dividend" and 0 <= gap <= 10:
            tags.append(f"EX_DIVIDEND({gap:+d}d)")
        elif ev in ("corporate_action", "index_rebalance") and -5 <= gap <= 10:
            tags.append(f"{ev.upper()}({gap:+d}d)")
        elif ev == "hard_to_borrow" and gap == 0:
            tags.append("HARD_TO_BORROW")
    if not any(ev == "earnings" for et, _, ev in events if et == t):
        tags.append("EARNINGS_DATE_UNCHECKED")
    return tags


def scan_day(snaps, dates, latest, events, out, ledger_rows):
    today = datetime.date(*map(int, latest.split("-")))
    hist_dates = [d for d in dates if d <= latest]
    for t in UNIVERSE:
        cur = snaps[latest].get(t)
        if not cur or not cur["contracts"]:
            out += [f"## {t}: NO DATA in latest snapshot", ""]
            continue
        contracts = cur["contracts"]
        close = cur["close"]
        total_oi = sum(c["oi"] for c in contracts.values())
        thin = total_oi < THIN_CHAIN_TOTAL_OI
        min_vol = THIN_MIN_VOL if thin else NEWPOS_MIN_VOL
        min_prem = THIN_MIN_PREMIUM if thin else NEWPOS_MIN_PREMIUM

        out.append(f"## {t}  (close {close}, total OI {total_oi:,}"
                   f"{', THIN chain' if thin else ''})")
        out.append("Daily aggregates. Put/call ratios describe activity, not direction.")
        out.append("```csv")
        out.append("date,close,pc_vol,pc_oi,put_prem_mid,call_prem_mid")
        for d in hist_dates:
            tc = snaps[d].get(t)
            if not tc:
                continue
            cv = pv = coi = poi = cprem = pprem = 0
            for sym, row in tc["contracts"].items():
                _, _, cp, _ = parse_contract(sym)
                _, pm, _ = premium_and_quality(row, d)
                pm = pm or 0
                if cp == "C":
                    cv += row["vol"]; coi += row["oi"]; cprem += pm
                else:
                    pv += row["vol"]; poi += row["oi"]; pprem += pm
            pc_vol = round(pv / cv, 2) if cv else ""
            pc_oi = round(poi / coi, 2) if coi else ""
            out.append(f"{d},{tc['close']},{pc_vol},{pc_oi},{int(pprem)},{int(cprem)}")
        out.append("```")

        # --- unusual-volume candidates (volume far above existing OI)
        cands = []
        for sym, row in contracts.items():
            ratio = row["vol"] / max(row["oi"], 1)
            prem_last, prem_mid, qflags = premium_and_quality(row, latest)
            prem_gate = prem_mid if prem_mid is not None else prem_last
            if ratio >= NEWPOS_VOLOI_RATIO and row["vol"] >= min_vol and prem_gate >= min_prem:
                _, exp, cp, strike = parse_contract(sym)
                dte = (exp - today).days
                tags = context_tags(t, sym, cp, strike, exp, dte, close, today,
                                    contracts, row, events)
                cands.append((prem_gate, sym, cp, strike, exp, dte, row, ratio,
                              prem_last, prem_mid, qflags, tags))
        if cands:
            out.append(f"UNUSUAL-VOLUME candidates (vol >= {NEWPOS_VOLOI_RATIO}x OI, "
                       f"vol >= {min_vol}, premium >= ${min_prem:,}):")
            out.append("```csv")
            out.append("contract,type,strike,expiry,dte,vol,oi,vol_oi_ratio,last,bid,ask,"
                       "prem_last,prem_mid,quality_flags,tags")
            for c in sorted(cands, key=lambda c: c[0], reverse=True):
                _, sym, cp, strike, exp, dte, row, ratio, pl, pmid, qf, tags = c
                out.append(f"{sym},{cp},{strike},{exp},{dte},{row['vol']},{row['oi']},"
                           f"{round(ratio, 1)},{row['last']},{row['bid']},{row['ask']},"
                           f"{int(pl)},{int(pmid) if pmid is not None else ''},"
                           f"{'|'.join(qf)},{'|'.join(tags)}")
                ledger_rows.append(ledger_row(latest, t, sym, "unusual_volume", cp, strike,
                                              exp, dte, close, row, pl, pmid, qf, tags))
            out.append("```")
        else:
            out.append("UNUSUAL-VOLUME candidates: none today.")

        # --- OI persistence: net open contracts rising over consecutive snapshots
        if len(hist_dates) >= 2:
            builds = []
            for sym, row in contracts.items():
                hist = [snaps[d][t]["contracts"].get(sym, {}).get("oi")
                        for d in hist_dates if t in snaps[d]]
                hist = [h for h in hist if h is not None]
                if len(hist) >= 2 and hist[-1] > hist[0]:
                    streak = 1
                    for a, b in zip(hist[-2::-1], hist[::-1]):
                        if b > a:
                            streak += 1
                        else:
                            break
                    growth = hist[-1] - hist[0]
                    if streak >= 2 and growth >= (100 if thin else 1000):
                        _, exp, cp, strike = parse_contract(sym)
                        builds.append((growth, sym, cp, strike, exp, streak, hist, row))
            if builds:
                out.append("OI BUILDS (net open contracts rising >= 2 consecutive snapshots, "
                           f"growth >= {'100 (thin)' if thin else '1,000'}). Rising OI says more "
                           "contracts are open; it does not say who opened them or which side they hold:")
                out.append("```csv")
                out.append("contract,type,strike,expiry,streak_days,oi_path,quality_flags,tags")
                for growth, sym, cp, strike, exp, streak, hist, row in sorted(
                        builds, key=lambda b: b[0], reverse=True)[:15]:
                    dte = (exp - today).days
                    pl, pmid, qf = premium_and_quality(row, latest)
                    tags = context_tags(t, sym, cp, strike, exp, dte, close, today,
                                        contracts, row, events)
                    out.append(f"{sym},{cp},{strike},{exp},{streak},{'->'.join(map(str, hist[-8:]))},"
                               f"{'|'.join(qf)},{'|'.join(tags)}")
                    if streak == 3:   # logged once, on the day the build first qualifies
                        ledger_rows.append(ledger_row(latest, t, sym, "oi_build", cp,
                                                      strike, exp, dte, close, row, pl, pmid, qf, tags))
                out.append("```")
            else:
                out.append("OI BUILDS: none meeting thresholds.")
        else:
            out.append(f"OI BUILDS: unavailable, only {len(hist_dates)} snapshot(s).")
        out.append("")


def ledger_row(date, t, sym, kind, cp, strike, exp, dte, close, row, pl, pmid, qf, tags):
    m = moneyness(cp, strike, close)
    return {"flag_date": date, "ticker": t, "contract": sym, "kind": kind, "type": cp,
            "strike": strike, "expiry": exp.isoformat(), "dte": dte,
            "dte_bucket": dte_bucket(dte), "moneyness": m if m is not None else "",
            "moneyness_bucket": moneyness_bucket(m), "vol": row["vol"], "oi": row["oi"],
            "prem_last": int(pl), "prem_mid": int(pmid) if pmid is not None else "",
            "close": close, "quality_flags": "|".join(qf), "tags": "|".join(tags)}


def write_ledger(rows, rebuild):
    existing = []
    if not rebuild and os.path.exists(LEDGER_FILE):
        existing = list(csv.DictReader(open(LEDGER_FILE)))
    new_dates = {r["flag_date"] for r in rows}
    kept = [r for r in existing if r["flag_date"] not in new_dates]
    allrows = sorted(kept + rows, key=lambda r: (r["flag_date"], r["ticker"], r["contract"], r["kind"]))
    with open(LEDGER_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS)
        w.writeheader()
        w.writerows(allrows)
    return len(allrows)


def main():
    rebuild = "--all" in sys.argv
    snaps = load_snapshots()
    if not snaps:
        sys.exit("FATAL: no snapshots found, run take_snapshot.py first")
    dates = sorted(snaps)
    events = load_events()
    ledger_rows = []
    latest = dates[-1]
    out = [f"# Scan candidates, data through {latest} close",
           f"Snapshots available: {len(dates)} ({dates[0]} to {latest})",
           "Deterministic output only. Tags describe context, they do not discard anything. "
           "Judgment layer happens in SKILL.md.",
           ""]
    for d in (dates if rebuild else [latest]):
        day_out = []
        scan_day(snaps, dates, d, events, day_out, ledger_rows)
        if d == latest:
            out += day_out
    os.makedirs(WORKSPACE, exist_ok=True)
    path = os.path.join(WORKSPACE, "scan_candidates.md")
    with open(path, "w") as f:
        f.write("\n".join(out))
    n = write_ledger(ledger_rows, rebuild)
    print(f"scan written: {path} ({round(os.path.getsize(path)/1024)} KB); "
          f"flag ledger: {n} rows in {LEDGER_FILE}")


if __name__ == "__main__":
    main()
