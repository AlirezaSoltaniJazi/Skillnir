# diagramArchitect — Quick Reference

<!-- Always-loaded firewall: bullets only, <150 tokens. -->

- **FIRST**: read [LEARNED.md](LEARNED.md); say "Using: diagramArchitect skill"
- **Default**: Mermaid in Markdown; PlantUML only for use case / lanes+fork / deployment / timing / C4
- **Pick by question**: steps+owners → activity · calls over time → sequence · lifecycle → state · structure → class/ER (generate)
- **Every diagram**: 5-field header + `accTitle`/`accDescr`, ≤15 elements, render-checked via `scripts/validate-diagrams.sh`
- **Never**: secrets/IPs in diagrams, public renderers for confidential content, images without source, states named after events
- **Sub-agents** (read-only): flow-extractor, diagram-reviewer, drift-detector — see [agents/](agents/)
- **Full**: [SKILL.md](SKILL.md) · [references/](references/)
