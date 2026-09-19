"""Optimize and sync AI docs across a target project.

Two modes:

- **Report** (default, dry-run) — AI scans every AI-context file in the
  project, identifies sync gaps and inconsistencies, and writes a single
  ``docs/ai-context-report.md`` with findings. No other files are modified.
- **Apply** — AI scans, then **edits files in place** to fix inconsistencies,
  add cross-references between docs, and sync the skill list across
  ``agents.md`` / ``llms.txt`` / ``INJECT.md`` / ``docs/*.md``.

Mirrors the dual SDK / subprocess execution pattern used by the other
generators (``generator.py``, ``rule_generator.py``, ``wiki_generator.py``).
"""

import asyncio
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from skillnir.backends import (
    BACKENDS,
    AIBackend,
    build_claude_sdk_kwargs,
    build_subprocess_command,
    load_config,
    maybe_compress_prompt,
    run_streaming_command,
)
from skillnir.generator import GenerationProgress, _emit, get_prompts_dir


@dataclass
class OptimizeDocsResult:
    success: bool
    mode: str = "report"  # "report" | "apply"
    report_path: Path | None = None
    files_touched: list[Path] = field(default_factory=list)
    error: str | None = None
    warning: str | None = None
    backend_used: AIBackend | None = None


REPORT_FILENAME = "ai-context-report.md"


def _max_turns_for(mode: str, doc_count: int) -> int:
    """Scale the agent turn budget to the number of AI docs in the project.

    A fixed budget starved large projects: apply mode edits each doc in its
    own turn (on top of the scan and the final report), so a project with N
    docs needs roughly 3*N turns, while the read-only report mode needs ~2*N.
    Mirrors the size-scaling ``docs_compressor`` already uses. Floors keep
    tiny projects from getting a budget too small to finish the scan.
    """
    if mode == "apply":
        return max(40, doc_count * 3)
    return max(20, doc_count * 2)


def _is_max_turns_error(text: str) -> bool:
    """True when a backend error string reports the turn limit was reached."""
    lowered = text.lower()
    return "maximum number of turns" in lowered or "max turns" in lowered


def load_optimize_prompt(version: str = "") -> str:
    """Load the AI sync/optimize system prompt."""
    prompt_file = get_prompts_dir(version) / "optimize-docs.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}\n"
            f"Expected at {get_prompts_dir(version)}/optimize-docs.md"
        )
    return prompt_file.read_text(encoding="utf-8")


def _build_user_prompt(target_project: Path, mode: str) -> str:
    """User prompt: describe the project and tell the AI which mode to run."""
    if mode == "apply":
        return (
            f"Optimize AI documentation for the project at {target_project}.\n"
            "Mode: APPLY. Follow phases 1-4 in the system prompt: scan, "
            "identify, fix, and add cross-references. Edit files in place.\n"
            "After fixing, write a brief summary of changes to "
            f"docs/{REPORT_FILENAME}."
        )
    return (
        f"Audit AI documentation for the project at {target_project}.\n"
        "Mode: REPORT (dry-run). Follow phases 1-3 in the system prompt: "
        "scan and identify, but **do not fix**. Write all findings and "
        f"recommended fixes to docs/{REPORT_FILENAME}.\n"
        "Do not edit any other file."
    )


def _snapshot_docs(target_project: Path) -> dict[Path, tuple[int, int]]:
    """Map each AI doc to (mtime_ns, size) so apply-mode in-place edits show up.

    A pure path-set diff only detected NEW files — files edited in place
    (the whole point of apply mode) were subtracted away and never reported.
    """
    from skillnir.docs_compressor import find_ai_docs

    paths: list[Path] = list(find_ai_docs(target_project))
    report = target_project / "docs" / REPORT_FILENAME
    if report.exists():
        paths.append(report.resolve())

    snapshot: dict[Path, tuple[int, int]] = {}
    for p in paths:
        try:
            st = p.stat()
        except OSError:
            continue
        snapshot[p] = (st.st_mtime_ns, st.st_size)
    return snapshot


