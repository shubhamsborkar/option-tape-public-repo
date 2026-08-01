"""Daily chain snapshot: CBOE delayed quotes -> markdown snapshot.

Writes data/snapshots/YYYY-MM-DD.md in this repo where the
date is the trading day of the data (taken from the CBOE api timestamp), NOT
the wall-clock date — running pre-open just re-captures the prior close.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from config import (KEEP_ALL, SNAP_MIN_OI, SNAP_MIN_VOLUME, UNIVERSE,
                    VAULT_REPO, WORKSPACE)


def main():
    chains_dir = os.path.join(WORKSPACE, "chains")
    os.makedirs(chains_dir, exist_ok=True)

    per_ticker = {}
    trade_dates = set()
    for t in UNIVERSE:
        url = f"https://cdn.cboe.com/api/global/delayed_quotes/options/{t}.json"
        raw = os.path.join(chains_dir, f"{t}.json")
        r = subprocess.run(["curl", "-s", "--max-time", "45", url, "-o", raw])
        if r.returncode != 0 or not os.path.exists(raw) or os.path.getsize(raw) < 1000:
            print(f"WARN: fetch failed for {t}, skipping")
            continue
        d = json.load(open(raw))
        per_ticker[t] = d
        for o in d["data"]["options"]:
            lt = o.get("last_trade_time") or ""
            if lt:
                trade_dates.add(lt[:10])

    if not per_ticker:
        sys.exit("FATAL: no chains fetched")

    # Trading date = latest actual trade, NOT the API timestamp (which is a
    # UTC cache time and rolls past midnight while the US market is closed —
    # early-IST runs would otherwise mislabel yesterday's close as today).
    snap_date = max(trade_dates)
    out_path = os.path.join(VAULT_REPO, "data", "snapshots", f"{snap_date}.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    lines = [
        f"# Chain snapshot — {snap_date} close (CBOE delayed quotes)",
        "",
        f"Filter: kept contracts with volume >= {SNAP_MIN_VOLUME} OR "
        f"open_interest >= {SNAP_MIN_OI} ({', '.join(sorted(KEEP_ALL))}: ALL contracts kept — thin chain).",
        "Columns: contract symbol (underlying + expiry YYMMDD + C/P + strike*1000), "
        "volume, open interest, last trade price, bid, ask, last trade time.",
        "",
    ]
    for t in UNIVERSE:
        if t not in per_ticker:
            lines += [f"## {t}  (FETCH FAILED THIS DAY)", ""]
            continue
        d = per_ticker[t]
        data = d["data"]
        opts = data["options"]
        kept = [o for o in opts if t in KEEP_ALL
                or (o.get("volume") or 0) >= SNAP_MIN_VOLUME
                or (o.get("open_interest") or 0) >= SNAP_MIN_OI]
        spot = data.get("close") or data.get("current_price") or ""
        lines.append(f"## {t}  (close: {spot}; contracts total {len(opts)}, "
                     f"kept {len(kept)}; api ts {d.get('timestamp', '')})")
        lines.append("```csv")
        lines.append("contract,volume,oi,last,bid,ask,last_trade_time")
        for o in kept:
            lines.append(f"{o['option']},{int(o.get('volume') or 0)},"
                         f"{int(o.get('open_interest') or 0)},{o.get('last_trade_price', '')},"
                         f"{o.get('bid', '')},{o.get('ask', '')},{o.get('last_trade_time', '')}")
        lines.append("```")
        lines.append("")

    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"snapshot written: {out_path} ({round(os.path.getsize(out_path)/1024)} KB, "
          f"{len(per_ticker)}/{len(UNIVERSE)} tickers)")


if __name__ == "__main__":
    main()
