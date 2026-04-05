# promptCompressor -- Quick Reference

- **FIRST**: Read [LEARNED.md](LEARNED.md)
- **Module**: `src/skillnir/compressor.py` -- pure Python, no deps, <100ms
- **Entry**: `compress_prompt(text) -> CompressionResult`
- **Config**: `compress_prompts: bool` in AppConfig / `~/.skillnir/config.json`
- **Integration**: Applied inside `build_subprocess_command()` in `backends.py`
- **REMOVE**: articles (a/an/the), auxiliaries (is/are/was), intensifiers (very/quite), fillers (basically/actually)
- **KEEP**: negations (not/never/without), numbers, URLs, code blocks, JSON templates `{{ }}`, markdown headers
- **Target**: 30-50% reduction on natural language, ~0% on structured data
- **Safety**: Protected zones detected first -- code/JSON/URLs never modified
- **Full guide**: See [SKILL.md](SKILL.md) and [references/](references/)
