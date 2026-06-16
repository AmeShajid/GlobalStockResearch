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
