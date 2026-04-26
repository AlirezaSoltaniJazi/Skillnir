---
name: frondendDeveloper
description: >-
  Generic frontend development skill for modern web applications. Covers component
  architecture, routing, state management, styling, forms, API integration, SSR/SSG,
  testing, accessibility, performance, and security across React, Vue, Angular, Svelte,
  Next.js, Nuxt, Remix, and Astro stacks. Activates when creating components, styling
  pages, adding routes, managing state, working with forms, fetching data, writing
  tests, auditing accessibility, optimizing performance, or editing any client-side
  source file.
compatibility: "TypeScript/JavaScript, React/Vue/Angular/Svelte, Next.js/Nuxt/Remix/Astro, Tailwind/CSS Modules/CSS-in-JS"
metadata:
  author: YOUR_PROJECT
  version: "1.0.0"
  sdlc-phase: development
allowed-tools: Read Edit Write Bash(npm:*) Bash(pnpm:*) Bash(npx:*) Bash(yarn:*) Bash(bun:*) Bash(node:*) Glob Grep Agent
---

<!-- SKILL.md target: ~300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: frondendDeveloper skill" at the very start of your response before doing any work.

## When to Use

1. Writing or modifying any file under `path/to/your/components/` or `path/to/your/pages/`
2. Creating new UI components (functional, SFC, class-based, standalone)
3. Adding routes (file-based, config-based, or code-based)
4. Styling with Tailwind, CSS Modules, styled-components, SCSS, or CSS-in-JS
5. Managing state (Redux, Zustand, Pinia, NgRx, Signals, Context, Jotai)
6. Working with forms, validation, API integration, SSR/SSG, testing, or accessibility

## Do NOT Use

- **Backend / API server code** (Express, Fastify, Django, Flask, Go, Java) — use the backend skill
- **Mobile code** (React Native, Flutter, Swift, Kotlin) — use the mobile skill
- **Infrastructure / DevOps** (Docker, CI/CD, Terraform, Kubernetes) — use the devops skill

## Architecture

```
path/to/your/src/
├── components/           # Reusable UI components
│   ├── ui/               # Primitives (Button, Input, Card, Modal)
│   ├── layout/           # Layout wrappers (Header, Sidebar, Footer)
│   └── features/         # Feature-specific compositions
├── pages/ (or routes/)   # Route-level page components
├── hooks/ (or composables/ or services/)  # Shared logic
├── store/ (or state/)    # Global state management
├── styles/               # Global styles, theme, design tokens
├── lib/ (or utils/)      # Pure utilities, helpers, constants
├── types/                # Shared TypeScript interfaces/types
└── __tests__/ (or co-located *.test.* / *.spec.*)
```

**Data flow**: User interaction → Event handler → State update → Re-render → DOM update.

**Styling layers**: Design tokens (CSS variables) → Utility classes (Tailwind) → Component styles (CSS Modules / scoped) → Inline styles (dynamic only).

## Key Patterns

| Pattern            | Approach                                           | Key Rule                                                      |
| ------------------ | -------------------------------------------------- | ------------------------------------------------------------- |
| Component files    | One component per file, named export preferred     | Filename matches component name (PascalCase or framework SFC) |
| Props/inputs       | TypeScript interface or type alias                 | Always type props — never use `any`                           |
| Composition        | Slots/children for content projection              | Prefer composition over prop-drilling or inheritance          |
| Custom hooks       | `use*` prefix (React/Vue) or injectable services   | Extract shared logic into reusable hooks/composables          |
| Error boundaries   | Framework error boundary at route level            | Wrap route trees — show fallback UI, log to service           |
| Data fetching      | React Query / SWR / Apollo / loader functions      | Colocate fetching with route or feature — never in primitives |
| Form handling      | Controlled via form library + schema validation    | Separate validation schema from UI — validate on blur+submit  |
| Lazy loading       | `React.lazy` / dynamic `import()` / route splitting| Split at route boundaries first, then heavy feature components |

See [references/component-patterns.md](references/component-patterns.md) for full code examples.

## Code Style

