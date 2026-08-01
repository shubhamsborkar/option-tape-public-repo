"""Recent insider filings (Form 4) for the universe, via EDGAR submissions API.

Lists filings from the last 60 days with document URLs. Claude reads the XML of
filings on FLAGGED tickers only (direction, size, 10b5-1 checkbox) — see SKILL.md.
Output: workspace/form4_recent.md
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from config import SEC_UA, UNIVERSE, WORKSPACE, curl_json

LOOKBACK_DAYS = 60


def main():
    cutoff = (datetime.date.today() - datetime.timedelta(days=LOOKBACK_DAYS)).isoformat()
    out = [f"# Form 4 filings since {cutoff} (EDGAR submissions API)",
           "Claude: for flagged tickers, open doc_url to read direction (P/S), size, and the 10b5-1 checkbox.",
           ""]
    for t, (cik, _tier) in UNIVERSE.items():
        try:
            d = curl_json(f"https://data.sec.gov/submissions/CIK{cik}.json", ua=SEC_UA)
        except Exception as e:
            out += [f"## {t}: FETCH FAILED ({e})", ""]
            continue
        recent = d.get("filings", {}).get("recent", {})
        rows = []
        for form, date, acc, doc in zip(recent.get("form", []),
                                        recent.get("filingDate", []),
                                        recent.get("accessionNumber", []),
                                        recent.get("primaryDocument", [])):
            if form == "4" and date >= cutoff:
                acc_nodash = acc.replace("-", "")
                url = (f"https://www.sec.gov/Archives/edgar/data/"
                       f"{int(cik)}/{acc_nodash}/{doc}")
                rows.append((date, acc, url))
        out.append(f"## {t} ({d.get('name', '')}): {len(rows)} Form 4(s)")
        for date, acc, url in rows:
            out.append(f"- {date} | {acc} | {url}")
        out.append("")
    path = os.path.join(WORKSPACE, "form4_recent.md")
    with open(path, "w") as f:
        f.write("\n".join(out))
    print(f"form4 list written: {path}")


if __name__ == "__main__":
    main()
