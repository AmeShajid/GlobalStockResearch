# Current Phase

> Phase 0.8 (Set Up Database Backup) completed 2026-06-22. Definition of Done checks passed: `backend/backup_database.py` runs `pg_dump` (custom/compressed `-Fc` format) against `threadpulse` and writes a UTC-timestamped dump (`threadpulse_YYYYMMDD_HHMMSS.dump`) into `backups/` — verified with two real runs whose archives `pg_restore --list` reads cleanly (849 bytes each; small because no tables exist yet); `backend/backup_scheduler.py` schedules the backup nightly via an APScheduler `BlockingScheduler` at the configured UTC hour with `coalesce=True` and a misfire grace window (cron wiring smoke-tested → next run 07:00 UTC); `pg_dump` runs without an absolute path (PostgreSQL 16 bin on PATH — `pg_dump (PostgreSQL) 16.14`); the password stays in gitignored `backend/.env` and is passed to `pg_dump` via the `PGPASSWORD` subprocess env var (never on the command line, never logged); `backups/` stays gitignored (`git check-ignore` matches the dumps; `git status` shows no backup files or secrets tracked); DB name, backup location, and nightly hour are all read from `config/config.yaml` (nothing hardcoded). **One DoD item deferred by user decision:** the off-machine copy. The code path exists and is config-driven (`copy_offsite` reads `system.offsite_backup_location`) but no-ops while that value is blank, so a real off-machine backup is not yet in place — to be enabled by setting the offsite path later. Dependency decision: `APScheduler==3.11.2` was installed early into `backend/.venv` and pinned in `backend/requirements.txt`, following the established "install early + pin" pattern. New `config/config.yaml` keys: `system.offsite_backup_location` (blank placeholder) and `system.backup_hour_utc: 7`.

> Phase 0.7 (Set Up PostgreSQL Database) completed 2026-06-16. Definition of Done checks passed: a database named `threadpulse` was created and is reachable on the local PostgreSQL 16 server; `backend/check_db_connection.py` opens a SQLAlchemy engine to `postgresql+psycopg2://postgres:<password>@localhost:5432/threadpulse`, runs `SELECT 1`, and prints `connection ok` (exit 0); the `postgres` password lives only in gitignored `backend/.env` (read via `python-dotenv`/`os.environ`) and the database name is read from `config/config.yaml` — neither is hardcoded and no secret is in any committed file; `git check-ignore` confirms `backend/.env` is ignored while `backend/.env.example` (a no-secret template) is tracked. Dependency decision: the DB libraries formally listed under Phase 1.2 were installed early and pinned in `backend/requirements.txt` (`SQLAlchemy==2.0.51`, `psycopg2-binary==2.9.12`, `python-dotenv==1.2.2`), following the Phase 0.5 "install early + pin" pattern (logged in `docs/decisions.md`).

> Phase 0.6 (Set Up Git and GitHub) completed 2026-06-16. Definition of Done checks passed: `git remote -v` confirms the repo is connected to GitHub (`origin → https://github.com/AmeShajid/GlobalStockResearch.git`); the existing root `.gitignore` was verified against Appendix E and already contained every required entry (`.env`, `backups/`, `data/`, `logs/`, `models/*.pkl` + `models/*.joblib`, `__pycache__/`, `.venv/`, `node_modules/`, `Thumbs.db`, `Desktop.ini`) — no edit needed; `backend/.venv/` is ignored (`git check-ignore` matches it, zero `.venv` files tracked), resolving the Phase 0.5 carry-over; `config/config.yaml` remains committed and tracked; no `.env`/secret files are tracked by git. The phase required no file changes — it was a verification pass that came up green.

> Phase 0.5 (Set Up Python Virtual Environment) completed 2026-06-16. Definition of Done checks passed: virtual environment created at `backend/.venv` (Python 3.11.9); activates with the `(.venv)` prefix via PowerShell with no execution-policy block needed; `backend/requirements.txt` created and pinned to `PyYAML==6.0.3`, rebuilds in one command (`pip install -r requirements.txt`); the deferred Phase 0.4 check now passes — `config/config.yaml` loads cleanly via `yaml.safe_load` (returned `config ok`); no secrets introduced. Note: `git status` showed all of `backend/` untracked including `backend/.venv/` — do not commit the venv; the `.gitignore` `.venv/` entry lands in Phase 0.6.

> Phase 0.4 (Create Project Folder Structure and Config File) completed 2026-06-02. Definition of Done checks passed: all ten folders exist (`frontend`, `backend`, `data`, `notebooks`, `models`, `docs`, `logs`, `backups`, `config`, `.claude\agents`); `config/config.yaml` created with all eight required sections populated with the blueprint's starting values; no secrets in the file; dependency-free structural check passed (8/8 sections present, no tabs). The full `yaml.safe_load` parse check was **deferred to Phase 0.5** (PyYAML is not yet installed — library installs are out of Phase 0.4 scope; logged in `docs/decisions.md`) and was completed in Phase 0.5.

> Phase 0.3 (Set Up VSCode Extensions) completed 2026-06-02. All seven extensions installed and verified via `code --list-extensions`. The blueprint's original PostgreSQL ID `ms-ossdata.vscode-postgresql` was deprecated; `ms-ossdata.vscode-pgsql` was used instead (logged in `docs/decisions.md`).

## Active phase
Phase 0.9 — Configure Windows Power Management and System Settings

## What is in scope
- Set system sleep to **Never** while plugged in (Settings → System → Power & battery → Screen and sleep) so collectors keep running. The screen-off timer can stay as-is — only system sleep matters.
- Set Power mode to **Best performance** while plugged in.
- Keep the production machine plugged in (battery operation not recommended).
- Set Windows Update **Active hours** to cover the typical working day (e.g. 8 AM – 11 PM) so scheduled restarts don't interrupt work.
- Add the project folder to **Windows Defender exclusions** (Virus & threat protection → Exclusions → Add folder) to prevent mid-run quarantines and I/O throttling during imports.
- Reaffirm the UTC timestamp rule (all stored timestamps in UTC; local time is display-only).

## What is explicitly out of scope
- The startup/auto-recovery script and Task Scheduler registration (Phase 7.13)
- Full environment validation sweep (Phase 0.10)
- Any collector/application code or database schemas (Milestone 1+)
- Library installs (none needed for this phase — these are OS settings)

## Definition of Done
- System will not sleep while plugged in (sleep set to Never)
- Power mode set to Best performance while plugged in
- Windows Update Active hours configured to cover the working day
- Project folder added to Windows Defender exclusions
- (No code changes expected — this is an OS configuration phase; nothing to commit unless docs are updated)

## Notes
- Last updated: 2026-06-22
- This is a Windows Settings / OS-configuration phase — the steps are performed in the Windows UI, not in code. There is likely nothing to commit beyond the doc updates made by the Phase End Ritual.
- The auto-recovery-after-reboot piece is intentionally deferred: Phase 7.13 builds the startup script registered in Task Scheduler. Active hours here only prevents reboots *during* work hours; it does not handle restart recovery.
- The UTC timestamp rule established back in Milestone 0 is reaffirmed here and must never be violated — every script that writes a timestamp converts to UTC before storing; only the dashboard converts to local time for display.
- After completion, move to Phase 0.10 (Validate Environment) — the final Milestone 0 sweep.
- **Carry-over from Phase 0.8:** the off-machine backup copy is still inactive (config-driven, no-ops while `system.offsite_backup_location` is blank). Not part of Phase 0.9's DoD, but set that path when ready so the nightly backup actually lands off-machine.
