# Current Phase

> Phase 0.1 (Install Core Software — Windows) completed 2026-06-01. All Definition of Done checks passed.

## Active phase
Phase 0.2 — Install Ollama (Windows)

## What is in scope
- Install Ollama for Windows from ollama.com (native Windows installer — no WSL needed)
- Pull the primary model: `ollama pull qwen2.5` (~4GB download)
- Pull the backup model: `ollama pull llama3`
- Note the GPU/RAM constraint: FinBERT and Ollama must never run simultaneously (sequential processing only)

## What is explicitly out of scope
- Any Python library installation, including PyTorch/FinBERT (Phase 1.2)
- Writing the sequential FinBERT → Ollama processing scripts (later milestones)
- VSCode extension setup (Phase 0.3)
- Project folder structure and config file (Phase 0.4)
- Any database schema creation (Phase 0.7)
- Any other milestone work
- Mac setup (handled in Appendix F separately, not now)

## Definition of Done
- Ollama for Windows is installed and the `ollama` command is available in a terminal
- `ollama pull qwen2.5` completed successfully (model present in `ollama list`)
- `ollama pull llama3` completed successfully (model present in `ollama list`)
- Ollama responds to a test prompt: `ollama run qwen2.5 "say hello"` returns a reply

## Notes
- Last updated: 2026-06-01
- Estimated time to complete: 15-40 minutes (mostly model download time; depends on connection speed)
- Reminder: never run FinBERT and Ollama at the same time — running both exhausts GPU memory regardless of card. Scripts process sequentially (all FinBERT scoring first, then Ollama summaries).
- CPU-only inference for FinBERT and Ollama on this machine (AMD GPU, no CUDA). This is acceptable — Ollama runs fine on CPU, just slower than NVIDIA. The 2-hour summary cache from Phase 7.4 absorbs the latency. FinBERT inference will be a few seconds per post, which is fine in batched mode.
- After completion, move to Phase 0.3 (Set Up VSCode Extensions)
