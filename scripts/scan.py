"""Scan the snapshot history for positioning anomalies.

Deterministic layer only: computes candidates and aggregates. The judgment
layer (exclusions, cross-referencing, scoring, the report) is Claude's job —
see SKILL.md. Output: workspace/scan_candidates.md
"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from config import (NEAR_EXPIRY_DTE, NEWPOS_MIN_PREMIUM, NEWPOS_MIN_VOL,
                    NEWPOS_VOLOI_RATIO, THIN_CHAIN_TOTAL_OI, THIN_MIN_PREMIUM,
                    THIN_MIN_VOL, UNIVERSE, VAULT_REPO, WORKSPACE,
                    parse_contract)

SNAP_DIR = os.path.join(VAULT_REPO, "data", "snapshots")


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
                close = float(h.group(2)) if h.group(2) else None
                snaps[date][ticker] = {"close": close, "contracts": {}}
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
                        "last": float(p[3]) if p[3] else 0.0,
                    }
                except ValueError:
                    continue
    return snaps


def main():
    snaps = load_snapshots()
    if not snaps:
        sys.exit("FATAL: no snapshots found — run take_snapshot.py first")
    dates = sorted(snaps)
    latest = dates[-1]
    today = datetime.date(*map(int, latest.split("-")))

    out = [f"# Scan candidates — data through {latest} close",
           f"Snapshots available: {len(dates)} ({dates[0]} … {latest})",
           "Deterministic output only. Judgment layer (exclusions, cross-refs, scoring) happens in SKILL.md.",
           ""]

    for t in UNIVERSE:
        cur = snaps[latest].get(t)
        if not cur or not cur["contracts"]:
            out += [f"## {t}: NO DATA in latest snapshot", ""]
            continue
        contracts = cur["contracts"]
        total_oi = sum(c["oi"] for c in contracts.values())
        thin = total_oi < THIN_CHAIN_TOTAL_OI
        min_vol = THIN_MIN_VOL if thin else NEWPOS_MIN_VOL
        min_prem = THIN_MIN_PREMIUM if thin else NEWPOS_MIN_PREMIUM

        # --- ticker-level aggregates across all snapshot days
        out.append(f"## {t}  (close {cur['close']}, total OI {total_oi:,}"
                   f"{', THIN chain' if thin else ''})")
        out.append("Daily aggregates (P/C by volume, P/C by OI, put prem proxy $, call prem proxy $):")
        out.append("```csv")
        out.append("date,close,pc_vol,pc_oi,put_prem,call_prem")
        for d in dates:
            tc = snaps[d].get(t)
            if not tc:
                continue
            cv = pv = coi = poi = cprem = pprem = 0
            for sym, row in tc["contracts"].items():
                _, _, cp, _ = parse_contract(sym)
                prem = row["vol"] * row["last"] * 100
                if cp == "C":
                    cv += row["vol"]; coi += row["oi"]; cprem += prem
                else:
                    pv += row["vol"]; poi += row["oi"]; pprem += prem
            pc_vol = round(pv / cv, 2) if cv else ""
            pc_oi = round(poi / coi, 2) if coi else ""
            out.append(f"{d},{tc['close']},{pc_vol},{pc_oi},{int(pprem)},{int(cprem)}")
        out.append("```")

        # --- new-position candidates (latest day)
        cands = []
        for sym, row in contracts.items():
            ratio = row["vol"] / max(row["oi"], 1)
            prem = row["vol"] * row["last"] * 100
            if ratio >= NEWPOS_VOLOI_RATIO and row["vol"] >= min_vol and prem >= min_prem:
                _, exp, cp, strike = parse_contract(sym)
                dte = (exp - today).days
                cands.append((prem, sym, cp, strike, exp, dte, row, ratio))
        if cands:
            out.append("NEW-POSITION candidates (vol >= "
                       f"{NEWPOS_VOLOI_RATIO}x OI, vol >= {min_vol}, premium proxy >= ${min_prem:,}):")
            out.append("```csv")
            out.append("contract,type,strike,expiry,dte,vol,oi,vol_oi_ratio,last,prem_proxy,flags")
            for prem, sym, cp, strike, exp, dte, row, ratio in sorted(cands, reverse=True):
                flags = []
                if dte <= NEAR_EXPIRY_DTE:
                    flags.append("ROLL_RISK")
                # deep ITM at ~intrinsic price = synthetic-stock / conversion /
                # dividend mechanics, not directional information
                if cur["close"] and ((cp == "C" and strike < cur["close"] * 0.93)
                                     or (cp == "P" and strike > cur["close"] * 1.07)):
                    flags.append("DEEP_ITM")
                out.append(f"{sym},{cp},{strike},{exp},{dte},{row['vol']},{row['oi']},"
                           f"{round(ratio, 1)},{row['last']},{int(prem)},"
                           f"{'|'.join(flags)}")
            out.append("```")
        else:
            out.append("NEW-POSITION candidates: none today.")

        # --- OI persistence (needs >= 2 snapshots)
        if len(dates) >= 2:
            builds = []
            for sym, row in contracts.items():
                hist = [snaps[d][t]["contracts"].get(sym, {}).get("oi")
                        for d in dates if t in snaps[d]]
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
                        builds.append((growth, sym, cp, strike, exp, streak, hist))
            if builds:
                out.append(f"OI BUILDS (rising >= 2 consecutive snapshots, growth >= {'100 (thin)' if thin else '1,000'}):")
                out.append("```csv")
                out.append("contract,type,strike,expiry,streak_days,oi_path")
                for growth, sym, cp, strike, exp, streak, hist in sorted(builds, reverse=True)[:15]:
                    out.append(f"{sym},{cp},{strike},{exp},{streak},{'->'.join(map(str, hist))}")
                out.append("```")
            else:
                out.append("OI BUILDS: none meeting thresholds.")
        else:
            out.append(f"OI BUILDS: unavailable — only {len(dates)} snapshot(s); "
                       "persistence signals activate as daily history accumulates.")
        out.append("")

    path = os.path.join(WORKSPACE, "scan_candidates.md")
    with open(path, "w") as f:
        f.write("\n".join(out))
    print(f"scan written: {path} ({round(os.path.getsize(path)/1024)} KB)")


if __name__ == "__main__":
    main()
