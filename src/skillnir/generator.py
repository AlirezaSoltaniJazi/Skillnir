"""AI docs generation with multi-backend support (Claude, Gemini, Copilot)."""

import asyncio
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from skillnir.backends import (
    BACKENDS,
    AIBackend,
    build_subprocess_command,
    load_config,
    parse_stream_line,
)


@dataclass
class GenerationProgress:
    """A single progress event streamed during generation."""

    kind: str  # "text" | "result_text" | "tool_use" | "status" | "error" | "phase"
    content: str
    tool_name: str = ""


@dataclass
class GenerationResult:
    success: bool
    agents_md_path: Path | None = None
    claude_md_path: Path | None = None
    error: str | None = None
    backend_used: AIBackend | None = None


def get_prompts_dir(version: str = "") -> Path:
    """Find skillnir's own prompts directory for a version.

    Version is auto-detected from .data/promptsv{N} directories.
    Empty version defaults to the latest discovered version.
    """
    if not version:
        from skillnir.backends import _default_prompt_version

        version = _default_prompt_version()
    num = version.removeprefix("v")
    subdir = f"promptsv{num}"
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".data" / subdir
        if candidate.is_dir():
            return candidate
        current = current.parent
    return Path.cwd() / ".data" / subdir


def load_prompt(version: str = "") -> str:
    """Load the master prompt for AI docs generation."""
    prompts_dir = get_prompts_dir(version)
    prompt_file = prompts_dir / "generate-ai-docs.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}\n"
            f"Expected at {prompts_dir}/generate-ai-docs.md"
        )
    return prompt_file.read_text(encoding="utf-8")


def _emit(
    on_progress: Callable[[GenerationProgress], None] | None,
    kind: str,
    content: str,
    tool_name: str = "",
) -> None:
    """Helper to emit a progress event if callback exists."""
    if on_progress:
        on_progress(GenerationProgress(kind=kind, content=content, tool_name=tool_name))


async def generate_docs_sdk(
    target_project: Path,
    prompt_text: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> GenerationResult:
    """Generate docs using claude-agent-sdk (async, streaming). Claude only."""
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

    options = ClaudeAgentOptions(
        system_prompt=prompt_text,
        max_turns=15,
        allowed_tools=["Read", "Glob", "Grep", "Bash", "Write"],
        permission_mode="acceptEdits",
        cwd=str(target_project),
    )

    user_prompt = (
        f"Generate AI documentation for the project at {target_project}. "
        "Follow all phases in the system prompt. "
        "Write agents.md to the project root and create the .claude/claude.md symlink."
    )

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
    except Exception as e:
        return GenerationResult(
            success=False,
            error=str(e),
            backend_used=AIBackend.CLAUDE,
        )

    return _check_outputs(target_project, AIBackend.CLAUDE)


def generate_docs_subprocess(
    target_project: Path,
    prompt_text: str,
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> GenerationResult:
    """Generate docs using any backend CLI subprocess with real-time streaming."""
    info = BACKENDS[backend]
    _emit(on_progress, "phase", f"Starting {info.name}...")

    user_prompt = (
        f"Generate AI documentation for the project at {target_project}. "
        "Follow all phases in the system prompt. "
        "Write agents.md to the project root and create the .claude/claude.md symlink."
    )

    full_prompt = prompt_text + "\n\n---\n\n" + user_prompt
    cmd = build_subprocess_command(backend, full_prompt, model=model)

    try:
        _emit(on_progress, "phase", "Scanning project...")

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

        proc.wait(timeout=300)
        stderr_thread.join(timeout=5)
        stderr = ''.join(stderr_chunks)

        if proc.returncode != 0:
            return GenerationResult(
                success=False,
                error=f"{info.name} exited with code {proc.returncode}: {stderr}",
                backend_used=backend,
            )

    except subprocess.TimeoutExpired:
        proc.kill()
        return GenerationResult(
            success=False,
            error=f"{info.name} timed out after 5 minutes.",
            backend_used=backend,
        )
    except FileNotFoundError:
        return GenerationResult(
            success=False,
            error=f"{info.cli_command} CLI not found in PATH.",
            backend_used=backend,
        )

    _emit(on_progress, "phase", "Verifying outputs...")
    return _check_outputs(target_project, backend)


def _check_outputs(target_project: Path, backend: AIBackend) -> GenerationResult:
    """Verify that expected output files were created."""
    agents_md = target_project / "agents.md"
    claude_md = target_project / ".claude" / "claude.md"

    if not agents_md.exists():
        return GenerationResult(
            success=False,
            error="agents.md was not created. The AI may need more turns or the project may be too complex.",
            backend_used=backend,
        )

    return GenerationResult(
        success=True,
        agents_md_path=agents_md,
        claude_md_path=(
            claude_md if claude_md.exists() or claude_md.is_symlink() else None
        ),
        backend_used=backend,
    )


def _claude_sdk_available() -> bool:
    """Check if claude-agent-sdk is importable."""
    try:
        import claude_agent_sdk  # noqa: F401

        return True
    except ImportError:
        return False


async def generate_docs(
    target_project: Path,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    prompt_version_override: str | None = None,
) -> GenerationResult:
    """Main entry point: load prompt, use configured backend, run generation."""
    _emit(on_progress, "phase", "Loading prompt...")

    config = load_config()
    version = prompt_version_override or config.prompt_version

    try:
        prompt_text = load_prompt(version)
    except FileNotFoundError as e:
        return GenerationResult(success=False, error=str(e))

    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    _emit(on_progress, "phase", f"Using {info.name}...")

    # Check CLI availability
    cli_available = bool(shutil.which(info.cli_command))

    # For Claude, try SDK first if available
    if backend == AIBackend.CLAUDE and _claude_sdk_available():
        _emit(on_progress, "status", "Using Claude SDK")
        return await generate_docs_sdk(target_project, prompt_text, on_progress)

    if not cli_available:
        return GenerationResult(
            success=False,
            error=f"{info.name} CLI ({info.cli_command}) not found in PATH.",
            backend_used=backend,
        )

    _emit(on_progress, "status", f"Using {info.name} ({model})")

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        generate_docs_subprocess,
        target_project,
        prompt_text,
        backend,
        model,
        on_progress,
    )
