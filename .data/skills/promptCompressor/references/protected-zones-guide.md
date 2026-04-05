# Protected Zones Guide

Protected zones are regions of text that must never be modified by compression. They are detected before any compression transforms are applied.

## Zone Types

### Code Blocks

**Pattern**: ` ```...``` ` (fenced code blocks)
**Regex**: ` ```[\s\S]*?``` `
**Why**: Code syntax would break if words are removed.

### Inline Code

**Pattern**: `` `...` `` (single backtick)
**Regex**: `` `[^`\n]+` ``
**Why**: Function names, CLI commands, variable names must be exact.

### JSON Templates

**Pattern**: `{{ ... }}` and `{{{{ ... }}}}`
**Regex**: `\{{2,}[\s\S]*?\}{2,}`
**Why**: Pipeline prompts use double-braced templates for AI output format instructions. Removing words from JSON keys/values would corrupt the expected output.

### URLs

**Pattern**: `https://...` or `http://...`
**Regex**: `https?://\S+`
**Why**: URLs are exact addresses — any character change breaks them.

### File Paths

**Pattern**: `/path/to/file` or `~/config`
**Regex**: `(?<!\w)[/~][\w./-]+(?:\.\w+)`
**Why**: File paths reference exact filesystem locations.

### Markdown Headers

**Pattern**: `## Header Text`
**Regex**: `^#+\s.*$` (multiline)
**Why**: Headers provide document structure used by AI to navigate sections.

## How Detection Works

1. All 6 regex patterns are run against the full text
2. Each match produces a `(start, end)` character index tuple
3. Overlapping zones are merged (e.g., inline code inside a code block)
4. The text is split into `(segment, is_protected)` pairs
5. Compression transforms only apply to `is_protected=False` segments
6. Protected segments pass through unchanged
7. All segments are reassembled in original order

## Adding New Zone Types

To add a new protected zone type:

1. Define a compiled regex at module level in `compressor.py`
2. Add it to the pattern list in `_find_protected_zones()`
3. Add a test in `TestProtectedZones` in `test_compressor.py`
