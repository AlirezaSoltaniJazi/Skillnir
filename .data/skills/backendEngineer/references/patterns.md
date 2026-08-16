# Python Patterns — Skillnir Backend

> Full code examples for key patterns used in the Skillnir project. Referenced from SKILL.md Key Patterns table.

---

## Result Object Pattern

All operations that can fail return result dataclasses instead of raising exceptions.
Note `inject_skill` takes a _list_ of tools and returns one result per tool — it injects
one skill into every selected tool's dotdir in a single call:

```python
from dataclasses import dataclass
from pathlib import Path

from skillnir.skills import Skill
from skillnir.tools import AITool, SOURCE_DOTDIR


@dataclass
class InjectionResult:
    tool: AITool
    symlink_path: Path
    created: bool
    error: str | None = None


def inject_skill(
    project_root: Path,
    skill: Skill,
    tools: list[AITool],
) -> list[InjectionResult]:
    """Create a symlink from each tool's dotdir to central skill storage."""
    results: list[InjectionResult] = []

    for tool in tools:
        tool_skills_dir = project_root / tool.dotdir / tool.skills_subpath
        symlink_path = tool_skills_dir / skill.dir_name

        if symlink_path.exists() or symlink_path.is_symlink():
            results.append(InjectionResult(tool=tool, symlink_path=symlink_path, created=False))
            continue

        try:
            tool_skills_dir.mkdir(parents=True, exist_ok=True)
            target = Path('..') / '..' / SOURCE_DOTDIR / 'skills' / skill.dir_name
            symlink_path.symlink_to(target)
            results.append(InjectionResult(tool=tool, symlink_path=symlink_path, created=True))
        except OSError as exc:
            results.append(
                InjectionResult(
                    tool=tool, symlink_path=symlink_path, created=False, error=str(exc)
                )
            )

    return results
```

---

## Registry Pattern

Centralized registries for multi-backend, multi-tool support:

```python
from dataclasses import dataclass, field
from enum import Enum


class AIBackend(Enum):
    CLAUDE = 'claude'
    CURSOR = 'cursor'
    GEMINI = 'gemini'
    COPILOT = 'copilot'


@dataclass(frozen=True)
class ModelInfo:
    id: str
    alias: str
    display_name: str
    is_default: bool = False
    tier: int = 2  # 1=powerful/expensive, 2=balanced, 3=cheap/fast


@dataclass(frozen=True)
class BackendInfo:
    name: str
    cli_command: str
    models: tuple[ModelInfo, ...]
    default_model: str  # alias of the default model
    slash_commands: dict[str, str] = field(default_factory=dict)


BACKENDS: dict[AIBackend, BackendInfo] = {
    AIBackend.CLAUDE: BackendInfo(
        name='Claude Code',
        cli_command='claude',
        models=(
            ModelInfo('claude-opus-5', 'opus', 'Claude Opus 5', is_default=True, tier=1),
            ModelInfo('claude-sonnet-5', 'sonnet', 'Claude Sonnet 5', tier=2),
            ModelInfo('claude-haiku-4-5', 'haiku', 'Claude Haiku 4.5', tier=3),
        ),
        default_model='opus',
    ),
    # ... more backends — see BACKENDS in src/skillnir/backends.py for the full
    # model lineups and additional BackendInfo fields (icon, usage_command, etc.)
}
```

---

## Frozen Dataclass Pattern

Immutable data models for tools, models, and metadata:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AITool:
    name: str
    dotdir: str
    company: str
    skills_subpath: str = 'skills'
    popularity: int = 0   # 1-10 (GitHub stars, user base, market share)
    performance: int = 0  # 1-10 (SWE-bench, coding quality, capabilities)
    price: int = 0        # 1-10 (10 = cheapest / most free)
    icon_url: str = ''
    ignore_file: str = ''  # e.g. '.claudeignore', empty if unsupported
    website_url: str = ''


TOOLS: tuple[AITool, ...] = (
    AITool('Claude Code', '.claude', 'Anthropic', popularity=9, performance=10, price=5),
    AITool('Cursor', '.cursor', 'Anysphere', popularity=9, performance=9, price=6),
    # ... 37 tools total — see TOOLS in src/skillnir/tools.py
)
```

---

## Callback Progress Pattern

Streaming updates from long-running operations:

```python
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class GenerationProgress:
    kind: str            # 'text', 'result_text', 'tool_use', 'status', 'error', 'phase'
    content: str
    tool_name: str = ''


