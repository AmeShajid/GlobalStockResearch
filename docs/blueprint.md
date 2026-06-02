# ThreadPulse — Personal Stock Research Intelligence System
## The Master Blueprint v4.0 — Foundations + Full Project Specification
### Windows-Primary Edition with Mac as Secondary Dev Machine
### For Claude Code v2.1.147 + Claude Max + Opus 4.7

---

# HOW TO USE THIS DOCUMENT

This blueprint has three parts. They are read in different ways and for different reasons.

**Part 1 — The Operating System.** Set up *once*. This is the meta-layer that makes every coding session more effective: project rules, file architecture, subagents, workflow, quality gates, and how to extract maximum value from Claude Max. Read this end-to-end before you touch any code. After that, you almost never reread it — but Claude does, every session.

**Part 2 — The Project Blueprint.** What you are actually building. This is ThreadPulse: vision, principles, tech stack, signal definitions, MVP, and eleven milestones from environment setup through ML maintenance. You read the section for whichever milestone you are currently in. Claude reads it on demand when working on that milestone.

**Part 3 — Appendices.** Ready-to-drop-in files. Copy these into your repository and you have a complete working operating system without writing any boilerplate. Includes `CLAUDE.md`, four subagent definitions, `current_phase.md` starter, `decisions.md` template, and `.gitignore`.

> **Reading order for day one:** Part 1 in full → Part 2 sections 2.1 through 2.6 (vision, principles, stack, signals, MVP) → Part 2 section 2.7 (Milestone 0) → Part 3 (copy files into the repo). After that, you start Phase 0.1 and only revisit other parts as you advance.

---
---

# PART 1 — THE OPERATING SYSTEM

*The infrastructure that makes every coding session sharper. Set up once, benefit forever.*

> **Dual-machine note.** This project is built and run on your Windows PC as the primary machine — that is where PostgreSQL lives, where APScheduler runs every 30 minutes, and where the collectors operate 24/7. Your MacBook Pro is a *secondary* development machine — you use it for editing code, reading documentation, running tests against a local test database, and pushing to GitHub when you are away from the Windows PC. You do **not** run two independent ThreadPulse instances. The data has one home. See Appendix F for the secondary-machine workflow.

---

## 1.1 — Core Philosophy

ThreadPulse is a personal research tool, not a public product. That framing has consequences for every design choice. Polish does not matter; data quality does. Liability concerns do not apply; ML readiness does. UI does not need to delight strangers; it needs to be scannable to one person at 7:30 in the morning over coffee. These ten rules govern every coding session. Claude must hold them. You must enforce them.

**1. Never hardcode thresholds.** Every numerical decision lives in `config/config.yaml`. Mention counts, velocity percentages, dollar amounts, time windows, ML hyperparameters — all in config. Quarterly threshold refinement (Milestone 11.4) becomes a five-minute edit instead of a code spelunking expedition.

**2. Never commit credentials.** All secrets live in `.env`. `.env` is in `.gitignore` before the first commit. No exceptions, including "I'll move it later" temporary commits.

**3. All timestamps in UTC.** Every database column storing a time is UTC. Local time conversion happens only in the dashboard display layer. Your entire ML pipeline depends on this being absolute.

**4. Store raw before processed.** Every collector writes the raw source payload (Reddit JSON, scraped HTML chunk, RSS XML, EDGAR filing) to its `raw_data` column *before* any extraction or sentiment scoring runs. If your extraction logic improves later you reprocess from raw without rescraping.

**5. Data quality over speed.** Every new data source ships with a mini validation checkpoint. You manually spot-check 20-30 records and confirm they match the upstream source before moving to the next milestone. Skipping this once will poison months of downstream data and you will not notice until ML training reveals the rot.

**6. No ML until the data pipeline is stable.** The model is built last (Milestone 9). Building it sooner means training on dirty data and learning ghosts. The MVP through Milestone 8 produces a clean labeled dataset; only then does the model get to see it.

**7. No buy/sell language in the system.** The dashboard does not say "buy signal" or "sell signal" anywhere. It says "high attention," "early signal," "Tier 3 overlap," "confirmed by news," "already moved." You make trade decisions; the system organizes information.

**8. Code stays beginner-readable.** No clever metaclasses, no nested ternaries, no implicit returns. Explicit over compact. Small functions over one-liner heroes. If you come back in three months you should immediately understand what every file does.

**9. Make surgical changes.** When asked to modify a file, Claude touches only the files needed for that task. No drive-by refactors. No "while I was there" cleanups. If improvement opportunities are spotted elsewhere, log them in `decisions.md` and address in a separate session.

**10. Explain before coding.** Every nontrivial task begins with: restate the task, list files Claude expects to touch, outline the implementation plan, get a sanity check from you. *Then* write code. This forty seconds prevents an hour of unwinding.

---

## 1.2 — Directory Architecture

The repository follows a clean separation between *configuration*, *documentation*, *backend*, *frontend*, and *operational artifacts*. This structure is created in Milestone 0 and never reorganized casually.

```
GlobalStockResearch/
├── CLAUDE.md                    Operating manual (always in context)
├── README.md                    Short public description
├── .gitignore
├── .env.example                 Template, no secrets
├── .claude/
│   └── agents/                  Native Claude Code subagents
│       ├── code-reviewer.md
│       ├── grill-me.md
│       ├── tech-debt-reviewer.md
│       └── design-reviewer.md
├── docs/
│   ├── blueprint.md             This document (or just Part 2 of it)
│   ├── current_phase.md         Active scope gate (changes weekly)
│   ├── decisions.md             Architectural decision log
│   ├── signal_definitions.md    Extract of §2.5 for quick reference
│   └── mvp_definition.md        Extract of §2.6 for quick reference
├── config/
│   └── config.yaml              Single source of truth for every threshold
├── backend/
│   ├── CLAUDE.md                Backend-specific rules
│   ├── app/
│   │   ├── collectors/          Reddit, prices, insider, news, earnings
│   │   ├── services/            Ticker extraction, sentiment, overlap
│   │   ├── models/              SQLAlchemy table definitions
│   │   ├── scheduler/           APScheduler jobs
│   │   └── api/                 FastAPI endpoints
│   ├── tests/
│   ├── scripts/                 One-off operations (historical imports)
│   ├── requirements.txt
│   └── .venv/                   gitignored
├── frontend/
│   ├── CLAUDE.md                Frontend-specific rules
│   ├── app/                     Next.js 14 app router
│   ├── components/
│   ├── lib/
│   └── package.json
├── notebooks/                   Jupyter — EDA, model training, backtests
├── models/                      Saved ML models with version naming
├── logs/                        Daily briefings + script logs
├── backups/                     gitignored, nightly DB dumps
└── data/                        gitignored, large historical imports
```

The `.claude/agents/` directory is the key architectural decision that distinguishes this setup from older Claude Code workflows. Subagents are markdown files with YAML frontmatter that Claude Code v2.1.147 discovers automatically. You do not paste files into chat. You invoke them by name.

---

## 1.3 — The Three-Tier Context System

Every document in this project belongs to one of three tiers. Understanding this prevents the most common failure mode of long Claude Code projects: context bloat, where the assistant is drowning in references and accomplishes less per session.

**Tier 1 — Always in context.** These are loaded into every session automatically (because `CLAUDE.md` lives at the repository root, and conventionally references `current_phase.md` early). They are short on purpose. If a Tier 1 file exceeds two hundred lines, something belongs in Tier 2.

- `CLAUDE.md` — operating manual, the rules of engagement
- `docs/current_phase.md` — what is in scope this week, what is explicitly out

**Tier 2 — Read on demand.** Claude opens these when relevant to the task at hand. The full project blueprint, the decision log, area-specific rules, signal definitions. These can be long — the blueprint itself is over a thousand lines — because they are only loaded when actually needed.

- `docs/blueprint.md` (or this document)
- `docs/decisions.md`
- `docs/signal_definitions.md`
- `docs/mvp_definition.md`
- `backend/CLAUDE.md`
- `frontend/CLAUDE.md`

**Tier 3 — Invocable specialists.** Subagents in `.claude/agents/`. These do not load into the main session at all. They are separate contexts that Claude switches into when delegated. They have their own focused instructions and return a result to the main session.

- `.claude/agents/code-reviewer.md`
- `.claude/agents/grill-me.md`
- `.claude/agents/tech-debt-reviewer.md`
- `.claude/agents/design-reviewer.md`

The rule: anything that belongs in *every* session goes in Tier 1. Anything that belongs in *some* sessions goes in Tier 2. Anything that benefits from *fresh context and a specialized lens* goes in Tier 3.

---

## 1.4 — The Subagent System

Claude Code v2.1.147 supports native subagents. They live in `.claude/agents/` as markdown files with YAML frontmatter. Once present, you invoke them with natural language: *"Use the code-reviewer subagent to check my Reddit collector."* Claude switches into that specialist's context, runs the review, returns a structured report, and your main session continues.

Four subagents cover the quality-gate workflow for ThreadPulse. Each is defined fully in Part 3 (Appendix B). Brief summary:

**code-reviewer.** Fresh-eyes review of completed code. No implementation bias. Checks adherence to project standards (UTC timestamps, config thresholds, raw data preservation, error handling, no credentials). Output is a prioritized issue list — Critical / Important / Nice-to-have. Invoke at the end of every phase before marking it complete.

**grill-me.** Plan interrogation. Stress-tests architectural decisions before code is written. Asks one relentless question at a time about edge cases, failure modes, validation strategy, alternatives, assumptions. Refuses vague answers. Continues until shared understanding is reached. Invoke before any phase that involves non-trivial design choices.

**tech-debt-reviewer.** Hunts for shortcuts and future maintenance problems across the codebase. Returns a P0/P1/P2/P3 prioritized debt report. Invoke weekly and before any major release. P0 means fix immediately; P3 means track only.

**design-reviewer.** UI/UX review of dashboard screenshots. Specifically checks for ThreadPulse design constraints: no buy/sell language, research-appropriate wording, signal confidence visually distinguishable, "already moved" warnings legible, information density appropriate. Invoke when building any new dashboard view.

**The pattern that works:** plan with grill-me → implement in main session → review with code-reviewer → fix in main session → for UI, also run design-reviewer on screenshots → run tech-debt-reviewer at the end of each milestone. This is not over-engineering. Each subagent run is short and cheap on the Max plan. Together they catch ninety percent of the issues that would otherwise emerge two months later as deeply embedded problems.

---

## 1.5 — The Build Workflow

Every task — meaning every nontrivial unit of work, roughly one to four hours of effort — follows this loop. Claude is instructed to follow it via `CLAUDE.md`. You enforce it by not accepting code that skips steps.

**Step 1 — Restate.** Claude restates the task in its own words. If the restatement is wrong, you correct it before any code is written.

**Step 2 — List affected files.** Claude names every file it expects to touch. New files are flagged as new. If anything looks wrong — wrong directory, missing a file, including something out of scope — you push back here.

**Step 3 — Plan.** Two to five sentences describing the implementation approach. What data structures, what flow, what edge cases. Not pseudocode; just the strategy.

**Step 4 — Smallest working change.** Claude implements the *minimum* code that satisfies the task. No bonus features. No "while I was here." If the change is large, it is broken into smaller commits, each individually reviewable.

**Step 5 — Test command.** Claude states the exact command you should run to verify the work — `python -m pytest tests/test_reddit_collector.py`, `npm run build`, `python scripts/validate_config.py`. If no test exists, Claude writes one or explains why the change is structurally untestable.

**Step 6 — Self-check.** Before claiming completion, Claude verifies the following internally and reports the result:

```
- [ ] Code runs without errors
- [ ] Tests pass (or N/A explained)
- [ ] Follows project standards (UTC, config, raw data, no secrets)
- [ ] No hardcoded thresholds
- [ ] Error handling exists where appropriate
- [ ] Logging is meaningful
- [ ] Surgical — only files in step 2 were touched
```

**Step 7 — Confidence statement.** Claude must explicitly state confidence at 95% or above to mark the task done. Anything below 95% is stated as concerns to be resolved before proceeding. This single rule prevents most "but it looked done" failures.

**Step 8 — Summary.** One paragraph: what changed, what to verify, what to commit. You read it, run the test command, and commit yourself.

---

## 1.6 — Session Management

A Claude Code session degrades as it lengthens. Context fills, earlier instructions blur with later ones, and recent corrections compete with original rules. The discipline is to manage session boundaries actively.

