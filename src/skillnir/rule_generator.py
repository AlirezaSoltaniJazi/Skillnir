"""Rule generation with multi-backend support (Claude, Gemini, Copilot)."""

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


def _snapshot_rules(target_project: Path) -> set[Path]:
    """Return current set of .mdc files in .cursor/rules/."""
    rules_dir = target_project / ".cursor" / "rules"
    if not rules_dir.is_dir():
        return set()
    return {p for p in rules_dir.glob("*.mdc")}


async def generate_rule_sdk(
    target_project: Path,
    rule_topic: str,
    prompt_text: str,
    before_files: set[Path],
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
        system_prompt=prompt_text,
        max_turns=10,
        allowed_tools=["Read", "Glob", "Grep", "Bash", "Write"],
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
    before_files: set[Path],
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

    try:
        _emit(on_progress, "phase", "Generating rule...")

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
            return RuleGenerationResult(
                success=False,
                error=f"{info.name} exited with code {proc.returncode}: {stderr}",
                backend_used=backend,
            )

    except subprocess.TimeoutExpired:
        proc.kill()
        return RuleGenerationResult(
            success=False,
            error=f"{info.name} timed out after 5 minutes.",
            backend_used=backend,
        )
    except FileNotFoundError:
        return RuleGenerationResult(
            success=False,
            error=f"{info.cli_command} CLI not found in PATH.",
            backend_used=backend,
        )

    _emit(on_progress, "phase", "Verifying outputs...")
    return _check_rule_outputs(target_project, before_files, backend)


def _check_rule_outputs(
    target_project: Path,
    before_files: set[Path],
    backend: AIBackend,
) -> RuleGenerationResult:
    """Verify that at least one new .mdc file was created."""
    after_files = _snapshot_rules(target_project)
    new_files = sorted(after_files - before_files)

    if not new_files:
        return RuleGenerationResult(
            success=False,
            error=(
                "No new .mdc files were created in .cursor/rules/. "
                "The AI may need more turns or the topic may be too broad."
            ),
            backend_used=backend,
        )

    return RuleGenerationResult(
        success=True,
        rule_files=new_files,
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