def _partial_outputs(
    target_project: Path,
    mode: str,
    before_files: dict[Path, tuple[int, int]],
    backend: AIBackend,
    turn_limit: int,
) -> OptimizeDocsResult:
    """Salvage a run that stopped at the turn limit.

    When the agent runs out of turns it may already have written the report
    and/or edited docs in place — that work is on disk and must not be thrown
    away as a total failure. If anything was produced *this run*, report
    success with a warning that the audit is likely incomplete; otherwise fail
    with an actionable message that names the limit.

    Salvage is keyed on what changed against ``before_files``, never on the
    report merely existing: a stale report left by a prior run would otherwise
    fake success even when this run produced nothing. Report mode's *only*
    deliverable is the report, so a stray edit to some other doc must not mark
    a report-less dry-run "complete" — there, success requires the report
    itself (matching ``_check_outputs``). Apply mode counts any in-place edit.
    """
    report_path = target_project / "docs" / REPORT_FILENAME
    after_files = _snapshot_docs(target_project)
    changed = sorted(
        path
        for path, signature in after_files.items()
        if before_files.get(path) != signature
    )
    report_written = report_path.resolve() in changed
    salvageable = report_written if mode == "report" else bool(changed)

    if salvageable:
        return OptimizeDocsResult(
            success=True,
            mode=mode,
            report_path=report_path if report_written else None,
            files_touched=changed,
            warning=(
                f"AI stopped after reaching the {turn_limit}-turn limit; the "
                "audit is likely incomplete. Review the changes and re-run to "
                "continue."
            ),
            backend_used=backend,
        )

    return OptimizeDocsResult(
        success=False,
        mode=mode,
        error=(
            f"AI reached the {turn_limit}-turn limit before producing any "
            "output. Try 'report' mode first, or run on a smaller doc set."
        ),
        backend_used=backend,
    )


