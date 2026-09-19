# Backend Registry Guide

Everything about the model catalog lives in `src/skillnir/backends.py`.

## Structures

```python
@dataclass(frozen=True)
class ModelInfo:
    id: str                 # exact provider model ID — what gets sent to the CLI/API
    alias: str              # short selectable name; unique within a backend
    display_name: str       # shown in the picker
    is_default: bool = False
    tier: int = 2           # 1=powerful, 2=balanced, 3=cheap/fast


@dataclass(frozen=True)
class BackendInfo:
    id: AIBackend
    name: str
    cli_command: str
    supports_stream_json: bool
    models: tuple[ModelInfo, ...]
    default_model: str      # an ALIAS, not an ID
    ...
```

## Resolution

```python
def resolve_model_id(backend: AIBackend, alias_or_id: str) -> str:
    """Resolve a model alias to its full ID. Returns as-is if not an alias."""
    info = BACKENDS[backend]
    for m in info.models:
        if m.alias == alias_or_id:
            return m.id
    return alias_or_id
```

Two consequences worth internalizing:

1. **First match wins** — a duplicated alias makes the later model unreachable.
2. **Unknown values pass through** — a full ID (or a typo) is returned untouched, so a wrong
   ID fails at the CLI, not here. That is why live verification matters.

## Adding a model

```python
models=(
    ModelInfo("claude-fable-5-1", "fable", "Claude Fable 5.1", tier=1),
    ModelInfo(
        "claude-opus-5", "opus", "Claude Opus 5", is_default=True, tier=1
    ),
    ModelInfo("claude-opus-4-8", "opus-4.8", "Claude Opus 4.8", tier=1),
    ...
    # legacy tail — still selectable under versioned aliases
    ModelInfo("claude-fable-5", "fable-5", "Claude Fable 5", tier=1),
    ModelInfo("claude-opus-4-5", "opus-4.5", "Claude Opus 4.5", tier=1),
),
default_model="opus",
```

Tuple order is the display order inside each tier group in the Switch Model dialog. Keep
newest-first within a family, and keep the legacy models in a tail at the end.

## Who reads this registry

| Consumer                                     | Reads                                 |
| -------------------------------------------- | ------------------------------------- |
| `ui/components/backend_picker.py`            | `backend_info.models`, grouped by tier |
| `cli.py` config menu                         | `info.models`                          |
| `build_subprocess_command()`                 | `resolve_model_id(...)`               |
| `AppConfig` defaults / `from_dict` fallback  | `default_model`                       |

None of them need editing when you add a model — that is the point of the registry.

## Tests that guard it

`tests/test_backends.py`:

- `TestResolveModelId` — pins each unversioned alias to its flagship ID
- `TestClaudeModelCatalog` — exactly one default, default alias resolves, aliases unique

Update the alias assertions in the same edit as the registry change; they are the only thing
that catches an alias pointing at the wrong model.
