# Common Issues

## "No models available for this account" (Cursor)

`cursor-agent --list-models` prints this when the CLI is installed but the account has no
model entitlement (not signed in, or a plan without CLI model access).

**Do not guess Cursor model IDs to fill the gap.** An unverifiable ID in the registry breaks
the picker for every Cursor user. Leave the existing entries alone, tell the user the list
could not be verified, and record it in LEARNED.md.

## `IneligibleTierError` (Gemini)

```
Error authenticating: IneligibleTierError: This client is no longer supported for
Gemini Code Assist for individuals. To continue using Gemini, please migrate to the
Antigravity suite of products
```

Google dropped free individual-tier support for `@google/gemini-cli`. The install command
still succeeds — the CLI just refuses to run. Two consequences:

1. The Gemini model list is unverifiable for that account.
2. The install hint is misleading without a `notes` caveat — see
   [install-hints-guide.md](install-hints-guide.md).

## Backend CLI not found

`shutil.which(info.cli_command)` drives the "CLI not found in PATH" message. Check that
`cli_command` in `backends.py` matches the actual binary:

| Backend | `cli_command` | Binary(s) actually installed      |
| ------- | ------------- | --------------------------------- |
| Claude  | `claude`      | `claude`                          |
| Cursor  | `agent`       | `cursor-agent` (and `agent`)      |
| Gemini  | `gemini`      | `gemini`                          |
| Copilot | `copilot`     | `copilot`                         |

A CLI installed under a different name (or only inside an IDE) will read as "not installed".

## `timeout` is not available on macOS

`timeout` is a GNU coreutils binary; plain macOS does not ship it, so a probe written as
`timeout 15 claude --version` silently produces nothing and looks like "no output". Either
run the command directly (`--version` / `--help` are non-interactive and safe) or install
`coreutils` and use `gtimeout`.

## A model ID 404s at runtime

Symptoms: generation fails immediately with a not-found error from the CLI, only for one
model. Causes, in order of likelihood:

1. A date suffix was appended to a dateless ID (current Claude IDs are already pinned)
2. The ID was copied from a blog/marketing page rather than the model doc
3. The model was retired — check the deprecations page

`resolve_model_id` passes unknown strings through untouched, so a bad ID is never caught in
Python; it only fails at the provider.

## Two models claim the default

`TestClaudeModelCatalog` catches this. Symptom without the test: the "default" badge shows on
one card while new configs resolve to another, because `default_model` resolves by alias and
`is_default` only drives the badge.

## The picker shows a stale list

The Switch Model dialog and the CLI config menu both read `BACKENDS` at call time, so there
is no cache to clear — a stale list means the registry itself was not edited, or the app is
running from a different checkout/install than the one you edited.
