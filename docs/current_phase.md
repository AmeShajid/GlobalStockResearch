# Current Phase

> Phase 0.7 (Set Up PostgreSQL Database) completed 2026-06-16. Definition of Done checks passed: a database named `threadpulse` was created and is reachable on the local PostgreSQL 16 server; `backend/check_db_connection.py` opens a SQLAlchemy engine to `postgresql+psycopg2://postgres:<password>@localhost:5432/threadpulse`, runs `SELECT 1`, and prints `connection ok` (exit 0); the `postgres` password lives only in gitignored `backend/.env` (read via `python-dotenv`/`os.environ`) and the database name is read from `config/config.yaml` — neither is hardcoded and no secret is in any committed file; `git check-ignore` confirms `backend/.env` is ignored while `backend/.env.example` (a no-secret template) is tracked. Dependency decision: the DB libraries formally listed under Phase 1.2 were installed early and pinned in `backend/requirements.txt` (`SQLAlchemy==2.0.51`, `psycopg2-binary==2.9.12`, `python-dotenv==1.2.2`), following the Phase 0.5 "install early + pin" pattern (logged in `docs/decisions.md`).

> Phase 0.6 (Set Up Git and GitHub) completed 2026-06-16. Definition of Done checks passed: `git remote -v` confirms the repo is connected to GitHub (`origin → https://github.com/AmeShajid/GlobalStockResearch.git`); the existing root `.gitignore` was verified against Appendix E and already contained every required entry (`.env`, `backups/`, `data/`, `logs/`, `models/*.pkl` + `models/*.joblib`, `__pycache__/`, `.venv/`, `node_modules/`, `Thumbs.db`, `Desktop.ini`) — no edit needed; `backend/.venv/` is ignored (`git check-ignore` matches it, zero `.venv` files tracked), resolving the Phase 0.5 carry-over; `config/config.yaml` remains committed and tracked; no `.env`/secret files are tracked by git. The phase required no file changes — it was a verification pass that came up green.

> Phase 0.5 (Set Up Python Virtual Environment) completed 2026-06-16. Definition of Done checks passed: virtual environment created at `backend/.venv` (Python 3.11.9); activates with the `(.venv)` prefix via PowerShell with no execution-policy block needed; `backend/requirements.txt` created and pinned to `PyYAML==6.0.3`, rebuilds in one command (`pip install -r requirements.txt`); the deferred Phase 0.4 check now passes — `config/config.yaml` loads cleanly via `yaml.safe_load` (returned `config ok`); no secrets introduced. Note: `git status` showed all of `backend/` untracked including `backend/.venv/` — do not commit the venv; the `.gitignore` `.venv/` entry lands in Phase 0.6.

> Phase 0.4 (Create Project Folder Structure and Config File) completed 2026-06-02. Definition of Done checks passed: all ten folders exist (`frontend`, `backend`, `data`, `notebooks`, `models`, `docs`, `logs`, `backups`, `config`, `.claude\agents`); `config/config.yaml` created with all eight required sections populated with the blueprint's starting values; no secrets in the file; dependency-free structural check passed (8/8 sections present, no tabs). The full `yaml.safe_load` parse check was **deferred to Phase 0.5** (PyYAML is not yet installed — library installs are out of Phase 0.4 scope; logged in `docs/decisions.md`) and was completed in Phase 0.5.

> Phase 0.3 (Set Up VSCode Extensions) completed 2026-06-02. All seven extensions installed and verified via `code --list-extensions`. The blueprint's original PostgreSQL ID `ms-ossdata.vscode-postgresql` was deprecated; `ms-ossdata.vscode-pgsql` was used instead (logged in `docs/decisions.md`).

## Active phase
Phase 0.8 — Set Up Database Backup

## What is in scope
- Write a Python script that exports the entire `threadpulse` PostgreSQL database to a compressed file in the `backups/` folder, using `pg_dump` under the hood.
- Schedule the backup to run nightly via APScheduler.
- Copy each backup off the machine (Google Drive or an external drive) — a backup that only lives on the same machine as the original is not a real backup.
- Confirm `pg_dump` is callable without an absolute path (its bin directory `C:\Program Files\PostgreSQL\16\bin` must be on PATH — already added in Phase 0.1; verify it covers `pg_dump.exe`).
- Read the backup location and database name from `config/config.yaml`; read the password from `backend/.env`. Never hardcode thresholds, paths, or secrets.

## What is explicitly out of scope
- Defining database tables / schemas (Milestone 1+ — Reddit tables in Phase 1.5, price/context tables in Phase 2.2)
- Windows power management settings (Phase 0.9)
- Full environment validation sweep (Phase 0.10)
- Heavy library installs such as PyTorch/FinBERT (Phase 1.2)
- Writing collector/application code (Milestone 1+)

## Definition of Done
- A Python backup script exists that runs `pg_dump` against `threadpulse` and writes a compressed dump into `backups/`
- The script is scheduled to run nightly via APScheduler
- Each backup is copied to an off-machine location (Google Drive or external drive)
- `pg_dump` runs without an absolute path (PostgreSQL 16 bin directory confirmed on PATH)
- The password stays in gitignored `backend/.env`; no secrets in any committed file; `backups/` stays gitignored
- Changes are committed (and pushed) following the branch workflow

## Notes
- Last updated: 2026-06-16
- PostgreSQL 16 is already installed and runs as the `postgresql-x64-16` Windows service (Phase 0.1); `psql` is on PATH (per `docs/decisions.md`, the bin directory was added manually). `pg_dump.exe` lives in the same bin directory, so it should already be on PATH — verify at phase start.
- **Library dependency to decide at phase start:** the scheduler needs `APScheduler` in `backend/.venv`. It is not yet installed; install it early and pin it in `requirements.txt` (same "install early + pin" pattern used for the DB libraries in Phase 0.7 and PyYAML in Phase 0.5), and log the choice in `docs/decisions.md`.
- The DB connection libraries (`SQLAlchemy`, `psycopg2-binary`, `python-dotenv`) are already installed and pinned from Phase 0.7; reuse `backend/.env` for the password and `config/config.yaml` (`system.backup_location`, `system.database_name`) for paths.
- Estimated database size after one year: ~20-50GB depending on historical import volume — keep an eye on free space on the PostgreSQL data drive.
- After completion, move to Phase 0.9 (Configure Windows Power Management and System Settings).
