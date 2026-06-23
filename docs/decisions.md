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

### 2026-06-01 — Install Node 20 via nvm-windows rather than the direct installer

**Context:** Phase 0.1 calls for Node.js 20 LTS. The machine initially had Node v24 installed, which is outside the spec.

**Decision:** Use nvm-windows (Node Version Manager for Windows) to install and select Node 20 LTS, rather than the direct nodejs.org Windows installer. Rationale: nvm-windows keeps multiple Node versions available side-by-side. We had v24 installed initially and needed to swap to v20 LTS for spec compliance; nvm makes that a one-command switch and lets us return to other versions without reinstalling.

**Alternatives considered:** Direct nodejs.org .msi installer (rejected — it manages only a single global Node version, so swapping away from the pre-existing v24 and keeping the option to switch back is awkward). Uninstalling v24 and installing v20 via .msi (rejected — loses the ability to keep multiple versions side-by-side).

**Consequences:** Easier to satisfy the spec's exact-version requirement and to change Node versions later. Adds nvm-windows as a tool the developer must be aware of (the active version is set with `nvm use`, not by reinstalling).

### 2026-06-01 — Keep Microsoft Store Python 3.11.9 instead of the python.org build

**Context:** Phase 0.1 requires `python --version` to report 3.11.x. The machine already had Python 3.11.9 installed from the Microsoft Store, while the blueprint's install instructions describe the python.org installer.

**Decision:** Keep the existing Microsoft Store Python 3.11.9 build for now. Rationale: it passes the Phase 0.1 DoD as-is. The Microsoft Store build is a known quantity and avoids an unnecessary reinstall. We may revisit in Phase 0.5 if virtual-environment issues arise.

**Alternatives considered:** Uninstall and reinstall from python.org (rejected for now — the Store build already passes the Definition of Done, so reinstalling is effort without immediate benefit).

**Consequences:** Phase 0.1 is satisfied without extra work. The Store build sandboxes some paths differently from the python.org build, which can occasionally affect virtual environments and global tool installs. We may revisit this in Phase 0.5 if virtual-environment issues arise.

### 2026-06-01 — Manually add PostgreSQL 16 bin directory to system PATH

**Context:** After installing PostgreSQL 16 via the EnterpriseDB Windows installer, `psql` was not findable from any terminal even though the `postgresql-x64-16` Windows service was running and pgAdmin connected fine.

**Decision:** Manually add `C:\Program Files\PostgreSQL\16\bin` to the system PATH. Rationale: the EnterpriseDB installer does not add the bin directory to PATH automatically on Windows 11. Without this, `psql` and the other command-line tools are not on PATH despite the database itself running correctly. This is a Windows-specific gotcha worth remembering for future PostgreSQL installs.

**Alternatives considered:** Always invoking `psql` by full path (rejected — tedious and error-prone). Relying on pgAdmin only (rejected — command-line `psql` is needed for scripts and verification steps).

**Consequences:** `psql` and the PostgreSQL CLI tools now work from any terminal, which the Phase 0.1 DoD and later verification steps depend on. Future PostgreSQL upgrades to a new major version will need the PATH updated to the new version's bin directory.

### 2026-06-01 — CPU-only inference path for FinBERT and Ollama (AMD GPU on primary machine)

**Context:** The primary Windows machine has an AMD GPU, not an NVIDIA one, so CUDA acceleration is unavailable for FinBERT (PyTorch) and Ollama.

**Decision:** Run FinBERT and Ollama inference CPU-only on this machine. Do not install CUDA Toolkit or treat `nvidia-smi`/`torch.cuda.is_available()` as part of the Definition of Done. Rationale: Ollama runs fine on CPU, just slower than on NVIDIA. The 2-hour summary cache from Phase 7.4 absorbs the latency, since summaries are not regenerated constantly. FinBERT inference will be a few seconds per post, which is acceptable in batched mode.

**Alternatives considered:** Pursuing AMD GPU acceleration via ROCm/DirectML (rejected — immature and unsupported on Windows for this stack, high setup cost for a personal tool). Buying/using an NVIDIA GPU (rejected — out of scope for a personal project right now).

