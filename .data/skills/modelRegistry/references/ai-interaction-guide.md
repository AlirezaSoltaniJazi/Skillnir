# AI Interaction Guide

Depth that does not belong in SKILL.md. The compact modes table lives there; this is the
rationale and the calibration.

## Proficiency calibration

| Signal from the user                              | Adjust to                                                        |
| ------------------------------------------------- | ---------------------------------------------------------------- |
| "what's an alias here", "why two fable entries"   | Teaching — explain the contract before touching anything          |
| "add fable 5.1", "refresh the list"               | Efficient — verify, edit, test, changelog; report as a table      |
| "picker shows the wrong model"                    | Diagnostic — resolve every alias first, then diff vs. live source |
| Pastes a model ID with no context                 | Verify it against the live doc before assuming it is real         |

## Anti-dependency

The failure mode for this skill is confident wrongness: stating a model ID from memory,
because the ID *looks* plausible and the user has no easy way to check it. Guard rails:

- Always say which IDs were **verified live** and which were **not verifiable** — never blur
  the two into one list.
- When a source is unreachable (no account models, ineligible tier, CLI missing), say so and
  stop. An omission is recoverable; a fabricated ID reaches production.
- When the user asserts a model exists that the doc does not list, re-fetch the doc before
  agreeing — the doc is newer than any training data.

## Why "never from memory" is absolute here

Model catalogs turn over on a scale of weeks-to-months, and the cost asymmetry is severe:

- A **missing** model = a user picks a slightly older one. Mild.
- A **wrong** model ID = every run on that selection fails at the provider, with an error
  that points at the CLI rather than at the registry. Hard to trace.

That asymmetry is why the skill spends a WebFetch on every check rather than trusting a
cached table, even one embedded in another skill.

## Reporting format

Report the outcome as a table, in this order: ID → alias → tier → verified?. Follow with an
explicit line for anything that could not be verified and why. Do not bury an unverifiable
backend in a footnote — it is the part the user most needs to act on.

## On corrections

When the user corrects a convention (alias naming, tier placement, which model should be the
default), restate it as a rule, apply it for the rest of the session, and append it to
LEARNED.md with the date. Conventions here are project preferences, not provider facts —
they are exactly the kind of thing that should accumulate.
