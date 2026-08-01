# AI Interaction Guide — Jira Skill

> Interaction modes, active-ticket memory rules, read-only vs mutating command handling, and common mistakes for the jira skill — referenced from SKILL.md. Full detail lives here so SKILL.md stays lean.

---

## Interaction Modes

Detect the mode from the user's phrasing and match your behavior to it. Modes can shift within one session — re-detect on every request. Everything instance-specific (`<KEY>`, the `<site>`, the `<Review status>`) is auto-detected at runtime or asked and recorded to LEARNED.md — never baked in.

### Create

**Signals**: "create/raise/log a ticket", "new story/task/bug", "open a Jira for…".
**Behavior**: run the full create-ticket flow — detect the `<KEY>` from git context, ask the issue type if unclear, search for the parent Epic/Story and present a numbered list, gather a non-technical description, **confirm every field**, then create. Record the result as the session active ticket.

```bash
acli jira workitem create --project <KEY> --type <Type> --parent <PARENT> --summary "…" --description "…" --assignee @me --json
```

### Update

**Signals**: "assign to…", "rename PROJ-123", "add a label", "edit the summary".
**Behavior**: edit an existing issue's fields. Restate the active ticket, state the exact change, confirm, then run:

```bash
acli jira workitem edit --key <KEY> --summary "…" --assignee "…"
```

### Transition

**Signals**: "move it to review", "mark done", "put it in progress".
**Behavior**: change status. The `<Review status>` (and any other target state) is instance-specific — pull it from LEARNED.md or ask; never assume a fixed string. Confirm first; on error, surface acli's exact message (it cannot list transitions) and record the real status name to LEARNED.md.

```bash
acli jira workitem transition --key <KEY> --status "<Review status>" --yes
```

### Search

**Signals**: "find…", "which epic…", "my open issues", "list the stories".
**Behavior**: read-only. Query and present a numbered list; never mutate. Also used to locate the parent during a Create flow.

```bash
acli jira workitem search --jql "…" --fields "key,summary,issuetype,status" --csv
```

### Teaching

**Signals**: "how does acli…", "what is the parent for…", "explain the create flow".
**Behavior**: explain with real commands, link to `references/`, and do not run any mutating command. Answer the concept, then offer to run the read-only version.

---

## Read-Only vs Mutating Commands

Read-only commands never change Jira state and can run without a confirm step. Mutating commands change state and **require an explicit confirmation of every field before you run them**.

| Kind      | Command                                                                                                                           | Confirm first? |
| --------- | --------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| Read-only | `acli jira auth status`                                                                                                           | No             |
| Read-only | `acli jira workitem search --jql "…" --fields "key,summary,issuetype,status" --csv`                                               | No             |
| Read-only | `acli jira workitem view <KEY> --fields "key,summary,status,assignee,description" --json`                                         | No             |
| Mutating  | `acli jira workitem create --project <KEY> --type <Type> --parent <PARENT> --summary "…" --description "…" --assignee @me --json` | **Yes**        |
| Mutating  | `acli jira workitem edit --key <KEY> --summary "…" --assignee "…"`                                                                | **Yes**        |
| Mutating  | `acli jira workitem transition --key <KEY> --status "<Review status>" --yes`                                                      | **Yes**        |
| Mutating  | `acli jira workitem comment create --key <KEY> --body "…"`                                                                        | **Yes**        |

Confirmation means echoing back the concrete values (project, type, parent, summary, description, assignee, or the exact status/comment) and waiting for the user's go-ahead. Never mutate on assumption. The `<site>` used to build any browse URL comes from `acli jira auth status`, never a hardcoded domain — an issue URL is `<site>/browse/<KEY>-<n>`.

---

## Session Active Ticket — Memory Rules

The active ticket is the one you are currently working with. It lives **only in your conversation context** — there is **no file and no LEARNED.md entry** for it. It is deliberately gone at session end.

- **State it** after creating, viewing, or resolving a specific ticket, and hold it:

  ```text
  Active ticket: KEY-nnn — <summary>
  ```

  (Concrete form, e.g. `Active ticket: PROJ-123 — sign-in button unresponsive`.)

- **Reuse it silently** on later Jira or PR requests in the same session — do not re-ask which ticket. Before any **mutating** command, restate it so the user sees what you are about to change:

  ```text
  Using active ticket KEY-nnn
  ```

- **Ask before creating a new one while one is active** — never silently replace the pointer:

  ```text
  You have active ticket KEY-nnn. Create a new one instead of using it? (y/n)
  ```

  Apply the same guard before overwriting the active pointer with a different ticket.

- **Record the created ticket as active** — the last step of every Create flow. A ticket you created but did not set as active is dropped context the next request cannot reuse.

- The github skill reads this same active ticket from context when it raises a PR against `{owner}/{repo}`, and may name the ticket in the branch (e.g. `<type>/<KEY>-<n>-<slug>`) or commit subject (e.g. `<KEY>-<n>: <subject>`). Keep the pointer accurate so the PR links the right issue.

---

## Common Mistakes

- **Hardcoding the `<KEY>`.** Keys differ per repo (e.g. `PROJ-123`, `ABC-42`). Always detect the project key from git context; never paste a literal key into a command you reuse.
- **Hardcoding the Jira domain.** The `<site>` is instance-specific — read it from `acli jira auth status` every session and build URLs as `<site>/browse/<KEY>-<n>`. Never bake a domain into the skill.
- **Dumping code or paths into descriptions.** File paths, function/class names, stack traces, and internal identifiers belong in the PR, not the Jira description. Keep Jira text non-technical and user-visible.
- **Guessing a transition status.** acli cannot list valid transitions, and the `<Review status>` name varies per instance. Do not invent one — run the transition, and if it is rejected, surface acli's exact error and record the real name to LEARNED.md.
- **Mutating before confirmation.** create / edit / transition / comment change state. Confirm every field first; search and view are the only commands safe to run unprompted.
- **Forgetting to record the created ticket as active.** After a successful create, always set `Active ticket: KEY-nnn — <summary>`. Skipping this loses the context that the next request (and the github skill's PR) depends on.

---

## Self-Learning

When a user correction or discovery reveals a durable convention, write it to [LEARNED.md](../LEARNED.md) under the matching heading:

- **Corrections** → `## Corrections` — the user overrode something you did.
- **Preferences** → `## Preferences` — a stated way the user wants Jira work handled.
- **Discovered Conventions** → `## Discovered Conventions` — confirmed facts such as a repo→`<KEY>` mapping, the real `<Review status>` name, or observed `--parent` behavior on this instance.

Use the exact format, one rule per line:

```text
- YYYY-MM-DD: rule
```

The active-ticket pointer is the one thing that never goes to LEARNED.md — it is context-only by design.
