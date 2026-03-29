# API & CLI Patterns

> Endpoint patterns, CLI command structure, subprocess spawning, and stream parsing conventions for the Skillnir project.

---

## CLI Command Structure (argparse)

The project uses argparse with subparsers for 17 commands. Each command handler follows this pattern:

```python
def _handle_install(args: argparse.Namespace) -> None:
    """Handle the install command — sync skills + inject symlinks."""
    target_root = _ask_target_project()
    source_dir = _ask_source_skills_dir()
    skills = discover_skills_from_dir(source_dir)

    selected = _ask_multi_select(
        'Select skills to install:',
        [(s.name, s) for s in skills],
    )

    for skill in selected:
        result = sync_skill(source_dir, target_root / '.data' / 'skills', skill.name)
        print(f'  {result.action}: {result.skill_name} (v{result.source_version})')
```

### Command Registration Pattern

```python
def main() -> None:
    parser = argparse.ArgumentParser(description='Skillnir CLI')
    subparsers = parser.add_subparsers(dest='command')

    # Each command gets its own subparser
    sub = subparsers.add_parser('install', help='Sync skills + inject symlinks')
    sub.set_defaults(func=_handle_install)

    sub = subparsers.add_parser('generate-docs', help='Generate agents.md with AI')
    sub.add_argument('--backend', choices=['claude', 'cursor', 'gemini', 'copilot'])
    sub.set_defaults(func=_handle_generate_docs)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
```

---

## Subprocess Spawning Pattern

All AI tool invocations use subprocess.Popen with real-time stream parsing:

```python
import subprocess
import threading
from pathlib import Path
from typing import Callable


def _run_cli_tool(
    cmd: list[str],
    cwd: Path,
    on_progress: Callable[[str], None] | None = None,
) -> str:
    """Run an external CLI tool with real-time output parsing."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        text=True,
    )

    # Drain stderr in a separate thread to prevent deadlocks
    stderr_lines: list[str] = []
    stderr_thread = threading.Thread(
        target=lambda: stderr_lines.extend(proc.stderr.readlines()),
        daemon=True,
    )
    stderr_thread.start()

    output_lines: list[str] = []
    for line in proc.stdout:
        stripped = line.rstrip('\n')
        output_lines.append(stripped)
        if on_progress:
            on_progress(stripped)

    proc.wait()
    stderr_thread.join(timeout=5)
    return '\n'.join(output_lines)
```

---

## Stream JSON Parsing

Claude, Cursor, and Gemini backends emit stream-json format:

```python
import json


def parse_stream_json_line(line: str) -> dict | None:
    """Parse a single line of stream-json output."""
    stripped = line.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None


def parse_stream_line(backend: 'AIBackend', line: str, on_progress: Callable | None) -> None:
    """Route stream line to the correct parser based on backend."""
    if backend.supports_stream_json:
        event = parse_stream_json_line(line)
        if event and on_progress:
            content = event.get('content', '')
            if content:
                on_progress(content)
    else:
        # Copilot: plain text output
        if on_progress:
            on_progress(line)
```

---

## CLI Command Building per Backend

```python
def build_subprocess_command(
    backend_info: 'BackendInfo',
    model: str,
    prompt: str,
    allowed_tools: str,
    max_turns: int = 15,
) -> list[str]:
    """Build the subprocess command for a given backend."""
    cmd = [backend_info.cli_command, '-p']

    if backend_info.supports_stream_json:
        cmd.extend(['--output-format', 'stream-json'])

    # Model resolution
    resolved_model = _resolve_model_id(backend_info, model)
    cmd.extend(['--model', resolved_model])

    # Backend-specific flags
    if backend_info.id == AIBackend.CLAUDE:
        cmd.extend(['--allowedTools', allowed_tools, '--max-turns', str(max_turns), '--verbose'])
    elif backend_info.id == AIBackend.CURSOR:
        cmd.append('--trust')
    elif backend_info.id == AIBackend.GEMINI:
        cmd.extend(['--approval-mode', 'yolo'])
    elif backend_info.id == AIBackend.COPILOT:
        cmd.append('--allow-all-tools')

    cmd.extend(['--', prompt])
    return cmd
```

---

## NiceGUI Page Routes

NiceGUI pages use decorator-based routing with per-page modules:

```python
from nicegui import ui


@ui.page('/generate-skill')
def generate_skill_page() -> None:
    """Page for AI-powered skill generation."""
    with layout.frame('Generate Skill'):
        scope = ui.select(
            'Scope',
            options=list(SCOPE_LABELS.keys()),
            value='backend',
        )

        async def on_generate():
            ui.notify('Generating...')
            result = await run_generation(scope.value)
            if result.success:
                ui.notify('Done!', type='positive')
            else:
                ui.notify(f'Error: {result.error}', type='negative')

        ui.button('Generate', on_click=on_generate)
```

---

## Config Persistence Pattern

```python
import json
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_DIR = Path.home() / '.skillnir'
CONFIG_FILE = CONFIG_DIR / 'config.json'


@dataclass
class AppConfig:
    backend: AIBackend = AIBackend.CLAUDE
    model: str = 'sonnet'
    prompt_version: str = 'v1'

    def to_dict(self) -> dict:
        return {'backend': self.backend.value, 'model': self.model, 'prompt_version': self.prompt_version}

    @classmethod
    def from_dict(cls, d: dict) -> 'AppConfig':
        return cls(
            backend=AIBackend(d.get('backend', 'claude')),
            model=d.get('model', 'sonnet'),
            prompt_version=d.get('prompt_version', 'v1'),
        )


def load_config() -> AppConfig:
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
            return AppConfig.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return AppConfig()
    return AppConfig()


def save_config(config: AppConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config.to_dict(), indent=2), encoding='utf-8')
```

---

## Result Dataclass Pattern

Every operation returns a result dataclass instead of raising exceptions:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SyncResult:
    skill_name: str
    action: str  # "copied" | "updated" | "skipped"
    source_version: str
    target_version: str | None = None


@dataclass
class InjectionResult:
    tool: 'AITool'
    symlink_path: Path
    created: bool
    error: str | None = None


@dataclass
class GenerationResult:
    success: bool
    agents_md_path: Path | None = None
    claude_md_path: Path | None = None
    error: str | None = None
    backend_used: 'AIBackend' | None = None
```

---

## YAML Frontmatter Parsing

```python
import yaml
from pathlib import Path


def parse_frontmatter(skill_md: Path) -> dict:
    """Parse YAML frontmatter from a skill SKILL.md file."""
    text = skill_md.read_text(encoding='utf-8')
    if not text.startswith('---'):
        return {}
    end = text.find('---', 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3:end]) or {}
```
