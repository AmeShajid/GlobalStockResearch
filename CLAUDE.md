# CLAUDE.md — ThreadPulse Project Rules

## Project Summary

ThreadPulse is a personal stock research intelligence system.
- Primary runtime: Windows PC (PostgreSQL, collectors, scheduler, dashboard)
- Secondary dev machine: MacBook Pro (code editing, tests, no production data)
- Private, personal tool (not a public product)
- Does not execute trades
- Does not output buy/sell recommendations
- Organizes Reddit, price, insider, news, earnings, and pattern data

## Before Starting Work

Always read these files in order:
1. This file (CLAUDE.md) — core rules
2. `docs/current_phase.md` — what is in scope right now
3. `backend/CLAUDE.md` OR `frontend/CLAUDE.md` — area-specific standards (when applicable)
4. `docs/blueprint.md` — open the relevant milestone section
5. `docs/decisions.md` — past architectural decisions (skim when relevant)

## Current Build Priority

Build MVP first:
- Milestone 0: Environment setup
- Milestone 1: Reddit data collection
- Milestone 2: Price tracking and market context
- Milestone 7 phases 7.1–7.6 + 7.11–7.13: Basic dashboard

Do not build until MVP is stable: OpenInsider, News, Earnings, Overlap detection, ML.

## The 10 Critical Rules

1. **Never hardcode thresholds** — read from `config/config.yaml`
2. **Never commit credentials** — use `.env` files (in `.gitignore`)
3. **All timestamps in UTC** — local time only in dashboard display
4. **Store raw before processed** — always preserve source data
5. **Data quality over speed** — every source needs validation
6. **No ML until data pipeline is stable** — ML is Milestone 9
7. **No buy/sell language** — research wording only
8. **Beginner-readable code** — explicit over clever
9. **Surgical changes** — only files needed for current task
10. **Explain before coding** — restate, list files, plan, then code

## Required Workflow

For every task:
1. Restate the task
2. List files you expect to touch
3. Explain the implementation plan
4. Make the smallest working change
5. State the test command
6. Self-check (all checklist items below)
7. State confidence level — must be 95%+ to proceed
8. Summarize what changed

**Self-check:**
- [ ] Code runs without errors
- [ ] Tests pass (or N/A explained)
- [ ] Follows project standards (UTC, config, raw data, no secrets)
- [ ] No hardcoded thresholds
- [ ] Error handling exists where appropriate
- [ ] Logging is meaningful
- [ ] Surgical — only files in step 2 touched

**95% confidence rule:**
- "95%+ confident this is complete and correct" → proceed
- "Less than 95%" → list concerns, get approval

## Session Management

- Long session (20+ exchanges)? Suggest `/clear` or new session
- Switching milestones? Start new session
- Claude cannot run `/clear` or `/compact` — only the user can
- New session starts fresh; reference past decisions via `docs/decisions.md`

## Git Discipline

Claude may run only: `git status`, `git diff`, `git log`, `git branch`.
Claude must never run: `git add`, `commit`, `push`, `merge`, `rebase`, `tag`.

When done, end with:
```
DONE.
[One paragraph explaining what was completed.]
Run [test command] to verify. You can review the diff and commit it yourself.
```

## Forbidden Behavior

Do not:
- Rewrite large parts without asking
- Add new technologies without approval
- Create fake/mock APIs in place of real implementations
- Skip validation steps
- Change database schemas silently
- Store timestamps in local time
- Put secrets in code
- Build future milestones early

## Tech Stack

**Primary OS:** Windows 10/11 (production runtime, PostgreSQL host, collectors)
**Secondary OS:** macOS (code editing on the go; no production data here)
**Backend:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL 16, APScheduler, PRAW, yfinance
**Frontend:** Next.js 14, React, Tailwind CSS
**Database:** Local PostgreSQL 16 on the Windows PC (one source of truth)
**Development:** VSCode, GitHub private repo, PowerShell 7 or Git Bash on Windows

## Test Commands

**Backend (Windows, with venv activated):** `python -m pytest`, `python scripts\validate_config.py`
**Frontend:** `npm run lint`, `npm run build`

Path separators in scripts: prefer `pathlib.Path` over string concatenation. Never hardcode `C:\Users\...` — use relative paths or read from config.

## Coding Style

Simple, readable code. Clear names. Comments for non-obvious logic. Small functions. Explicit over compact.

## Subagents (Separate Sessions)

Invoke by name. They live in `.claude/agents/`:

- **code-reviewer** — fresh-eyes review after a phase is complete
- **grill-me** — interrogate plans before building
- **tech-debt-reviewer** — hunt for maintenance problems
- **design-reviewer** — UI/UX screenshot review

Use them. They are short, cheap, and catch real issues.

## Reference Files

**Always:** This file + `docs/current_phase.md`

**On demand:**
- `docs/blueprint.md` — the master spec (read the relevant milestone)
- `docs/decisions.md` — architectural decision log
- `docs/signal_definitions.md` — signal threshold reference
- `docs/mvp_definition.md` — MVP completion criteria
