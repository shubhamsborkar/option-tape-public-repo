# The disagreement detector — an options tape for long term investors

A Claude Code workflow that reads US options positioning (free Cboe delayed
data), insider Form 4 filings (SEC EDGAR), and House congressional trade
disclosures as a thesis-surveillance instrument. It answers one question,
daily: **is the options market disagreeing with me about a business I own?**

Built and run live for the Alpha with AI proof-of-work edition. Every dated
report in `outputs/` is a real run from the build, wrong turns included.

## What is here

- `skill/SKILL.md` — the instruction file Claude Code follows on "run the tape"
- `scripts/` — five small programs: config, daily snapshot, scan, insider
  fetch, congressional fetch
- `process/methodology.md` — every signal, threshold, scoring rule, and
  limitation, stated plainly
- `data/scan-log.md` — the append-only ledger of every run, quiet ones included
- `data/snapshots/` — the raw daily chain snapshots from the live run, so any
  number in any report can be traced to the exact contract row it came from
- `outputs/` — the dated disagreement reports from the live two-week run

Snapshots cannot be backfilled: your own archive starts the day you run the
snapshot script for the first time, so start early.

## Run it on the stocks you own

1. Put your own name and email in `scripts/config.py` (SEC EDGAR requires a
   real contact in the User-Agent).
2. Edit `UNIVERSE` in `scripts/config.py` to the names you actually own or
   genuinely follow. Ten to twenty works well.
3. Install the skill for Claude Code (copy `skill/SKILL.md` and `scripts/`
   into a `~/.claude/skills/options-tape/` folder), or simply open this repo
   in Claude Code and ask it to follow SKILL.md.
4. Say "run the tape" once a day after the US close. The next day's run
   adjudicates today's candidates against the open interest that settled
   overnight.

## What it is not

Not a trade-idea generator. It never recommends buying, selling, or holding
anything. Flagged names are questions to investigate about businesses you
already know. Most days the honest output is: quiet. Quiet is a finding.
