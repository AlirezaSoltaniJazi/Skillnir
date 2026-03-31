"""One-line module description — what this module does."""

import json
from dataclasses import dataclass, field
from pathlib import Path

from skillnir.skills import Skill


# --- Constants ---

DEFAULT_TIMEOUT = 30
SUPPORTED_FORMATS = ('yaml', 'json')


# --- Data Models ---

@dataclass(frozen=True)
class ImmutableConfig:
    """Configuration that should not change after creation."""

    name: str
    version: str
    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass
class OperationResult:
    """Result of an operation that can succeed or fail."""

    success: bool
    message: str
    error: str | None = None


# --- Public API ---

def perform_operation(
    source: Path,
    target: Path,
    on_progress: 'Callable[[str], None] | None' = None,
) -> OperationResult:
    """Perform the main operation.

    Args:
        source: Source path to process.
        target: Target path for output.
        on_progress: Optional callback for progress updates.

    Returns:
        OperationResult with success status and message.
    """
    if not source.exists():
        return OperationResult(
            success=False,
            message='Source not found',
            error=f'Path does not exist: {source}',
        )

    try:
        _process_files(source, target, on_progress)
        return OperationResult(success=True, message='Operation completed')
    except OSError as exc:
        return OperationResult(
            success=False,
            message='Operation failed',
            error=str(exc),
        )


# --- Private Helpers ---

def _process_files(
    source: Path,
    target: Path,
    on_progress: 'Callable[[str], None] | None' = None,
) -> None:
    """Process files from source to target."""
    target.mkdir(parents=True, exist_ok=True)

    for path in source.iterdir():
        if path.is_file():
            content = path.read_text(encoding='utf-8')
            (target / path.name).write_text(content, encoding='utf-8')
            if on_progress:
                on_progress(f'Processed: {path.name}')