**Consequences:** No CUDA dependency to manage; the GPU-related Phase 0.2 steps are skipped on this machine. Inference is slower, so historical/batch imports should favor off-peak or overnight runs. The sequential FinBERT-then-Ollama constraint still applies (both compete for CPU/RAM). If throughput becomes a problem later, an NVIDIA GPU would unlock CUDA without code changes (PyTorch picks up CUDA automatically).

### 2026-06-01 — qwen2.5 first-token latency on CPU is noticeable; rely on the Phase 7.4 summary cache

**Context:** During Phase 0.2 verification, the first `ollama run qwen2.5 "say hello"` took noticeably long — roughly 1-2 minutes for the initial model load plus first response. This is the expected behavior of CPU-only inference (AMD GPU on this machine, no CUDA — see prior entry), where the ~4.7GB model must be loaded from disk into RAM before the first token is produced.

**Decision:** Treat noticeable cold-start latency as a known, accepted characteristic of CPU-only Ollama on this machine rather than a problem to optimize away now. Lean on the 2-hour summary cache from Phase 7.4 to keep the dashboard responsive: summaries are generated once and served from cache for two hours, so users rarely trigger a live cold inference while browsing.

**Alternatives considered:** Keeping the model permanently resident in RAM via a long Ollama keep-alive (rejected for now — wastes RAM that FinBERT needs under the sequential-processing constraint, and the Phase 7.4 cache already solves the user-facing latency). Pursuing GPU acceleration (already rejected in the prior entry — AMD/ROCm immature on Windows).

**Consequences:** The first inference after the model is unloaded pays a one-time load cost (~1-2 min). Subsequent inferences within the same Ollama session are much faster because the model stays loaded in RAM until it is evicted or Ollama is idle past its keep-alive window. This makes the Phase 7.4 summary cache important rather than optional for dashboard responsiveness, and reinforces favoring batched/overnight runs for any work that would otherwise trigger repeated cold loads.

### 2026-06-02 — Use `ms-ossdata.vscode-pgsql` for the PostgreSQL VSCode extension (blueprint ID was deprecated)

**Context:** Phase 0.3 specified installing the PostgreSQL extension by the ID `ms-ossdata.vscode-postgresql` (named in `blueprint.md` §2.7 and `current_phase.md`). During installation, `code --install-extension ms-ossdata.vscode-postgresql` failed with "Extension not found" — that ID is Microsoft's older, now-deprecated PostgreSQL extension and is no longer installable from the marketplace.

**Decision:** Install Microsoft's current official PostgreSQL extension `ms-ossdata.vscode-pgsql` (same publisher, `ms-ossdata`) instead, and correct the dead ID in `blueprint.md` §2.7 Phase 0.3 and `current_phase.md` so the docs match reality. Rationale: it is the same intended technology (the official Microsoft PostgreSQL extension), just the current ID; the older `vscode-postgresql` extension is deprecated and uninstallable.

**Alternatives considered:** Installing a third-party PostgreSQL extension (rejected — the spec calls for the official Microsoft one, and substituting an unrelated publisher would be a real technology change). Leaving the PostgreSQL extension uninstalled (rejected — it is part of the Phase 0.3 Definition of Done). Keeping the docs pointing at the dead ID (rejected — future installs would hit the same failure).

**Consequences:** Phase 0.3 DoD is met with the working extension. The docs now name the correct, installable ID. If a future blueprint revision still references `ms-ossdata.vscode-postgresql`, it should be read as `ms-ossdata.vscode-pgsql`.

### 2026-06-02 — Defer `config.yaml` YAML parse validation from Phase 0.4 to Phase 0.5

**Context:** Phase 0.4's Definition of Done includes verifying `config/config.yaml` loads via `yaml.safe_load` (`python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('config/config.yaml').read_text()); print('config ok')"`). PyYAML is not installed yet — it belongs to the venv/dependency phases (Phase 0.5 creates the venv; library installs are Phase 1.2 territory). Phase 0.4 explicitly forbids library installation in its out-of-scope list, so the exact DoD command could not run inside Phase 0.4.

