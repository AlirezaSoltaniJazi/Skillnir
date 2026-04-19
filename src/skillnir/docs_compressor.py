"""Compress AI-related docs with rule-based + optional AI-driven tone pass.

Walks a target project for canonical AI-context files (agents.md, INJECT.md,
SKILL.md, llms.txt, docs/*.md, .cursor/rules/*.mdc, references/*.md, etc.),
compresses each via the rule-based ``compressor.compress_prompt()``, and
optionally runs a follow-up AI tone pass through Claude to tighten phrasing
without losing meaning.

Symlinks are skipped so the canonical source-of-truth file is only rewritten
once (mirrors the approach in ``injector.py``).
"""

import asyncio
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from skillnir.backends import (
    BACKENDS,
    AIBackend,
    build_claude_sdk_kwargs,
    build_subprocess_command,
    load_config,
    parse_stream_line,
)
from skillnir.compressor import compress_prompt
from skillnir.generator import GenerationProgress, _emit, get_prompts_dir


@dataclass
class FileCompressionReport:
    """Per-file before/after stats from rule-based compression."""

    path: Path
    original_chars: int
    compressed_chars: int
    reduction_pct: float
    written: bool = False
    error: str | None = None


@dataclass
class CompressDocsResult:
    """Aggregate result of a compress-docs run."""

    files: list[FileCompressionReport] = field(default_factory=list)
    total_original_chars: int = 0
    total_compressed_chars: int = 0
    total_reduction_pct: float = 0.0
    applied: bool = False
    ai_tone_applied: bool = False
    error: str | None = None
    backend_used: AIBackend | None = None


# ── Canonical AI-doc file patterns ──────────────────────────────────────────
# Each entry is either a literal relative path or a glob. ``find_ai_docs``
# resolves them against the target project root and skips symlinks so we
# never compress both a symlink and its target.

_AI_DOC_GLOBS: tuple[str, ...] = (
    # Project root single-file context
    "agents.md",
    "AGENTS.md",
    "INJECT.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursorrules",
    "llms.txt",
    # Tool dotdir originals (NOT symlinks — those resolve to the same files)
    ".claude/CLAUDE.md",
    # Cursor rules
    ".cursor/rules/*.mdc",
    # Wiki pages (the canonical 6 from generate-wiki)
    "docs/architecture.md",
    "docs/modules.md",
    "docs/dataflow.md",
    "docs/extending.md",
    "docs/getting-started.md",
    "docs/troubleshooting.md",
    # Skills (each skill has multiple doc files)
    ".data/skills/*/SKILL.md",
    ".data/skills/*/INJECT.md",
    ".data/skills/*/LEARNED.md",
    ".data/skills/*/references/*.md",
    ".data/skills/*/agents/*.md",
)


def find_ai_docs(project_root: Path) -> list[Path]:
    """Return canonical AI-related doc paths under ``project_root``.

    Skips symlinks (those point to a file already in the list) and entries
    that don't exist. Dedupes by ``(st_dev, st_ino)`` so case-insensitive
    filesystems (macOS APFS/HFS+, Windows NTFS) don't double-count when
    both ``agents.md`` and ``AGENTS.md`` resolve to the same file. Sorted
    by path for stable reporting.
    """
    found_by_inode: dict[tuple[int, int], Path] = {}

    def _add(path: Path) -> None:
        if not path.is_file() or path.is_symlink():
            return
        try:
            st = path.stat()
        except OSError:
            return
        key = (st.st_dev, st.st_ino)
        # Keep the first encountered path for a given inode — pattern
        # iteration order is stable (driven by ``_AI_DOC_GLOBS``), so the
        # lowercase variant wins on case-insensitive filesystems because
        # it appears first in the tuple.
        if key not in found_by_inode:
            found_by_inode[key] = path.resolve()

    for pattern in _AI_DOC_GLOBS:
        if any(ch in pattern for ch in "*?["):
            for path in project_root.glob(pattern):
                _add(path)
        else:
            _add(project_root / pattern)

    return sorted(found_by_inode.values())


