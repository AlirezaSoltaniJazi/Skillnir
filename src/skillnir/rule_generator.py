"""Rule generation with multi-backend support (Claude, Gemini, Copilot)."""

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
class RuleGenerationResult:
    success: bool
    rule_files: list[Path] = field(default_factory=list)
    error: str | None = None
    backend_used: AIBackend | None = None


def load_rule_prompt(version: str = "") -> str:
    """Load the rule generation prompt."""
    prompt_file = get_prompts_dir(version) / "generate-rule-general.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}\n"
            f"Expected at {get_prompts_dir(version)}/generate-rule-general.md"
        )
    return prompt_file.read_text(encoding="utf-8")


def _build_rule_user_prompt(target_project: Path, rule_topic: str) -> str:
    """Construct the runtime user prompt with project-specific details."""
    return (
        f"Create a Cursor rule for the project at {target_project}.\n"
        f'Rule topic: "{rule_topic}"\n'
        f"Follow all instructions in the system prompt.\n"
        f"Write the .mdc file to: {target_project}/.cursor/rules/\n"
        f"Create the .cursor/rules/ directory if it doesn't exist: "
        f"mkdir -p {target_project}/.cursor/rules"
    )


def _snapshot_rules(target_project: Path) -> dict[Path, tuple[int, int]]:
    """Map each .mdc file to (mtime_ns, size) so in-place updates are detected."""
    rules_dir = target_project / ".cursor" / "rules"
    if not rules_dir.is_dir():
        return {}
    snapshot: dict[Path, tuple[int, int]] = {}
    for p in rules_dir.glob("*.mdc"):
        try:
            st = p.stat()
        except OSError:
            continue
        snapshot[p] = (st.st_mtime_ns, st.st_size)
    return snapshot


async def generate_rule_sdk(
    target_project: Path,
    rule_topic: str,
    prompt_text: str,
    before_files: dict[Path, tuple[int, int]],
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> RuleGenerationResult:
    """Generate rule using claude-agent-sdk (async, streaming). Claude only."""
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
        max_turns=10,
        allowed_tools=["Read", "Glob", "Grep", "Bash", "Edit", "Write"],
        permission_mode="acceptEdits",
        cwd=str(target_project),
        **build_claude_sdk_kwargs(),
    )

    user_prompt = _build_rule_user_prompt(target_project, rule_topic)

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
        return RuleGenerationResult(
            success=False,
            error=str(e),
            backend_used=AIBackend.CLAUDE,
        )

    return _check_rule_outputs(target_project, before_files, AIBackend.CLAUDE)


def generate_rule_subprocess(
    target_project: Path,
    rule_topic: str,
    prompt_text: str,
    before_files: dict[Path, tuple[int, int]],
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> RuleGenerationResult:
    """Generate rule using any backend CLI subprocess with real-time streaming."""
    info = BACKENDS[backend]
    _emit(on_progress, "phase", f"Starting {info.name}...")

    user_prompt = _build_rule_user_prompt(target_project, rule_topic)
    full_prompt = prompt_text + "\n\n---\n\n" + user_prompt
    cmd = build_subprocess_command(backend, full_prompt, model=model, max_turns=10)

    _emit(on_progress, "phase", "Generating rule...")

    try:
        run = run_streaming_command(
            cmd, backend, target_project, on_progress, timeout=300
        )
    except FileNotFoundError:
        return RuleGenerationResult(
            success=False,
            error=f"{info.cli_command} CLI not found in PATH.",
            backend_used=backend,
        )

    if run.timed_out:
        return RuleGenerationResult(
            success=False,
            error=f"{info.name} timed out after 5 minutes.",
            backend_used=backend,
        )
    if run.returncode != 0:
        return RuleGenerationResult(
            success=False,
            error=f"{info.name} exited with code {run.returncode}: {run.stderr}",
            backend_used=backend,
        )

    _emit(on_progress, "phase", "Verifying outputs...")
    return _check_rule_outputs(target_project, before_files, backend)


def _check_rule_outputs(
    target_project: Path,
    before_files: dict[Path, tuple[int, int]],
    backend: AIBackend,
) -> RuleGenerationResult:
    """Verify that at least one .mdc file was created or updated.

    Updating an existing rule (re-running a topic that already has a file)
    is a legitimate success — a pure new-path diff pushed the AI toward
    creating duplicate near-identical rule files.
    """
    after_files = _snapshot_rules(target_project)
    touched = sorted(
        path
        for path, signature in after_files.items()
        if before_files.get(path) != signature
    )

    if not touched:
        return RuleGenerationResult(
            success=False,
            error=(
                "No .mdc files were created or updated in .cursor/rules/. "
                "The AI may need more turns or the topic may be too broad."
            ),
            backend_used=backend,
        )

    return RuleGenerationResult(
        success=True,
        rule_files=touched,
        backend_used=backend,
    )


def _claude_sdk_available() -> bool:
    try:
        import claude_agent_sdk  # noqa: F401

        return True
    except ImportError:
        return False


async def generate_rule(
    target_project: Path,
    rule_topic: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    prompt_version_override: str | None = None,
) -> RuleGenerationResult:
    """Main entry point: load prompt, use configured backend, generate rule."""
    _emit(on_progress, "phase", "Loading rule prompt...")

    config = load_config()
    version = prompt_version_override or config.prompt_version

    try:
        prompt_text = load_rule_prompt(version)
    except FileNotFoundError as e:
        return RuleGenerationResult(success=False, error=str(e))

    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    _emit(on_progress, "phase", f"Using {info.name}...")

    before_files = _snapshot_rules(target_project)

    cli_available = bool(shutil.which(info.cli_command))

    if backend == AIBackend.CLAUDE and _claude_sdk_available():
        _emit(on_progress, "status", "Using Claude SDK")
        return await generate_rule_sdk(
            target_project, rule_topic, prompt_text, before_files, on_progress
        )

    if not cli_available:
        return RuleGenerationResult(
            success=False,
            error=f"{info.name} CLI ({info.cli_command}) not found in PATH.",
            backend_used=backend,
        )

    _emit(on_progress, "status", f"Using {info.name} ({model})")

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        generate_rule_subprocess,
        target_project,
        rule_topic,
        prompt_text,
        before_files,
        backend,
        model,
        on_progress,
    )
