# Current Phase

> Phase 0.10 (Validate Environment) completed 2026-06-22. Definition of Done checks passed: `backend/validate_environment.py` runs ten checks and all PASS (exit 0) — Python 3.11.9; `config/config.yaml` loads via `yaml.safe_load`; PostgreSQL `threadpulse` reachable from Python (SQLAlchemy `SELECT 1`, DB name read from config + password from gitignored `backend/.env`, nothing hardcoded); virtualenv active; Node 20.20.2; psql 16.14; pg_dump 16.14 on PATH; git remote → GitHub; Ollama 0.30.9 present; system sleep = Never while plugged in. The script separates CORE checks (Python / config / DB / venv — fatal, exit 1 if any fail) from SUPPORTING checks (Node / psql / pg_dump / git / Ollama / sleep — WARN only, needed by later milestones) so it doubles as a one-command environment health check. Paths via `pathlib`, no secrets, no hardcoded thresholds.

> Phase 0.9 (Configure Windows Power Management and System Settings) completed 2026-06-22. Definition of Done checks passed: system sleep while plugged in set to **Never** (`powercfg /change standby-timeout-ac 0`, verified AC index `0x00000000`); Power mode set to **Best performance** (`powercfg /overlaysetactive ded574b5-45a0-4f42-8737-46345c09c238`); Windows Update **Active hours** set to 8 AM–11 PM (registry `ActiveHoursStart=8` / `ActiveHoursEnd=23`, auto-adjust off) via elevated PowerShell; project folder `GlobalStockResearch` added to **Windows Defender exclusions** (`Add-MpPreference -ExclusionPath`) via elevated PowerShell. The sleep and power-mode settings were applied programmatically and verified; the two admin-elevation settings (active hours, Defender) were run by the user. No application code (OS-configuration phase); the UTC timestamp rule was reaffirmed. **Milestone 0 (Environment Setup) is now fully complete — all phases 0.1–0.10 done. Next: Milestone 1 (Reddit Data Collection).**

> Phase 0.8 (Set Up Database Backup) completed 2026-06-22. Definition of Done checks passed: `backend/backup_database.py` runs `pg_dump` (custom/compressed `-Fc` format) against `threadpulse` and writes a UTC-timestamped dump (`threadpulse_YYYYMMDD_HHMMSS.dump`) into `backups/` — verified with two real runs whose archives `pg_restore --list` reads cleanly (849 bytes each; small because no tables exist yet); `backend/backup_scheduler.py` schedules the backup nightly via an APScheduler `BlockingScheduler` at the configured UTC hour with `coalesce=True` and a misfire grace window (cron wiring smoke-tested → next run 07:00 UTC); `pg_dump` runs without an absolute path (PostgreSQL 16 bin on PATH — `pg_dump (PostgreSQL) 16.14`); the password stays in gitignored `backend/.env` and is passed to `pg_dump` via the `PGPASSWORD` subprocess env var (never on the command line, never logged); `backups/` stays gitignored (`git check-ignore` matches the dumps; `git status` shows no backup files or secrets tracked); DB name, backup location, and nightly hour are all read from `config/config.yaml` (nothing hardcoded). **One DoD item deferred by user decision:** the off-machine copy. The code path exists and is config-driven (`copy_offsite` reads `system.offsite_backup_location`) but no-ops while that value is blank, so a real off-machine backup is not yet in place — to be enabled by setting the offsite path later. Dependency decision: `APScheduler==3.11.2` was installed early into `backend/.venv` and pinned in `backend/requirements.txt`, following the established "install early + pin" pattern. New `config/config.yaml` keys: `system.offsite_backup_location` (blank placeholder) and `system.backup_hour_utc: 7`.

> Phase 0.7 (Set Up PostgreSQL Database) completed 2026-06-16. Definition of Done checks passed: a database named `threadpulse` was created and is reachable on the local PostgreSQL 16 server; `backend/check_db_connection.py` opens a SQLAlchemy engine to `postgresql+psycopg2://postgres:<password>@localhost:5432/threadpulse`, runs `SELECT 1`, and prints `connection ok` (exit 0); the `postgres` password lives only in gitignored `backend/.env` (read via `python-dotenv`/`os.environ`) and the database name is read from `config/config.yaml` — neither is hardcoded and no secret is in any committed file; `git check-ignore` confirms `backend/.env` is ignored while `backend/.env.example` (a no-secret template) is tracked. Dependency decision: the DB libraries formally listed under Phase 1.2 were installed early and pinned in `backend/requirements.txt` (`SQLAlchemy==2.0.51`, `psycopg2-binary==2.9.12`, `python-dotenv==1.2.2`), following the Phase 0.5 "install early + pin" pattern (logged in `docs/decisions.md`).

