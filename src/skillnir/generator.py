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
    build_claude_sdk_kwargs,
    build_subprocess_command,
    load_config,
    maybe_compress_prompt,
    run_streaming_command,
)

# Canonical output filenames. The industry standard is uppercase AGENTS.md,
# but this pipeline historically wrote lowercase — accept either casing on
# lookup so runs on case-sensitive filesystems don't report false failures.
AGENTS_MD_NAMES: tuple[str, ...] = ("agents.md", "AGENTS.md")
CLAUDE_MD_NAMES: tuple[str, ...] = (".claude/claude.md", ".claude/CLAUDE.md")


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


# ---------------------------------------------------------------------------
# Context pack — deterministic project inventory for user prompts
# ---------------------------------------------------------------------------

_PACK_SKIP_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".idea",
        ".vscode",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".nicegui",
        "dist",
        "build",
        "target",
        ".next",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
    }
)
_PACK_MANIFESTS = (
    "pyproject.toml",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "requirements.txt",
    "Gemfile",
    "pom.xml",
    "build.gradle",
)
_PACK_MAX_FILES = 200
_PACK_MAX_CHARS = 4000
_PACK_HEAD_LINES = 30


def _list_project_files(target_project: Path) -> list[str]:
    """Repo-relative file list — git ls-files when available, walk otherwise."""
    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=str(target_project),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.splitlines()[: _PACK_MAX_FILES * 2]
    except OSError, subprocess.SubprocessError:
        pass

    files: list[str] = []
    root_depth = len(target_project.parts)
    for current, dirnames, filenames in target_project.walk():
        dirnames[:] = sorted(d for d in dirnames if d not in _PACK_SKIP_DIRS)
        if len(current.parts) - root_depth >= 4:
            dirnames[:] = []
            continue
        for filename in sorted(filenames):
            files.append(str((current / filename).relative_to(target_project)))
            if len(files) >= _PACK_MAX_FILES * 2:
                return files
    return files


def _head_of(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    return "\n".join(lines[:_PACK_HEAD_LINES])


def build_context_pack(target_project: Path) -> str:
    """Deterministic project inventory appended to generation user prompts.

    Hands the agent a file listing, language histogram, manifest heads,
    and README head up front so its capped turns go to targeted reads
    instead of blind Glob/Read discovery. Capped at ~4KB; returns "" if
    the project is unreadable.
    """
    try:
        files = _list_project_files(target_project)
    except OSError:
        return ""
    if not files:
        return ""

    ext_counts: dict[str, int] = {}
    for f in files:
        ext = Path(f).suffix or "(none)"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    top_exts = sorted(ext_counts.items(), key=lambda kv: -kv[1])[:5]

    sections = [
        "PROJECT INVENTORY (auto-generated — use it to target your reads, "
        "verify anything you rely on):",
        "Languages by file count: "
        + ", ".join(f"{ext} ({count})" for ext, count in top_exts),
        "Files:\n" + "\n".join(files[:_PACK_MAX_FILES]),
    ]
    if len(files) > _PACK_MAX_FILES:
        sections.append(f"... and {len(files) - _PACK_MAX_FILES} more files")

    for manifest in _PACK_MANIFESTS:
        manifest_path = target_project / manifest
        if manifest_path.is_file():
            head = _head_of(manifest_path)
            if head:
                sections.append(f"--- {manifest} (head) ---\n{head}")
            if len(sections) >= 6:
                break

    readme = target_project / "README.md"
    if readme.is_file():
        head = _head_of(readme)
        if head:
            sections.append(f"--- README.md (head) ---\n{head}")

    pack = "\n\n".join(sections)
    if len(pack) > _PACK_MAX_CHARS:
        pack = pack[:_PACK_MAX_CHARS] + "\n...(truncated)"
    return pack


def _build_user_prompt(target_project: Path) -> str:
    """Runtime user prompt for docs generation, with the project inventory."""
    prompt = (
        f"Generate AI documentation for the project at {target_project}. "
        "Follow all phases in the system prompt. "
        "Write agents.md to the project root and create the .claude/claude.md symlink."
    )
    pack = build_context_pack(target_project)
    if pack:
        prompt += "\n\n" + pack
    return prompt


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
        system_prompt=maybe_compress_prompt(prompt_text),
        max_turns=15,
        allowed_tools=["Read", "Glob", "Grep", "Bash", "Write"],
        permission_mode="acceptEdits",
        cwd=str(target_project),
        **build_claude_sdk_kwargs(),
    )

    user_prompt = _build_user_prompt(target_project)

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

    user_prompt = _build_user_prompt(target_project)

    full_prompt = prompt_text + "\n\n---\n\n" + user_prompt
    cmd = build_subprocess_command(backend, full_prompt, model=model)

    _emit(on_progress, "phase", "Scanning project...")

    try:
        run = run_streaming_command(
            cmd, backend, target_project, on_progress, timeout=300
        )
    except FileNotFoundError:
        return GenerationResult(
            success=False,
            error=f"{info.cli_command} CLI not found in PATH.",
            backend_used=backend,
        )

    if run.timed_out:
        return GenerationResult(
            success=False,
            error=f"{info.name} timed out after 5 minutes.",
            backend_used=backend,
        )
    if run.returncode != 0:
        return GenerationResult(
            success=False,
            error=f"{info.name} exited with code {run.returncode}: {run.stderr}",
            backend_used=backend,
        )

    _emit(on_progress, "phase", "Verifying outputs...")
    return _check_outputs(target_project, backend)


def _check_outputs(target_project: Path, backend: AIBackend) -> GenerationResult:
    """Verify that expected output files were created (either casing)."""
    agents_md = next(
        (
            target_project / name
            for name in AGENTS_MD_NAMES
            if (target_project / name).exists()
        ),
        None,
    )
    claude_md = next(
        (
            target_project / name
            for name in CLAUDE_MD_NAMES
            if (target_project / name).exists() or (target_project / name).is_symlink()
        ),
        None,
    )

    if agents_md is None:
        return GenerationResult(
            success=False,
            error="agents.md was not created. The AI may need more turns or the project may be too complex.",
            backend_used=backend,
        )

    return GenerationResult(
        success=True,
        agents_md_path=agents_md,
        claude_md_path=claude_md,
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