async def optimize_docs_sdk(
    target_project: Path,
    mode: str,
    prompt_text: str,
    before_files: dict[Path, tuple[int, int]],
    max_turns: int,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    model: str | None = None,
) -> OptimizeDocsResult:
    """Optimize via claude-agent-sdk (async, streaming). Claude only."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        query,
    )

    from skillnir.usage import session_tracker

    _emit(on_progress, "phase", "Connecting to Claude SDK...")

    # Apply mode needs Edit; report mode only needs Read + Write (the report).
    tools = (
        ["Read", "Glob", "Grep", "Bash", "Edit", "Write"]
        if mode == "apply"
        else ["Read", "Glob", "Grep", "Bash", "Write"]
    )

    options = ClaudeAgentOptions(
        system_prompt=maybe_compress_prompt(prompt_text),
        max_turns=max_turns,
        allowed_tools=tools,
        permission_mode="acceptEdits",
        cwd=str(target_project),
        **build_claude_sdk_kwargs(model=model),
    )

    user_prompt = _build_user_prompt(target_project, mode)

    # The SDK yields the ResultMessage (subtype "error_max_turns") just before
    # the CLI's non-zero exit re-raises as a ProcessError, so a flag set here
    # survives into the except/normal-exit branches below.
    hit_max_turns = False

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
                if getattr(message, 'subtype', '') == 'error_max_turns':
                    hit_max_turns = True
    except Exception as exc:
        if hit_max_turns or _is_max_turns_error(str(exc)):
            return _partial_outputs(
                target_project, mode, before_files, AIBackend.CLAUDE, max_turns
            )
        return OptimizeDocsResult(
            success=False,
            mode=mode,
            error=str(exc),
            backend_used=AIBackend.CLAUDE,
        )

    if hit_max_turns:
        return _partial_outputs(
            target_project, mode, before_files, AIBackend.CLAUDE, max_turns
        )
    return _check_outputs(target_project, mode, before_files, AIBackend.CLAUDE)


def optimize_docs_subprocess(
    target_project: Path,
    mode: str,
    prompt_text: str,
    before_files: dict[Path, tuple[int, int]],
    backend: AIBackend,
    model: str,
    max_turns: int,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> OptimizeDocsResult:
    """Optimize via backend CLI subprocess with real-time streaming."""
    info = BACKENDS[backend]
    _emit(on_progress, "phase", f"Starting {info.name}...")

    user_prompt = _build_user_prompt(target_project, mode)
    full_prompt = prompt_text + "\n\n---\n\n" + user_prompt
    cmd = build_subprocess_command(
        backend, full_prompt, model=model, max_turns=max_turns
    )

    try:
        run = run_streaming_command(
            cmd, backend, target_project, on_progress, timeout=600
        )
    except FileNotFoundError:
        return OptimizeDocsResult(
            success=False,
            mode=mode,
            error=f"{info.cli_command} CLI not found in PATH.",
            backend_used=backend,
        )

    if run.timed_out:
        return OptimizeDocsResult(
            success=False,
            mode=mode,
            error=f"{info.name} timed out after 10 minutes.",
            backend_used=backend,
        )
    if run.returncode != 0:
        # A max-turns exit is non-zero too — salvage whatever was produced
        # instead of discarding it, matching the SDK path. The signal rides
        # stdout (run.max_turns_hit); stderr is only a secondary fallback.
        if run.max_turns_hit or _is_max_turns_error(run.stderr):
            return _partial_outputs(
                target_project, mode, before_files, backend, max_turns
            )
        return OptimizeDocsResult(
            success=False,
            mode=mode,
            error=f"{info.name} exited with code {run.returncode}: {run.stderr}",
            backend_used=backend,
        )

    return _check_outputs(target_project, mode, before_files, backend)


def _check_outputs(
    target_project: Path,
    mode: str,
    before_files: dict[Path, tuple[int, int]],
    backend: AIBackend,
) -> OptimizeDocsResult:
    """Verify expected outputs exist (report mode: report only; apply: any diff)."""
    report_path = target_project / "docs" / REPORT_FILENAME

    if not report_path.exists():
        return OptimizeDocsResult(
            success=False,
            mode=mode,
            error=(
                f"docs/{REPORT_FILENAME} was not created. "
                "The AI may need more turns or the project may be too small."
            ),
            backend_used=backend,
        )

    after_files = _snapshot_docs(target_project)
    new_or_modified = sorted(
        path
        for path, signature in after_files.items()
        if before_files.get(path) != signature
    )

    return OptimizeDocsResult(
        success=True,
        mode=mode,
        report_path=report_path,
        files_touched=new_or_modified,
        backend_used=backend,
    )


def _claude_sdk_available() -> bool:
    try:
        import claude_agent_sdk  # noqa: F401

        return True
    except ImportError:
        return False


async def optimize_docs(
    target_project: Path,
    mode: str = "report",
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    prompt_version_override: str | None = None,
) -> OptimizeDocsResult:
    """Main entry point. ``mode`` is ``"report"`` (default) or ``"apply"``."""
    if mode not in ("report", "apply"):
        return OptimizeDocsResult(
            success=False, mode=mode, error=f"Unknown mode: {mode!r}"
        )

    _emit(on_progress, "phase", "Loading optimize prompt...")

    config = load_config()
    version = prompt_version_override or config.prompt_version

    try:
        prompt_text = load_optimize_prompt(version)
    except FileNotFoundError as exc:
        return OptimizeDocsResult(success=False, mode=mode, error=str(exc))

    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    _emit(on_progress, "phase", f"Using {info.name}...")

    before_files = _snapshot_docs(target_project)
    # Budget turns to project size — a fixed cap starved large doc sets and
    # surfaced as an opaque "reached maximum number of turns" failure.
    max_turns = _max_turns_for(mode, len(before_files))
    cli_available = bool(shutil.which(info.cli_command))

    if backend == AIBackend.CLAUDE and _claude_sdk_available():
        _emit(on_progress, "status", "Using Claude SDK")
        return await optimize_docs_sdk(
            target_project,
            mode,
            prompt_text,
            before_files,
            max_turns,
            on_progress,
            model=model,
        )

    if not cli_available:
        return OptimizeDocsResult(
            success=False,
            mode=mode,
            error=f"{info.name} CLI ({info.cli_command}) not found in PATH.",
            backend_used=backend,
        )

    _emit(on_progress, "status", f"Using {info.name} ({model})")

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        optimize_docs_subprocess,
        target_project,
        mode,
        prompt_text,
        before_files,
        backend,
        model,
        max_turns,
        on_progress,
    )
