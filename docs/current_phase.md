# Current Phase

> Phase 0.2 (Install Ollama — Windows) completed 2026-06-01. All Definition of Done checks passed: Ollama 0.30.0 installed via winget, qwen2.5 pulled (4.7GB), llama3 pulled (4.7GB), test prompt `ollama run qwen2.5 "say hello"` returned a reply.

## Active phase
Phase 0.3 — Set Up VSCode Extensions

## What is in scope
- Install the following VSCode extensions:
  - Python
  - Pylance
  - ESLint
  - Prettier
  - PostgreSQL — specifically the `ms-ossdata.vscode-postgresql` extension
  - GitLens
  - Jupyter

## What is explicitly out of scope
- Project folder structure and config file (Phase 0.4)
- Python virtual environment setup (Phase 0.5)
- Git/GitHub configuration and `.gitignore` (Phase 0.6)
- Database creation in pgAdmin (Phase 0.7)
- Any Python library installation, including PyTorch/FinBERT (Phase 1.2)
- Any other milestone work
- Mac setup (handled in Appendix F separately, not now)

## Definition of Done
- All seven extensions are installed and enabled in VSCode:
  Python, Pylance, ESLint, Prettier, PostgreSQL (`ms-ossdata.vscode-postgresql`), GitLens, Jupyter
- Each extension appears in the VSCode Extensions panel as installed (not just searched)

## Notes
- Last updated: 2026-06-01
- Estimated time to complete: 5-15 minutes (extension downloads are small)
- Pylance is the language server that powers Python IntelliSense; it installs alongside the Python extension but confirm it is present and enabled.
- ESLint and Prettier are for the Next.js/React frontend (Milestone 7); install them now so the environment is ready.
- The PostgreSQL extension has multiple options in the marketplace — install the official `ms-ossdata.vscode-postgresql` one specifically.
- After completion, move to Phase 0.4 (Create Project Folder Structure and Config File)
