"""Evaluate logged flags against the rule written down before looking.

The rule lives in process/evaluation-plan.md and is not changed after results
come in. In short:
- Horizons: 20 snapshot days (primary), 5 and 60 (secondary), counted in
  trading days on file, from the flag-day close.
- Primary outcome: the absolute move in the underlying. Direction is not
  assumed, because end-of-day data cannot say which side opened a position.
- Evaluated set: clean flags only (see is_clean).
- Control: the same ticker on days with no clean flag, in the same
  earnings bucket (within the earnings window or not) and the same volatility
  regime (tercile of the ticker's own trailing 20-day realised volatility).
- Flags and controls are reported separately for earnings and non-earnings.
- No verdict below MIN_RESOLVED resolved flags in a bucket.

Output: workspace/evaluation.md
"""
import csv
import datetime
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(__file__))
from config import EARNINGS_WINDOW_DAYS, UNIVERSE, VAULT_REPO, WORKSPACE
from scan import LEDGER_FILE, load_events, load_snapshots

HORIZONS = (5, 20, 60)
PRIMARY = 20
MIN_RESOLVED = 100
VOL_LOOKBACK = 20


def closes_by_ticker(snaps):
    dates = sorted(snaps)
    return dates, {t: [snaps[d].get(t, {}).get("close") for d in dates] for t in UNIVERSE}


def fwd_return(series, i, h):
    if i + h >= len(series) or not series[i] or not series[i + h]:
        return None
    return series[i + h] / series[i] - 1


def trailing_vol(series, i):
    if i < VOL_LOOKBACK:
        return None
    rets = []
    for k in range(i - VOL_LOOKBACK + 1, i + 1):
        a, b = series[k - 1], series[k]
        if a and b:
            rets.append(math.log(b / a))
    return statistics.pstdev(rets) if len(rets) >= VOL_LOOKBACK - 2 else None


def is_clean(f):
    """The evaluated set: flags whose footprint is not already explained by
    mechanics or weak data. Everything else stays in the ledger for reading,
    but is not scored."""
    tags, quality = f["tags"], f["quality_flags"]
    return (not quality and f["dte_bucket"] != "0-7"
            and not any(x in tags for x in ("NEAR_EXPIRY", "DEEP_ITM",
                                             "PROBABLE_MULTI_LEG", "ADJUSTED_CONTRACT")))


def main():
    if not os.path.exists(LEDGER_FILE):
        sys.exit("No flag ledger yet: run scan.py --all first")
    snaps = load_snapshots()
    dates, closes = closes_by_ticker(snaps)
    idx = {d: i for i, d in enumerate(dates)}
    events = load_events()
    earn = {}
    for t, d, ev in events:
        if ev == "earnings":
            earn.setdefault(t, []).append(d)


    def earnings_bucket(t, dstr):
        if t not in earn:
            return "unchecked"
        d = datetime.date(*map(int, dstr.split("-")))
        near = any(abs((e - d).days) <= EARNINGS_WINDOW_DAYS for e in earn[t])
        return "earnings" if near else "non_earnings"

    vols = {t: [trailing_vol(closes[t], k) for k in range(len(dates))] for t in UNIVERSE}
    cuts = {}
    for t, vs in vols.items():
        known = [x for x in vs if x is not None]
        cuts[t] = statistics.quantiles(known, n=3) if len(known) >= 3 else None

    def vol_regime(t, i):
        v = vols[t][i]
        if v is None or cuts[t] is None:
            return "unknown"
        lo, hi = cuts[t]
        return "low" if v <= lo else "high" if v > hi else "mid"

    all_flags = list(csv.DictReader(open(LEDGER_FILE)))
    flags = [f for f in all_flags if is_clean(f)]
    flagged_days = {(f["ticker"], f["flag_date"]) for f in flags}

    # One observation per flagged ticker-day (several contracts on the same
    # day share one underlying outcome and must not be counted as many).
    obs = {}
    for f in flags:
        key = (f["ticker"], f["flag_date"])
        if key in obs or f["flag_date"] not in idx:
            continue
        i = idx[f["flag_date"]]
        obs[key] = {"eb": earnings_bucket(*key), "vr": vol_regime(f["ticker"], i),
                    "r": {h: fwd_return(closes[f["ticker"]], i, h) for h in HORIZONS}}

    controls = {}
    for t in UNIVERSE:
        for d, i in idx.items():
            if (t, d) in flagged_days:
                continue
            controls[(t, d)] = {"eb": earnings_bucket(t, d), "vr": vol_regime(t, i),
                                "r": {h: fwd_return(closes[t], i, h) for h in HORIZONS}}

    out = ["# Flag evaluation", "",
           f"Snapshots on file: {len(dates)} ({dates[0]} to {dates[-1]}). "
           f"Flag rows in ledger: {len(all_flags)}, of which clean (evaluated): {len(flags)}. "
           f"Clean flagged ticker-days: {len(obs)}.",
           f"Rule: process/evaluation-plan.md. Primary horizon {PRIMARY} trading days, "
           f"outcome = absolute underlying move, no verdict below {MIN_RESOLVED} resolved, "
           "non-overlapping flagged ticker-days per bucket.", ""]
    unchecked = sum(1 for o in obs.values() if o["eb"] == "unchecked")
    if unchecked:
        out += [f"{unchecked} flagged ticker-days have no earnings dates on file (data/events.csv), "
                "so they are not evaluated: the plan keeps earnings and non-earnings apart.", ""]
    for eb in ("earnings", "non_earnings"):
        out.append(f"## Bucket: {eb}")
        out.append("| horizon | flagged resolved | flagged median abs move | "
                   "matched controls | control median abs move | verdict |")
        out.append("|---|---|---|---|---|---|")
        for h in HORIZONS:
            # Non-overlapping: per ticker, a flag counts only if its window
            # starts after the previous counted flag's window has ended.
            fa, cset = [], set()
            last_i = {}
            for (t, d), o in sorted(obs.items(), key=lambda kv: kv[0][1]):
                if o["eb"] != eb or o["r"][h] is None:
                    continue
                i = idx[d]
                if t in last_i and i - last_i[t] < h:
                    continue
                last_i[t] = i
                fa.append(abs(o["r"][h]))
                for (ct, cd), c in controls.items():
                    if ct == t and c["eb"] == eb and c["vr"] == o["vr"] and c["r"][h] is not None:
                        cset.add((ct, cd))
            ca = [abs(controls[k]["r"][h]) for k in cset]
            fm = f"{statistics.median(fa):.2%}" if fa else "n/a"
            cm = f"{statistics.median(ca):.2%}" if ca else "n/a"
            if len(fa) < MIN_RESOLVED:
                verdict = f"INSUFFICIENT DATA ({len(fa)}/{MIN_RESOLVED})"
            else:
                verdict = ("flags moved more than controls" if statistics.median(fa) > statistics.median(ca)
                           else "no difference from controls")
            out.append(f"| {h}d{' (primary)' if h == PRIMARY else ''} | {len(fa)} | {fm} | "
                       f"{len(ca)} | {cm} | {verdict} |")
        out.append("")
    os.makedirs(WORKSPACE, exist_ok=True)
    path = os.path.join(WORKSPACE, "evaluation.md")
    open(path, "w").write("\n".join(out))
    print(f"evaluation written: {path}")


if __name__ == "__main__":
    main()
