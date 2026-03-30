# Common Issues — Skillnir Frontend

> Troubleshooting guide for common NiceGUI and UI pitfalls in the Skillnir project.

---

## NiceGUI Import Side Effects

### `RuntimeError: NiceGUI is not running`

**Cause**: Importing `from nicegui import ui` at module level triggers NiceGUI initialization.
**Fix**: Import `ui` inside functions, especially in `layout.py`:

```python
# ✅ Correct — lazy import inside function
def header():
    from nicegui import ui
    # ... use ui

# ❌ Wrong — module-level import causes side effects
from nicegui import ui  # at top of layout.py
```

---

## Async Event Loop

### `RuntimeError: Event loop is already running`

**Cause**: Calling `asyncio.run()` inside a NiceGUI page handler (NiceGUI runs its own event loop).
**Fix**: Use `await` directly in `async def` page functions.

### Timer not stopping

**Cause**: Forgetting to set `control['active'] = False` after async operation.
**Fix**: Always stop the timer in a `finally` block:

```python
control = start_elapsed_timer(refs, start_time)
try:
    result = await operation()
finally:
    control['active'] = False
```

---

## Styling Issues

### Custom CSS classes not applying

**Cause**: Class defined in `_GLOBAL_CSS` but not loaded.
**Fix**: Ensure `__init__.py` is properly loaded. The `_GLOBAL_CSS` string is injected via `ui.add_head_html()` or similar mechanism.

### Dark mode colors not changing

**Cause**: Using Tailwind color classes instead of theme-adaptive custom classes.
**Fix**: Use `.text-secondary` (custom) instead of `.text-gray-400` (Tailwind). Custom classes adapt to `.body--dark` / `.body--light`.

### Card borders not showing

**Cause**: Missing `.props('flat bordered')` — default Quasar cards have shadows, not borders.
**Fix**: Add `.props('flat bordered')` for bordered cards without shadows.

---

## Navigation Issues

### Page not appearing in app

**Cause**: Module not imported in `__init__.py`.
**Fix**: Add import to `src/skillnir/ui/__init__.py`:

```python
from skillnir.ui.pages import (  # noqa: F401
    new_module,  # Add this line
    ...
)
```

### Navigation drawer missing

**Cause**: Forgot to call `header()` at the start of the page function.
**Fix**: Always call `header()` as the first line in every `@ui.page` function.

---

## State Issues

### Storage value not persisting

**Cause**: Using `app.storage.general` instead of `app.storage.user`.
**Fix**: Use `app.storage.user` for per-browser persistence.

### Config not saving

**Cause**: Modifying `config` object without calling `save_config()`.
**Fix**: Always call `save_config(config)` after modifying AppConfig fields.

---

## i18n Issues

### Translation key showing instead of text

**Cause**: Key not found in locale JSON file.
**Fix**: Add the key to `src/skillnir/locales/en.json` (fallback) and all other locale files.

### RTL layout not applying

**Cause**: Missing `is_rtl()` check for Arabic/Persian.
**Fix**: Check `is_rtl(lang)` and add RTL classes:

```python
if is_rtl(lang):
    container.classes(add='rtl')
```

---

## Lambda Closure Gotcha

### All click handlers use the same route

**Cause**: Lambda capturing loop variable by reference.
**Fix**: Bind with default argument:

```python
# ✅ Correct — default argument captures value
lambda route=item_route: ui.navigate.to(route)

# ❌ Wrong — captures reference, always uses last value
lambda: ui.navigate.to(item_route)
```