async def generate_docs_sdk(
    target_project: Path,
    prompt_text: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> GenerationResult:
    """Generate docs using claude-agent-sdk with streaming. Claude only."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        query,
    )

    options = ClaudeAgentOptions(system_prompt=prompt_text, cwd=str(target_project))
    user_prompt = _build_user_prompt(target_project)

    async for message in query(prompt=user_prompt, options=options):
        if isinstance(message, AssistantMessage) and on_progress:
            for block in message.content:
                if isinstance(block, TextBlock):
                    _emit(on_progress, 'text', block.text)
                elif isinstance(block, ToolUseBlock):
                    _emit(on_progress, 'tool_use', f'Using {block.name}...', tool_name=block.name)
        elif isinstance(message, ResultMessage) and message.usage:
            session_tracker.record('claude', message.usage, message.total_cost_usd)

    return _check_outputs(target_project, AIBackend.CLAUDE)
```

Note the SDK yields typed message objects (`AssistantMessage`, `ResultMessage`) with content
`Block`s (`TextBlock`, `ToolUseBlock`) — not a generic object with a `.type`/`.content` pair.
See `generate_docs_sdk()` in `src/skillnir/generator.py` for the full implementation.

---

## Subprocess Backend Pattern

Running external CLI tools with streaming output. In this codebase the raw `Popen` +
threading plumbing lives once in `run_streaming_command()` (`src/skillnir/backends.py`)
and is shared by every non-Claude backend; callers like `generate_docs_subprocess()`
(`src/skillnir/generator.py`) build a command, call it, then interpret the result:

```python
import subprocess
import threading
from pathlib import Path


def run_streaming_command(
    cmd: list[str],
    backend: AIBackend,
    cwd: Path | str,
    on_progress: Callable | None = None,
    timeout: float = 600,
) -> StreamedRunResult:
    """Run a backend CLI, streaming stdout lines through `parse_stream_line`.

    Both pipes are drained on daemon threads so `timeout` is a real wall-clock
    deadline — a CLI that hangs while keeping stdout open gets killed instead
    of blocking the reader loop forever.
    """
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=str(cwd)
    )

    stderr_chunks: list[str] = []

    def _drain_stderr() -> None:
        for line in proc.stderr:
            stderr_chunks.append(line)

    def _drain_stdout() -> None:
        for line in proc.stdout:
            parse_stream_line(backend, line, on_progress)

    stderr_thread = threading.Thread(target=_drain_stderr, daemon=True)
    stdout_thread = threading.Thread(target=_drain_stdout, daemon=True)
    stderr_thread.start()
    stdout_thread.start()

    timed_out = False
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        timed_out = True

    stdout_thread.join(timeout=5)
    stderr_thread.join(timeout=5)

    return StreamedRunResult(
        returncode=proc.returncode, stderr=''.join(stderr_chunks), timed_out=timed_out
    )


def generate_docs_subprocess(
    target_project: Path,
    prompt_text: str,
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> GenerationResult:
    """Generate docs via any backend CLI subprocess with real-time streaming."""
    cmd = build_subprocess_command(backend, prompt_text, model=model)
    run = run_streaming_command(cmd, backend, target_project, on_progress, timeout=300)

    if run.timed_out:
        return GenerationResult(success=False, error='Timed out.', backend_used=backend)
    if run.returncode != 0:
        return GenerationResult(success=False, error=run.stderr, backend_used=backend)
    return _check_outputs(target_project, backend)
```

---

## Version-Aware Sync Pattern

Syncing skills with version comparison. `source_dir`/`target_dir` are the parent
`.data/skills/`-style directories, not individual skill paths — `skill_name` selects
which skill inside them:

```python
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SyncResult:
    skill_name: str
    action: str  # "copied" | "updated" | "skipped"
    source_version: str
    target_version: str | None = None


def sync_skill(source_dir: Path, target_dir: Path, skill_name: str) -> SyncResult:
    """Sync a single skill from source to target with version comparison."""
    source_skill_dir = source_dir / skill_name
    target_dir.mkdir(parents=True, exist_ok=True)
    source_version = _get_skill_version(source_skill_dir)

    # Avoid self-deletion when source and target resolve to the same directory.
    if source_dir.resolve() == target_dir.resolve():
        return SyncResult(skill_name=skill_name, action='skipped', source_version=source_version)

    target_skill_dir = target_dir / skill_name
    if not target_skill_dir.exists():
        shutil.copytree(source_skill_dir, target_skill_dir)
        return SyncResult(skill_name=skill_name, action='copied', source_version=source_version)

    target_version = _get_skill_version(target_skill_dir)
    if source_version == target_version:
        return SyncResult(
            skill_name=skill_name,
            action='skipped',
            source_version=source_version,
            target_version=target_version,
        )

    shutil.rmtree(target_skill_dir)
    shutil.copytree(source_skill_dir, target_skill_dir)
    return SyncResult(
        skill_name=skill_name,
        action='updated',
        source_version=source_version,
        target_version=target_version,
    )
```

---

## CLI Command Pattern

`cli.py` does **not** use argparse subparsers. There is a single positional `command`
argument on the top-level parser; its `choices=[...]` list enumerates every command, and
`main()` dispatches to a zero-arg, underscore-prefixed handler via a chain of `elif`
branches. Adding a new CLI subcommand with interactive prompts means three edits, all in
`cli.py`:

```python
import questionary


# 1. Add the new string to the choices=[...] list on main()'s `command` argument:
#        choices=[
#            "install", "install-ignore", ..., "my-command",
#        ],

# 2. Add a dispatch branch in main():
#    elif args.command == "my-command":
#        _my_command()

# 3. Define the handler:
def _my_command() -> None:
    """Handle the my-command CLI action."""
    project_root = Path(
        questionary.path(
            'Target project root:',
            default=str(Path.cwd()),
        ).ask()
    )
    if project_root is None:
        return

    confirm = questionary.confirm(
        f'Proceed with {project_root}?',
        default=True,
    ).ask()
    if not confirm:
        return

    result = core_operation(project_root)
    _print_report(result)
```