> Phase 0.6 (Set Up Git and GitHub) completed 2026-06-16. Definition of Done checks passed: `git remote -v` confirms the repo is connected to GitHub (`origin → https://github.com/AmeShajid/GlobalStockResearch.git`); the existing root `.gitignore` was verified against Appendix E and already contained every required entry (`.env`, `backups/`, `data/`, `logs/`, `models/*.pkl` + `models/*.joblib`, `__pycache__/`, `.venv/`, `node_modules/`, `Thumbs.db`, `Desktop.ini`) — no edit needed; `backend/.venv/` is ignored (`git check-ignore` matches it, zero `.venv` files tracked), resolving the Phase 0.5 carry-over; `config/config.yaml` remains committed and tracked; no `.env`/secret files are tracked by git. The phase required no file changes — it was a verification pass that came up green.

> Phase 0.5 (Set Up Python Virtual Environment) completed 2026-06-16. Definition of Done checks passed: virtual environment created at `backend/.venv` (Python 3.11.9); activates with the `(.venv)` prefix via PowerShell with no execution-policy block needed; `backend/requirements.txt` created and pinned to `PyYAML==6.0.3`, rebuilds in one command (`pip install -r requirements.txt`); the deferred Phase 0.4 check now passes — `config/config.yaml` loads cleanly via `yaml.safe_load` (returned `config ok`); no secrets introduced. Note: `git status` showed all of `backend/` untracked including `backend/.venv/` — do not commit the venv; the `.gitignore` `.venv/` entry lands in Phase 0.6.

> Phase 0.4 (Create Project Folder Structure and Config File) completed 2026-06-02. Definition of Done checks passed: all ten folders exist (`frontend`, `backend`, `data`, `notebooks`, `models`, `docs`, `logs`, `backups`, `config`, `.claude\agents`); `config/config.yaml` created with all eight required sections populated with the blueprint's starting values; no secrets in the file; dependency-free structural check passed (8/8 sections present, no tabs). The full `yaml.safe_load` parse check was **deferred to Phase 0.5** (PyYAML is not yet installed — library installs are out of Phase 0.4 scope; logged in `docs/decisions.md`) and was completed in Phase 0.5.

> Phase 0.3 (Set Up VSCode Extensions) completed 2026-06-02. All seven extensions installed and verified via `code --list-extensions`. The blueprint's original PostgreSQL ID `ms-ossdata.vscode-postgresql` was deprecated; `ms-ossdata.vscode-pgsql` was used instead (logged in `docs/decisions.md`).

## Active phase
Phase 1.1 — Create a Reddit App (Milestone 1: Reddit Data Collection)

## What is in scope
- Create a Reddit **script** app at reddit.com/prefs/apps (logged into your Reddit account): name it **ThreadPulse**, set redirect URI to `http://localhost:8080`.
- Capture the generated **Client ID** and **Client Secret**.
- Store both in `backend/.env` (the same gitignored file that already holds `POSTGRES_PASSWORD`) as `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`; add matching no-secret placeholders to `backend/.env.example`.
- Confirm the credentials load from the environment (read via `os.environ` / `python-dotenv`), never hardcoded.

## What is explicitly out of scope
- Installing PRAW or any Python dependencies (Phase 1.2)
- Building the ticker dictionary / blocklist / exclusion list (Phase 1.3)
- Installing or wiring FinBERT (Phase 1.4)
- Defining Reddit database tables (Phase 1.5)
- Writing the collection script or making any live Reddit API call beyond an optional credential sanity check (Phase 1.6)

## Definition of Done
- A Reddit **script** app exists named ThreadPulse with redirect URI `http://localhost:8080`
- `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` are present in gitignored `backend/.env`
- `backend/.env.example` lists both keys as no-secret placeholders
- `git check-ignore backend/.env` confirms the secrets file is ignored; no credentials in any tracked file
- (No production code expected — this is a credential-setup phase)

## Notes
- Last updated: 2026-06-22
- This is largely a **manual, browser-based** step on Reddit's site — only you can create the app and obtain the credentials. Claude can add the `.env` / `.env.example` keys and a credential-load check, but cannot generate Reddit credentials.
- Critical Rule #2: credentials live only in `.env`, never in code or any committed file.
- Reddit API policy can change; the Arctic Shift historical dumps (Phase 1.8) are the insurance against any future live-API restriction.
- **Pacing plan (agreed):** scaffolding phases may be clustered (1.3 ticker/blocklist + 1.5 schema, then the code for 1.6/1.7), but the data-touching phases stay individually gated: 1.6 collector → 1.7 scheduler → 1.8 historical import → **1.9 validation**. The 1.9 mini-validation (85% ticker-extraction accuracy on 50 posts) is the MVP gate and is not to be rushed.
- After 1.1, move to Phase 1.2 (install Python dependencies — PRAW, spaCy, transformers, torch, feedparser, etc.).
- **Carry-over from Phase 0.8:** the off-machine backup copy is still inactive (config-driven, no-ops while `system.offsite_backup_location` is blank). Set that path when ready so the nightly backup actually lands off-machine.
