"""Shared config for the options-tape disagreement detector.

Edit UNIVERSE below to the names YOU own or genuinely follow (10-20 works well).
Tier 1 = your core names: every daily report gives them a status line even when
quiet. Tier 2 = your wider bench of businesses you would want to own someday.
"""
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_REPO = REPO_ROOT                      # snapshots + reports live in this repo
WORKSPACE = os.path.join(REPO_ROOT, "workspace")

# SEC EDGAR requires a real contact in the User-Agent. Put YOUR name and email.
SEC_UA = "YOUR NAME your.email@example.com"

# ticker -> (cik 10-digit, tier)
UNIVERSE = {
    "ACN":  ("0001467373", 1),
    "SOLS": ("0002064953", 1),
    "LULU": ("0001397187", 1),
    "ORCL": ("0001341439", 1),
    "MSFT": ("0000789019", 2),
    "GOOGL": ("0001652044", 2),
    "AAPL": ("0000320193", 2),
    "NVDA": ("0001045810", 2),
    "V":    ("0001403161", 2),
    "MA":   ("0001141391", 2),
    "COST": ("0000909832", 2),
    "ASML": ("0000937966", 2),
    "TSM":  ("0001046179", 2),
    "MCO":  ("0001059556", 2),
    "SPGI": ("0000064040", 2),
    "ISRG": ("0001035267", 2),
}

# Chains with total OI under this are "thin" — lower signal thresholds apply
THIN_CHAIN_TOTAL_OI = 50_000

# Snapshot keep-filter (documented in every snapshot file header)
SNAP_MIN_VOLUME = 25
SNAP_MIN_OI = 100
KEEP_ALL = {"SOLS"}  # thin chains keep every contract

# Scan thresholds (independent design — rationale in repo process/methodology.md)
NEWPOS_VOLOI_RATIO = 2.5      # volume >= 2.5x max(OI,1) => opening, not managing
NEWPOS_MIN_VOL = 250          # liquid names: minimum contracts traded
NEWPOS_MIN_PREMIUM = 200_000  # liquid names: volume * last * 100 floor ($)
THIN_MIN_VOL = 50             # thin chains
THIN_MIN_PREMIUM = 50_000     # thin chains
NEAR_EXPIRY_DTE = 3           # <=3 DTE flagged as likely roll/expiry mechanics


def curl_json(url, ua=None):
    """Fetch JSON via curl subprocess (this Mac's python3 lacks SSL certs)."""
    import json as _json
    import subprocess
    cmd = ["curl", "-s", "--max-time", "45", url]
    if ua:
        cmd = ["curl", "-s", "--max-time", "45", "-H", f"User-Agent: {ua}", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"curl failed for {url}: rc={r.returncode}")
    return _json.loads(r.stdout)


def parse_contract(sym):
    """AAPL260918C00325000 -> (underlying, date(2026,9,18), 'C', 325.0)."""
    import datetime
    body = sym[-15:]
    underlying = sym[:-15]
    yy, mm, dd = int(body[0:2]), int(body[2:4]), int(body[4:6])
    cp = body[6]
    strike = int(body[7:]) / 1000.0
    return underlying, datetime.date(2000 + yy, mm, dd), cp, strike