**Decision:** Defer the `yaml.safe_load` parse validation to Phase 0.5. As in-phase verification for Phase 0.4, ran a dependency-free structural check instead (confirmed all 8 required top-level sections present and no tab characters). The full parse check becomes one of Phase 0.5's first verification tasks once PyYAML is available in the venv.

**Alternatives considered:** Installing PyYAML globally just to satisfy the Phase 0.4 DoD (rejected — violates Phase 0.4 scope, which forbids library installs, and pollutes the global interpreter ahead of the venv being created in Phase 0.5). A stdlib-only approximate YAML parser (rejected — weaker guarantee than a real parse, not worth the complexity when Phase 0.5 is imminent).

**Consequences:** Phase 0.4 is considered complete with structural verification only. Phase 0.5 must include a `config.yaml` parse step (with PyYAML added to `requirements.txt`) as one of its first verification tasks, and that step is recorded in Phase 0.5's Definition of Done.

### 2026-06-16 — Microsoft Store Python 3.11.9 works fine for the venv (resolves the Phase 0.5 watch item)

**Context:** The 2026-06-01 decision to keep the Microsoft Store Python 3.11.9 build flagged Phase 0.5 as the point to revisit if virtual-environment issues arose, because the Store build sandboxes some paths differently from the python.org build, which can occasionally affect virtual environments.

**Decision:** Keep the Microsoft Store Python 3.11.9 build. During Phase 0.5, `python -m venv .venv` created `backend/.venv` with Python 3.11.9, activation via `.\.venv\Scripts\Activate.ps1` produced the `(.venv)` prefix with no execution-policy block needed, `python` resolved to the venv interpreter, and PyYAML installed and imported cleanly. No sandboxed-path quirks were observed, so there is no reason to switch to the python.org build.

**Alternatives considered:** Reinstalling Python from python.org (rejected — the Store build works for venv creation, activation, and package installs, so a reinstall would be effort without benefit). Watching for issues but taking no decision (rejected — the watch item from 2026-06-01 should be explicitly closed so a future session does not re-investigate).

**Consequences:** The Store build is confirmed adequate for the venv workflow on the primary Windows machine; the 2026-06-01 watch item is closed. If venv/global-tool path issues surface in a later phase, switching to the python.org build remains the fallback.

### 2026-06-16 — Pin exact dependency versions in requirements.txt

**Context:** Phase 0.5 created `backend/requirements.txt` as the single source for rebuilding the venv. A convention was needed for how versions are recorded so that `pip install -r requirements.txt` reproduces the same environment on both the Windows production machine and the MacBook dev machine.

**Decision:** Pin exact versions with `==` (e.g. `PyYAML==6.0.3`) rather than leaving dependencies unpinned or using floating ranges (`>=`). Capture the version actually installed and record it.

**Alternatives considered:** Unpinned dependencies (rejected — non-reproducible; a fresh install could pull a newer, untested version). Floating lower bounds like `PyYAML>=6.0` (rejected — same reproducibility risk across the two machines). Adding a lockfile tool such as pip-tools/poetry (rejected for now — overkill for the small dependency set this early; revisit if the dependency graph grows complex).

**Consequences:** Reproducible environments across machines and over time, supporting Critical Rule #5 (data quality / reliability). Updating a dependency becomes a deliberate, logged change (bump the pin) rather than an accidental drift. Periodic manual review is needed to pick up security/bugfix updates since pins do not float.

### 2026-06-16 — Install the Phase 1.2 database libraries early to satisfy the Phase 0.7 connection check

**Context:** Phase 0.7's Definition of Done requires a Python script that opens a SQLAlchemy engine to the local `threadpulse` database and prints `connection ok`. That needs `SQLAlchemy`, a PostgreSQL driver (`psycopg2-binary`), and `python-dotenv` to read the password from `.env`. The blueprint formally lists these libraries under Phase 1.2, so the same fork seen with PyYAML in Phase 0.5 (install early vs. defer the live check) applied here.

**Decision:** Install the three libraries early into `backend/.venv` now and pin them in `backend/requirements.txt` (`SQLAlchemy==2.0.51`, `psycopg2-binary==2.9.12`, `python-dotenv==1.2.2`), following the same "install early + pin" pattern used for PyYAML in Phase 0.5. This lets the Phase 0.7 DoD run for real this phase rather than deferring the live `connection ok` check to Phase 1.2.