| Rule               | Convention                                                     |
| ------------------ | -------------------------------------------------------------- |
| Language           | TypeScript strict mode — no `any`, no `@ts-ignore` without justification |
| Formatter          | Prettier (or project-defined formatter) — never manual formatting |
| Import style       | Absolute path aliases (`@/components/Button`) — no deep relative paths |
| Import order       | Node built-ins → third-party → aliased local → relative local  |
| Naming — files     | PascalCase for components (`Button.tsx`), camelCase for utilities (`formatDate.ts`) |
| Naming — components| PascalCase (`<UserProfile />`, `<StatCard />`)                 |
| Naming — hooks     | camelCase with `use` prefix (`useAuth`, `useDebounce`)         |
| Naming — constants | SCREAMING_SNAKE_CASE (`API_BASE_URL`, `MAX_RETRIES`)          |
| Naming — types     | PascalCase with suffix (`UserProps`, `AuthState`, `ApiResponse`) |
| Naming — CSS       | kebab-case for classes, BEM or utility-first by project choice |
| Exports            | Named exports preferred — default exports only for pages/routes |
| Strings            | Single quotes (or project convention) — template literals for interpolation only |

See [references/code-style.md](references/code-style.md) for full formatting examples.

## Common Recipes

1. **Add a new component**: Create `ComponentName.tsx` (or `.vue`/`.svelte`) → define typed props interface → implement render → export named → add to barrel `index.ts` if present → write co-located test
2. **Add a new route**: Create page file in `pages/` (or add to router config) → wrap with layout → add error boundary → add to navigation → add route guard if auth-required
3. **Add global state**: Create slice/store/atom in `store/` → define typed state shape → export selectors/actions → connect in components via hook/composable → add dev tools integration
4. **Add a form**: Define Zod/Yup schema → create form with hook (React Hook Form / VeeValidate / Angular Reactive Forms) → wire validation → handle submit → display field-level errors
5. **Add an API endpoint call**: Create typed request/response interfaces → add service function in `lib/api/` → integrate with data-fetching hook → handle loading/error/success states → add optimistic update if needed
6. **Add i18n**: Add translation keys to locale JSON files → wrap user-facing strings with `t()` function → test fallback to default locale

## Testing Standards

| Rule               | Convention                                                    |
| ------------------ | ------------------------------------------------------------- |
| Unit framework     | Vitest or Jest with TypeScript support                        |
| Component testing  | React Testing Library / Vue Test Utils / Angular Testing      |
| E2E framework      | Playwright or Cypress                                         |
| Test file location | Co-located (`Button.test.tsx`) or mirrored `__tests__/` dir   |
| Naming             | `describe('ComponentName')` → `it('should behavior')`        |
| Query priority     | `getByRole` > `getByLabelText` > `getByText` > `getByTestId` |
| What to test       | User interactions, state transitions, conditional rendering, edge cases |
| What NOT to test   | Framework internals, third-party library behavior, CSS output |
| Mocking            | Mock API calls and external services — never mock the component under test |

See [references/test-patterns.md](references/test-patterns.md) for full test examples.

## Performance Rules

- Lazy-load routes and heavy components with dynamic `import()` — never bundle everything upfront
- Memoize expensive computations (`useMemo`, `computed`, `memo()`) — but don't memoize everything blindly
- Virtualize long lists (>100 items) with `react-virtual`, `vue-virtual-scroller`, or equivalent
- Optimize images: use `next/image`, `<picture>`, WebP/AVIF, lazy loading with `loading="lazy"`
- Minimize re-renders: stable references for callbacks, avoid creating objects/arrays in render
- Code-split third-party libraries: import only what's used (`import { debounce } from 'lodash-es'`)
- Monitor Web Vitals (LCP < 2.5s, FID < 100ms, CLS < 0.1) — measure in CI with Lighthouse
- Avoid layout thrashing: batch DOM reads/writes, use `transform` over `top/left` for animations
- Prefetch critical routes: use `<link rel="prefetch">` or router prefetch for likely next pages

## Security

- Sanitize all dynamic HTML — never use `dangerouslySetInnerHTML` / `v-html` / `[innerHTML]` with user data
- Validate and sanitize URL parameters before use in routing or API calls
- Never store secrets (API keys, tokens) in client-side code or localStorage
- Use `httpOnly` cookies for auth tokens — not localStorage/sessionStorage
- Apply CSP headers — restrict `script-src`, `style-src`, `img-src` to known origins
- Audit dependencies regularly (`npm audit`, `pnpm audit`) — fix critical/high severity immediately
- Escape user input in URL construction — prevent open redirect vulnerabilities

See [references/security-checklist.md](references/security-checklist.md) for detailed checklists.

## Anti-Patterns

