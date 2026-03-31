# Python Patterns — Skillnir Backend

> Full code examples for key patterns used in the Skillnir project. Referenced from SKILL.md Key Patterns table.

---

## Result Object Pattern

All operations that can fail return result dataclasses instead of raising exceptions:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class InjectionResult:
    tool: str
    symlink_path: Path
    created: bool
    error: str | None = None


def inject_skill(skill_path: Path, tool_dir: Path) -> InjectionResult:
    """Create symlink from tool directory to central skill storage."""
    symlink = tool_dir / 'skills' / skill_path.name
    try:
        symlink.parent.mkdir(parents=True, exist_ok=True)
        if symlink.exists() or symlink.is_symlink():
            return InjectionResult(
                tool=tool_dir.name,
                symlink_path=symlink,
                created=False,
            )
        symlink.symlink_to(skill_path)
        return InjectionResult(
            tool=tool_dir.name,
            symlink_path=symlink,
            created=True,
        )
    except OSError as exc:
        return InjectionResult(
            tool=tool_dir.name,
            symlink_path=symlink,
            created=False,
            error=str(exc),
        )
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
    tier: str = 'standard'


@dataclass(frozen=True)
class BackendInfo:
    name: str
    cli_command: str
    supported_models: tuple[ModelInfo, ...]
    default_model: str
    slash_commands: tuple[str, ...] = field(default_factory=tuple)


BACKENDS: dict[AIBackend, BackendInfo] = {
    AIBackend.CLAUDE: BackendInfo(
        name='Claude Code',
        cli_command='claude',
        supported_models=(
            ModelInfo('claude-sonnet-4-20250514', 'sonnet', 'Sonnet 4', is_default=True),
            ModelInfo('claude-opus-4-20250514', 'opus', 'Opus 4', tier='premium'),
        ),
        default_model='claude-sonnet-4-20250514',
    ),
    # ... more backends
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
    popularity: int    # 1-10 scale
    performance: int   # 1-10 scale
    price: int         # 1-10 scale (10 = free)
    icon_url: str = ''

    @property
    def score(self) -> float:
        return (self.popularity + self.performance + self.price) / 3


TOOLS: tuple[AITool, ...] = (
    AITool('Claude Code', '.claude', 'Anthropic', 9, 10, 7),
    AITool('Cursor', '.cursor', 'Anysphere', 10, 9, 5),
    # ... more tools
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
    kind: str          # 'text', 'tool_use', 'status', 'error', 'phase'
    content: str
    tool_name: str | None = None


async def generate_docs_sdk(
    prompt: str,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> str:
    """Generate docs using Claude SDK with streaming."""
    result_parts: list[str] = []

    async for message in query(prompt, model=model):
        if message.type == 'text':
            result_parts.append(message.content)
            if on_progress:
                on_progress(GenerationProgress(
                    kind='text',
                    content=message.content,
                ))

    return ''.join(result_parts)
```

---

## Subprocess Backend Pattern

Running external CLI tools with streaming output:

```python
import subprocess
import threading
from pathlib import Path


def generate_docs_subprocess(
    prompt: str,
    cli_command: str,
    project_root: Path,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> GenerationResult:
    """Generate docs via external CLI subprocess."""
    cmd = [cli_command, '--print', '--model', 'sonnet', prompt]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=project_root,
        text=True,
    )

    # Read stderr in background thread
    stderr_lines: list[str] = []

    def _read_stderr():
        for line in proc.stderr:
            stderr_lines.append(line)

    thread = threading.Thread(target=_read_stderr, daemon=True)
    thread.start()

    # Stream stdout
    output_parts: list[str] = []
    for line in proc.stdout:
        output_parts.append(line)
        if on_progress:
            on_progress(GenerationProgress(kind='text', content=line))

    proc.wait()
    thread.join(timeout=5)

    return GenerationResult(
        success=proc.returncode == 0,
        content=''.join(output_parts),
        error=''.join(stderr_lines) if proc.returncode != 0 else None,
    )
```

---

## Version-Aware Sync Pattern

Syncing skills with version comparison:

```python
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SyncResult:
    skill_name: str
    action: str        # 'copied', 'updated', 'skipped'
    source_version: str | None = None
    target_version: str | None = None


def sync_skill(source: Path, target: Path) -> SyncResult:
    """Sync a single skill with version comparison."""
    skill_name = source.name

    if not target.exists():
        shutil.copytree(source, target)
        return SyncResult(skill_name=skill_name, action='copied')

    source_version = _read_version(source / 'SKILL.md')
    target_version = _read_version(target / 'SKILL.md')

    if source_version == target_version:
        return SyncResult(
            skill_name=skill_name,
            action='skipped',
            source_version=source_version,
            target_version=target_version,
        )

    # Avoid self-deletion
    if source.resolve() == target.resolve():
        return SyncResult(skill_name=skill_name, action='skipped')

    shutil.rmtree(target)
    shutil.copytree(source, target)
    return SyncResult(
        skill_name=skill_name,
        action='updated',
        source_version=source_version,
        target_version=target_version,
    )
```

---

## CLI Command Pattern

Adding a new CLI subcommand with interactive prompts:

```python
import argparse

import questionary


def _setup_parsers(subparsers: argparse._SubParsersAction) -> None:
    subparsers.add_parser(
        'my-command',
        help='Description of the command',
    )


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
