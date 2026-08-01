"""House congressional periodic transaction reports (PTRs), last 60 days.

Downloads the House Clerk index, caches PTR PDFs, extracts text with pypdf,
greps for universe tickers + company names. Scanned (no-text) PDFs are counted
honestly, never silently dropped. Senate: not covered (site blocks scripts) —
v1 is House-only and every report must say so.
Output: workspace/ptr_matches.md
"""
import datetime
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, os.path.dirname(__file__))
from config import UNIVERSE, WORKSPACE

LOOKBACK_DAYS = 60
# grep needles per ticker: ticker word + distinctive company-name fragment
NEEDLES = {
    "ACN": ["ACN", "Accenture"], "SOLS": ["SOLS", "Solstice Advanced"],
    "LULU": ["LULU", "lululemon", "Lululemon"], "ORCL": ["ORCL", "Oracle"],
    "MSFT": ["MSFT", "Microsoft"], "GOOGL": ["GOOGL", "GOOG", "Alphabet"],
    "AAPL": ["AAPL", "Apple Inc"], "NVDA": ["NVDA", "NVIDIA", "Nvidia"],
    "V": ["Visa"], "MA": ["Mastercard"], "COST": ["COST", "Costco"],
    "ASML": ["ASML"], "TSM": ["TSM", "Taiwan Semiconductor"],
    "MCO": ["MCO", "Moody"], "SPGI": ["SPGI", "S&P Global"],
    "ISRG": ["ISRG", "Intuitive Surgical"],
}


def pdf_text(path):
    try:
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    except Exception:
        return ""


def main():
    year = datetime.date.today().year
    cutoff = datetime.date.today() - datetime.timedelta(days=LOOKBACK_DAYS)
    ptr_dir = os.path.join(WORKSPACE, "ptrs")
    os.makedirs(ptr_dir, exist_ok=True)

    zpath = os.path.join(WORKSPACE, f"{year}FD.zip")
    subprocess.run(["curl", "-s", "--max-time", "60",
                    f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip",
                    "-o", zpath], check=True)
    with zipfile.ZipFile(zpath) as z:
        z.extract(f"{year}FD.xml", WORKSPACE)

    root = ET.parse(os.path.join(WORKSPACE, f"{year}FD.xml")).getroot()
    ptrs = []
    for m in root.findall("Member"):
        if (m.findtext("FilingType") or "") != "P":
            continue
        fd = m.findtext("FilingDate") or ""
        try:
            mm, dd, yy = map(int, fd.split("/"))
            fdate = datetime.date(yy, mm, dd)
        except ValueError:
            continue
        if fdate >= cutoff:
            ptrs.append({
                "docid": m.findtext("DocID"),
                "name": f"{m.findtext('First') or ''} {m.findtext('Last') or ''}".strip(),
                "state": m.findtext("StateDst") or "",
                "date": fdate.isoformat(),
            })

    out = [f"# House PTRs filed since {cutoff.isoformat()} ({len(ptrs)} reports)",
           "Senate NOT covered (efdsearch blocks scripts) — v1 is House-only; say so in any report.",
           "Congressional data lags: trades may be up to 45 days older than the filing date.",
           ""]
    matched, no_text = [], []
    for p in ptrs:
        pdf = os.path.join(ptr_dir, f"{p['docid']}.pdf")
        if not os.path.exists(pdf):
            subprocess.run(["curl", "-s", "--max-time", "60",
                            f"https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{year}/{p['docid']}.pdf",
                            "-o", pdf])
        text = pdf_text(pdf)
        if len(text.strip()) < 50:
            no_text.append(p)
            continue
        hits = sorted({t for t, needles in NEEDLES.items()
                       if any(re.search(rf"\b{re.escape(n)}", text) for n in needles)})
        if hits:
            matched.append((p, hits))

    out.append(f"## Matches on universe tickers: {len(matched)}")
    for p, hits in matched:
        out.append(f"- {p['date']} | {p['name']} ({p['state']}) | tickers: {', '.join(hits)} | "
                   f"PDF: {os.path.join(ptr_dir, p['docid'] + '.pdf')}")
    out.append("")
    out.append(f"## Unparseable (scanned/no text layer): {len(no_text)} of {len(ptrs)}")
    for p in no_text:
        out.append(f"- {p['date']} | {p['name']} ({p['state']}) | DocID {p['docid']} — "
                   "Claude may Read the PDF visually if a flagged ticker warrants it")

    path = os.path.join(WORKSPACE, "ptr_matches.md")
    with open(path, "w") as f:
        f.write("\n".join(out))
    print(f"ptr matches written: {path} ({len(matched)} matched, {len(no_text)} unparseable, {len(ptrs)} total)")


if __name__ == "__main__":
    main()