| Anti-Pattern                                  | Why It's Wrong                                                     |
| --------------------------------------------- | ------------------------------------------------------------------ |
| Using `any` type for props or state           | Defeats TypeScript — use proper interfaces/generics                |
| Prop-drilling through 3+ levels               | Use context, state manager, or composition — not deep prop chains  |
| Business logic in components                  | Extract to hooks/services — components are for rendering           |
| Fetching data in leaf components              | Fetch at route/feature level — pass data down or use cache layer   |
| Inline styles for static values               | Use CSS classes — inline only for truly dynamic runtime values     |
| Giant monolith components (>300 lines)         | Split into smaller composed components — single responsibility     |
| Ignoring accessibility                        | Every interactive element needs keyboard access + ARIA — not optional |
| Suppressing TypeScript errors with `@ts-ignore`| Fix the type — suppression hides real bugs                         |
| Index files as component names (`index.tsx`)  | Name the file after the component — easier to find in editors/tabs |
| Catching errors silently (`catch {}`)         | Log to error service, show user feedback — never swallow errors    |

## Code Generation Rules

1. **Read before writing** — always read the target file and related components before changes
2. **Match existing style** — follow the project's formatter, naming, and import conventions exactly
3. **One component per file** — each component in its own file with matching name
4. **Type everything** — use TypeScript interfaces on all props, state, and API responses
5. **Accessibility first** — add ARIA attributes, keyboard handlers, focus management from the start
6. **On correction** — acknowledge, restate as rule, apply to all subsequent actions, write to [LEARNED.md](LEARNED.md)
7. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then project files, ask ONE question, write preference to [LEARNED.md](LEARNED.md)

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode       | Detection Signal                                                       | Behavior                                                             |
| ---------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Diagnostic | "not rendering", "layout broken", "hydration error", "white screen"    | Read component + dependencies, trace render chain, fix minimally     |
| Efficient  | "another component like X", "add page for Y", "same card as Z"        | Minimal explanation, replicate existing patterns, apply conventions   |
| Teaching   | "what is this hook", "how does X work", "explain this pattern"         | Explain with project examples, link to references/                   |
| Review     | "review this component", "check my code", "audit accessibility"        | Read-only analysis, check against conventions, report without changes |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections → `## Corrections` section
- Preferences → `## Preferences` section
- Discovered conventions → `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Sub-Agent Delegation

| Agent             | Role                                         | Spawn When                                          | Tools                          |
| ----------------- | -------------------------------------------- | --------------------------------------------------- | ------------------------------ |
| component-auditor | Read-only component analysis for consistency | Accessibility audit, component pattern compliance   | Read Glob Grep                 |
| style-enforcer    | Design system and style compliance check     | UI consistency review, theme audit, design system   | Read Glob Grep                 |
| test-writer       | Component and E2E test generation            | "write tests for X", new component, coverage gaps   | Read Edit Write Glob Grep Bash |

**Delegation rules**: Spawn when task is self-contained and won't need follow-up context. Never delegate tasks requiring architectural decisions. See [agents/](agents/) for full definitions.

## Freedom Levels

| Level             | Scope                                                                          | Examples                                               |
| ----------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------ |
| **MUST** follow   | TypeScript strict, typed props, accessibility, error boundaries, named exports | "MUST type all props", "MUST add keyboard support"     |
| **SHOULD** follow | Memoization for expensive ops, co-located tests, barrel exports, prefetch      | "SHOULD memoize", "SHOULD co-locate test"              |
| **CAN** customize | Spacing values, animation timing, icon choice, color shades, layout variations | "CAN adjust gap", "CAN choose different icon"          |

## References

| File                                                                     | Description                                                |
| ------------------------------------------------------------------------ | ---------------------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                 | **Auto-updated.** Corrections, preferences, conventions    |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference (hallucination firewall)     |
| [references/component-patterns.md](references/component-patterns.md)     | Component structure, composition, lifecycle with examples   |
| [references/code-style.md](references/code-style.md)                     | TypeScript conventions, imports, formatting with examples   |
| [references/state-patterns.md](references/state-patterns.md)             | State management and data fetching patterns with examples   |
| [references/test-patterns.md](references/test-patterns.md)               | Component and E2E testing strategies with examples          |
| [references/security-checklist.md](references/security-checklist.md)     | XSS prevention, CSP, sanitization checklists               |
| [references/common-issues.md](references/common-issues.md)               | Hydration, rendering, styling troubleshooting               |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols            |
| [references/component-template.tsx](references/component-template.tsx)   | Copy-paste component boilerplate (React TSX)               |
| [assets/config-example.ts](assets/config-example.ts)                     | Build/lint/formatter config templates                      |
| [scripts/validate-frontend.sh](scripts/validate-frontend.sh)             | Naming + structure convention checker                      |
| [agents/component-auditor.md](agents/component-auditor.md)               | Read-only component analysis agent                         |
| [agents/style-enforcer.md](agents/style-enforcer.md)                     | Design system compliance agent                             |
| [agents/test-writer.md](agents/test-writer.md)                           | Component and E2E test generation agent                    |
