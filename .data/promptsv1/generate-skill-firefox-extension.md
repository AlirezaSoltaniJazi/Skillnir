# Firefox Extension Skill Generator

> **Base instructions**: The shared base instructions (structure, quality gates, execution order) are already included above this prompt — do NOT attempt to read \_base-skill-generator.md from disk; it does not exist in the target project. Below are Firefox extension-specific overrides.

```
ROLE:     Senior Firefox / WebExtensions developer analyzing a production browser extension codebase
GOAL:     Generate a production-grade Firefox (WebExtensions) extension skill directory
SCOPE:    Extension code only — manifest, content scripts, background scripts/event pages, popup/options pages, sidebar, devtools panels. Ignore backend API, web app UI, mobile code
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Firefox Extension Only

Ignore backend API, web app UI, and mobile code. Scan for:

**Manifest & Structure**

- Manifest version (V2 vs V3 — Firefox supports both)
- `browser_specific_settings.gecko` (`id`, `strict_min_version`, `update_url`) — required for many APIs and AMO
- Permissions, `optional_permissions`, and `host_permissions` declarations
- content_scripts configuration (matches, run_at, world)
- Background configuration (`background.scripts` event page vs `background.service_worker`; `persistent` flag on MV2)
- `sidebar_action` / `browser_action` (MV2) vs `action` (MV3)
- web_accessible_resources entries (MV3 object form with `matches`)
- content_security_policy directives
- Icons and branding assets

**Content Scripts**

- Injection patterns (matches, run_at, world)
- Dynamic registration via `browser.contentScripts.register` / `browser.scripting.registerContentScripts`
- DOM manipulation techniques
- CSS injection patterns
- Isolated world vs MAIN world; Xray vision / `wrappedJSObject` / `exportFunction` / `cloneInto` for page-script interaction
- Messaging to background

**Background (Event Page / Service Worker)**

- Non-persistent event page lifecycle (MV2 `persistent: false`, MV3 event pages)
- Service worker support (Firefox 121+) vs event-page scripts
- Persistence patterns (alarms API, idle detection, state recovery)
- Event-driven architecture
- State management (`browser.storage` vs in-memory)

**WebExtension APIs (`browser.*`)**

- `browser.runtime` usage (promise-based `browser.*` vs callback `chrome.*`)
- webextension-polyfill usage for the `browser`/`chrome` namespace
- `browser.tabs` usage
- `browser.storage` patterns (.local/.sync/.session/.managed)
- `browser.webRequest` (Firefox keeps blocking webRequest in MV3) vs `browser.declarativeNetRequest`
- `browser.scripting` usage
- `browser.sidebarAction` (sidebar) usage
- `browser.menus` (context menus) usage
- `browser.contextualIdentities` (containers) usage
- `browser.theme` / `browser.notifications` / `browser.action`

**Message Passing**

- Content↔background messaging
- Popup↔background messaging
- External messaging (externally_connectable / native messaging via `browser.runtime.connectNative`)
- Long-lived connections (`browser.runtime.connect`/ports)
- One-time messages (`sendMessage`/`onMessage`, promise-based)
- Typed message schemas

**UI Surfaces**

- Popup (browser_action/action) implementation
- Options page (`options_ui`, embedded/full page)
- Sidebar (`sidebar_action`) implementation
- Devtools panel implementation
- Content script injected UI (shadow DOM)

**Security**

- Content Security Policy configuration
- web_accessible_resources exposure (scoped with `matches`)
- Origin restrictions
- Native messaging host allowlist
- Script injection controls
- No eval/new Function / no remotely hosted code enforcement

**Build & Packaging**

- Bundler (webpack/vite/rollup/esbuild)
- `web-ext` CLI (lint / run / build / sign)
- TypeScript support
- Hot reload setup (`web-ext run` with reload)
- Environment configs (dev/prod/staging)
- Source maps configuration

**Testing**

- Unit testing (Jest/Vitest mocking `browser.*` APIs with sinon-chrome / jest-webextension-mock / webextensions-jsdom)
- E2E testing (Playwright/Puppeteer for Firefox, `web-ext run`)
- Integration testing background/event page
- Testing content scripts

**Code Quality**

- TypeScript usage and strictness
- Type definitions (`@types/firefox-webext-browser` / `webextension-polyfill` types)
- Linting (`web-ext lint` + eslint) configuration
- Error handling patterns (promise rejection handling)
- Logging approach

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_firefox_extension.md`:

1. **Architecture Patterns** — how this extension structures code across manifest, background/event page, content scripts, and UI surfaces
2. **Coding Conventions** — style, naming, structure conventions
3. **Package Patterns** — key packages and idiomatic usage (webextension-polyfill, web-ext)
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected build tooling and manifest version
7. **Message passing conventions** — message schemas, routing, promise-based error handling

