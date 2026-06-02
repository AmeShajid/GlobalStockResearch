# Current Phase

> Phase 0.3 (Set Up VSCode Extensions) completed 2026-06-02. All Definition of Done checks passed: seven extensions installed and verified via `code --list-extensions` — `ms-python.python`, `ms-python.vscode-pylance`, `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`, `ms-ossdata.vscode-pgsql`, `eamodio.gitlens`, `ms-toolsai.jupyter`. Note: the blueprint's original PostgreSQL ID `ms-ossdata.vscode-postgresql` was deprecated/uninstallable; the current official `ms-ossdata.vscode-pgsql` was used instead (logged in `docs/decisions.md`).

## Active phase
Phase 0.4 — Create Project Folder Structure and Config File

## What is in scope
- Create these subfolders in the repo root if not already present:
  `frontend`, `backend`, `data`, `notebooks`, `models`, `docs`, `logs`, `backups`, `config`, `.claude\agents`
  - PowerShell one-liner from the blueprint:
    `New-Item -ItemType Directory -Force -Path frontend, backend, data, notebooks, models, docs, logs, backups, config, .claude\agents`
- Create `config/config.yaml` — the single source of truth for every threshold, time window, and parameter. Every script reads from this file; thresholds are never hardcoded.
- `config.yaml` must contain at minimum these sections:
  - **Reddit signal thresholds** — min mention count (10), min velocity increase (50%), min sentiment confidence (60%), collection interval minutes (30), target subreddits list
  - **Insider signal thresholds** — min transaction value ($100,000), high significance ($500,000), very high significance ($1,000,000), lookback window days (30)
  - **Overlap detection time windows** — Reddit window hours (48), insider window days (14)
  - **Price movement thresholds** — flat significance % (3%), volatility multiplier (1.5), measurement intervals in trading days (1, 3, 7, 14, 30)
  - **ML thresholds** — min labeled examples per category before training (300), model degradation F1-drop alert threshold (0.05)
  - **System settings** — timezone (UTC), database name, log file location, backup location
  - **Exclusion list** — tickers/company names never to track (starts empty, grown over time)
  - **Blocklist** — valid ticker symbols that are also common English words, never extracted as tickers

## What is explicitly out of scope
- Python virtual environment setup (Phase 0.5)
- Git/GitHub configuration and `.gitignore` (Phase 0.6)
- Database creation in pgAdmin (Phase 0.7)
- Database backup script (Phase 0.8)
- Any Python library installation, including PyTorch/FinBERT (Phase 1.2)
- Writing code that *reads* config.yaml (later phases) — this phase only creates the file
- Any other milestone work
- Mac setup (handled in Appendix F separately, not now)

## Definition of Done
- All ten folders exist in the repo root: `frontend`, `backend`, `data`, `notebooks`, `models`, `docs`, `logs`, `backups`, `config`, `.claude\agents`
- `config/config.yaml` exists and is valid YAML (parses without error)
- `config.yaml` contains all eight required sections listed in scope, each populated with the blueprint's starting values
- No credentials or secrets in `config.yaml` (secrets live in `.env`, handled in Phase 0.6)
- File is readable by a simple Python check (e.g. `python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('config/config.yaml').read_text()); print('config ok')"`)

## Notes
- Last updated: 2026-06-02
- `docs` already exists; the `New-Item -Force` command is safe to run over existing folders (it does not overwrite their contents).
- Some folders (`data/`, `logs/`, `models/`, `backups/`) will later be gitignored (Phase 0.6) — creating them now is fine; they may need a `.gitkeep` if you want the empty folders tracked.
- All thresholds in `config.yaml` are starting values; they get refined during quarterly tuning in Milestone 11 by editing this one file.
- Reinforces Critical Rule #1 (never hardcode thresholds) — every later script reads from this file.
- After completion, move to Phase 0.5 (Set Up Python Virtual Environment)
