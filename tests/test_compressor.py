"""Tests for skillnir.compressor — prompt compression rules and safety."""

from skillnir.compressor import (
    CompressionResult,
    compress_prompt,
    _find_protected_zones,
    _compress_phrases,
    _compress_words,
    _collapse_whitespace,
)


class TestProtectedZones:
    def test_code_blocks_detected(self):
        text = "before ```python\nprint('hello')\n``` after"
        zones = _find_protected_zones(text)
        assert len(zones) == 1
        assert text[zones[0][0] : zones[0][1]].startswith("```")

    def test_inline_code_detected(self):
        text = "use `compress_prompt()` here"
        zones = _find_protected_zones(text)
        assert any(text[s:e] == "`compress_prompt()`" for s, e in zones)

    def test_json_templates_detected(self):
        text = 'value: {{"key": "val"}}'
        zones = _find_protected_zones(text)
        assert len(zones) >= 1

    def test_urls_detected(self):
        text = "visit https://example.com/path for info"
        zones = _find_protected_zones(text)
        assert any("https://example.com/path" in text[s:e] for s, e in zones)

    def test_markdown_headers_detected(self):
        text = "## My Header\nsome text"
        zones = _find_protected_zones(text)
        assert any("## My Header" in text[s:e] for s, e in zones)

    def test_no_zones_in_plain_text(self):
        text = "this is plain text with nothing special"
        zones = _find_protected_zones(text)
        assert len(zones) == 0

    def test_overlapping_zones_merged(self):
        text = "```code with `inline` inside```"
        zones = _find_protected_zones(text)
        # Should merge into single zone covering the whole code block
        assert len(zones) == 1


class TestPhraseCompression:
    def test_in_order_to_becomes_to(self):
        assert "to run" in _compress_phrases("in order to run")

    def test_due_to_becomes_because(self):
        assert "because" in _compress_phrases("due to the fact that")

    def test_is_able_to_becomes_can(self):
        assert "can" in _compress_phrases("is able to")

    def test_multiple_phrases_replaced(self):
        text = "In order to make sure that the system is able to process"
        result = _compress_phrases(text)
        assert "in order to" not in result.lower()
        assert "make sure that" not in result.lower()
        assert "is able to" not in result.lower()

    def test_case_insensitive(self):
        assert "to" == _compress_phrases("In Order To").strip()


class TestWordCompression:
    def test_articles_removed(self):
        result = _compress_words("the cat sat on a mat")
        assert "the " not in result.lower()
        assert " a " not in result

    def test_auxiliaries_removed(self):
        result = _compress_words("it is designed to be fast")
        assert " is " not in result
        assert " be " not in result

    def test_intensifiers_removed(self):
        result = _compress_words("very fast and extremely good")
        assert "very" not in result
        assert "extremely" not in result

    def test_fillers_removed(self):
        result = _compress_words("basically just a simple tool")
        assert "basically" not in result
        assert "just" not in result

    def test_negations_preserved(self):
        result = _compress_words("do not remove this")
        assert "not" in result

    def test_never_preserved(self):
        result = _compress_words("never skip this step")
        assert "never" in result

    def test_without_preserved(self):
        result = _compress_words("works without issues")
        assert "without" in result

    def test_must_preserved(self):
        result = _compress_words("you must follow the rules")
        assert "must" in result

    def test_word_boundaries_respected(self):
        # "a" removal must not affect "data", "area", "metadata"
        result = _compress_words("process a large dataset with data")
        assert "dataset" in result
        assert "data" in result

    def test_numbers_preserved(self):
        result = _compress_words("there are 42 items in the list")
        assert "42" in result


class TestWhitespaceCollapse:
    def test_multiple_spaces_collapsed(self):
        assert "word word" in _collapse_whitespace("word    word")

    def test_multiple_blank_lines_collapsed(self):
        result = _collapse_whitespace("line1\n\n\n\nline2")
        assert result.count("\n") <= 2

    def test_trailing_spaces_removed(self):
        result = _collapse_whitespace("hello   \nworld   ")
        assert "   " not in result