**Start a new session when:** switching milestones, switching from implementation to review, after a long stretch (twenty-plus message exchanges), after `/compact` has fired twice, when behavior starts feeling subtly off.

**Keep the same session when:** continuing closely related work within one phase, iterating on a single file, debugging a specific bug.

**The `/clear` and `/compact` commands.** Both compress conversation history. `/clear` is aggressive — it drops everything except the system prompt. `/compact` summarizes recent context. You run these, not Claude. A good rhythm: `/compact` when responses start including unnecessary preamble or losing focus; `/clear` when starting a new phase.

**Context window on Max + Opus 4.7.** You have 1M context. This is plenty for ThreadPulse — even loading the entire blueprint, all CLAUDE.md files, and three subagent files leaves the vast majority of context free. The "save tokens at all costs" mindset from older Claude versions is overcalibrated for your setup. Keep CLAUDE.md lean because cluttered top-of-context prompts dilute attention, not because you are running out of tokens.

**Subagents reset context.** Each subagent invocation starts fresh. This is a feature: code-reviewer must not see how the code was written, only that it exists. Pass the subagent everything it needs in the invocation message — file paths, the standard to check against, what to focus on.

---

## 1.7 — Quality Gates

Each milestone has a Definition of Done. This is not negotiable. You do not advance to the next milestone until the current one passes its gate. Skipping gates is how data pipelines end up unmaintainable.

**Per-phase gate:** Self-check passes, code-reviewer subagent has run and any Critical or Important issues are resolved, test command produces clean output.

**Per-milestone gate:** All phases complete, the milestone's mini validation checkpoint passes (manual spot-check of 20-30 records against the upstream source), tech-debt-reviewer has run on the milestone's new code and any P0 or P1 debt is resolved or explicitly logged in `decisions.md` with a planned fix date.

**Weekly gate (independent of milestones):** Run tech-debt-reviewer on recent changes. Run a query checking for duplicate rows in any table populated this week. Confirm the most recent collector run logged successfully and produced a nonzero record count.

The MVP itself (Milestones 0, 1, 2, and Phases 7.1–7.6 + 7.11–7.13) has its own complete gate defined in §2.6. The MVP gate is the most important one. Do not begin Milestone 3 until the MVP gate passes.

---

## 1.8 — Maximizing Claude Max for ThreadPulse

The $200/month plan unlocks four things that matter for this project specifically. Knowing what each one is for prevents both under-use (treating Max like Pro) and over-use (burning premium tokens on boilerplate).

**Opus 4.7 with one-million-token context.** Use this as your default. For ThreadPulse the gnarliest reasoning happens in: overlap detection scoring logic, ML feature engineering and leakage audits, ticker disambiguation across the company-name mapping, and dashboard architectural decisions. Opus 4.7 is materially better than Sonnet at these. For routine code (table definitions, simple endpoints, basic React components), you can drop to Sonnet via the model switcher to conserve weekly quota — but Max gives you enough Opus headroom that you do not need to micromanage this.

**Generous weekly token budget.** Liberate yourself from old-Claude rationing. Run subagents whenever they apply. Use grill-me twice on the same plan if the first pass surfaced issues. Run tech-debt-reviewer weekly without guilt. The cost of an unused token is one hundred percent waste; the cost of an extra review is sometimes catching a Critical bug.

**Parallel sessions.** With Max you can have an implementation session running in one terminal and a code-reviewer session running in another, against the same repository, without one blocking the other. This is especially useful in Milestones 1, 2, and 7 where there's enough surface area to parallelize: collector implementation in one window, schema review or dashboard sketching in another. You can even split this across machines — run the implementation session on the Windows PC where the database is and you can actually test it, while running a planning or review session on the MacBook Pro.

**Stable access during peak hours.** Max users get prioritized capacity. Plan no work around this — but if you find yourself coding at 3pm Eastern when traffic is highest, you'll notice the difference compared to free or Pro.

**What Max does *not* unlock that older docs claim:** multi-agent orchestration is now in `claude agents` natively; the "Workflow tool" mentioned in the v2.1.147 release notes is off by default and not needed for the MVP. You do not need to enable anything beyond what is described in this document.

---

## 1.9 — Git Discipline

Claude is authorized to read git state (`git status`, `git diff`, `git log`, `git branch`) but never to mutate it (`git add`, `git commit`, `git push`, `git merge`, `git rebase`, `git tag`). All commits are made by you, after reviewing what changed.

**Commit cadence.** One commit per logical change. After Claude completes a task and you've verified it, you commit. Do not let work pile up uncommitted — losing a session's worth of work to a crash or a bad refactor is far more painful than the discipline of frequent commits.

**Commit messages.** Short imperative summary, optional body. Examples that match this project: `add reddit_posts table with indexes`, `implement ticker extraction with blocklist`, `fix UTC handling in price snapshot script`. Avoid: `WIP`, `updates`, `stuff from today`.

**Branching.** Default to a single `main` branch until you have a reason for more. Once you start work on Milestone 9 (ML), a long-running `ml-experiments` branch becomes worth it. Until then, branches add ceremony for no benefit on a one-person project.

**Push frequency.** After every commit or every two commits. GitHub is your offsite backup; if your machine fails and you have not pushed in three weeks, you have effectively no backup.

---
---

# PART 2 — THE PROJECT BLUEPRINT

*The ThreadPulse specification. What you are building, milestone by milestone.*

---

## 2.1 — Vision

ThreadPulse is a fully personal, private stock research intelligence system that runs entirely on your own computer. It is not a public product, it has no users other than you, and it costs nothing to operate. The goal is to replace the hours you currently spend manually browsing Reddit, checking financial news, monitoring insider trading activity, and tracking earnings — and replace all of that with a single dashboard that does it automatically, stores everything historically, and eventually learns to predict which signal combinations are most likely to result in meaningful stock price movements.

The system monitors multiple independent data sources simultaneously, detects when those sources overlap on the same stock ticker, and over time builds a labeled historical record that powers a machine learning model. That model's job is to tell you — based on everything the system has seen — how likely a given signal combination is to result in a significant price move, in what direction, and within what timeframe.

**This is a research tool, not a trading signal generator.** The system will never output "buy" or "sell." It outputs organized information — "High Reddit heat, confirmed by news, insider activity present 6 days ago, stock up 4% this week, broad market trending up." You interpret that information and make your own decisions. This distinction is intentional and important.

---

## 2.2 — What It Does and What It Results In

### What It Does

- Continuously monitors selected Reddit communities for stock ticker mentions and captures the sentiment and context of every discussion
- Monitors OpenInsider and SEC EDGAR for insider buying and selling activity, filtered by meaningful transaction sizes
- Pulls real-time and historical stock price data for every ticker that appears across any data source
- Tracks broad market context — SPY, QQQ, VIX, and major macro economic events — daily so every signal is evaluated against what the overall market is doing
- Cross-references Reddit buzz with real news to determine whether community sentiment is backed by actual news events
- Detects overlap — when Reddit, insider activity, and news all point at the same ticker simultaneously
- Monitors the earnings calendar and captures pre-earnings sentiment, analyst expectations, actual results, and post-earnings price movement
- Stores everything in a structured local database with clean timestamps and proper relationships between data points
- Displays all of this in a clean personal dashboard you access through your browser
- After enough data is accumulated, trains a machine learning model that scores each signal combination by historical accuracy and predicts future price movement probability
- Tracks your personal watchlist of stocks regardless of Reddit activity
- Generates a daily briefing summary every morning so you stay informed without actively opening the dashboard

### What It Results In

A living, compounding intelligence system that gets smarter the longer it runs. After several months of operation you will have a dataset no one else has — your own labeled record of which Reddit communities, which insider activity patterns, which news combinations, and which earnings conditions have historically preceded significant stock moves. The machine learning model trained on that data becomes your personal research edge.

---

## 2.3 — Project-Specific Principles

The ten rules in §1.1 govern Claude's behavior across every session. The principles below are domain-specific to financial data and ML, layered on top of the operating rules. Both sets apply.

**Validate after every new data source.** Every milestone that introduces a new data source ends with a mini validation checkpoint. You manually spot check records, run anomaly queries, and confirm timestamps before moving to the next milestone. This is non-negotiable.

**Log everything.** Every time a script runs, it writes a log entry — how many records were collected, any errors encountered, how long it took. These logs save enormous debugging time months later when something starts behaving oddly.

**Treat sentiment as aggregate, not individual.** A single Reddit post's sentiment score is unreliable. Trust aggregate sentiment across many posts. Two hundred posts averaging 68% positive confidence is meaningful. One post at 90% positive is not.

**This system compounds.** Every day it runs it gets more valuable. A simple system that runs reliably every day beats a complex system that crashes. Keep it running.

**Timestamps are sacred.** Every piece of data must be stored with the exact timestamp it represents — not when you collected it, but when it happened. All timestamps in UTC. The ML model depends on this being consistent. Never compromise on it.

---

## 2.4 — Complete Tech Stack (Windows Primary)

### Operating Environment

| Item | Choice |
|---|---|
| Primary Machine | Your Windows PC (production runtime + database host) |
| Secondary Machine | MacBook Pro (code editing + Claude Code sessions on the go) |
| Code Editor | Visual Studio Code (on both machines) |
| Terminal | Windows Terminal (primary) or VSCode integrated terminal |
| Shell | PowerShell 7 (recommended) or Git Bash; pick one and use it consistently |
| Runtime Environments | Python 3.11, Node.js 20 LTS |
| Package Source | Direct installers from official websites, or `winget` if available |

### Frontend — The Dashboard

| Tool | Purpose |
|---|---|
| Next.js 14 | React framework that powers your dashboard UI |
| Tailwind CSS | Styling — clean UI without writing custom CSS |
| React | Component-based UI building (comes with Next.js) |

### Backend — The Engine

| Tool | Purpose |
|---|---|
| Python 3.11 | Primary language for all data collection, processing, and ML |
| FastAPI | Connects your Python backend to your Next.js frontend via API |
| APScheduler | Runs your data collection scripts automatically on a schedule |
| Uvicorn | Runs your FastAPI server locally |

### Database

| Tool | Purpose |
|---|---|
| PostgreSQL 16 (local, Windows) | Primary database — stores all collected data permanently on the Windows PC |
| pgAdmin 4 | Visual interface to inspect and query your database |
| psycopg2-binary | Python library that connects your scripts to PostgreSQL |
| SQLAlchemy | Python ORM — manages database tables and relationships cleanly |

### Data Collection — Reddit

| Tool | Purpose |
|---|---|
| PRAW | Official Reddit Python library for live data collection |
| Arctic Shift data dumps | Free historical Reddit data going back to 2015+ |

### Data Collection — Stock Prices

| Tool | Purpose | Role |
|---|---|---|
| yfinance | Free Yahoo Finance library — historical and current prices | Primary |
| Alpha Vantage free tier | Backup price data source | Fallback only |

### Data Collection — Market Context

| Tool | Purpose |
|---|---|
| yfinance | Daily SPY, QQQ, VIX data |
| pandas_market_calendars | Trading calendar awareness — knows every market holiday and trading day |

### Data Collection — Insider Trading

| Tool | Purpose |
|---|---|
| Requests + BeautifulSoup | Python scraping libraries for OpenInsider and SEC EDGAR |

### Data Collection — News

| Tool | Purpose |
|---|---|
| GDELT Project | Free global news dataset going back to 2013 — historical training data |
| feedparser | Free live news from Reuters, Yahoo Finance, CNBC — no API key needed |

### Data Collection — Earnings

| Tool | Purpose |
|---|---|
| yfinance | Historical earnings results, expected vs actual EPS, dates |
| BeautifulSoup scraping | Supplemental earnings data from StockAnalysis.com and Macrotrends |

### AI and NLP Layer

| Tool | Purpose |
|---|---|
| FinBERT (Hugging Face, ProsusAI/finbert) | Financial sentiment analysis — runs locally, no API cost |
| spaCy | Ticker extraction from Reddit posts — runs locally |
| Ollama for Windows | Runs large language models locally on your Windows PC |
| Qwen 2.5 via Ollama | Generates summaries and insights — cached, not regenerated constantly |
| Google Gemini free API | Backup AI for summary generation |

### Machine Learning Stack

| Tool | Purpose |
|---|---|
| pandas | Data manipulation and preparation |
| numpy | Numerical computing |
| scikit-learn | ML model training — Random Forest, XGBoost, logistic regression |
| imbalanced-learn | Class imbalance handling — SMOTE oversampling |
| Jupyter Notebooks | Interactive environment for data exploration and model experimentation |
| matplotlib + seaborn | Visualizing model performance and signal accuracy |
| PyTorch (later phase) | Advanced neural network models if needed |

