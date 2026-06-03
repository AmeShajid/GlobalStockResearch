# Current Phase

> Phase 0.4 (Create Project Folder Structure and Config File) completed 2026-06-02. Definition of Done checks passed: all ten folders exist (`frontend`, `backend`, `data`, `notebooks`, `models`, `docs`, `logs`, `backups`, `config`, `.claude\agents`); `config/config.yaml` created with all eight required sections populated with the blueprint's starting values; no secrets in the file; dependency-free structural check passed (8/8 sections present, no tabs). The full `yaml.safe_load` parse check was **deferred to Phase 0.5** (PyYAML is not yet installed — library installs are out of Phase 0.4 scope; logged in `docs/decisions.md`).

> Phase 0.3 (Set Up VSCode Extensions) completed 2026-06-02. All seven extensions installed and verified via `code --list-extensions`. The blueprint's original PostgreSQL ID `ms-ossdata.vscode-postgresql` was deprecated; `ms-ossdata.vscode-pgsql` was used instead (logged in `docs/decisions.md`).

## Active phase
Phase 0.5 — Set Up Python Virtual Environment

## What is in scope
- Inside the `backend` folder, create a Python virtual environment:
  `python -m venv .venv`
- Activate it and confirm the `(.venv)` prefix appears in the prompt:
  - **PowerShell:** `.\.venv\Scripts\Activate.ps1`
    - If PowerShell blocks the script, run once: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
  - **cmd.exe:** `.venv\Scripts\activate.bat`
  - **Git Bash:** `source .venv/Scripts/activate`
- Create `backend/requirements.txt` and keep it updated with every library installed. `pip install -r requirements.txt` should be able to rebuild the environment in one command.
- **Carry-over from Phase 0.4:** run the deferred `config.yaml` parse validation as one of the first verification tasks once a YAML parser is available in the venv (`python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('config/config.yaml').read_text()); print('config ok')"`). This requires PyYAML — add it to `requirements.txt` and install it into the venv.

## What is explicitly out of scope
- Git/GitHub configuration and `.gitignore` (Phase 0.6)
- Database creation in pgAdmin (Phase 0.7)
- Database backup script (Phase 0.8)
- Heavy library installs such as PyTorch/FinBERT (Phase 1.2)
- Writing collector/application code (Milestone 1+)
- Mac setup (handled in Appendix F separately, not now)

## Definition of Done
- A virtual environment exists at `backend/.venv`
- The environment activates and the `(.venv)` prefix appears in the prompt
- `backend/requirements.txt` exists and lists the libraries installed so far
- The deferred Phase 0.4 check passes: `config/config.yaml` loads cleanly via `yaml.safe_load` (PyYAML installed in the venv)
- No credentials or secrets introduced

## Notes
- Last updated: 2026-06-02
- Decision 2026-06-01 (Keep Microsoft Store Python 3.11.9) flagged Phase 0.5 as the point to revisit if virtual-environment issues arise — watch for sandboxed-path quirks when creating/activating the venv.
- Per the Phase 0.4 deferral decision, completing the `yaml.safe_load` validation is part of Phase 0.5's first verification tasks.
- After completion, move to Phase 0.6 (Set Up Git and GitHub).
