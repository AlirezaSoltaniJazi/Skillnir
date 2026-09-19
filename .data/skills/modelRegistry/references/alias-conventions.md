# Alias, Tier and Default Conventions

## The alias contract

| Alias form                  | Points at                  | Example                       |
| --------------------------- | -------------------------- | ----------------------------- |
| Unversioned (`opus`)        | That family's **newest**   | `opus` → `claude-opus-5`      |
| Versioned (`opus-4.8`)      | One pinned older model     | `opus-4.8` → `claude-opus-4-8` |

**Why unversioned aliases track the newest:** saved configs (`~/.skillnir/config.json`) store
the *alias*, not the ID. A user who picked "opus" once keeps getting the current flagship as
new models ship, without touching their config. If the alias stayed pinned to an old model,
every user would silently be left behind on a superseded model.

**Why the demoted model keeps a versioned alias:** someone may need to pin a known-good
version (reproducibility, a regression, cost). Dropping the alias makes that model
unreachable from the picker even though the provider still serves it.

## Worked example — a new flagship ships

Fable 5.1 supersedes Fable 5:

```python
# before
ModelInfo("claude-fable-5", "fable", "Claude Fable 5", tier=1),

# after
ModelInfo("claude-fable-5-1", "fable", "Claude Fable 5.1", tier=1),   # takes the alias
...
ModelInfo("claude-fable-5", "fable-5", "Claude Fable 5", tier=1),     # demoted, legacy tail
```

Then in `tests/test_backends.py`:

```python
def test_fable_alias_resolves_to_id(self):
    result = resolve_model_id(AIBackend.CLAUDE, "fable")
    assert result == "claude-fable-5-1"

def test_prior_fable_alias_still_resolves(self):
    result = resolve_model_id(AIBackend.CLAUDE, "fable-5")
    assert result == "claude-fable-5"
```

The same pattern was applied for `opus` (→ Opus 5, old one became `opus-4.8`) and `sonnet`
(→ Sonnet 5, old one became `sonnet-4.6`).

## Versioned alias naming

Use the human version with a dot, not the API ID's dashes:

| API ID              | Alias      |
| ------------------- | ---------- |
| `claude-opus-4-8`   | `opus-4.8` |
| `claude-sonnet-4-6` | `sonnet-4.6` |
| `claude-fable-5`    | `fable-5`  |

Aliases must be unique per backend — `resolve_model_id` returns the first match, so a
duplicate silently shadows a model.

## Tier

| Tier | Picker group      | Meaning                     |
| ---- | ----------------- | --------------------------- |
| 1    | Powerful          | Flagship / most capable     |
| 2    | Balanced          | Mid-tier workhorse          |
| 3    | Fast & Affordable | Small, fast, cheap          |

Tier is purely presentational — it decides which group the card lands in. A legacy flagship
keeps tier 1; it does not get demoted to tier 2 just for being older.

## The default

- Exactly **one** `is_default=True` per backend.
- `default_model` is an **alias string**, and it must resolve.
- The default should be the provider's own recommended general-purpose model, not
  necessarily the most expensive one. (Anthropic currently recommends Opus 5 for most
  workloads, with Fable 5.1 reserved for demanding reasoning — so `opus`, not `fable`.)

## Models to omit

Do **not** list a model that most accounts cannot call:

- Invitation-only / private-preview models (e.g. Claude Mythos, Project Glasswing)
- Models gated behind a separate contract

Listing them looks like a choice and fails at runtime, which is worse than not offering them.