def _compress_file_rule_based(path: Path) -> FileCompressionReport:
    """Run rule-based compression on one file. Pure read; never writes here."""
    try:
        original = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return FileCompressionReport(
            path=path,
            original_chars=0,
            compressed_chars=0,
            reduction_pct=0.0,
            error=str(exc),
        )

    result = compress_prompt(original)
    return FileCompressionReport(
        path=path,
        original_chars=result.original_chars,
        compressed_chars=result.compressed_chars,
        reduction_pct=result.reduction_pct,
    )


def _aggregate(reports: list[FileCompressionReport]) -> tuple[int, int, float]:
    """Sum char counts and compute overall reduction percentage."""
    total_original = sum(r.original_chars for r in reports if r.error is None)
    total_compressed = sum(r.compressed_chars for r in reports if r.error is None)
    if total_original == 0:
        return 0, 0, 0.0
    pct = ((total_original - total_compressed) / total_original) * 100.0
    return total_original, total_compressed, pct


def compress_docs_dry_run(project_root: Path) -> CompressDocsResult:
    """Scan AI docs, return per-file compression stats. **Writes nothing.**"""
    docs = find_ai_docs(project_root)
    reports = [_compress_file_rule_based(d) for d in docs]
    total_o, total_c, total_pct = _aggregate(reports)
    return CompressDocsResult(
        files=reports,
        total_original_chars=total_o,
        total_compressed_chars=total_c,
        total_reduction_pct=total_pct,
        applied=False,
    )


def compress_docs_apply_rule_based(project_root: Path) -> CompressDocsResult:
    """Apply rule-based compression in place. AI tone pass is separate."""
    docs = find_ai_docs(project_root)
    reports: list[FileCompressionReport] = []
    for path in docs:
        report = _compress_file_rule_based(path)
        if report.error is None:
            try:
                original = path.read_text(encoding="utf-8")
                compressed = compress_prompt(original).compressed
                path.write_text(compressed, encoding="utf-8")
                report.written = True
            except OSError as exc:
                report.error = str(exc)
        reports.append(report)

    total_o, total_c, total_pct = _aggregate(reports)
    return CompressDocsResult(
        files=reports,
        total_original_chars=total_o,
        total_compressed_chars=total_c,
        total_reduction_pct=total_pct,
        applied=True,
    )


# ── Optional AI tone pass ───────────────────────────────────────────────────


def load_tone_prompt(version: str = "") -> str:
    """Load the AI tone-tightening system prompt."""
    prompt_file = get_prompts_dir(version) / "compress-docs-tone.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}\n"
            f"Expected at {get_prompts_dir(version)}/compress-docs-tone.md"
        )
    return prompt_file.read_text(encoding="utf-8")


def _build_tone_user_prompt(target_project: Path, doc_paths: list[Path]) -> str:
    """User prompt listing every file to tighten."""
    rel = [str(p.relative_to(target_project)) for p in doc_paths]
    file_list = "\n".join(f"- {p}" for p in rel)
    return (
        f"Tighten the tone of these AI documentation files in {target_project}.\n"
        "Read each, then Edit in place per the rules in the system prompt:\n\n"
        f"{file_list}"
    )


