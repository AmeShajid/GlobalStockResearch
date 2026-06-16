# Current Phase

> Phase 0.5 (Set Up Python Virtual Environment) completed 2026-06-16. Definition of Done checks passed: virtual environment created at `backend/.venv` (Python 3.11.9); activates with the `(.venv)` prefix via PowerShell with no execution-policy block needed; `backend/requirements.txt` created and pinned to `PyYAML==6.0.3`, rebuilds in one command (`pip install -r requirements.txt`); the deferred Phase 0.4 check now passes — `config/config.yaml` loads cleanly via `yaml.safe_load` (returned `config ok`); no secrets introduced. Note: `git status` showed all of `backend/` untracked including `backend/.venv/` — do not commit the venv; the `.gitignore` `.venv/` entry lands in Phase 0.6.

> Phase 0.4 (Create Project Folder Structure and Config File) completed 2026-06-02. Definition of Done checks passed: all ten folders exist (`frontend`, `backend`, `data`, `notebooks`, `models`, `docs`, `logs`, `backups`, `config`, `.claude\agents`); `config/config.yaml` created with all eight required sections populated with the blueprint's starting values; no secrets in the file; dependency-free structural check passed (8/8 sections present, no tabs). The full `yaml.safe_load` parse check was **deferred to Phase 0.5** (PyYAML is not yet installed — library installs are out of Phase 0.4 scope; logged in `docs/decisions.md`) and was completed in Phase 0.5.

> Phase 0.3 (Set Up VSCode Extensions) completed 2026-06-02. All seven extensions installed and verified via `code --list-extensions`. The blueprint's original PostgreSQL ID `ms-ossdata.vscode-postgresql` was deprecated; `ms-ossdata.vscode-pgsql` was used instead (logged in `docs/decisions.md`).

## Active phase
Phase 0.6 — Set Up Git and GitHub

## What is in scope
- Confirm the repository is connected to GitHub: `git remote -v`.
- Verify and update the existing `.gitignore` at the repository root (we already have one from earlier setup — do not create a fresh file; see Appendix E in `docs/blueprint.md` for the full template). At minimum confirm it contains:
  - `.env`
  - `backups/`, `data/`, `logs/`, `models/`
  - `__pycache__/`, `.venv/`, `node_modules/`
  - `Thumbs.db`, `desktop.ini`
- Secrets handling (per Critical Rule #2): all credentials live in `.env`, which is gitignored. `config/config.yaml` contains **no secrets** and must stay committed — every later ThreadPulse script reads from it, so it has to be present in fresh checkouts. Do **not** add `config.yaml` to `.gitignore`.
- Carry-over from Phase 0.5: ensure `.venv/` is in `.gitignore` so `backend/.venv/` is never committed (it currently shows as untracked).
- Commit and push after every meaningful work session.

## What is explicitly out of scope
- Database creation in pgAdmin (Phase 0.7)
- Database backup script (Phase 0.8)
- Heavy library installs such as PyTorch/FinBERT (Phase 1.2)
- Writing collector/application code (Milestone 1+)
- Mac setup (handled in Appendix F separately, not now)

## Definition of Done
- `git remote -v` confirms the repo is connected to GitHub
- The existing `.gitignore` at the repository root contains the entries listed above
- `backend/.venv/` is ignored by git (no longer appears as untracked content to commit)
- `config/config.yaml` remains committed (it contains no secrets and is required by later scripts)
- No credentials or secrets are tracked by git (secrets live only in `.env`)
- Changes are committed (and pushed) following the branch workflow

## Notes
- Last updated: 2026-06-16
- A `.gitignore` already exists and is tracked (from earlier setup) — this phase verifies/updates it, it does not create one. The full template lives in Appendix E of `docs/blueprint.md`.
- `config/config.yaml` is safe to commit and stays in version control; only `.env` holds secrets and only `.env` is gitignored.
- Phase 0.5 flagged that `backend/.venv/` currently shows as untracked; adding/confirming the `.venv/` entry in `.gitignore` here resolves it.
- After completion, move to Phase 0.7 (Set Up PostgreSQL Database).
