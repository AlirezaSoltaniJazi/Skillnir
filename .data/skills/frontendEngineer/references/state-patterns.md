# State Patterns — Skillnir Frontend

> Storage, async progress, and callback patterns with full examples.

---

## Browser Storage

NiceGUI's `app.storage.user` persists data per-browser session:

```python
from nicegui import app, ui

# Read with default
is_dark = app.storage.user.get('dark_mode', True)
sound_enabled = app.storage.user.get('sound_enabled', True)

# Write on change
def on_dark_toggle(e):
    dark.value = e.value
    app.storage.user['dark_mode'] = e.value
    ui.notify(
        'Dark mode enabled' if e.value else 'Light mode enabled',
        type='info',
    )

ui.switch('', value=is_dark, on_change=on_dark_toggle)
```

**Rules**:
- Use `app.storage.user` for UI preferences only (dark mode, sound, etc.)
- Always provide defaults with `.get(key, default)`
- Show `ui.notify()` confirmation after state changes

---

## Disk Config Storage

Application-level config persisted to `~/.skillnir/config.json`:

```python
from skillnir.backends import load_config, save_config

config = load_config()          # Returns AppConfig dataclass
config.backend = 'claude'       # Modify
save_config(config)             # Persist to disk
```

**Rules**:
- Use `load_config()` / `save_config()` — never read/write JSON directly
- Config includes: backend, model, language, prompt_version
- Language via `get_current_language()` / `set_language(code)`

---

## Page-Level State

Mutable dicts for page-scoped state:

```python
state = {
    'target_root': '',
    'skills': [],
    'selected_skills': [],
}

# Pass state to handlers
def on_submit():
    path = Path(state['target_root']).resolve()
    if not path.is_dir():
        ui.notify('Directory not found', type='negative')
        return
    # ... process
```

---

## Async Progress Callback

Long-running operations use the progress panel pattern:

```python
import time

from skillnir.ui.components.progress_panel import (
    format_duration,
    make_on_progress,
    progress_panel,
    start_elapsed_timer,
)


async def run_generation(container):
    # 1. Build progress UI
    refs = progress_panel(container, max_log_lines=300)

    # 2. Start elapsed timer
    start_time = time.time()
    control = start_elapsed_timer(refs, start_time)

    # 3. Create callback
    counters = {'tools': 0, 'lines': 0}
    on_progress = make_on_progress(refs, counters)

    # 4. Run async operation
    try:
        result = await generate_docs(
            target=target_path,
            on_progress=on_progress,
        )
    finally:
        # 5. Stop timer
        control['active'] = False

    # 6. Show result
    duration = format_duration(int(time.time() - start_time))
    if result.success:
        ui.notify(f'Done in {duration}', type='positive')
    else:
        ui.notify(f'Failed: {result.error}', type='negative')
```

**Rules**:
- Always stop the timer in a `finally` block
- Use `format_duration()` for human-readable time
- Show result via `ui.notify()` + `result_card()`

---

## i18n State

Language state flows through translations:

```python
from skillnir.i18n import get_current_language, is_rtl, set_language, t

lang = get_current_language()  # Reads from config, defaults to 'en'

# Use in components
ui.label(t('pages.home.title', lang))

# With substitution
ui.label(t('messages.found_count', lang, count=str(5)))

# RTL check for Arabic/Persian
if is_rtl(lang):
    container.classes(add='rtl')

# Change language (persists to disk)
set_language('fa')
ui.navigate.to('/settings')  # Reload page to apply
```

**Supported languages**: en, de, nl, pl, fa, uk, sq, fr, ar
**RTL languages**: ar, fa