class TestCompressPrompt:
    def test_returns_compression_result(self):
        result = compress_prompt("the quick brown fox")
        assert isinstance(result, CompressionResult)
        assert result.original == "the quick brown fox"
        assert result.original_chars == len("the quick brown fox")
        assert result.compressed_chars <= result.original_chars

    def test_empty_string(self):
        result = compress_prompt("")
        assert result.compressed == ""
        assert result.reduction_pct == 0.0

    def test_whitespace_only(self):
        result = compress_prompt("   ")
        assert result.reduction_pct == 0.0

    def test_json_template_preserved(self):
        text = 'Output this: {{"id": "test", "name": "Model"}}'
        result = compress_prompt(text)
        assert '{{"id": "test", "name": "Model"}}' in result.compressed

    def test_url_preserved(self):
        text = "Visit https://www.swebench.com/ for details"
        result = compress_prompt(text)
        assert "https://www.swebench.com/" in result.compressed

    def test_code_block_preserved(self):
        text = "Run this:\n```python\nprint('hello')\n```\nThen continue."
        result = compress_prompt(text)
        assert "```python\nprint('hello')\n```" in result.compressed

    def test_markdown_header_preserved(self):
        text = "## Instructions\nThe system is very fast."
        result = compress_prompt(text)
        assert "## Instructions" in result.compressed

    def test_natural_language_compresses(self):
        text = (
            "The system was designed to be able to process a very large "
            "number of items in order to ensure that the results are "
            "extremely accurate and basically reliable."
        )
        result = compress_prompt(text)
        assert result.reduction_pct > 20
        # Key words preserved
        assert "system" in result.compressed
        assert "process" in result.compressed
        assert "results" in result.compressed

    def test_reduction_percentage_calculated(self):
        text = "The system is very essentially a basically simple tool."
        result = compress_prompt(text)
        assert result.reduction_pct > 0
        expected_pct = (
            (result.original_chars - result.compressed_chars)
            / result.original_chars
            * 100
        )
        assert abs(result.reduction_pct - round(expected_pct, 1)) < 0.1

    def test_pure_code_minimal_compression(self):
        text = '```\ndef foo(x):\n    return x * 2\n```'
        result = compress_prompt(text)
        # Code block should be untouched
        assert "def foo(x):" in result.compressed
        assert "return x * 2" in result.compressed


class TestIntegrationWithPipelinePrompts:
    """Test compress_prompt on actual pipeline prompt patterns."""

    def test_json_structure_in_prompt_intact(self):
        text = """\
Return EXACTLY this JSON array:

[
  {{{{
    "id": "provider-model",
    "name": "Model Name",
    "scores": {{{{
      "coding": 92.1
    }}}}
  }}}}
]

The model must be very accurate and is able to handle tasks."""
        result = compress_prompt(text)
        # JSON template must survive
        assert '"id": "provider-model"' in result.compressed
        assert '"coding": 92.1' in result.compressed
        # Natural language should compress
        assert result.reduction_pct > 5

    def test_url_heavy_prompt_intact(self):
        text = """\
Search these sources:
1. https://www.swebench.com/ for coding benchmarks
2. https://artificialanalysis.ai/ for pricing data
3. https://lmarena.ai/ for ELO ratings

The system is basically designed to be very comprehensive."""
        result = compress_prompt(text)
        assert "https://www.swebench.com/" in result.compressed
        assert "https://artificialanalysis.ai/" in result.compressed
        assert "https://lmarena.ai/" in result.compressed

    def test_mixed_content_prompt(self):
        text = """\
## Instructions

Use `WebFetch` to search the following benchmark sources.

The model is very important and has been designed to be extremely fast.
In order to make sure that the results are accurate, you must verify."""
        result = compress_prompt(text)
        assert "## Instructions" in result.compressed
        assert "`WebFetch`" in result.compressed
        assert "must" in result.compressed
        assert "verify" in result.compressed
        assert result.reduction_pct > 10