### Version Control and Backup

| Tool | Purpose |
|---|---|
| Git for Windows | Version control — includes Git Bash, a unix-style shell |
| GitHub (private repo) | Free private repository to back up your code |
| Automated DB backup script | Daily PostgreSQL backup to external drive or Google Drive |

### Windows-Specific Operational Notes

**Sleep prevention.** Open Settings → System → Power & battery → Screen and sleep. Set "When plugged in, put my device to sleep after" to **Never**. Set screen-off timer to whatever you want — only the *system* sleep matters for keeping the collectors running. If running on battery is acceptable, repeat the same toggle for "On battery power, put my device to sleep after" but this drains the battery quickly. Plug it in and keep it plugged in.

**Startup at login.** Windows uses **Task Scheduler** for this. Phase 7.13 produces a `.bat` file that starts everything; Task Scheduler is configured to run that batch file "At log on of any user" with "Run with highest privileges" if needed.

**Path separators.** Internally Python uses `pathlib.Path` which handles `\` vs `/` automatically. In scripts, prefer `pathlib.Path(__file__).parent / "config" / "config.yaml"` over hardcoded strings. In PowerShell, forward slashes work in most contexts. In `.bat` files, use backslashes. Never hardcode an absolute path like `C:\Users\Ame\...` — use relative paths from the repository root or read from `config.yaml`.

**PostgreSQL as a Windows Service.** The PostgreSQL installer registers itself as a Windows Service that starts automatically at boot. You can verify with `services.msc` → look for `postgresql-x64-16`. You do not need to start it manually; it is always running once installed.

**GPU acceleration.** If your Windows PC has an NVIDIA GPU, both FinBERT (via PyTorch with CUDA) and Ollama (with CUDA backend) will use it automatically once CUDA toolkit is installed. This makes FinBERT inference 5-10× faster than CPU-only and Ollama summaries usable in real time. If you do not have an NVIDIA GPU, both still work — FinBERT runs slower (a few seconds per post is fine; you process them in batches), and Ollama is slower (the 2-hour summary cache from Phase 7.4 exists specifically to absorb this).

**Shell choice.** Use PowerShell 7 (the modern cross-platform version) or Git Bash, but pick one and stick to it. Mixing causes confusion when scripts work in one but not the other. PowerShell is recommended because it's native and the most documented for Windows; Git Bash is preferred only if you want unix-style commands.

**Antivirus.** Windows Defender occasionally flags Python scripts that scrape websites or that write to many files quickly (your collectors do both). Add exclusions for `~\Downloads\GlobalStockResearch\` so Defender does not throttle file I/O or quarantine scripts mid-run. Settings → Privacy & security → Windows Security → Virus & threat protection → Manage settings → Exclusions → Add folder.

---

## 2.5 — Signal Definitions

Before writing a single line of code, every signal type must be precisely defined. This document is the source of truth. All scripts must implement exactly these definitions. When you change a threshold, you change it in `config/config.yaml` and reference these definitions to understand why the threshold exists.

**Reddit Signal — Valid when all of the following are true:**
- Ticker has received at least 10 mentions in a rolling 24-hour window
- Mention velocity is up at least 50% compared to the prior 24-hour window
- Average sentiment confidence across those mentions is above 60%
- Ticker passes the blocklist and exclusion list checks

**Insider Signal — Valid when all of the following are true:**
- Transaction type is a purchase, not a sale
- Total transaction value is at or above $100,000
- Filing date is within the last 30 days for overlap detection purposes
- Ticker is not on the exclusion list

**News Confirmation — Valid when:**
- At least one non-duplicate news article about the ticker has been published in the last 48 hours
- The article's FinBERT sentiment is in the same direction as the Reddit signal (both positive or both negative)

**Overlap Tiers:**
- Tier 1 — Single source only. Weakest signal. Tracked but not prominently surfaced.
- Tier 2 — Any two sources confirming in the same direction within their respective time windows.
- Tier 3 — All three sources (Reddit, insider, news) confirming in the same direction within their respective time windows. Strongest signal. Prominently surfaced.

**Successful Outcome — Defined as:**
- Stock moves more than the significance threshold in the signaled direction within 7 trading days
- Starting threshold: 3% flat, to be replaced with volatility-adjusted threshold (1.5x average daily range) after initial models are trained
- Success is measured from the price snapshot at the exact moment of signal detection

**Failed Outcome — Defined as:**
- Stock does not move more than the threshold in the signaled direction within 7 trading days
- This includes moves in the opposite direction

---

## 2.6 — The MVP Definition and Success Metric

**MVP = Milestones 0 + 1 + 2 + Phases 7.1 through 7.6 + Phases 7.11–7.13 of Milestone 7.**

The MVP gives you: Reddit ticker tracking, sentiment scoring, price movement tracking, watchlist, paper trade tracker, daily briefing, and a clean dashboard. That alone replaces hours of manual research.

**The MVP is complete when all five conditions hold:**

1. Reddit posts are collected every 30 minutes reliably for 30 consecutive days with no crashes
2. Ticker extraction passes an 85% accuracy check on a manual spot sample of 50 posts
3. Price movement labels are calculating correctly in trading days for all signals
4. The trending tickers dashboard is displaying live data correctly
5. The daily briefing file is generating every morning

Only after all five are confirmed do you move to Milestone 3: OpenInsider, Milestone 4: Overlap Detection, Milestone 5: News, Milestone 6: Earnings, full dashboard completion, and eventually ML.

---

## 2.7 — Milestone 0: Environment Setup

*Goal: Get your Windows PC fully prepared to build and run this project. Mac setup is covered separately in Appendix F as a lighter "dev companion" install.*

---

### Phase 0.1 — Install Core Software (Windows)

Install **Visual Studio Code** from code.visualstudio.com — pick the User Installer (x64).

Install **Windows Terminal** from the Microsoft Store if not already present. This gives you tabs and a much better terminal experience than the legacy `cmd.exe`.

Install **Python 3.11** from python.org. During installation, **check the box that says "Add python.exe to PATH"** before clicking Install. This is the single most important checkbox in the entire setup — miss it and every Python command will fail until you fix it. Verify with `python --version` (should report 3.11.x).

Install **Node.js 20 LTS** from nodejs.org. Use the Windows Installer (.msi). Accept the default to add `npm` and `node` to PATH. Verify with `node --version` (should report v20.x.x).

Install **Git for Windows** from git-scm.com. During install, when asked about the default editor, choose VSCode if you want; when asked about path handling, choose "Git from the command line and also from 3rd-party software" (the default); accept the rest of the defaults. This installs both the `git` command and Git Bash. Verify with `git --version`.

Install **PostgreSQL 16** from postgresql.org. The installer is the EnterpriseDB Windows installer. During installation:
- It will ask you to set a master password for the `postgres` superuser — **write this down and store it somewhere safe outside your PC** (a password manager is ideal). If you lose this password you lose access to your database, which means you lose all your data.
- It will ask for a port — accept the default 5432.
- It will ask whether to launch Stack Builder at the end — uncheck it, you don't need any add-ons for ThreadPulse.

PostgreSQL installs as a Windows Service that starts at boot automatically.

Install **pgAdmin 4** — this is bundled with the PostgreSQL installer. If it's not, download separately from pgadmin.org.

(Optional but recommended) Install **PowerShell 7** from the Microsoft Store or via `winget install Microsoft.PowerShell`. The version that ships with Windows is PowerShell 5.1, which is older and more limited. PowerShell 7 is cross-platform and matches the shell you'd use on macOS.

---

### Phase 0.2 — Install Ollama (Windows)

Download and install **Ollama for Windows** from ollama.com (it has a native Windows installer now — no WSL needed). Once installed, open a terminal and download the Qwen2.5 model: `ollama pull qwen2.5`. Download Llama 3 as a backup: `ollama pull llama3`. The Qwen2.5 download is around 4GB.

**GPU and RAM management note:** FinBERT and Ollama both use your GPU and RAM. Never run them simultaneously. Your scripts must process them sequentially — run all FinBERT sentiment scoring first, then call Ollama for summaries separately. If you have an NVIDIA GPU with CUDA installed, both will use it. Running both at the same time will exhaust GPU memory regardless of how powerful your card is.

**NVIDIA GPU users:** install the latest NVIDIA Studio or Game Ready driver, then install CUDA Toolkit 12.x from developer.nvidia.com. Verify with `nvidia-smi` in PowerShell. PyTorch will automatically use CUDA once it's available; `torch.cuda.is_available()` should return `True` after Phase 1.2 dependency install.

**Non-GPU users:** everything still works on CPU, just slower. Plan to run historical Reddit imports overnight rather than during the day.

---

### Phase 0.3 — Set Up VSCode Extensions

Install: Python, Pylance, ESLint, Prettier, PostgreSQL (the official Microsoft `ms-ossdata.vscode-pgsql` one), GitLens, and Jupyter.

> Note: earlier drafts named the PostgreSQL extension `ms-ossdata.vscode-postgresql`. That is Microsoft's older, now-deprecated extension and no longer installs via `code --install-extension`. Use the current official ID `ms-ossdata.vscode-pgsql` (same publisher).

---

### Phase 0.4 — Create Project Folder Structure and Config File

Your project folder already exists at `C:\Users\Ame\Downloads\GlobalStockResearch` (per your screenshot). Inside it create these subfolders if not yet present:

`frontend`, `backend`, `data`, `notebooks`, `models`, `docs`, `logs`, `backups`, `config`, `.claude\agents`.

From PowerShell in the repo root:
```powershell
New-Item -ItemType Directory -Force -Path frontend, backend, data, notebooks, models, docs, logs, backups, config, .claude\agents
```

Inside the `config` folder, create a file named `config.yaml`. This is the single source of truth for every threshold, time window, and parameter in the entire project. Every script reads from this file. You never hardcode a threshold in a script.

The config file must contain at minimum:

- **Reddit signal thresholds** — minimum mention count (10), minimum velocity increase (50%), minimum sentiment confidence (60%), collection interval in minutes (30), target subreddits list
- **Insider signal thresholds** — minimum transaction value ($100,000), high significance threshold ($500,000), very high significance threshold ($1,000,000), lookback window in days (30)
- **Overlap detection time windows** — Reddit window in hours (48), insider window in days (14)
- **Price movement thresholds** — flat significance threshold percentage (3%), volatility multiplier for adjusted threshold (1.5), measurement intervals in trading days (1, 3, 7, 14, 30)
- **ML thresholds** — minimum labeled examples per category before training (300), model degradation alert threshold in F1 score drop (0.05)
- **System settings** — timezone (UTC), database name, log file location, backup location
- **Exclusion list** — a list of tickers and company names that should never be tracked, populated as you discover bad data
- **Blocklist** — the list of valid ticker symbols that are also common English words, never to be extracted as tickers

When you do quarterly threshold refinement in Milestone 11, you update this one file and every script automatically uses the new values.

---

### Phase 0.5 — Set Up Python Virtual Environment

Inside your `backend` folder, create a Python virtual environment: `python -m venv .venv`. Activate it:

- **PowerShell:** `.\.venv\Scripts\Activate.ps1`
  - If PowerShell blocks the script, run once: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **cmd.exe:** `.venv\Scripts\activate.bat`
- **Git Bash:** `source .venv/Scripts/activate`

You will know it's activated because your prompt prefix changes to `(.venv)`. Create a `requirements.txt` file and keep it updated with every library you install. If your environment ever needs to be rebuilt, `pip install -r requirements.txt` does it in one command.

---

### Phase 0.6 — Set Up Git and GitHub

The repository is already initialized and connected to GitHub (per your screenshot — main branch, GitLens active). Confirm: `git remote -v`. Create `.gitignore` immediately (see Appendix E for the full template) and confirm it contains `.env`, `config.yaml` (if it ever contains credentials — better to keep secrets in `.env`), `backups/`, `data/`, `logs/`, `models/`, `__pycache__/`, `.venv/`, `node_modules/`, `Thumbs.db`, `desktop.ini`. Commit and push after every meaningful work session.

---

### Phase 0.7 — Set Up PostgreSQL Database

Open pgAdmin, connect to your local PostgreSQL (it should appear automatically as the default local server; enter the master password you set in Phase 0.1). Create a database named `threadpulse`. Verify the connection works from Python with a one-line script that opens a SQLAlchemy engine to `postgresql://postgres:<password>@localhost:5432/threadpulse` and prints `connection ok`. Store the password in `.env`, not in code.

