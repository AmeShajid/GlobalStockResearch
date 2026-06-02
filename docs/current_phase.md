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
