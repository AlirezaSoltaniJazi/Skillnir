# promptCompressor — Quick Reference

- **FIRST**: read [LEARNED.md](LEARNED.md)
- **Module**: `compressor.py` — pure Python, no deps, <100ms; entry `compress_prompt(text)`
- **Wired in**: `build_subprocess_command()` in `backends.py`, gated by `compress_prompts` config
- **REMOVE**: articles, auxiliaries, intensifiers, fillers
- **KEEP**: negations, numbers, URLs, code, JSON `{{ }}`, headers
- **Safety**: protected zones detected first — code/JSON/URLs never touched; ~30-50% on prose, ~0% structured
- **Full guide**: [SKILL.md](SKILL.md), [references/](references/)
