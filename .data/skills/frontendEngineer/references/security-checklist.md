# Security Checklist — Skillnir Frontend

> XSS prevention, storage safety, path validation, and input sanitization checklists.

---

## XSS Prevention

- [ ] Never use `ui.run_javascript()` with unsanitized user input
- [ ] Never use `ui.html()` with user-provided content — prefer NiceGUI elements
- [ ] Never interpolate user data into `.style()` CSS expressions without validation
- [ ] Use NiceGUI's built-in escaping — avoid raw HTML construction
- [ ] Validate file paths before displaying in UI labels

```python
# ✅ Safe — NiceGUI escapes content automatically
ui.label(user_input)

# ❌ Dangerous — raw HTML with user data
ui.html(f'<div>{user_input}</div>')

# ❌ Dangerous — user data in JavaScript
ui.run_javascript(f'alert("{user_input}")')
```

---

## Storage Safety

- [ ] Set `storage_secret` parameter in `ui.run()` for encrypted browser storage
- [ ] Never store secrets (API keys, tokens) in `app.storage.user`
- [ ] Validate data read from `app.storage.user` — it can be tampered with
- [ ] Use `.get(key, default)` to handle missing/corrupted storage keys

```python
# ✅ Safe — encrypted storage with fallback
ui.run(storage_secret='skillnir-local')
is_dark = app.storage.user.get('dark_mode', True)

# ❌ Dangerous — trusting stored data without validation
config = app.storage.user['config']  # May not exist or be corrupted
```

---

## Path Validation

- [ ] Validate all user-provided paths with `Path.resolve()` before operations
- [ ] Check paths exist with `Path.is_dir()` / `Path.is_file()` before use
- [ ] Display validation errors via `ui.notify()` — never expose raw exceptions
- [ ] Never use string concatenation for paths — use `Path /` operator

```python
# ✅ Safe path validation in UI
path = Path(target_input.value).resolve()
if not path.is_dir():
    ui.notify('Directory not found', type='negative')
    return
```

---

## Error Display

- [ ] Use `ui.notify(message, type='negative')` for user-facing errors
- [ ] Never expose stack traces, file paths, or internal details in UI
- [ ] Log detailed errors server-side, show generic messages client-side
- [ ] Use `try/except` around file operations with user-friendly error messages

```python
# ✅ Safe error handling
try:
    result = process_target(path)
except OSError:
    ui.notify('Could not access the target directory', type='negative')

# ❌ Dangerous — exposing internals
except Exception as e:
    ui.notify(str(e), type='negative')  # May contain file paths, stack info
```

---

## Content Security

- [ ] Serve static files via `app.add_static_files()` — not inline base64
- [ ] Validate file types before serving as static assets
- [ ] Use `storage_secret` parameter for session encryption
- [ ] Never embed credentials in source code or client-side storage
