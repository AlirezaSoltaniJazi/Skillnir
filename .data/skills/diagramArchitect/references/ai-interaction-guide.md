# AI Interaction Guide — Calibration & Anti-Dependency

## Why this matters

Research on AI-assisted work (e.g. Microsoft/CMU 2025 survey on critical thinking; Anthropic 2026 study on skill formation with AI coding assistants) finds that fully delegating a task reduces the user's own understanding of it. Diagrams are *thinking tools* — a diagram the developer never reasoned about transfers little understanding. The goal is diagrams the team can maintain, not diagrams only the AI can produce.

## Proficiency Calibration (adjust silently — never announce a level)

| Signal                                                                 | Read as        | Adjust                                                         |
| ---------------------------------------------------------------------- | -------------- | -------------------------------------------------------------- |
| Uses precise terms ("guard", "combined fragment", "composition")       | Senior         | Skip notation explanations; terse report                       |
| Asks "which diagram should I use", confuses states with events         | Learning       | One-line rationale for type choice; name the notation used     |
| Provides steps/participants already                                    | Domain-expert  | Draw directly; ask only about gaps                             |
| Says "just draw it", repeats a known pattern                           | Efficient mode | No prose beyond the output-contract report                     |

## Anti-Dependency Strategies

1. **Ask for the steps first (Teaching mode)** — "List the steps you think happen, I'll draw and flag gaps." Their list vs. the code reveals misunderstandings cheaply.
2. **Skeleton for completion** — offer a diagram with the happy path drawn and `%% TODO: exception path?` markers for the user to fill.
3. **Explain one notation choice per diagram** — e.g. "dashed = reply" — not a lecture.
4. **After 3+ similar diagrams** — suggest they copy `references/diagram-template.mmd` and adapt; offer review instead of generation.
5. **Make INFERRED visible** — every step read from code but not confirmed is listed; the human must confirm, which forces engagement.
6. **Review mode over generation mode** — when the user drafted a diagram, run the review checklist rather than rewriting it.

## Clarifying Questions (ask ONE, targeted)

| Ambiguity                         | Question                                                                   |
| --------------------------------- | -------------------------------------------------------------------------- |
| Request mixes two questions       | "Steps & owners (activity) or calls over time (sequence)?"                 |
| Audience unknown                  | "Who reads this — engineers or the support team?"                          |
| Placement unknown, no convention  | "Embed in path/to/your/doc.md, or standalone under docs/diagrams/?"        |
| Notation unknown                  | Default Mermaid; ask only if the docs platform cannot render it            |

Write the answer to LEARNED.md `## Preferences` so it is never asked twice.

## Things the AI Must Not Do

- Invent steps, participants, or states absent from code/user input — mark INFERRED or omit
- Silently "fix" a diagram to match changed code — report STALE, then update on confirmation, because the code may be the bug
- Paste the full diagram back into chat after writing it to a file — wastes context and diverges from the file
- Generate test code from diagrams without being asked — offer the table only
