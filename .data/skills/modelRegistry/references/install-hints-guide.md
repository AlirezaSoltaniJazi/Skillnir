# CLI Install Hints Guide

The "hint section for installing different models" is the per-backend CLI setup guide shown
in the web UI — the welcome popup on first run, and the **?** (CLI setup guide) button in the
app bar.

## Where it lives

`src/skillnir/ui/components/welcome_dialog.py` → `_CLI_SETUP_INFO`

```python
_CLI_SETUP_INFO: tuple[dict, ...] = (
    {
        'name': 'Claude Code',
        'icon': 'smart_toy',
        'install': 'npm install -g @anthropic-ai/claude-code',
        'install_alt': 'brew install --cask claude-code',
        'login': 'claude login',
        'verify': 'claude --version',
        'notes': 'Requires Node.js 18+. macOS users can also install via Homebrew (cask).',
    },
    ...
)
```

`_cli_install_content()` renders one expansion panel per entry, showing Install → (or
`install_alt`) → Login → Verify → notes. Adding a field to the dict is not enough; the
renderer only shows the keys it reads.

## Field contract

| Field         | Required | Notes                                                            |
| ------------- | -------- | ---------------------------------------------------------------- |
| `name`        | yes      | Display name of the backend                                      |
| `icon`        | yes      | Material icon name                                               |
| `install`     | yes      | Primary install command                                          |
| `install_alt` | no       | Secondary install path, or `None` (renderer skips it when falsy) |
| `login`       | yes      | How to authenticate                                              |
| `verify`      | yes      | Command that proves the CLI works                                |
| `notes`       | yes      | Prerequisites and caveats (runtime version, account needs)       |

`cli_command` in `backends.py` must match the binary the `verify` command invokes — that is
what `shutil.which()` checks at runtime. If they disagree, the app reports "CLI not found"
while the guide tells the user it is installed.

## Verifying the hints are still correct

For each backend, run the `verify` command; if it is missing, follow the `install` command
in a scratch environment and confirm it still resolves.

```bash
claude --version
cursor-agent --version
gemini --version
copilot --version
```

Then sanity-check the package still exists upstream:

```bash
npm view @anthropic-ai/claude-code version
npm view @google/gemini-cli version
npm view @github/copilot version
```

## When to update a hint

| Situation                                        | Action                                                              |
| ------------------------------------------------ | ------------------------------------------------------------------- |
| Package renamed or moved registries              | Update `install` / `install_alt`                                    |
| Login flow changed (e.g. moved into a TUI)       | Update `login`, and say so in `notes`                               |
| Minimum runtime bumped (Node 18 → 22)            | Update `notes` — it is the only place prerequisites appear          |
| Provider drops a tier / changes eligibility      | Add a caveat to `notes`; do **not** silently leave a dead install   |
| Backend no longer usable at all                  | Keep the entry, document it in `notes`, and record it in LEARNED.md |

**Why notes matter more than they look:** the install command usually still "works" after a
provider changes eligibility — it installs a CLI that then refuses to run. The only place a
user learns that beforehand is `notes`.

## Known live caveats

Check LEARNED.md for the current state; as of the last audit:

- **Gemini** — `@google/gemini-cli` raises `IneligibleTierError` for individual free-tier
  accounts (Google redirects them to "Antigravity"). The install command succeeds; the CLI
  then fails. Worth a `notes` caveat.
- **Copilot** — requires Node 22+ and a GitHub account with Copilot access; login happens via
  `/login` inside the TUI, not a flag.

## After editing

1. `uv run black -S --check src/skillnir/ui/components/welcome_dialog.py`
2. `uv run pylint src/skillnir/ui/components/welcome_dialog.py --rcfile=.pylintrc`
3. Open the app (`uv run skillnir ui`) → **?** in the app bar → confirm each panel renders
4. Add a CHANGELOG entry under `## [Unreleased]` if a user-visible instruction changed
