"""{{Module description — one line, ends with period.}}"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class {{Name}}Type(Enum):
    """{{Describe the enum purpose.}}"""

    OPTION_A = 'option_a'
    OPTION_B = 'option_b'


@dataclass(frozen=True)
class {{Name}}Info:
    """Immutable configuration/metadata for {{name}}.

    Use frozen=True for configuration objects that should not change after creation.
    Use field(default_factory=...) for mutable default values.
    """

    id: str
    name: str
    type: {{Name}}Type
    tags: tuple[str, ...] = ()
    options: dict[str, str] = field(default_factory=dict)


@dataclass
class {{Name}}Result:
    """Result of a {{name}} operation.

    Use regular (non-frozen) dataclass for operation results.
    Include an action/status field and optional error field.
    """

    name: str
    action: str  # "created" | "updated" | "skipped"
    success: bool = True
    error: str | None = None


# ---------------------------------------------------------------------------
# Registry / Constants
# ---------------------------------------------------------------------------

{{UPPER_NAME}}_REGISTRY: dict[{{Name}}Type, {{Name}}Info] = {
    {{Name}}Type.OPTION_A: {{Name}}Info(
        id='option-a',
        name='Option A',
        type={{Name}}Type.OPTION_A,
    ),
}


# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------


def discover_{{name}}s(root: Path) -> list[{{Name}}Info]:
    """Discover {{name}} entries from a directory."""
    if not root.is_dir():
        return []
    results: list[{{Name}}Info] = []
    for entry in sorted(root.iterdir()):
        if entry.is_dir():
            # Parse and validate entry
            results.append(
                {{Name}}Info(
                    id=entry.name,
                    name=entry.name,
                    type={{Name}}Type.OPTION_A,
                )
            )
    return results


def process_{{name}}(info: {{Name}}Info, target: Path) -> {{Name}}Result:
    """Process a single {{name}} entry."""
    target.mkdir(parents=True, exist_ok=True)

    if (target / info.id).exists():
        return {{Name}}Result(name=info.name, action='skipped')

    # Perform the operation
    (target / info.id).mkdir()
    return {{Name}}Result(name=info.name, action='created')
