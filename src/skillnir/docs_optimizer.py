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
from skillnir.generator import GenerationProgress, _emit, get_prompts_dir


@dataclass
class OptimizeDocsResult:
    success: bool
    mode: str = "report"  # "report" | "apply"
    report_path: Path | None = None
    files_touched: list[Path] = field(default_factory=list)
    error: str | None = None
    backend_used: AIBackend | None = None


REPORT_FILENAME = "ai-context-report.md"


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


def _snapshot_docs(target_project: Path) -> set[Path]:
    """Capture current AI doc paths so we can diff what changed in apply mode."""
    from skillnir.docs_compressor import find_ai_docs

    snapshot: set[Path] = set(find_ai_docs(target_project))
    report = target_project / "docs" / REPORT_FILENAME
    if report.exists():
        snapshot.add(report.resolve())
    return snapshot


async def optimize_docs_sdk(
    target_project: Path,
    mode: str,
    prompt_text: str,
    before_files: set[Path],
    on_progress: Callable[[GenerationProgress], None] | None = None,
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
        system_prompt=prompt_text,
        max_turns=30 if mode == "apply" else 20,
        allowed_tools=tools,
        permission_mode="acceptEdits",
        cwd=str(target_project),
        **build_claude_sdk_kwargs(),
    )

    user_prompt = _build_user_prompt(target_project, mode)

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
        return OptimizeDocsResult(
            success=False,
            mode=mode,
            error=str(exc),
            backend_used=AIBackend.CLAUDE,
        )

    return _check_outputs(target_project, mode, before_files, AIBackend.CLAUDE)


def optimize_docs_subprocess(
    target_project: Path,
    mode: str,
    prompt_text: str,
    before_files: set[Path],
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> OptimizeDocsResult:
    """Optimize via backend CLI subprocess with real-time streaming."""
    info = BACKENDS[backend]
    _emit(on_progress, "phase", f"Starting {info.name}...")

    user_prompt = _build_user_prompt(target_project, mode)
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
        stderr = ''.join(stderr_chunks)

        if proc.returncode != 0:
            return OptimizeDocsResult(
                success=False,
                mode=mode,
                error=f"{info.name} exited with code {proc.returncode}: {stderr}",
                backend_used=backend,
            )

    except subprocess.TimeoutExpired:
        proc.kill()
        return OptimizeDocsResult(
            success=False,
            mode=mode,
            error=f"{info.name} timed out after 10 minutes.",
            backend_used=backend,
        )
    except FileNotFoundError:
        return OptimizeDocsResult(
            success=False,
            mode=mode,
            error=f"{info.cli_command} CLI not found in PATH.",
            backend_used=backend,
        )

    return _check_outputs(target_project, mode, before_files, backend)


def _check_outputs(
    target_project: Path,
    mode: str,
    before_files: set[Path],
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
    new_or_modified = sorted(after_files - before_files)

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
    cli_available = bool(shutil.which(info.cli_command))

    if backend == AIBackend.CLAUDE and _claude_sdk_available():
        _emit(on_progress, "status", "Using Claude SDK")
        return await optimize_docs_sdk(
            target_project, mode, prompt_text, before_files, on_progress
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
        on_progress,
    )