**Alternatives considered:** Defer the live check to Phase 1.2 (rejected — mirrors the Phase 0.4 YAML deferral, but here the libraries are small, stable, and the whole point of Phase 0.7 is to *verify* the database is reachable; deferring would leave the phase's core deliverable unproven). Installing globally instead of into the venv (rejected — pollutes the global interpreter and breaks reproducibility; the venv + pinned requirements is the established convention).

**Consequences:** The Phase 0.7 connection check is fully runnable now. `requirements.txt` carries the DB libraries ahead of Phase 1.2, which is fine — Phase 1.2 simply finds them already present. Transitive dependencies (`greenlet`, `typing-extensions`) are installed automatically and left unpinned, consistent with pinning only direct dependencies.

### 2026-06-22 — Install APScheduler early and pin it for the Phase 0.8 nightly backup

**Context:** Phase 0.8's Definition of Done requires the database backup to run nightly via APScheduler. APScheduler was not yet in `backend/.venv`. The same fork seen with PyYAML (Phase 0.5) and the DB libraries (Phase 0.7) applied: install now to make the phase's scheduling deliverable real, or defer.

**Decision:** Install `APScheduler==3.11.2` into `backend/.venv` now and pin it in `backend/requirements.txt`, following the established "install early + pin" pattern. The scheduler is implemented as a standalone `BlockingScheduler` daemon (`backend/backup_scheduler.py`) that the user starts manually, with `coalesce=True` and a misfire grace window so a PC that was off/asleep runs one catch-up backup rather than a burst.

**Alternatives considered:** Defer scheduling wiring to the later Phase 1.7 / Phase 7 daemon (rejected — nightly scheduling is explicitly in Phase 0.8's DoD, so deferring would leave the phase's core deliverable unproven). Use the Windows Task Scheduler instead of APScheduler (rejected — the blueprint specifies APScheduler as the project's scheduler, and standardizing on one scheduler keeps the stack consistent). Leave APScheduler unpinned (rejected — breaks the reproducibility convention from the 2026-06-16 pinning decision).

**Consequences:** Phase 0.8's nightly-backup DoD item is satisfiable and was smoke-tested (cron job wires to the configured UTC hour). `requirements.txt` carries APScheduler ahead of its formal Phase 1.7 use, which is fine — Phase 1.7 finds it already present. Transitive deps (`tzlocal`, `tzdata`) are installed automatically and left unpinned, consistent with pinning only direct dependencies. The standalone daemon is a stepping stone; Phase 7/1.7 may fold backup scheduling into a larger collection daemon later.

### 2026-06-22 — Defer the off-machine backup copy; ship it config-driven and inactive

**Context:** Phase 0.8's DoD includes copying each backup off the machine (Google Drive folder or external drive) — "a backup that only lives on the same machine is not a real backup." Choosing the destination is a real, user-specific decision (which Drive folder, or which external drive letter), and the user opted to decide it later rather than commit a path now.

**Decision:** Implement the off-machine copy as a config-driven step keyed on a new `config/config.yaml` value, `system.offsite_backup_location`, and ship it **inactive**: when the value is blank, `copy_offsite()` logs that the offsite copy was skipped and no-ops; the local dump still succeeds. The user enables real off-machine backups later by setting the path. Also added `system.backup_hour_utc` so the nightly run time is config-driven rather than hardcoded (Critical Rule #1).

**Alternatives considered:** Hardcode a Google Drive or `D:\` path now (rejected — the correct destination is user/machine-specific and unknown; hardcoding a path violates the no-hardcoded-paths rule and would likely be wrong). Block Phase 0.8 completion until a path is chosen (rejected — the script, scheduler, and local dump are all done and verified; gating the whole phase on one external decision adds no value). Treat the offsite copy as required-now and fail loudly when unset (rejected — would make every local backup fail until configured, which is worse than a working local backup plus a clear skip message).

**Consequences:** Phase 0.8 ships with one DoD item (off-machine copy) intentionally open — recorded in `current_phase.md`. The code path is complete and tested for the skip case; enabling it later is a one-line config change with no code edit. An offsite copy failure at runtime (e.g. external drive unplugged) warns but preserves the good local dump rather than throwing it away. Until the path is set, the project's data is **not** protected against a full machine loss — a deliberate, logged temporary gap to close before relying on the backups.

### 2026-06-22 — Apply Phase 0.9 power settings via `powercfg` instead of clicking through Settings

**Context:** Phase 0.9 is described in the blueprint as a manual Windows-Settings-UI phase (set sleep to Never, Power mode to Best performance, Active hours, Defender folder exclusion). Several of these are scriptable and verifiable, which is preferable to unverifiable UI clicks for a phase whose whole point is a known-good machine state.

**Decision:** Apply the two non-elevated settings programmatically and verify them: system sleep while plugged in via `powercfg /change standby-timeout-ac 0` (verified by reading back the AC standby-idle index as `0x00000000` = Never), and Power mode via `powercfg /overlaysetactive ded574b5-45a0-4f42-8737-46345c09c238` (the Best-performance overlay GUID). The two settings that require administrator elevation — Windows Update Active Hours (registry `HKLM\...\WindowsUpdate\UX\Settings` `ActiveHoursStart=8`/`ActiveHoursEnd=23`, with "adjust automatically" off) and the Windows Defender folder exclusion (`Add-MpPreference -ExclusionPath`) — were handed to the user to run in an elevated PowerShell, because the assistant's shell is non-interactive and cannot trigger a UAC prompt.

**Alternatives considered:** Do everything by hand in the Settings UI as the blueprint literally describes (rejected — unverifiable and slower; `powercfg` gives a machine-readable confirmation). Attempt all four programmatically including the admin ones from the assistant shell (rejected — `Add-MpPreference` and the active-hours registry writes need elevation, and `Start-Process -Verb RunAs` would require an interactive UAC prompt the non-interactive shell cannot satisfy).

**Consequences:** Sleep and power-mode states are confirmed in code and re-checked by the Phase 0.10 validator (`validate_environment.py` reads the same `powercfg` AC index). The two admin items depend on the user having run the provided elevated commands; the validator does not yet assert the Defender exclusion (it cannot be read without admin) or the active-hours values, so those remain user-attested rather than machine-verified.

### 2026-06-22 — Phase 0.10 validator splits CORE (fatal) from SUPPORTING (warn) checks

**Context:** Phase 0.10 is the final Milestone 0 sweep — confirm Python, Node, PostgreSQL, the database connection, Git, the venv, config loading, Ollama, and the sleep setting are all good. A single pass/fail script risks being too blunt: some tools (Node, Ollama) are not actually needed until much later milestones, so failing the whole environment because Ollama is absent would be misleading at the start of Milestone 1.

**Decision:** Implement `backend/validate_environment.py` as one readable script (one function per check) that classifies each check as CORE or SUPPORTING. CORE = Python 3.11.x, `config.yaml` loads, PostgreSQL reachable from Python, venv active — a CORE failure prints `FAIL` and the script exits 1. SUPPORTING = Node 20.x, psql 16.x, pg_dump on PATH, git→GitHub, Ollama present, sleep disabled on AC — these print `WARN` when missing/wrong but do not fail the run. DB name is read from `config.yaml` and the password from gitignored `.env`, reusing the Phase 0.7 connection pattern; paths use `pathlib`.

**Alternatives considered:** A flat all-or-nothing validator (rejected — would false-fail before later milestones install their tools, e.g. Node for the dashboard, and erode trust in the green/red signal). A pytest-based suite (rejected for now — this is a human-run environment sanity check, not unit-tested logic; a plain script with clear printed lines is more readable and matches the existing `check_db_connection.py` style). Separate one-off scripts per tool (rejected — harder to run as a single "is my environment ready?" command).

**Consequences:** The script doubles as an ongoing one-command health check that stays green as the environment legitimately evolves, and only goes red when something the current work actually depends on is broken. The CORE/SUPPORTING line is a judgement call that may need revisiting as milestones advance (e.g. Node becomes CORE once dashboard work in Milestone 7 begins).
