# Current Phase

> Phase 0.6 (Set Up Git and GitHub) completed 2026-06-16. Definition of Done checks passed: `git remote -v` confirms the repo is connected to GitHub (`origin → https://github.com/AmeShajid/GlobalStockResearch.git`); the existing root `.gitignore` was verified against Appendix E and already contained every required entry (`.env`, `backups/`, `data/`, `logs/`, `models/*.pkl` + `models/*.joblib`, `__pycache__/`, `.venv/`, `node_modules/`, `Thumbs.db`, `Desktop.ini`) — no edit needed; `backend/.venv/` is ignored (`git check-ignore` matches it, zero `.venv` files tracked), resolving the Phase 0.5 carry-over; `config/config.yaml` remains committed and tracked; no `.env`/secret files are tracked by git. The phase required no file changes — it was a verification pass that came up green.

> Phase 0.5 (Set Up Python Virtual Environment) completed 2026-06-16. Definition of Done checks passed: virtual environment created at `backend/.venv` (Python 3.11.9); activates with the `(.venv)` prefix via PowerShell with no execution-policy block needed; `backend/requirements.txt` created and pinned to `PyYAML==6.0.3`, rebuilds in one command (`pip install -r requirements.txt`); the deferred Phase 0.4 check now passes — `config/config.yaml` loads cleanly via `yaml.safe_load` (returned `config ok`); no secrets introduced. Note: `git status` showed all of `backend/` untracked including `backend/.venv/` — do not commit the venv; the `.gitignore` `.venv/` entry lands in Phase 0.6.

> Phase 0.4 (Create Project Folder Structure and Config File) completed 2026-06-02. Definition of Done checks passed: all ten folders exist (`frontend`, `backend`, `data`, `notebooks`, `models`, `docs`, `logs`, `backups`, `config`, `.claude\agents`); `config/config.yaml` created with all eight required sections populated with the blueprint's starting values; no secrets in the file; dependency-free structural check passed (8/8 sections present, no tabs). The full `yaml.safe_load` parse check was **deferred to Phase 0.5** (PyYAML is not yet installed — library installs are out of Phase 0.4 scope; logged in `docs/decisions.md`) and was completed in Phase 0.5.

> Phase 0.3 (Set Up VSCode Extensions) completed 2026-06-02. All seven extensions installed and verified via `code --list-extensions`. The blueprint's original PostgreSQL ID `ms-ossdata.vscode-postgresql` was deprecated; `ms-ossdata.vscode-pgsql` was used instead (logged in `docs/decisions.md`).

## Active phase
Phase 0.7 — Set Up PostgreSQL Database

## What is in scope
- Open pgAdmin, connect to the local PostgreSQL server (the default local server should appear automatically; authenticate with the `postgres` master password set in Phase 0.1).
- Create a database named `threadpulse`.
- Verify the connection from Python: a one-line script opens a SQLAlchemy engine to `postgresql://postgres:<password>@localhost:5432/threadpulse` and prints `connection ok`.
- Store the `postgres` password in `.env` (gitignored), **never** in code. Read it from the environment in the verification script.

## What is explicitly out of scope
- Defining database tables / schemas (Milestone 1+ — Reddit tables in Phase 1.5, price/context tables in Phase 2.2)
- Database backup script and `pg_dump`/PATH setup (Phase 0.8)
- Windows power management settings (Phase 0.9)
- Full environment validation sweep (Phase 0.10)
- Heavy library installs such as PyTorch/FinBERT (Phase 1.2)
- Writing collector/application code (Milestone 1+)

## Definition of Done
- A database named `threadpulse` exists and is reachable in pgAdmin
- A Python script using a SQLAlchemy engine connects to `threadpulse` and prints `connection ok`
- The `postgres` password lives only in `.env` (gitignored) and is read from the environment — it is not present in any committed file
- `.env` remains gitignored; no secrets are tracked by git
- Changes are committed (and pushed) following the branch workflow

## Notes
- Last updated: 2026-06-16
- PostgreSQL 16 is already installed and runs as the `postgresql-x64-16` Windows service (Phase 0.1); `psql` is on PATH (per `docs/decisions.md`, the bin directory was added manually).
- **Library dependency to decide at phase start:** the SQLAlchemy connection check needs `SQLAlchemy` + a Postgres driver (`psycopg2-binary`) in the venv. These are listed under Phase 1.2, so either install them early into `backend/.venv` and pin them in `requirements.txt` (preferred — the same pattern used when PyYAML was added in Phase 0.5), or defer the SQLAlchemy parse-style check the way the Phase 0.4 YAML check was deferred. Log whichever choice in `docs/decisions.md`.
- Keep the password out of code: store as e.g. `POSTGRES_PASSWORD=...` in `backend/.env` and load via `python-dotenv`/`os.environ`. Never hardcode `C:\...` paths or the password.
- After completion, move to Phase 0.8 (Set Up Database Backup).