async def _ai_tone_pass_sdk(
    target_project: Path,
    doc_paths: list[Path],
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> str | None:
    """Run AI tone pass via claude-agent-sdk. Returns error string or None."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        query,
    )

    from skillnir.usage import session_tracker

    _emit(on_progress, "phase", "Connecting to Claude SDK for tone pass...")

    try:
        prompt_text = load_tone_prompt()
    except FileNotFoundError as exc:
        return str(exc)

    options = ClaudeAgentOptions(
        system_prompt=prompt_text,
        max_turns=max(20, len(doc_paths) * 2),
        allowed_tools=["Read", "Edit", "Write"],
        permission_mode="acceptEdits",
        cwd=str(target_project),
        **build_claude_sdk_kwargs(),
    )

    user_prompt = _build_tone_user_prompt(target_project, doc_paths)

    try:
        async for message in query(prompt=user_prompt, options=options):
            if isinstance(message, AssistantMessage) and on_progress:
                for block in message.content:
                    if isinstance(block, TextBlock):
                        _emit(on_progress, "text", block.text)
                    elif isinstance(block, ToolUseBlock):
                        _emit(
                            on_progress,
                            "tool_use",
                            f"Using {block.name}...",
                            tool_name=block.name,
                        )
            elif isinstance(message, ResultMessage):
                if message.usage:
                    session_tracker.record(
                        'claude',
                        message.usage,
                        getattr(message, 'total_cost_usd', None),
                    )
    except Exception as exc:
        return str(exc)
    return None


def _ai_tone_pass_subprocess(
    target_project: Path,
    doc_paths: list[Path],
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> str | None:
    """Run AI tone pass via backend subprocess CLI."""
    info = BACKENDS[backend]
    _emit(on_progress, "phase", f"Starting {info.name} for tone pass...")

    try:
        prompt_text = load_tone_prompt()
    except FileNotFoundError as exc:
        return str(exc)

    user_prompt = _build_tone_user_prompt(target_project, doc_paths)
    full_prompt = prompt_text + "\n\n---\n\n" + user_prompt
    cmd = build_subprocess_command(backend, full_prompt, model=model)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_project),
        )

        import threading

        stderr_chunks: list[str] = []

        def _drain_stderr() -> None:
            for err_line in proc.stderr:
                stderr_chunks.append(err_line)

        stderr_thread = threading.Thread(target=_drain_stderr, daemon=True)
        stderr_thread.start()

        for line in proc.stdout:
            parse_stream_line(backend, line, on_progress)

        proc.wait(timeout=600)
        stderr_thread.join(timeout=5)

        if proc.returncode != 0:
            return f"{info.name} exited with code {proc.returncode}: " + ''.join(
                stderr_chunks
            )
    except subprocess.TimeoutExpired:
        proc.kill()
        return f"{info.name} timed out after 10 minutes."
    except FileNotFoundError:
        return f"{info.cli_command} CLI not found in PATH."
    return None


def _claude_sdk_available() -> bool:
    try:
        import claude_agent_sdk  # noqa: F401

        return True
    except ImportError:
        return False


async def compress_docs_apply(
    project_root: Path,
    with_ai_tone: bool = True,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
) -> CompressDocsResult:
    """Apply rule-based compression and (optionally) an AI tone pass.

    Pipeline:
      1. Scan project for canonical AI doc paths
      2. Apply rule-based compression in place (always)
      3. If ``with_ai_tone`` is True, dispatch a Claude SDK / subprocess
         session that Edits each file to tighten tone further

    Returns a :class:`CompressDocsResult` with per-file stats. The char counts
    reflect step 2 only; the tone pass writes are separate (re-read the file
    afterwards if you need post-tone size).
    """
    _emit(on_progress, "phase", "Scanning AI docs...")
    rule_based_result = compress_docs_apply_rule_based(project_root)

    if not with_ai_tone:
        return rule_based_result

    written_paths = [r.path for r in rule_based_result.files if r.written]
    if not written_paths:
        rule_based_result.error = "No files were compressed; skipping AI tone pass."
        return rule_based_result

    config = load_config()
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]
    rule_based_result.backend_used = backend

    cli_available = bool(shutil.which(info.cli_command))

    if backend == AIBackend.CLAUDE and _claude_sdk_available():
        _emit(on_progress, "status", "Using Claude SDK for tone pass")
        err = await _ai_tone_pass_sdk(project_root, written_paths, on_progress)
    elif cli_available:
        _emit(on_progress, "status", f"Using {info.name} ({model}) for tone pass")
        loop = asyncio.get_event_loop()
        err = await loop.run_in_executor(
            None,
            _ai_tone_pass_subprocess,
            project_root,
            written_paths,
            backend,
            model,
            on_progress,
        )
    else:
        rule_based_result.error = (
            f"{info.name} CLI ({info.cli_command}) not found; "
            "rule-based compression applied, AI tone pass skipped."
        )
        return rule_based_result

    if err:
        rule_based_result.error = err
        return rule_based_result

    rule_based_result.ai_tone_applied = True
    return rule_based_result