---

## PHASE 3: BEST PRACTICES

Integrate for the detected manifest version and build tooling:

1. `browser.*` promise-first API usage (webextension-polyfill for the `browser`/`chrome` namespace, `async`/`await` over callbacks)
2. `browser_specific_settings.gecko.id` + `strict_min_version` set correctly (required for AMO and version-gated APIs)
3. Manifest V3 on Firefox specifics (non-persistent event pages, `host_permissions`, blocking `webRequest` still available — a key difference from Chrome — plus `declarativeNetRequest`)
4. Least-privilege permissions (activeTab over tabs, minimal host_permissions, optional_permissions for non-critical)
5. Message passing architecture (type-safe message schemas, promise-based responses, port lifecycle)
6. Event-page persistence (alarms for keep-alive, state recovery after termination, no reliance on global state surviving)
7. Content script isolation (avoid global namespace pollution, shadow DOM for injected UI, Xray-safe page interaction via `exportFunction`/`cloneInto`)
8. CSP compliance (no inline scripts, no eval, no remotely hosted code, strict CSP policy)
9. Storage patterns (`browser.storage.local` vs .sync vs .session, quota management, migration between storage types)
10. Cross-browser compatibility (single codebase for Firefox + Chrome/Edge via webextension-polyfill, feature detection over user-agent sniffing)
11. AMO (addons.mozilla.org) compliance (mandatory signing, review guidelines, source-code submission for minified builds, privacy policy)
12. Tooling & performance (`web-ext lint`/`run`/`build`/`sign`, `about:debugging` for temporary loads, lazy content-script injection, efficient DOM observation with MutationObserver)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Firefox / WebExtensions task — manifest editing, content script development, background/event-page logic, popup/options/sidebar UI, message passing, `browser.*` API usage, cross-browser polyfill work, extension debugging (`about:debugging`, `web-ext`), permission management, AMO signing and publishing, extension security review.

**`allowed-tools`**: `Read Edit Write Bash(npm:*) Bash(npx:*) Bash(node:*) Bash(web-ext:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (chrome-extension skill for Chrome-only work, frontend skill for web app UI, js skill for general JS/TS)
3. **Architecture** — extension structure diagram, manifest overview, message flow (brief prose/table only — do NOT render an ASCII directory tree or multi-line structure diagram in SKILL.md; put any full structure map in `references/architecture-guide.md`, per the ≤5-line code-block gate)
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only (TypeScript conventions, imports). Full formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only (add new browser API, create content script, add sidebar/menu, sign with web-ext), no code blocks
7. **Testing Standards** — rules list + link to references/
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for CSP, permissions, origin verification, native messaging
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, Firefox / MDN WebExtensions docs
12. **Session Protocols** (≤20 lines) — interaction modes with Firefox extension-specific detection signals (e.g., "manifest.json / gecko id error" for Diagnostic, "another content script like X" for Efficient, "what does browser.runtime do" for Teaching), plus self-learning via LEARNED.md; deeper guidance (proficiency calibration, anti-dependency nudges) goes to references/ai-interaction-guide.md — never into SKILL.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/manifest-patterns.md` — manifest + `browser_specific_settings` configuration patterns and examples
- `references/message-passing-guide.md` — typed message schemas, routing, promise-based responses, port lifecycle examples
- `references/background-patterns.md` — event-page/service-worker persistence, lifecycle, state recovery patterns
- `references/cross-browser-guide.md` — webextension-polyfill, Chrome↔Firefox differences, feature detection
- `references/code-style.md` — import order, TypeScript conventions, formatting with full examples
- `references/security-checklist.md` — per-permission, per-content-script, per-CSP verification checklists
- `references/common-issues.md` — troubleshooting common Firefox extension pitfalls (Xray vision, signing, event-page suspension)
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `content-script-template.ts` — copy-paste content script template
- `assets/manifest-template.json` — manifest.json starter template (with `browser_specific_settings`)
- `scripts/validate-firefox-extension.sh` — manifest + structure + `web-ext lint` convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent            | Role                                              | Tools                          | Spawn When                                                      |
| ---------------- | ------------------------------------------------- | ------------------------------ | --------------------------------------------------------------- |
| code-reviewer    | Read-only code analysis against SKILL.md patterns | Read Glob Grep                 | PR review, code audit, architecture compliance check            |
| security-auditor | CSP and permissions audit for extension security  | Read Glob Grep                 | Security review, permission audit, CSP verification             |
| test-writer      | Test generation following project conventions     | Read Edit Write Glob Grep Bash | "write tests for X", new content script creation, coverage gaps |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/code-reviewer.md` — read-only Firefox extension code analysis agent
- `agents/security-auditor.md` — CSP and permissions audit agent
- `agents/test-writer.md` — test generation agent
