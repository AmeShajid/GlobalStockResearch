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