---

### Phase 0.8 — Set Up Database Backup

Write a Python script that runs nightly via APScheduler and exports your entire PostgreSQL database to a compressed file in your `backups` folder, then copies it to Google Drive or an external drive. Use `pg_dump` under the hood — on Windows it lives at `C:\Program Files\PostgreSQL\16\bin\pg_dump.exe`. Add that bin directory to your PATH so the script can call `pg_dump` without an absolute path. A backup that only lives on the same machine as the original is not a real backup.

**Estimated database size:** After one year of operation, expect roughly 20-50GB of total database storage depending on how much historical data you import. Plan your disk allocation accordingly. PostgreSQL handles this size easily on a local machine but you need the space available — keep an eye on free space on the drive where you installed PostgreSQL (usually `C:`, but if you have a separate data drive that's a better location for the data directory).

---

### Phase 0.9 — Configure Windows Power Management and System Settings

Open Settings (Win+I) → System → Power & battery → Screen and sleep. Set "When plugged in, put my device to sleep after" to **Never**. The screen-off timer can stay at whatever you want — only the system sleep matters for keeping the collectors running. If your PC sleeps, all scrapers stop and you lose data collection windows.

In Settings → System → Power & battery → Power mode, set this to "Best performance" while plugged in.

Plug in and stay plugged in. Battery operation is not recommended for the production machine — it limits CPU performance and drains quickly.

**Disable scheduled restarts during work hours.** Settings → Windows Update → Advanced options → Active hours — set this to cover your typical working day (e.g. 8 AM – 11 PM). Windows will still install updates and reboot, but not while you're using the machine. The startup script from Phase 7.13 handles automatic recovery after a reboot.

**Add the project folder to Windows Defender exclusions.** Settings → Privacy & security → Windows Security → Virus & threat protection → Manage settings → Exclusions → Add folder → select `C:\Users\Ame\Downloads\GlobalStockResearch`. This prevents Defender from quarantining scripts mid-run or throttling file I/O during historical imports.

Phase 7.13 builds the startup script that you'll register in Task Scheduler so collection resumes automatically after a reboot or Windows update.

**UTC timestamp rule:** All timestamps in this project are stored in UTC. Every script that writes a timestamp converts to UTC before storing. The dashboard display layer is the only place that converts UTC to your local timezone for readability. This rule is established now in Milestone 0 and never violated.

---

### Phase 0.10 — Validate Environment

Confirm: `python --version` returns 3.11.x, `node --version` returns v20.x.x, `psql --version` returns 16.x, PostgreSQL is accessible from pgAdmin and from Python, Ollama responds to a test prompt (`ollama run qwen2.5 "say hello"`), Git is connected to GitHub (`git remote -v` shows your repo), virtual environment activates correctly with the `(.venv)` prefix appearing in your prompt, `config.yaml` exists and is readable by a test Python script, and Windows will not sleep while plugged in.

---

## 2.8 — Milestone 1: Reddit Data Collection

*Goal: Have a working pipeline that pulls Reddit posts, extracts stock tickers and sentiment, and stores everything reliably.*

---

### Phase 1.1 — Create a Reddit App

Go to reddit.com/prefs/apps while logged into your Reddit account. Click "Create App." Select "script." Name it ThreadPulse. Set redirect URI to http://localhost:8080.

Store the Client ID and Client Secret in a `.env` file inside your `backend` folder. Never put these credentials anywhere else.

**Reddit API policy note:** Reddit tightened its API policies in 2023 and may do so again. PRAW access for personal scripts is currently permitted but terms could change. Your historical data from Arctic Shift dumps is your insurance against this — even if live Reddit API access became restricted, your historical dataset remains intact.

---

### Phase 1.2 — Install Python Dependencies

With virtual environment activated, install: PRAW, python-dotenv, psycopg2-binary, SQLAlchemy, pandas, spaCy, transformers, torch, feedparser, requests, beautifulsoup4, pyyaml, pytz, pandas_market_calendars.

Download spaCy's English language model: `python -m spacy download en_core_web_sm`.

Update `requirements.txt`: `pip freeze > requirements.txt`.

---

### Phase 1.3 — Build Your Ticker Dictionary, Blocklist, and Exclusion List

**Ticker dictionary:** Download the complete list of all valid NYSE and NASDAQ ticker symbols from the NASDAQ website. Store as a reference file.

**Blocklist:** Already defined in your `config.yaml`. Must include at minimum: A, I, IT, ARE, FOR, ON, BE, DO, GO, OR, AT, BY, SO, IF, ME, MY, US, AM, PM, AN, DD, RH, AI, EV, IPO, CEO, CFO, ETF, and any others discovered during testing. This list grows over time as false positives are found.

**Exclusion list:** Also in `config.yaml`. Contains tickers and company names that consistently produce bad data — pumped stocks, tickers that are structurally noisy, or any source you decide to stop tracking. Populated as you discover problems.

**Company name to ticker mapping:** Build a dictionary that maps company names to ticker symbols so "Nvidia," "NVIDIA," and "nvidia" all extract as NVDA. yfinance provides company names for all tickers. Store this mapping in your database.

**All formats of the same entity must resolve to the same canonical ticker:** NVDA, $NVDA, $nvda, nvda, Nvidia, and NVIDIA must all become NVDA before storage.

---

### Phase 1.4 — Install and Set Up FinBERT

Install from Hugging Face — the ProsusAI/finbert model. Downloads to your local machine and runs entirely offline after initial download. On Windows with an NVIDIA GPU, transformers + PyTorch will use CUDA automatically once `torch.cuda.is_available()` returns True. Without a GPU, it runs on CPU — slower but functional.

FinBERT returns positive, negative, or neutral labels with a confidence score. Store both the label and the confidence score. A 55% confidence score and a 92% confidence score are not the same thing.

**Sarcasm and Reddit language:** FinBERT was trained on financial news, not Reddit slang. It will misclassify sarcasm, memes, and emoji-heavy posts. This is expected. The solution is aggregate sentiment — never trust a single post's score, only trust the average across many posts on the same ticker in the same time window.

**Emoji sentiment layer:** Alongside FinBERT, implement a simple rule-based emoji check. Rocket, fire, and moon emojis add a small positive adjustment to the aggregate sentiment score. Bear and red chart emojis add a small negative adjustment. These rules are simple, free, and improve aggregate accuracy on Reddit text without additional complexity.

**Sequential processing:** FinBERT runs before Ollama. Never run both at the same time. See Phase 0.2 GPU note.

---

### Phase 1.5 — Define Reddit Database Tables with Indexes

Before writing the collection script, define your database tables in PostgreSQL.

**subreddits table:** name, date added, active status. Index on name.

**reddit_posts table:** Reddit post ID (primary key), subreddit, title, body text, author, upvote count, comment count, post creation timestamp in UTC, collection timestamp in UTC, raw post JSON. The raw JSON column stores the complete original post data before any processing. This allows you to reprocess historical posts if your extraction logic improves later without re-scraping. Index on subreddit and post creation timestamp.

**reddit_tickers table:** auto-increment ID (primary key), post ID (foreign key to reddit_posts), ticker symbol, sentiment label, sentiment confidence score, emoji sentiment adjustment, extraction timestamp in UTC. Index on ticker and extraction timestamp. Composite index on ticker plus extraction timestamp for range queries.

**reddit_signals table:** auto-increment ID (primary key), ticker, signal start timestamp in UTC, mention count in 24-hour window, mention velocity percentage change, aggregate sentiment score, signal tier, valid flag (whether this signal meets the threshold definition from the config). Index on ticker and signal start timestamp.

**subreddit_accuracy table:** subreddit name, total signals generated, signals that resulted in successful outcomes, win rate percentage, minimum signal count before win rate is considered meaningful (50), last updated timestamp. This table fills over time as price movement labels accumulate.

---

### Phase 1.6 — Build the Reddit Collection Script with Rate Limit Handling

Write the collection script. It must include rate limit handling from the start — not added later.

Rate limit handling: if Reddit's API returns a rate limit error, the script uses exponential backoff — wait 1 second and retry, then 2 seconds, then 4 seconds, then 8 seconds, up to a maximum of 60 seconds. The script never crashes due to a rate limit error. It waits, retries, and logs the rate limit event.

Process subreddits sequentially, not simultaneously.

Before processing any post, check if its Reddit post ID already exists in `reddit_posts`. If it does, skip it. This prevents duplicates regardless of how many times the script runs.

For each new post, store the raw JSON first, then run ticker extraction, then run FinBERT, then store the processed results. Storing raw JSON first means a crash during processing doesn't lose the original post.

At the end of every run write a log entry: timestamp, subreddits processed, posts collected, tickers extracted, any rate limit events, any errors, duration.

---

### Phase 1.7 — Set Up APScheduler with Correct Configuration

Configure APScheduler to run the Reddit collection script every 30 minutes.

**Critical APScheduler settings:** Set `coalesce=True` so that if multiple scheduled runs were missed (PC was off or asleep), only one catch-up run executes when it comes back on rather than triggering all missed runs simultaneously. Set `misfire_grace_time` to 300 seconds (5 minutes) so a run that starts slightly late is still executed rather than skipped.

The scheduler runs as a background process. It handles errors gracefully — a failed run logs the failure and waits for the next scheduled run.

---

### Phase 1.8 — Load Historical Reddit Data with Checkpointing

Download Arctic Shift data dumps for r/wallstreetbets from 2019, r/stocks and r/investing from 2020. These are large files. Allow significant time for download and processing.

**Checkpointing is required:** Write the historical import script to save its progress after every 10,000 records processed — storing the last successfully processed record ID or timestamp to a checkpoint file. If the script crashes or is interrupted, it reads the checkpoint file on restart and continues from where it stopped rather than starting over. Processing years of Reddit data through FinBERT will take days on even a powerful machine. A crash without checkpointing means starting over.

All timestamps from historical imports must be the original post creation timestamps in UTC — not the import date.

---

### Phase 1.9 — Mini Validation Checkpoint

Manually open 20 random posts from your database and find the originals on Reddit. Verify tickers extracted match what was actually discussed. Verify sentiment labels feel directionally correct. Check for false positives and update your blocklist. Confirm post timestamps match original post dates in UTC. Run a query checking for duplicate post IDs. Fix any systematic issues before proceeding.

---

## 2.9 — Milestone 2: Stock Price Tracking, Market Context, and Macro Calendar

*Goal: Pull price data for all tickers in trading days, add broad market context, macro event awareness, and handle corporate actions.*

---

### Phase 2.1 — Install Trading Calendar Library

Install `pandas_market_calendars`. All price movement calculations in this project use trading days, never calendar days. A signal on Friday afternoon has its first full market response on Monday. Every time interval in this project uses this library for all date calculations.

---

### Phase 2.2 — Define Price and Context Database Tables with Indexes

**tickers table:** ticker symbol (primary key), company name, exchange, sector, industry, market cap category (large/mid/small cap), first seen date, active status, notes field. Index on sector and industry for filtering.

**daily_prices table:** auto-increment ID, ticker, date, open, close, high, low, volume, adjusted close. Index on ticker. Composite index on ticker plus date — this is the most frequently queried table in the entire project.

**price_snapshots table:** auto-increment ID, ticker, UTC timestamp, price. Index on ticker and timestamp.

**market_context table:** date (primary key), SPY close, SPY daily percent change, QQQ close, QQQ daily percent change, VIX close, market regime label (bull/bear/sideways based on SPY vs its 50-day moving average — above means bull, below means bear, within 1% means sideways). This is a simplified starting regime definition to be refined over time. Index on date.

**macro_events table:** event ID (primary key), event name (CPI Release, FOMC Meeting, Jobs Report, etc.), scheduled date, actual date if different, notes. This is a simple reference table. It is manually maintained or populated from a free economic calendar source. When a signal fires two days before an FOMC meeting, that context is available to you and your ML model. Index on scheduled date.

**corporate_actions table:** auto-increment ID, original ticker, new ticker or null if delisted, action type (rename/acquisition/delisting/bankruptcy), effective date, notes. When a company changes its ticker or disappears, this table ensures your historical price labels don't break silently.

**signal_price_labels table:** auto-increment ID, signal ID, signal source table name, ticker, signal UTC timestamp, price at signal time, price after 1 trading day, price after 3 trading days, price after 7 trading days, price after 14 trading days, price after 30 trading days, percent change at each interval, binary significant move label at each interval (based on config threshold), volatility-adjusted move label at each interval, "already moved" flag (true if stock had already moved more than 10% in the 7 trading days before the signal). Composite index on signal source and signal ID.

---

### Phase 2.3 — Build the Price Collection Script

Use yfinance as the primary source. Pull full daily price history for all tickers in your database. Run daily after market close. Capture real-time price snapshots at the moment any new signal is detected.

Pull SPY, QQQ, and VIX daily on the same schedule for your `market_context` table. Calculate the market regime label automatically based on SPY vs its 50-day moving average.

If yfinance fails, log the failure and attempt the same data from Alpha Vantage free tier (25 requests per day) for gap-filling.

Add sector, industry, and market cap data for every new ticker via yfinance when first added to the `tickers` table.

---

### Phase 2.4 — Handle Corporate Actions

Before pulling price data for any ticker, check the `corporate_actions` table. If an action exists, use the correct symbol for the correct time period. Maintain this table manually as you encounter tickers that no longer exist or have been renamed.

---

### Phase 2.5 — Calculate Price Movement Labels

Write the labeling script. For every signal in any source table, calculate and store price movement at each interval from the config file (default: 1, 3, 7, 14, 30 trading days). All intervals use `pandas_market_calendars`.

Calculate both the flat percentage threshold label and the volatility-adjusted label. Start with the flat threshold as the training target and add the volatility-adjusted version after initial models are trained.

Set the "already moved" flag for any signal where the stock had already moved more than 10% in the 7 trading days before the signal. This is surfaced prominently in the dashboard as a warning.

This script runs nightly and fills in labels for signals whose measurement windows have passed.

---

### Phase 2.6 — Populate Macro Events Table

Manually populate your `macro_events` table with the next 12 months of known scheduled macro events: FOMC meeting dates (published by the Federal Reserve at the start of each year), monthly CPI release dates (published by BLS), monthly Jobs Report dates (published by BLS). Update this table at the start of each new year. This takes 20 minutes once a year and gives every signal meaningful macro context.

---

### Phase 2.7 — Mini Validation Checkpoint

Randomly sample 30 signals. Manually verify price movement labels against stock charts. Verify all intervals are in trading days by checking a Friday signal — its 1-day label should reflect Monday's close. Verify market context data exists for all signal dates. Verify sector and industry are populated for all active tickers.

---

## 2.10 — Milestone 3: OpenInsider Data Collection

*Goal: Pull insider trading activity with meaningful size filtering, store raw data, and link to price data.*

---

### Phase 3.1 — Define Insider Database Tables with Indexes

**insider_filings table:** auto-increment ID (primary key), ticker, company name, insider name, insider title, transaction type, shares traded, price per share, total transaction value, significance tier (standard/high/very high based on config thresholds), filing date in UTC, transaction date in UTC, SEC filing URL, raw scraped data JSON. Index on ticker and transaction date. Index on significance tier.

---

### Phase 3.2 — Understand What Makes an Insider Signal Meaningful

Insider buying is more meaningful than selling. Apply the minimum dollar threshold from your config ($100K default). CEO and CFO buys carry more weight than peripheral board members — store the title. Multiple insiders buying simultaneously is stronger than a single insider. These distinctions become ML features.

---

### Phase 3.3 — Build the OpenInsider Scraper with Health Monitoring

Write the scraper using Requests and BeautifulSoup. Store raw scraped data in the JSON column before processing, same pattern as Reddit posts.

**Scraper health check:** After every run, validate that the number of fields extracted matches the expected schema. If the field count is wrong or key fields are empty, the scraper has likely hit a layout change. Log a prominent warning and halt storage of that run's data rather than storing garbage. The daily briefing will surface this failure.

Run every 4 hours during market days. Historical scrape going back to 2014 as a one-time operation with checkpointing.

Apply significance filtering from config before marking records as valid signals.

---

### Phase 3.4 — Extend Price Movement Labels to Cover Insider Filings

The nightly labeling script from Milestone 2 is extended to also process `insider_filings`. Every filing gets the same price movement label treatment — 1, 3, 7, 14, 30 trading days post-filing, flat and volatility-adjusted labels.

---

### Phase 3.5 — Mini Validation Checkpoint

Sample 20 insider filings. Verify against original SEC filings on EDGAR. Confirm transaction amounts and dates are correct. Confirm filings below the $100K threshold are not stored. Confirm price movement labels look correct.

---

## 2.11 — Milestone 4: Overlap Detection

*Goal: Detect when multiple sources point at the same ticker and score those overlaps by tier.*

---

### Phase 4.1 — Define Overlap Database Tables with Indexes

**signal_overlaps table:** auto-increment ID (primary key), ticker, overlap detected timestamp in UTC, sources involved (stored as array or comma-separated), individual signal IDs from each source, overlap tier (1/2/3), market context at overlap time (SPY change, QQQ change, VIX level, regime label, any macro event within 3 days), price movement outcome once available. Index on ticker and overlap timestamp. Index on tier.

---

### Phase 4.2 — Build Overlap Detection with Subreddit Reliability Weighting

Write the overlap detection script. It runs after each collection cycle. Time windows are read from `config.yaml`. Check for existing overlaps for this ticker within this window before inserting to prevent duplicates.

When calculating overlap tier, weight the Reddit source by the contributing subreddit's reliability score from the `subreddit_accuracy` table. A Tier 2 overlap where the Reddit signal comes from a historically accurate subreddit is a stronger signal than the same overlap from a historically noisy subreddit. Store the weighted confidence alongside the raw tier.

**Subreddit reliability score formula:** Raw win rate is total successful outcome signals divided by total closed signals from that subreddit. Apply a minimum signal count before the score is considered meaningful — 50 signals minimum from config. Weight recent signals more heavily than older ones using a 90-day recency decay: signals from the last 90 days count at full weight, signals 90-180 days old at 75% weight, older than 180 days at 50% weight. This prevents old subreddit behavior from dominating the score.

---

### Phase 4.3 — Mini Validation Checkpoint

Confirm overlaps are being detected correctly by manually verifying 5 Tier 2 and 5 Tier 3 overlaps in your database against the underlying source records. Confirm time windows match config values. Confirm duplicate overlaps are not being created.

---

## 2.12 — Milestone 5: News Integration

*Goal: Pull news for every active ticker, deduplicate across sources, and generate Reddit-news cross-reference verdicts.*

---

### Phase 5.1 — Define News Database Tables with Indexes

**news_articles table:** auto-increment ID (primary key), headline, source publication, URL, publication timestamp in UTC, ticker, relevance score, FinBERT sentiment label, sentiment confidence, content hash for deduplication (first 80 characters of headline normalized to lowercase with punctuation removed), duplicate flag, raw article data. Index on ticker and publication timestamp. Index on content hash for fast deduplication lookups.

---

### Phase 5.2 — Implement News Deduplication

Before inserting any article, compute the content hash. Check whether that hash already exists in the `news_articles` table. If it does, store the article but set the duplicate flag to true. All signal calculations and ML features exclude duplicate-flagged articles. This prevents the same Reuters story published on Yahoo Finance, CNBC, and MarketWatch from being counted as three independent news signals.

---

### Phase 5.3 — Load Historical News from GDELT

GDELT is large. Process it in batches. Filter for stock-relevant articles using your company name to ticker mapping. Only accept a match if the company name appears in a clear financial context or the ticker symbol itself appears in the article. Do not rely on fuzzy name matching alone — "Apple" in a headline without financial context is not AAPL. Implement checkpointing for the GDELT import.

---

### Phase 5.4 — Set Up Live News Collection via RSS

Configure `feedparser` to monitor Yahoo Finance, Reuters Business, CNBC, and MarketWatch RSS feeds every 15 minutes. For each new article: extract tickers, run deduplication check, run FinBERT sentiment, store with UTC timestamp and raw data preserved.

Rate limiting for RSS: add a 2-second delay between requests to each feed source to avoid being blocked.

---

### Phase 5.5 — Build Reddit-News Cross Reference Verdict

For any ticker with an active Reddit signal, compare news sentiment from the same time window. Store one of three verdicts on the `reddit_signals` table: Confirmed (Reddit and news both in same direction), Contradicted (Reddit and news in opposite directions — flag prominently), or Unconfirmed (no relevant news exists — possible hype, flag as such).

---

### Phase 5.6 — Mini Validation Checkpoint

Spot check 20 news articles. Verify correct ticker extraction. Verify deduplication is working by finding a major news event and confirming it appears only once with duplicates correctly flagged. Verify sentiment labels. Verify all timestamps are UTC.

---

## 2.13 — Milestone 6: Earnings Integration

*Goal: Capture the full earnings cycle and label all four outcome combinations.*

---

### Phase 6.1 — Define Earnings Database Tables with Indexes

**earnings_calendar table:** auto-increment ID, ticker, expected earnings date, expected EPS, expected revenue, data capture timestamp in UTC. Index on ticker and expected earnings date.

**earnings_results table:** auto-increment ID, ticker, actual earnings date in UTC, actual EPS, expected EPS at report time, EPS surprise percentage, actual revenue, revenue surprise, beat/miss/in-line label, guidance label (raised/lowered/maintained/not provided), raw source data. Index on ticker and actual earnings date.

**earnings_outcomes table:** auto-increment ID, ticker, earnings date, pre-earnings Reddit aggregate sentiment (14-day window before report), pre-earnings news sentiment (14-day window before report), pre-earnings macro events in that window, result label, outcome combination label (one of four combinations), price 1 trading day before, price 1 trading day after, price 7 trading days after, price 30 trading days after, percent moves, macro event within 3 days flag. Index on ticker and earnings date.

---

### Phase 6.2 — Build Earnings Calendar Monitor

Pull upcoming earnings dates from yfinance weekly. Supplement with Macrotrends scraping for completeness. When an earnings date is within 14 days, tag the ticker as pre-earnings and begin capturing Reddit and news sentiment tagged as pre-earnings context. Pre-earnings sentiment capture is time-boxed to the 14 days before the report date.

---

### Phase 6.3 — Build Post-Earnings Capture

Runs the day after each stored earnings date. Pulls actual results from yfinance supplemented by scraping. Calculates surprises. Labels outcome. Captures price movement at each interval in trading days. Links pre-earnings sentiment to this specific event.

---

### Phase 6.4 — Label All Four Outcome Combinations

Beat and stock rose. Beat and stock fell. Miss and stock rose. Miss and stock fell. These four labels are the multi-class training target for the earnings prediction model.

---

### Phase 6.5 — Mini Validation Checkpoint

Manually verify 10 completed earnings events against public records. Confirm actual EPS matches published results. Confirm price movements are correct. Confirm outcome labels match reality. Confirm pre-earnings sentiment is from the 14-day window before the report, not after.

---

## 2.14 — Milestone 7: The Personal Dashboard

*Goal: Build the visual frontend that brings all your data together.*

---

### Phase 7.1 — Set Up Next.js Project

Inside your `frontend` folder, initialize a Next.js 14 project. Install and configure Tailwind CSS.

---

### Phase 7.2 — Build FastAPI Backend

Set up FastAPI with endpoints for all data your dashboard needs. FastAPI runs on port 8000, Next.js on port 3000.

---

### Phase 7.3 — Build Personal Watchlist with Notes

Build the watchlist feature first. A table in your database for tickers you manually add. Each entry has: ticker symbol, date added, personal notes field (free text — "watching for earnings catalyst," "AI infrastructure play," "high risk momentum only"), and active status. The system automatically tracks these tickers for price, news, Reddit activity, and earnings regardless of whether signals exist for them.

Simple management interface in the dashboard: add ticker, add or edit notes, remove ticker.

---

### Phase 7.4 — Build Trending Stocks View (MVP Core)

The main view. Reddit-ranked tickers with heat score, trend direction, verdict, top threads, news cross-check, Why It's Trending summary, Before vs After Reddit comparison, and market context.

**Why It's Trending summaries via Ollama:** These are generated by Ollama with Qwen and are cached. Generate a new summary for a ticker only when: it has not had a summary generated in the last 2 hours, or its underlying data has changed significantly (mention count increased by more than 20%). Store the generated summary and its generation timestamp. The dashboard displays the cached version. This prevents the GPU from being continuously hammered by LLM calls.

**Price already moved warning:** If the stock has moved more than 10% in the 7 trading days before the signal, display a prominent warning that the move may already be priced in. Read the "already moved" flag from the `signal_price_labels` table.

---

### Phase 7.5 — Build Early Signals View

Tickers with rapidly spiking mention velocity and limited news coverage. Each card shows mention spike percentage, posts per hour, news coverage status, and contributing subreddits with their reliability scores.

---

### Phase 7.6 — Build Community Picker

Subreddit toggle in the sidebar. Stored as a local preference. Updates the trending feed when changed.

---

### Phase 7.7 — Build Insider Activity View

Recent insider buying filtered to your significance threshold from config. Shows insider name, title, ticker, transaction size, significance tier, and price movement since filing. Highlights tickers where insider activity overlaps with Reddit signals.

---

### Phase 7.8 — Build Overlap Dashboard

Dedicated view for Tier 2 and Tier 3 overlaps. Each card shows contributing sources, market context at time of overlap (including any macro events within 3 days), signal age, and subreddit reliability score of contributing Reddit signals.

---

### Phase 7.9 — Build Earnings Tracker

Upcoming earnings with pre-earnings sentiment. Post-earnings results with outcome combination labels and price movement. Historical record of how pre-earnings sentiment correlated with outcomes over time.

---

### Phase 7.10 — Build Dynamic Blocklist Management

In the dashboard settings area, add a simple interface to manage the blocklist and exclusion list from the config file without editing code. You can: mark a ticker extraction as a false positive which adds it to the blocklist, mark a news article as unrelated to the ticker it was matched to, and mark a subreddit post as incorrectly processed. These manual corrections update the config and can trigger reprocessing of affected records.

This is how the system improves over time — you correct mistakes as you find them during normal use.

---

### Phase 7.11 — Build Paper Trade Tracker

Add a "Watch This Signal" button on every signal card. Creates a record in a `paper_trades` table: ticker, signal type, signal tier, signal strength at time of flagging, market context at flagging time, your personal notes, and date flagged. The system automatically tracks what happened to that stock over the next 30 trading days and reports back: was this signal right, by how much, how long did it take.

**Paper trade success definition (from config):** A watched signal is marked successful if the stock moves more than the config significance threshold in the direction the signal suggested within 7 trading days. Store both the binary success label and the actual magnitude of move for richer analysis.

This is placed here in Milestone 7 — not Milestone 10 — because you want to start building your personal track record immediately from day one of having a working dashboard.

---

### Phase 7.12 — Build Daily Briefing Output

A Python script via APScheduler runs every morning at 8am and writes a plain text briefing file to your `logs` folder. Contents: today's date and market regime, any new Tier 3 overlaps in the last 24 hours, Early Signals with mention spikes above 200% in the last 12 hours, any watchlist tickers with significant activity, upcoming earnings in the next 7 days for watchlist tickers, any macro events in the next 7 days, and system health summary — records collected from each source yesterday, any sources that returned zero records (flag as likely failure), any scraper health check failures.

APScheduler configuration for this job: if the 8am run is missed (PC was off or asleep), run it on the next startup regardless of time.

---

### Phase 7.13 — Build Startup Script

Create a batch file at the root of your project folder named `start_threadpulse.bat`. This file starts all required services in the correct order with a single double-click: confirms PostgreSQL Windows Service is running, starts the FastAPI backend via Uvicorn (in a new window), starts the APScheduler collection daemon (in a new window), starts the Next.js frontend (in a new window). Each service in its own window so you can see logs without them stepping on each other.

A starter template:

```batch
@echo off
REM start_threadpulse.bat — launches all ThreadPulse services

REM 1. PostgreSQL: should already be running as a Windows Service
net start postgresql-x64-16 2>nul

REM 2. Activate venv and start FastAPI backend in a new window
start "ThreadPulse Backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\activate.bat && uvicorn app.main:app --port 8000"

REM 3. Start the scheduler in a new window
start "ThreadPulse Scheduler" cmd /k "cd /d %~dp0backend && .venv\Scripts\activate.bat && python app\scheduler\run.py"

REM 4. Start Next.js frontend in a new window
start "ThreadPulse Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo All ThreadPulse services started.
```

**Register with Task Scheduler to run automatically at login.**

1. Open Task Scheduler (Win+R → `taskschd.msc`).
2. Create Basic Task → name it "ThreadPulse Startup".
3. Trigger: "When I log on".
4. Action: "Start a program" → browse to your `start_threadpulse.bat`.
5. Finish, then open the task's Properties → check "Run with highest privileges" → on the Settings tab, uncheck "Stop the task if it runs longer than" (the scheduler is meant to run forever).

From this point forward, ThreadPulse starts itself when you log into your Windows PC.

**Verification.** Reboot the PC. Log in. Wait 2 minutes. Check that four windows have opened (PostgreSQL doesn't open one since it's a service), the FastAPI window shows `Uvicorn running on http://127.0.0.1:8000`, and you can navigate to `http://localhost:3000` in a browser to see the dashboard. If any one of those is missing, that's the broken link to investigate.

---

## 2.15 — Milestone 8: Data Validation and Quality Assurance

*Goal: Confirm your entire dataset is clean and trustworthy before touching ML.*

Note: Mini validation checkpoints were completed after each milestone. This is the comprehensive final audit across all sources together.

---

### Phase 8.1 — Cross-Source Data Audit

Confirm all tables have data covering expected date ranges with no large gaps. Confirm all timestamps are UTC original event timestamps. Confirm price movement labels exist for all signals whose windows have passed. Confirm market context data exists for all signal dates. Confirm macro events table is populated for the relevant historical period. Look for tickers in Reddit data with no price data. Look for earnings events with no pre-earnings sentiment.

---

### Phase 8.2 — Assess Dataset Size Per Signal Type

Count labeled examples per category: Reddit only, insider only, Reddit plus insider, Reddit plus news, all three together, earnings events. Minimum 300 labeled examples per category before training. If any category is thin, import more historical data for that source before proceeding.

---

### Phase 8.3 — Survivorship Bias Assessment

Your historical dataset may be missing companies that went bankrupt, were delisted, or were acquired. Note which categories of stocks — particularly small caps and penny stocks — are most likely affected by survivorship bias. Treat model predictions for similar stocks with appropriate skepticism. Where possible, supplement with historical ticker data from `corporate_actions` records.

---

## 2.16 — Milestone 9: Machine Learning Foundation

*Goal: Define targets, engineer features, train models on clean data, and validate without leakage.*

---

### Phase 9.1 — Define Prediction Targets

Primary: binary classification — will the stock move more than the significance threshold in either direction within 7 trading days? Yes or No.

Secondary: direction classification — will the move be up or down?

Tertiary (later): magnitude regression — how large will the move be?

Start with binary only.

---

### Phase 9.2 — Data Leakage Audit — CRITICAL

Before building features or training any model, perform a formal data leakage audit. For every feature you plan to use, answer: was this information available before the signal timestamp T? If no or maybe, do not use it.

Examples of leakage to eliminate: price data from after the signal, earnings results that hadn't been reported yet, news published after the signal, insider filings dated after the signal, sentiment from posts made after the signal.

Document which features passed the leakage check. Store this document in your `notebooks` folder. Do not proceed until this audit is complete.

> **Grill-me checkpoint:** Before starting Phase 9.2, invoke the grill-me subagent on your planned feature list. Data leakage is the single most common cause of "amazing" models that crash in production. Make grill-me earn its keep here.

---

### Phase 9.3 — Feature Engineering with Null Handling

For each signal event, extract all features. All must pass the leakage check.

Reddit features: aggregate sentiment score, average confidence, mention count in prior 24 hours, mention count in prior 7 days, mention velocity percentage change, contributing subreddits and their reliability scores, ratio of bullish to bearish posts, average upvotes.

Insider features: insider buying exists in prior 30 days (yes/no), significance tier, number of simultaneous buyers, days since most recent buy, total dollar value in past 30 days.

News features: deduplicated article count in prior 24 hours, sentiment score, major outlet flag, news-Reddit sentiment agreement flag.

Price features: momentum over prior 7 trading days, price relative to 52-week range, volume vs 30-day average, average daily volatility over prior 30 days.

Market context features: SPY change, QQQ change, VIX level, market regime label, macro event within 3 days flag.

Overlap features: source combination present, time gap between signals, sentiment consistency across sources.

Stock classification: sector, industry, market cap category.

**Null handling — required for every feature:** Define what value represents "feature absent" for each feature and store it consistently. Absence of insider buying is not null — it is 0 (no buying). Absence of news is not null — it is 0 articles and a neutral sentiment score of 0.5. Null values in scikit-learn will cause errors or silent bad predictions. Every feature has a defined default value when data is absent.

---

### Phase 9.4 — Handle Class Imbalance

Apply SMOTE from imbalanced-learn to your training set only. Never apply to test set. Also try scikit-learn's `class_weight="balanced"` parameter. Compare results from both approaches. The method that produces better precision on the minority class (significant moves) is the one to use.

---

### Phase 9.5 — Exploratory Data Analysis

In Jupyter Notebooks, answer: what percentage of signals resulted in significant moves at each interval? Which signal type has the highest raw hit rate? Which subreddits have been most accurate? Are signals more reliable in certain market regimes? What is the typical time lag between signal and peak move? Are there sector patterns? Document findings before proceeding.

---

### Phase 9.6 — Train Models Using Time-Series Split

Train on older data, test on more recent data. Never randomly shuffle. Example split: train on 2019-2023, test on 2024 onwards.

Order: Logistic Regression (baseline), Random Forest (feature importance), XGBoost (primary production model).

Record for each: training date range, test date range, precision, recall, F1 score, accuracy.

---

### Phase 9.7 — Feature Importance Analysis

Extract feature importance from your best model. This tells you which data sources and signal combinations have historically been most reliable. Use this to refine collection priorities — if insider features consistently score highest, that data pipeline deserves the most maintenance attention.

---

### Phase 9.8 — Volatility-Adjusted Threshold Refinement

Replace the flat 3% threshold with a volatility-adjusted one (1.5x average daily range). Retrain with adjusted labels and compare to flat threshold results.

---

### Phase 9.9 — Earnings Prediction Model

Multi-class classification with four target classes (the four outcome combinations). Train on historical earnings events using time-series split.

---

### Phase 9.10 — Backtesting Report

Build the backtesting report in Jupyter Notebooks. Answer: if you had acted on every Tier 2 signal historically, what would have happened? Tier 3 only? Earnings predictions?

**Critical:** The backtesting report evaluates only on your held-out test set — the data from your most recent time period that was never used in training. Evaluating on training data measures memorization, not real performance. The backtest must use only the test set. Present cumulative accuracy over time to see whether model performance is stable across different market periods.

---

## 2.17 — Milestone 10: Integrate ML Into the Dashboard

*Goal: Surface model predictions and historical accuracy in your dashboard.*

---

### Phase 10.1 — Save and Version Models

Save models using scikit-learn `joblib`. Naming convention: `modeltype_traindate_datarange_F1score.pkl`. This ensures you can always roll back to a previous version if a new one performs worse.

---

### Phase 10.2 — Build Prediction API Endpoint

FastAPI endpoint that accepts a ticker, loads the current model, extracts features from your database, runs prediction, and returns probability score, direction, confidence level, and model version used.

---

### Phase 10.3 — Add Prediction Scores to Dashboard

Label these as "Historical Pattern Score" not "Prediction." Include a plain English explanation: "Score is elevated because Reddit mentions are up 240% in 12 hours, insider buying occurred 6 days ago, news sentiment is confirming, broad market is in bull regime."

---

### Phase 10.4 — Build Signal Accuracy Tracker

Dashboard section showing historical accuracy of each signal type updated as new outcomes are recorded. Win rate per signal combination. This is your personal performance record.

---

### Phase 10.5 — Build Backtesting Report View

Visual dashboard version of the backtesting report from Milestone 9. Charts showing signal accuracy by type over time. Win/loss rates per signal combination. Average magnitude of correct versus incorrect calls.

---

## 2.18 — Milestone 11: Ongoing Maintenance and Improvement

*Goal: Keep the system running reliably and models improving.*

---

### Phase 11.1 — Daily Health Checks

Already built into the daily briefing from Phase 7.12. This phase ensures you keep the briefing script updated as new data sources are added so every source is monitored.

---

### Phase 11.2 — Scraper Health Monitoring

For each scraper, validate field counts and data structure after every run. Halt storage and flag loudly if the structure has changed. Built into each scraper from Milestone 3 onwards.

---

### Phase 11.3 — Monthly Model Retraining

Retrain monthly. Compare new F1 score to previous version on the same test set. If F1 score drops more than 5% versus the previous version, do not deploy automatically — investigate whether a market regime change is making old patterns obsolete before deploying. Document every retraining cycle in your `notebooks` folder.

---

### Phase 11.4 — Quarterly Threshold Refinement

Every three months, review all thresholds in `config.yaml` against your accumulated data. Adjust based on evidence. The signal definitions document from §2.5 is the reference — when you change a threshold, update both the config and the signal definitions document so they stay in sync.

---

### Phase 11.5 — Expand Data Sources

When the core system is stable and you want to expand, add these in order of value:

Short interest data from FINRA — published twice monthly, shows how heavily shorted each stock is. High short interest plus Reddit attention is historically the strongest overlap combination.

SEC 13F filings from EDGAR — institutional investor positions updated quarterly. Adds context to why certain stocks may be gaining attention.

Reddit comment-level data — the actual DD posts and counter-arguments live in comments, not post bodies. This would significantly improve sentiment quality for r/wallstreetbets and r/stocks specifically.

Each new source follows the same pattern: define tables with indexes, build collection script with rate limiting and health monitoring, preserve raw data before processing, import historical data with checkpointing, add mini validation checkpoint, integrate into overlap detection, add to ML features.

---

## 2.19 — Milestone Summary Table

| Milestone | Goal | Depends On | MVP? |
|---|---|---|---|
| 0 — Environment Setup | Machine fully prepared | Nothing | YES |
| 1 — Reddit Collection | Live + historical Reddit data | Milestone 0 | YES |
| 2 — Price + Market Context | Price, labels, context, macro | Milestone 1 | YES |
| 3 — OpenInsider | Insider filings stored | Milestone 2 | NO |
| 4 — Overlap Detection | Multi-source signals flagged | Milestones 1-3 | NO |
| 5 — News Integration | News cross-reference working | Milestone 4 | NO |
| 6 — Earnings Integration | Full earnings cycle captured | Milestone 5 | NO |
| 7 — Dashboard | Full dashboard + startup script | Milestones 1-6 | PARTIAL* |
| 8 — Data Validation | Clean dataset confirmed | Milestone 7 | NO |
| 9 — ML Foundation | Models trained and validated | Milestone 8 | NO |
| 10 — ML in Dashboard | Predictions in UI | Milestone 9 | NO |
| 11 — Ongoing Improvement | System maintained and improving | Milestone 10 | NO |

*MVP uses Phases 7.1 through 7.6 plus 7.11, 7.12, and 7.13. Remaining phases built as other sources come online.

---

## 2.20 — Daily Usage Workflow

Once the full system is running, a typical morning looks like this:

Open the daily briefing file from your `logs` folder. Read the system health summary first — if any source failed overnight, investigate before looking at signals. Read the Tier 3 overlaps that appeared in the last 24 hours. Read the Early Signals with high mention velocity. Note any upcoming earnings or macro events in the next 7 days.

Open the dashboard in your browser. Go to the Overlap Dashboard and review any Tier 3 signals in detail. For each one: read the actual Reddit threads driving the buzz, read the news articles cross-referenced to it, check the market context, check whether the "already moved" warning is present, check the watchlist notes if you've been tracking this stock. If the signal looks interesting, click "Watch This Signal" to start paper tracking it.

Check the Earnings Tracker for any upcoming reports on watchlist tickers. Review the pre-earnings sentiment being captured.

Check the Insider Activity view for any significant new filings.

The entire morning review should take 15-30 minutes. The system has done the data collection, cross-referencing, and organization. Your job is interpretation and decision-making.

---

## 2.21 — What This System Does NOT Do

This system does not execute trades. It is a research tool.

This system does not guarantee profitable signals. Markets are noisy and even strong signals fail. The ML model estimates probabilities based on historical patterns, not certainties.

This system does not replace your own judgment. It organizes information and surfaces patterns. You decide what to do.

This system does not need to be perfect from day one. An imperfect system running consistently for six months produces more value than a perfect system that never ships.

This system does not need all milestones complete before it is useful. The MVP alone — Reddit tracking plus price data plus basic dashboard — replaces significant manual research work.

---
---

# PART 3 — APPENDICES: DROP-IN FILES

*Copy each appendix into the indicated file. These are ready to use as-is. No edits required for day one.*

---

## Appendix A — `CLAUDE.md` (repository root)

> **Save as:** `CLAUDE.md` at the root of `GlobalStockResearch/`.
> **Purpose:** Operating manual loaded into every Claude Code session.

```markdown
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
```

---

## Appendix B — Subagents (`.claude/agents/`)

> **Save as:** Four files inside `.claude/agents/` in the repository root.
> **Purpose:** Native Claude Code v2.1.147 subagents. Auto-discovered after restart.

---

### B.1 — `.claude/agents/code-reviewer.md`

```markdown
---
name: code-reviewer
description: Use PROACTIVELY after completing a phase or before committing significant code. Fresh-eyes review of code quality, correctness, and adherence to ThreadPulse standards. No implementation bias.
tools: Read, Grep, Glob, Bash
---

You are a code reviewer for ThreadPulse with fresh eyes and no implementation bias.

## Your Mission

Review code for quality, correctness, and adherence to ThreadPulse standards WITHOUT the context of how it was built.

## Before Reviewing

Read these files to understand project standards:
1. `CLAUDE.md` — core project rules
2. `backend/CLAUDE.md` OR `frontend/CLAUDE.md` (whichever applies)
3. `docs/current_phase.md` — what was in scope for this work

## Review Focus

**For Backend Code:**
- Follows backend/CLAUDE.md standards
- UTC timestamps used correctly
- No hardcoded thresholds (uses config)
- Raw data preserved before processing
- Error handling exists and is appropriate
- Logging is clear and useful
- No credentials in code
- Tests exist for core logic
- Functions are small and focused
- Code is beginner-readable

**For Frontend Code:**
- Follows frontend/CLAUDE.md standards
- No buy/sell recommendation language anywhere
- Research-focused wording
- Loading states exist
- Error states handled
- UTC converted to local only in display
- Tailwind CSS used correctly
- Components are focused and reusable

**For Database Code:**
- UTC timestamps on all time columns
- Indexes on ticker and date columns
- Foreign keys defined
- Unique constraints prevent duplicates
- Raw data preservation columns exist

## Review Output Format

**Summary:**
- Overall assessment (Good / Needs Work / Critical Issues)
- Confidence level (0-100%)

**Critical Issues (must fix before proceeding):**
- Issues that break core rules
- Security problems
- Data integrity risks

**Important Issues (should fix soon):**
- Code quality problems
- Missing tests
- Poor error handling

**Nice to Have (optional improvements):**
- Refactoring suggestions
- Performance optimizations
- Style improvements

## Review Principles

1. No implementation bias — you don't know how/why it was built
2. Fresh perspective — first time seeing this code
3. Standards-focused — does it follow CLAUDE.md rules?
4. Constructive — suggest fixes, not just criticism
5. Specific — point to exact lines/files

## Important

You are a REVIEWER, not an IMPLEMENTER. Identify issues. Do not fix them unless explicitly asked.
```

---

### B.2 — `.claude/agents/grill-me.md`

```markdown
---
name: grill-me
description: Use BEFORE writing code for any nontrivial phase. Interrogates plans relentlessly to surface edge cases, assumptions, and gaps before they become bugs.
tools: Read, Grep, Glob
---

You are a relentless interviewer who stress-tests plans by interrogating every decision.

## Your Mission

Interview the user about their plan until you reach shared understanding and have walked down every branch of the decision tree.

## How to Grill

Ask questions relentlessly about:
1. **Why this approach?** What alternatives exist?
2. **What could go wrong?** Edge cases, failure modes.
3. **How will you know it works?** Validation strategy.
4. **What dependencies exist?** What must be built first?
5. **What can be simplified?** Is this the simplest approach?
6. **What assumptions are you making?** Are they valid?
7. **How will this scale?** Future implications.
8. **What happens if X fails?** Error scenarios.

## Interview Style

Relentless but constructive:
- One question at a time
- Wait for answer before next question
- Probe deeper when answers are vague
- Challenge assumptions
- Point out inconsistencies
- Suggest alternatives for consideration

**Do not accept:**
- "I'll figure it out later"
- "It should work"
- "That's how I always do it"
- Vague plans
- Unconsidered edge cases

**Do accept:**
- Well-reasoned decisions
- Acknowledged trade-offs
- Clear validation plans
- Explicit assumptions

## When You're Done

Stop interrogating when:
1. All major decisions have clear reasoning
2. Edge cases are considered
3. Dependencies are mapped out
4. Validation strategy exists
5. You and the user have shared understanding

## Output Format

After interrogation is complete, provide:

**Plan Summary:**
- Core decisions and why
- Key assumptions (validated)
- Dependencies identified
- Edge cases considered
- Validation strategy

**Risks Identified:**
- What could still go wrong
- Mitigation strategies

**Confidence Level:**
- How solid is this plan? (0-100%)
- What's still uncertain?

## ThreadPulse Context

Read `CLAUDE.md` and `docs/current_phase.md` to understand:
- What work is currently allowed
- What constraints exist
- What standards must be followed

## Important

This is a PLANNING session, not an IMPLEMENTATION session. The goal is to stress-test ideas before coding begins.
```

---

### B.3 — `.claude/agents/tech-debt-reviewer.md`

```markdown
---
name: tech-debt-reviewer
description: Use WEEKLY and at the end of each milestone. Hunts for technical debt, shortcuts, and maintenance problems. Returns P0/P1/P2/P3 prioritized debt report.
tools: Read, Grep, Glob, Bash
---

You hunt for technical debt, shortcuts, and future maintenance problems in the ThreadPulse codebase.

## Your Mission

Identify technical debt that will cause problems later and prioritize it by severity.

## What is Tech Debt?

Code that works now but will cause problems later:
- Hardcoded values that should be configurable
- Missing error handling
- No tests for critical paths
- Copy-pasted code (should be DRY)
- TODOs and FIXMEs
- Overly complex code
- Missing documentation
- Tight coupling
- Magic numbers
- Inconsistent patterns

## Review Checklist

**Configuration debt:**
- Any hardcoded thresholds? (should be in config)
- Any hardcoded URLs, paths, credentials?
- Any environment-specific assumptions?

**Data quality debt:**
- Missing validation checks?
- No duplicate prevention?
- Raw data not preserved?
- Timestamps not in UTC?

**Error handling debt:**
- Missing try-except blocks?
- Silent failures (swallowed exceptions)?
- No fallback strategies?
- Errors not logged?

**Testing debt:**
- Critical code paths without tests?
- No validation scripts?
- Untested edge cases?

**Code quality debt:**
- Functions too long (>50 lines)?
- Deeply nested code?
- Unclear variable names?
- Copy-pasted code?
- Commented-out code?

**Security debt:**
- Credentials in code?
- SQL injection risks?
- Missing input validation?

**Scalability debt:**
- N+1 query problems?
- Missing indexes?
- No pagination?

## Debt Prioritization

**P0 — Critical (fix immediately):** security issues, data integrity risks, crashes in production, credentials exposed.

**P1 — High (fix this phase):** missing error handling, no duplicate prevention, hardcoded thresholds, missing critical tests.

**P2 — Medium (fix next phase):** code complexity, missing documentation, minor optimizations, TODOs for non-critical features.

**P3 — Low (fix when convenient):** style inconsistencies, minor refactoring, nice-to-have features.

## Output Format

**Tech Debt Report:**

**Critical Debt (P0):** [count]
- [Issue 1]: file, line, description, why critical
- [Issue 2]: ...

**High Priority Debt (P1):** [count]
- [Issue 1]: file, line, description, impact
- [Issue 2]: ...

**Medium Priority Debt (P2):** [count]
- [Issue 1]: file, line, description
- [Issue 2]: ...

**Low Priority Debt (P3):** [count]
- [Summary of minor issues]

**Recommended Actions:**
1. Fix P0 immediately
2. Address P1 before phase completion
3. Track P2 for next phase (log in `docs/decisions.md`)
4. Ignore P3 for now

**Debt Trend:**
- Getting better or worse?
- Any patterns emerging?

## ThreadPulse-Specific Checks

Always check for:
- Hardcoded thresholds (should use config)
- Non-UTC timestamps
- Missing raw data preservation
- Credentials in code
- Future milestone creep (building too much)

## Important

REVIEW only. Identify debt, do not fix it. Fixes happen in separate implementation sessions.
```

---

### B.4 — `.claude/agents/design-reviewer.md`

```markdown
---
name: design-reviewer
description: Use when reviewing UI screenshots from the ThreadPulse dashboard. Checks layout, information hierarchy, research-appropriate language, and signal confidence visualization.
tools: Read, Grep
---

You review UI designs and screenshots to ensure the ThreadPulse dashboard is clean, functional, and user-friendly.

## Your Mission

Review UI screenshots and provide actionable design feedback aligned with ThreadPulse goals.

## Design Principles for ThreadPulse

Remember: ThreadPulse is a personal research tool, NOT a public product.

1. **Function over form** — clean and readable beats pretty
2. **Research language** — never buy/sell recommendations
3. **Information density** — show meaningful data efficiently
4. **Scanning friendly** — quick visual parsing
5. **Minimal friction** — fast interaction, no unnecessary clicks

## Screenshot Review Process

### Step 1 — Overall Assessment
- Does it look clean and professional?
- Is information hierarchy clear?
- Can you quickly understand what you're looking at?
- Is it overwhelming or just right?

### Step 2 — Detailed Review

**Layout & structure:** logical information flow, proper whitespace, consistent spacing, clear sections.

**Typography:** readable font sizes, proper hierarchy, consistent font usage, good contrast.

**Color usage:** research-appropriate (not trading-app red/green), consistent meaning (green=confirmed, yellow=early), good contrast, not overwhelming.

**Data presentation:** important info prominent, less important subdued, numbers formatted clearly, timestamps readable.

**Interaction:** buttons clearly clickable, links distinguishable, active states visible, disabled states clear.

**ThreadPulse-specific:**
- No "BUY/SELL" language visible
- Research-focused wording
- Signal confidence clearly shown
- Multiple source confirmation visible
- "Already moved" warnings clear

### Step 3 — Specific Feedback

**Good:** what works well, what should be kept.

**Issues:** what's not working, why it's a problem, severity (Critical / Important / Nice-to-have).

**Suggestions:** specific improvements, alternative approaches, code/CSS snippets if helpful.

### Step 4 — Priority Fixes

1. Fix immediately (breaks usability)
2. Fix before shipping (quality issues)
3. Consider later (polish items)

## ThreadPulse Dashboard Views

Know what you're reviewing:
- Watchlist view (user's tracked tickers)
- Trending tickers view (high Reddit activity)
- Early signals view (before price movement)
- Community picker (subreddit filter)
- Signal detail view (individual ticker deep-dive)
- Overlap dashboard (Tier 2 / Tier 3 signals)
- Earnings tracker (pre/post earnings)
- Insider activity view

Each view has different information density and interaction needs.

## Important

This is a REVIEW session for design/UI only. Code implementation happens in separate sessions.
```

---

## Appendix C — `docs/current_phase.md` (Phase 0.1 Starter)

> **Save as:** `docs/current_phase.md`.
> **Purpose:** The active scope gate. Update this at the start of every new phase.

```markdown
# Current Phase

## Active phase
Phase 0.1 — Install Core Software (Windows)

## What is in scope
- Install VSCode, Windows Terminal, Python 3.11 (with Add to PATH checked), Node.js 20 LTS, Git for Windows, PostgreSQL 16, pgAdmin 4
- Optional: PowerShell 7
- Verify each tool launches and reports a version
- Record PostgreSQL master password securely (in a password manager, outside the repo)

## What is explicitly out of scope
- Any Python library installation (Phase 1.2)
- Any database schema creation (Phase 0.7)
- Any code (no implementation work yet, only environment setup)
- Any other milestone work
- Mac setup (handled in Appendix F separately, not now)

## Definition of Done
- `python --version` returns 3.11.x
- `node --version` returns v20.x.x
- `psql --version` returns PostgreSQL 16.x
- `code --version` returns a version
- `git --version` returns a version
- pgAdmin 4 opens and connects to local PostgreSQL
- PostgreSQL Windows Service is running (verify in services.msc)
- All passwords/credentials stored outside the repo (in a password manager)

## Notes
- Last updated: [date]
- Estimated time to complete: 45-90 minutes (slower than Mac because installers are not bundled)
- After completion, move to Phase 0.2 (Ollama for Windows)
```

---

## Appendix D — `docs/decisions.md` (Template)

> **Save as:** `docs/decisions.md`.
> **Purpose:** Architectural decision log. Append-only. Every nontrivial choice gets an entry.

```markdown
# Architectural Decision Log

Append-only record of nontrivial choices. Each entry follows the format below. Entries are not edited or deleted; if a decision is reversed, a new entry supersedes the old one and references it.

---

## Template

### YYYY-MM-DD — [Short title of decision]

**Context:** What prompted this decision?

**Decision:** What was decided?

**Alternatives considered:** What else was on the table, and why was it rejected?

**Consequences:** What does this make easier or harder?

**Supersedes:** [link to prior decision if this one reverses it, otherwise omit]

---

## Entries

### 2026-05-28 — Adopt three-tier context system

**Context:** Earlier iterations of the project had a flat documentation structure with all reference material referenced from `CLAUDE.md`, which caused context bloat in long sessions.

**Decision:** Split documentation into three tiers. Tier 1 always in context (`CLAUDE.md`, `current_phase.md`). Tier 2 read on demand (`blueprint.md`, `decisions.md`, etc.). Tier 3 invocable subagents (`.claude/agents/*.md`).

**Alternatives considered:** Single monolithic `CLAUDE.md` (rejected — too long, attention dilutes). Multiple area-specific `CLAUDE.md` files only (rejected — does not address the review/specialist use case that subagents handle better).

**Consequences:** Cleaner top-of-context prompts. Subagents bring fresh-eyes review without bloating the main session. Requires the discipline of knowing which tier a piece of information belongs to.
```

---

## Appendix E — `.gitignore`

> **Save as:** `.gitignore` at repository root.
> **Purpose:** Keep secrets, large data, and machine-specific files out of git.

```
# Environment and secrets
.env
.env.local
.env.*.local
*.pem
*.key

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
ENV/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
build/
dist/

# Node / Next.js
node_modules/
.next/
out/
.turbo/
.vercel/

# IDE / Editor
.vscode/
.idea/
*.swp
*.swo

# Windows
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db
Desktop.ini
$RECYCLE.BIN/
*.lnk

# macOS (secondary dev machine artifacts)
.DS_Store
.AppleDouble
.LSOverride
Icon
._*
.Spotlight-V100
.Trashes

# Project-specific large or sensitive data
backups/
data/
logs/
models/*.pkl
models/*.joblib
notebooks/.ipynb_checkpoints/

# Database dumps
*.sql
*.dump

# Local Claude artifacts (optional — many projects commit .claude/agents/)
# .claude/
```

---

## Appendix F — Mac as Secondary Dev Machine

> **Purpose:** How to use the MacBook Pro for ThreadPulse development without splitting the data or breaking the production runtime on the Windows PC.

### The rule of one data source

PostgreSQL lives on the Windows PC. The collectors run on the Windows PC. The dashboard's "production" copy runs on the Windows PC. The Mac never holds production data. This is non-negotiable. Two independent PostgreSQL instances diverging silently is exactly the kind of data quality problem that corrupts ML training months later.

### What the Mac IS for

- Editing code (VSCode + Claude Code work identically on macOS)
- Running unit tests against a local **test database** (a tiny SQLite or local Postgres instance used only for tests, never for real signals)
- Reading the blueprint and decisions log
- Working with Claude on planning, grilling, design review, code review — none of which need the production database
- Pushing commits to GitHub, which the Windows PC then pulls

### What the Mac is NOT for

- Running live Reddit collectors (would create duplicate data once Windows pulls and runs)
- Running the APScheduler daemon
- Holding the "real" `threadpulse` database
- Generating production signals or labels
- Anything that writes to the real data store

### Minimal Mac setup

Only what you need to *edit and test*, not to *run*:

```bash
# Install Homebrew if not present, then:
brew install python@3.11 node@20 git
brew install --cask visual-studio-code
# Optionally for local tests only:
brew install postgresql@16
brew services start postgresql@16
```

Then clone the repo:
```bash
cd ~/Code   # or wherever you keep projects
git clone <your-github-url> GlobalStockResearch
cd GlobalStockResearch
python3.11 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

For the optional local test database on Mac: create a separate database named `threadpulse_test` (never `threadpulse`, to prevent accidents). Point your test suite at this via a `DATABASE_URL` override in a `.env.test` file. Production data never touches this database.

### Daily workflow across both machines

1. **On Windows (primary).** This machine is running 24/7. Collectors fire every 30 minutes. You work here when implementing collectors, running historical imports, checking the dashboard with real data.
2. **On Mac (secondary).** You open VSCode + Claude Code on the Mac when you want to write code somewhere comfortable. You edit files, run unit tests against the local test DB, commit, push.
3. **Sync.** At the start of any work session on either machine: `git pull`. At the end of any work session: `git push`. The repo is the only thing that crosses machines.
4. **Database access from Mac.** If you want to query the production database from the Mac (read-only is safer), you can: (a) open the Windows PC's PostgreSQL port to your local network and connect via pgAdmin on the Mac, or (b) just take a periodic `pg_dump` from Windows, copy it to the Mac, and restore into `threadpulse_readonly` for ad-hoc analysis. Option (b) is safer because you can't accidentally write to production.

### What about Claude Code on Mac?

Identical experience. The `.claude/agents/` files are committed to the repo, so they're available on both machines after `git pull`. `CLAUDE.md` is identical because the rules don't change based on OS. The only thing different is that when you run things locally on the Mac, you're using the test database — and Claude needs to know that. The simplest way is to update `docs/current_phase.md` at the start of a Mac session to add a line like `Working from Mac — point all DB operations at threadpulse_test, do not touch production data.` Claude will respect it.

### Edge case: the Windows PC is down

If your Windows PC crashes or needs to be reset, the Mac is your backup for *code* (via GitHub) but not for *data*. The nightly DB backup script from Phase 0.8 is what protects the data — make sure those backups land in cloud storage that the Mac can access too. Restore on the Windows PC once it's back up; the Mac is not the recovery target.

---

# DAY-ONE ACTION CHECKLIST

You have read the blueprint. Now you set up the operating system on the Windows PC and start Phase 0.1.

**One-time setup on the Windows PC (30-45 minutes):**

1. From `C:\Users\Ame\Downloads\GlobalStockResearch` in PowerShell, create the directory skeleton:
   ```powershell
   New-Item -ItemType Directory -Force -Path .claude\agents, docs, config, backend, frontend, notebooks, models, logs, backups, data
   ```
2. Save this entire blueprint as `docs\blueprint.md`.
3. From Appendix A, copy the contents into a new file `CLAUDE.md` at the repo root.
4. From Appendix B, copy each of the four subagent blocks into its own file inside `.claude\agents\` (`code-reviewer.md`, `grill-me.md`, `tech-debt-reviewer.md`, `design-reviewer.md`). Make sure each starts with the YAML frontmatter block (`---` lines).
5. From Appendix C, save the contents as `docs\current_phase.md`.
6. From Appendix D, save the contents as `docs\decisions.md`.
7. From Appendix E, save the contents as `.gitignore` at the repo root.
8. Commit and push:
   ```
   git add .
   git commit -m "set up project operating system: CLAUDE.md, subagents, docs"
   git push
   ```
9. Restart Claude Code (`Ctrl+C` then `claude` again in the terminal). Verify subagents are loaded by typing `/agents` — you should see all four listed.

**You are now ready to start Phase 0.1.** Open the terminal in VSCode, run `claude`, and your first message should be:

> Start a new session for Phase 0.1. Read CLAUDE.md and docs/current_phase.md. Walk me through Phase 0.1 step by step. I am on a Windows PC. Wait for me to confirm each install before moving on.

**Once Windows setup is stable, do the Mac side (15 minutes):**

10. On the MacBook Pro, clone the repo from GitHub.
11. Follow Appendix F's minimal Mac setup section.
12. Open VSCode + Claude Code on the Mac. The subagents and CLAUDE.md will already be there from the clone.
13. At the start of every Mac session, `git pull` first. At the end, `git push` before closing.

That's it. Everything else is in the blueprint. Your operating system is set up; the project itself is what you build from here.

---

*End of Master Blueprint v4.0 — Foundations + Full Project Specification*
*Windows-primary edition with Mac as secondary dev machine*
*For Claude Code v2.1.147 + Claude Max + Opus 4.7 with 1M context*
*Updated through integration of original ThreadPulse blueprint v3.0 + operating system layer*
