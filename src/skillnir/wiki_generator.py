"""Project wiki generation with multi-backend support (Claude, Gemini, Copilot).

Generates a token-efficient ``llms.txt`` index plus a ``docs/`` folder with
focused markdown pages (architecture, modules, dataflow, extending,
getting-started, troubleshooting). Sibling to ``generator.py`` (single-file
agents.md) and ``rule_generator.py`` (Cursor .mdc files).
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
from skillnir.generator import (
    GenerationProgress,
    _emit,
    build_context_pack,
    get_prompts_dir,
)


@dataclass
class WikiGenerationResult:
    success: bool
    llms_txt_path: Path | None = None
    docs_dir: Path | None = None
    files_created: list[Path] = field(default_factory=list)
    error: str | None = None
    backend_used: AIBackend | None = None


def load_wiki_prompt(version: str = "") -> str:
    """Load the project wiki generation prompt."""
    prompt_file = get_prompts_dir(version) / "generate-wiki.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}\n"
            f"Expected at {get_prompts_dir(version)}/generate-wiki.md"
        )
    return prompt_file.read_text(encoding="utf-8")


def _build_wiki_user_prompt(target_project: Path) -> str:
    """Construct the runtime user prompt for wiki generation."""
    prompt = (
        f"Generate a project wiki for the project at {target_project}.\n"
        "Follow all phases in the system prompt.\n"
        f"Write llms.txt to the project root and create the docs/ folder under "
        f"{target_project}/docs/ with the markdown pages listed in the prompt."
    )
    pack = build_context_pack(target_project)
    if pack:
        prompt += "\n\n" + pack
    return prompt


def _snapshot_wiki(target_project: Path) -> dict[Path, tuple[int, int]]:
    """Map wiki artefacts (llms.txt + docs/*.md) to (mtime_ns, size)."""
    snapshot: dict[Path, tuple[int, int]] = {}
    docs_dir = target_project / "docs"
    paths = [target_project / "llms.txt"]
    if docs_dir.is_dir():
        paths.extend(docs_dir.glob("*.md"))
    for p in paths:
        try:
            st = p.stat()
        except OSError:
            continue
        snapshot[p] = (st.st_mtime_ns, st.st_size)
    return snapshot


async def generate_wiki_sdk(
    target_project: Path,
    prompt_text: str,
    before_files: dict[Path, tuple[int, int]],
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> WikiGenerationResult:
    """Generate wiki using claude-agent-sdk (async, streaming). Claude only."""
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
        system_prompt=maybe_compress_prompt(prompt_text),
        max_turns=20,
        allowed_tools=["Read", "Glob", "Grep", "Bash", "Edit", "Write"],
        permission_mode="acceptEdits",
        cwd=str(target_project),
        **build_claude_sdk_kwargs(),
    )

    user_prompt = _build_wiki_user_prompt(target_project)

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
        return WikiGenerationResult(
            success=False,
            error=str(e),
            backend_used=AIBackend.CLAUDE,
        )

    return _check_wiki_outputs(target_project, before_files, AIBackend.CLAUDE)


def generate_wiki_subprocess(
    target_project: Path,
    prompt_text: str,
    before_files: dict[Path, tuple[int, int]],
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> WikiGenerationResult:
    """Generate wiki using any backend CLI subprocess with real-time streaming."""
    info = BACKENDS[backend]
    _emit(on_progress, "phase", f"Starting {info.name}...")

    user_prompt = _build_wiki_user_prompt(target_project)
    full_prompt = prompt_text + "\n\n---\n\n" + user_prompt
    cmd = build_subprocess_command(backend, full_prompt, model=model)

    _emit(on_progress, "phase", "Scanning project...")

    try:
        run = run_streaming_command(
            cmd, backend, target_project, on_progress, timeout=600
        )
    except FileNotFoundError:
        return WikiGenerationResult(
            success=False,
            error=f"{info.cli_command} CLI not found in PATH.",
            backend_used=backend,
        )

    if run.timed_out:
        return WikiGenerationResult(
            success=False,
            error=f"{info.name} timed out after 10 minutes.",
            backend_used=backend,
        )
    if run.returncode != 0:
        return WikiGenerationResult(
            success=False,
            error=f"{info.name} exited with code {run.returncode}: {run.stderr}",
            backend_used=backend,
        )

    _emit(on_progress, "phase", "Verifying outputs...")
    return _check_wiki_outputs(target_project, before_files, backend)


def _check_wiki_outputs(
    target_project: Path,
    before_files: dict[Path, tuple[int, int]],
    backend: AIBackend,
) -> WikiGenerationResult:
    """Verify llms.txt + at least one new or updated docs/*.md page."""
    after_files = _snapshot_wiki(target_project)
    new_files = sorted(
        path
        for path, signature in after_files.items()
        if before_files.get(path) != signature
    )
    llms_txt = target_project / "llms.txt"
    docs_dir = target_project / "docs"

    if not llms_txt.exists():
        return WikiGenerationResult(
            success=False,
            error=(
                "llms.txt was not created. The AI may need more turns or the "
                "project may be too complex."
            ),
            backend_used=backend,
        )

    if not docs_dir.is_dir() or not any(docs_dir.glob("*.md")):
        return WikiGenerationResult(
            success=False,
            error="No docs/*.md pages were created.",
            backend_used=backend,
        )

    return WikiGenerationResult(
        success=True,
        llms_txt_path=llms_txt,
        docs_dir=docs_dir,
        files_created=new_files,
        backend_used=backend,
    )


def _claude_sdk_available() -> bool:
    try:
        import claude_agent_sdk  # noqa: F401

        return True
    except ImportError:
        return False


async def generate_wiki(
    target_project: Path,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    prompt_version_override: str | None = None,
) -> WikiGenerationResult:
    """Main entry point: load prompt, use configured backend, generate wiki."""
    _emit(on_progress, "phase", "Loading wiki prompt...")

    config = load_config()
    version = prompt_version_override or config.prompt_version

    try:
        prompt_text = load_wiki_prompt(version)
    except FileNotFoundError as e:
        return WikiGenerationResult(success=False, error=str(e))

    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    _emit(on_progress, "phase", f"Using {info.name}...")

    before_files = _snapshot_wiki(target_project)

    cli_available = bool(shutil.which(info.cli_command))

    if backend == AIBackend.CLAUDE and _claude_sdk_available():
        _emit(on_progress, "status", "Using Claude SDK")
        return await generate_wiki_sdk(
            target_project, prompt_text, before_files, on_progress
        )

    if not cli_available:
        return WikiGenerationResult(
            success=False,
            error=f"{info.name} CLI ({info.cli_command}) not found in PATH.",
            backend_used=backend,
        )

    _emit(on_progress, "status", f"Using {info.name} ({model})")

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        generate_wiki_subprocess,
        target_project,
        prompt_text,
        before_files,
        backend,
        model,
        on_progress,
    )
