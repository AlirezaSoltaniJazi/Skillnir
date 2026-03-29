# skillnir — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Scope**: Cross-cutting skill system rules — file ownership, content placement, activation protocols
- **Skills dir**: `.data/skills/` (backendEngineer, frontendEngineer, devopsEngineer, skillnir)
- **File ownership**: SKILL.md = generated (don't edit), LEARNED.md = AI writes, INJECT.md = hallucination firewall (50-150 tokens)
- **Key rules**: Read SKILL.md before editing any skill file; one rule per LEARNED.md entry; `YYYY-MM-DD:` date format; announce skill activation
- **Never**: Write preferences to SKILL.md, edit skill files without reading SKILL.md first, put code in SKILL.md (use references/), skip LEARNED.md check on ambiguity
- **Self-learning**: On correction → write to LEARNED.md. On ambiguity → check LEARNED.md first. On convention discovery → write to LEARNED.md.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
