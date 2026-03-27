# Frontend Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are frontend-specific overrides.

```
ROLE:     Senior frontend engineer analyzing a production client-side codebase
GOAL:     Generate a production-grade frontend skill directory
SCOPE:    Client-side code only — ignore server/, backend/, api/ (Python/Go/Java), mobile/, infra
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Frontend Only

Ignore backend, mobile, and infrastructure code. Scan for:

**Framework & Toolchain**

- Framework (React/Vue/Angular/Svelte/Next.js/Nuxt/Remix/Astro/etc.)
- Language (TypeScript/JavaScript — strict mode? version?)
- Package manager (npm/pnpm/yarn/bun) + lock file
- Build tool (Vite/Webpack/Turbopack/esbuild/Rollup)
- Monorepo setup (Nx, Turborepo, Lerna)
- Key dependencies and roles

**Component Architecture**

- Pattern (functional, class-based, SFC, standalone)
- File structure (single file, co-located styles, barrel exports)
- Naming conventions (PascalCase files, kebab-case, index.ts)
- Props/inputs (interfaces, types, decorators)
- Slots/children/content projection
- Lifecycle usage + change detection strategy (OnPush, signals)

**State Management**

- Solution (Redux/Zustand/Pinia/NgRx/Signals/Context/Jotai)
- Where state lives (global store, component-local, URL params)
- Data fetching (React Query/SWR/Apollo/RxJS/fetch wrappers)
- Caching strategy + optimistic updates

**Routing**

- Router (React Router/Vue Router/Angular Router/file-based)
- Route structure (file-based, config-based, code-based)
- Guards/middleware + dynamic routes + nested routing

**Styling**

- CSS approach (CSS Modules/Tailwind/styled-components/SCSS/CSS-in-JS)
- Design system (Material UI, Ant Design, Shadcn, custom)
- Theming + responsive strategy + animation library

**SSR/SSG/ISR** (if applicable)

- Rendering strategy (SSR, SSG, ISR, hybrid)
- Data fetching at build/request time (getServerSideProps, loader, etc.)
- Hydration patterns + streaming

**Code Quality**

- TypeScript strictness level
- Linting (ESLint rules, Prettier)
- Import conventions (absolute paths, aliases, barrel files)
- Error handling (Error Boundaries, try/catch, result types)
- i18n approach

**Testing**

- Unit framework (Jest/Vitest/Karma)
- Component testing (React Testing Library/Vue Test Utils)
- E2E (Playwright/Cypress)
- Test file location + mock strategy

**Forms & Validation**

- Form library (React Hook Form/Formik/Angular Reactive Forms/VeeValidate)
- Validation (Zod/Yup/class-validator/custom)
- Error display patterns

**API Communication**

- HTTP client (Axios/fetch/HttpClient)
- API layer structure (services, hooks, repositories)
- Request/response typing + error handling
- Auth token management (interceptors, headers)

**Micro-Frontends** (if applicable)

- Module federation / import maps / web components
- Shared dependencies + routing coordination

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_frontend.md`:

1. **Component Patterns** — how this project structures UI components
2. **State & Data Flow** — how data moves through the app
3. **Coding Conventions** — naming, file structure, import style
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected framework
7. **Rendering strategy** — SSR/SSG/CSR conventions and data fetching patterns

---

## PHASE 3: BEST PRACTICES

Integrate for the detected framework:

- Component composition and reusability
- Accessibility (WCAG 2.1 AA, ARIA patterns, keyboard navigation, focus management)
- Performance (lazy loading, code splitting, memoization, virtual scrolling, bundle optimization)
- SEO (SSR/SSG patterns, meta tags, structured data)
- Error boundaries and graceful degradation
- Testing strategy (what to unit test vs E2E)
- Security (XSS prevention, CSP, sanitization, dependency auditing, classify by severity)
- Responsive design patterns
- State management best practices for detected solution
- Web vitals optimization (LCP, FID, CLS)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY frontend task — component creation, styling, state management, routing, forms, API integration, testing, accessibility, performance optimization, SSR/SSG, UI/UX.

**`allowed-tools`**: `Read Edit Write Bash(npm:*) Bash(pnpm:*) Bash(npx:*) Glob Grep` (adjust for detected package manager)

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend, mobile, infra)
3. **Architecture** — component tree overview, directory structure, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. TypeScript conventions, imports, file structure details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for XSS, sanitization, CSP verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, design system links
12. **Adaptive Interaction Protocols** — interaction modes with frontend-specific detection signals (e.g., "what is this hook" for Teaching, "another component like X" for Efficient, "render error" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/component-patterns.md` — component structure, composition, lifecycle (ALL code examples go here)
- `references/code-style.md` — TypeScript conventions, imports, formatting with full examples
- `references/security-checklist.md` — XSS prevention, sanitization, CSP verification checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/component-template.{{ext}}` — copy-paste component boilerplate (use detected extension: .tsx, .vue, .svelte)
- `references/state-patterns.md` — state management and data fetching
- `references/common-issues.md` — troubleshooting common frontend pitfalls
- `assets/config-example.{{ext}}` — build/lint/formatter config template
- `scripts/validate-frontend.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent             | Role                                                           | Tools                          | Spawn When                                                           |
| ----------------- | -------------------------------------------------------------- | ------------------------------ | -------------------------------------------------------------------- |
| component-auditor | Read-only component analysis for accessibility and consistency | Read Glob Grep                 | Accessibility audit, performance review, component consistency check |
| style-enforcer    | Design system and style compliance verification                | Read Glob Grep                 | UI consistency review, design system adherence check, theme audit    |
| test-writer       | Component and E2E test generation                              | Read Edit Write Glob Grep Bash | "write tests for X", new component creation, coverage gaps           |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/component-auditor.md` — read-only component analysis agent
- `agents/style-enforcer.md` — design system compliance agent
- `agents/test-writer.md` — component and E2E test generation agent
