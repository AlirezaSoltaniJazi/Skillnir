# Chrome Extension Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are Chrome extension-specific overrides.

```
ROLE:     Senior Chrome extension developer analyzing a production browser extension codebase
GOAL:     Generate a production-grade Chrome extension skill directory
SCOPE:    Extension code only — manifest, content scripts, service workers, popup/options pages, side panel, devtools panels. Ignore backend API, web app UI, mobile code
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Chrome Extension Only

Ignore backend API, web app UI, and mobile code. Scan for:

**Manifest & Structure**

- Manifest version (V2 vs V3)
- Permissions and host_permissions declarations
- content_scripts configuration (matches, run_at, world)
- Background configuration (service_worker vs scripts)
- web_accessible_resources entries
- content_security_policy directives
- Icons and branding assets

**Content Scripts**

- Injection patterns (matches, run_at, world)
- DOM manipulation techniques
- CSS injection patterns
- Isolated world vs MAIN world usage
- Messaging to service worker

**Service Worker / Background**

- Lifecycle management patterns
- Persistence patterns (alarms API, offscreen documents)
- Event-driven architecture
- State management (chrome.storage vs in-memory)

**Chrome APIs**

- chrome.runtime usage
- chrome.tabs usage
- chrome.storage patterns (.local/.sync/.session)
- chrome.webRequest vs chrome.declarativeNetRequest
- chrome.scripting usage
- chrome.sidePanel usage
- chrome.contextMenus usage
- chrome.notifications usage
- chrome.action usage

**Message Passing**

- Content↔background messaging
- Popup↔background messaging
- External messaging (externally_connectable)
- Long-lived connections (chrome.runtime.connect/ports)
- One-time messages (sendMessage/onMessage)
- Typed message schemas

**UI Surfaces**

- Popup (action) implementation
- Options page (embedded/full page)
- Side panel implementation
- Devtools panel implementation
- Content script injected UI (shadow DOM)

**Security**

- Content Security Policy configuration
- web_accessible_resources exposure
- Origin restrictions
- externally_connectable whitelist
- Script injection controls
- No eval/new Function enforcement

**Build & Packaging**

- Bundler (webpack/vite/rollup/esbuild/crxjs)
- TypeScript support
- Hot reload setup
- Environment configs (dev/prod/staging)
- Source maps configuration

**Testing**

- Unit testing (Jest/Vitest mocking chrome.* APIs with jest-chrome)
- E2E testing (Puppeteer/Playwright with --load-extension)
- Integration testing service worker
- Testing content scripts

**Code Quality**

- TypeScript usage and strictness
- Type definitions (@anthropic-ai/chrome-types or @anthropic-ai/web-extensions)
- Linting (eslint) configuration
- Error handling patterns
- Logging approach

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_chrome_extension.md`:

1. **Architecture Patterns** — how this extension structures code across manifest, service worker, content scripts, and UI surfaces
2. **Coding Conventions** — style, naming, structure conventions
3. **Package Patterns** — key packages and idiomatic usage
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected build tooling and manifest version
7. **Message passing conventions** — message schemas, routing, error handling

---

## PHASE 3: BEST PRACTICES

Integrate for the detected manifest version and build tooling:

1. Manifest V3 compliance (no remotely hosted code, service worker lifecycle, declarativeNetRequest over webRequest blocking)
2. Least-privilege permissions (activeTab over tabs, minimal host_permissions, optional_permissions for non-critical)
3. Message passing architecture (type-safe message schemas, error handling, response patterns, port lifecycle)
4. Service worker persistence (alarms for keep-alive, offscreen documents for long tasks, state recovery after termination)
5. Content script isolation (avoid global namespace pollution, shadow DOM for injected UI, minimal DOM footprint)
6. CSP compliance (no inline scripts, no eval, nonce-based if needed, strict CSP policy)
7. Storage patterns (chrome.storage.local vs .sync vs .session, quota management, migration between storage types)
8. Cross-browser compatibility (webextension-polyfill for Firefox/Edge, feature detection over user-agent sniffing)
9. Chrome Web Store compliance (required permission justifications, review guidelines, privacy policy)
10. Performance (lazy content script injection via chrome.scripting, minimal background wake-ups, efficient DOM observation with MutationObserver)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Chrome extension task — manifest editing, content script development, service worker logic, popup/options UI, message passing, chrome.* API usage, extension debugging, permission management, Chrome Web Store publishing, extension security review.

**`allowed-tools`**: `Read Edit Write Bash(npm:*) Bash(npx:*) Bash(node:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (frontend skill for web app UI, js skill for general JS/TS)
3. **Architecture** — extension structure diagram, manifest overview, message flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only (TypeScript conventions, imports). Full formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only (add new chrome API, create content script, add context menu), no code blocks
7. **Testing Standards** — rules list + link to references/
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for CSP, permissions, origin verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, Chrome extension docs
12. **Adaptive Interaction Protocols** — interaction modes with Chrome extension-specific detection signals (e.g., "manifest.json error" for Diagnostic, "another content script like X" for Efficient, "what does chrome.runtime do" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/manifest-patterns.md` — manifest configuration patterns and examples
- `references/message-passing-guide.md` — typed message schemas, routing, port lifecycle examples
- `references/service-worker-patterns.md` — persistence, lifecycle, state recovery patterns
- `references/code-style.md` — import order, TypeScript conventions, formatting with full examples
- `references/security-checklist.md` — per-permission, per-content-script, per-CSP verification checklists
- `references/common-issues.md` — troubleshooting common Chrome extension pitfalls
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `content-script-template.ts` — copy-paste content script template
- `assets/manifest-template.json` — manifest.json starter template
- `scripts/validate-chrome-extension.sh` — manifest + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent            | Role                                                    | Tools                          | Spawn When                                                       |
| ---------------- | ------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------- |
| code-reviewer    | Read-only code analysis against SKILL.md patterns       | Read Glob Grep                 | PR review, code audit, architecture compliance check             |
| security-auditor | CSP and permissions audit for extension security        | Read Glob Grep                 | Security review, permission audit, CSP verification              |
| test-writer      | Test generation following project conventions           | Read Edit Write Glob Grep Bash | "write tests for X", new content script creation, coverage gaps  |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/code-reviewer.md` — read-only Chrome extension code analysis agent
- `agents/security-auditor.md` — CSP and permissions audit agent
- `agents/test-writer.md` — test generation agent
