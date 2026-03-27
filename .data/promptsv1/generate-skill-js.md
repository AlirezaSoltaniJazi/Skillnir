# JavaScript/TypeScript Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are JS/TS-specific overrides.

```
ROLE:     Senior JavaScript/TypeScript engineer analyzing a production JS/TS codebase
GOAL:     Generate a production-grade JS/TS development skill directory
SCOPE:    JavaScript and TypeScript code only — ignore backend (Python/Go/Java), mobile-native (Swift/Kotlin), infra (Docker/Terraform)
OUTPUT:   SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — JS/TS Only

**Language & Runtime**

- Language (JavaScript/TypeScript — strict mode? version?)
- Runtime (Node.js/Deno/Bun — version)
- Package manager (npm/pnpm/yarn/bun) + lock file
- TypeScript config (tsconfig.json — strictness, module system, target)
- Monorepo setup (Nx, Turborepo, Lerna, workspaces)
- Key dependencies and their roles

**Framework & Architecture**

- Framework (React/Vue/Angular/Svelte/Next.js/Nuxt/Express/Fastify/NestJS/Hono/etc.)
- Architecture pattern (MVC, layered, modular, microservices, serverless)
- Server-side (Express/Fastify/NestJS/Hono) vs client-side (React/Vue/Angular) vs full-stack (Next.js/Nuxt/Remix)
- API patterns (REST/GraphQL/tRPC — routing, middleware, validation)
- State management (Redux/Zustand/Pinia/NgRx/Signals/Jotai)
- Data fetching (React Query/SWR/Apollo/fetch wrappers/tRPC)

**Code Quality**

- TypeScript strictness level and custom rules
- Linting (ESLint rules, Prettier config, Biome)
- Import conventions (absolute paths, aliases, barrel files)
- Error handling approach (try/catch, Result types, error boundaries)
- Naming conventions (camelCase, PascalCase — where each is used)
- Module system (ESM/CJS/hybrid)

**Testing**

- Unit framework (Jest/Vitest/Mocha)
- Component testing (React Testing Library/Vue Test Utils/Angular TestBed)
- E2E (Playwright/Cypress/WebDriverIO)
- API testing (Supertest/Pactum)
- Test file location + mock strategy
- Coverage tooling

**Build & Tooling**

- Build tool (Vite/Webpack/Turbopack/esbuild/Rollup/tsup/SWC)
- Bundling strategy (code splitting, tree shaking, lazy loading)
- Dev server and HMR setup
- Environment variables pattern (.env, runtime config)
- Pre-commit hooks (husky, lint-staged)

**Database & ORM** (if applicable)

- ORM/query builder (Prisma/Drizzle/TypeORM/Sequelize/Knex/Mongoose)
- Database (PostgreSQL/MySQL/MongoDB/SQLite)
- Migration approach
- Schema validation (Zod/Yup/Joi/class-validator)

**Deployment**

- Deploy target (Vercel/Netlify/AWS Lambda/Docker/Node server)
- SSR/SSG/ISR strategy (if applicable)
- Edge functions or middleware

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_js.md`:

1. **Architecture Patterns** — how this project structures JS/TS code
2. **Component/Module Patterns** — UI components or API modules
3. **Data Flow** — state management, data fetching, API communication
4. **Coding Conventions** — naming, file structure, import style
5. **Things to ALWAYS do** — non-negotiable patterns observed
6. **Things to NEVER do** — anti-patterns explicitly avoided
7. **Framework-specific wisdom** — patterns unique to the detected framework

---

## PHASE 3: BEST PRACTICES

Integrate for the detected stack:

- TypeScript best practices (strict mode, discriminated unions, branded types, const assertions)
- Error handling hierarchy (custom errors, error boundaries, global handlers)
- Performance (lazy loading, code splitting, memoization, bundle optimization)
- Security (XSS prevention, input sanitization, CSP, dependency auditing)
- Testing strategy (what to unit test vs integration test vs E2E)
- Async patterns (Promises, async/await, error handling in async code)
- API design (validation, error responses, pagination, versioning)
- Node.js best practices (event loop, streams, graceful shutdown, clustering)
- Package management (lockfile discipline, dependency auditing, peer dependencies)
- Accessibility (ARIA, semantic HTML, keyboard navigation — if UI framework)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY JavaScript/TypeScript task — Node.js server code, React/Vue/Angular components, API endpoints, database queries, testing, build config, TypeScript patterns, package management, deployment.

**`allowed-tools`**: `Read Edit Write Bash(npm:*) Bash(npx:*) Bash(pnpm:*) Bash(node:*) Bash(tsx:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend if Python/Go/Java, mobile, infra)
3. **Architecture** — project structure diagram, module boundaries, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. TypeScript conventions, imports, formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with JS/TS-specific detection signals (e.g., "what is this type" for Teaching, "another component like X" for Efficient, "TypeError" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/patterns.md` — component/module/API patterns with full code examples (ALL code examples go here)
- `references/code-style.md` — TypeScript conventions, imports, formatting with full examples
- `references/security-checklist.md` — XSS, CSP, dependency audit, input validation checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/template.ts` (or `.tsx`) — copy-paste component/module boilerplate
- `references/test-patterns.md` — testing patterns with full examples
- `references/common-issues.md` — troubleshooting common JS/TS pitfalls
- `assets/tsconfig-example.json` — TypeScript config template
- `scripts/validate-js.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent           | Role                                                     | Tools                          | Spawn When                                                        |
| --------------- | -------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------------- |
| code-reviewer   | Read-only TypeScript/JavaScript code analysis            | Read Glob Grep                 | PR review, type safety audit, code quality check                  |
| test-writer     | Test generation (Jest/Vitest) following project patterns | Read Edit Write Glob Grep Bash | "write tests for X", new module/component creation, coverage gaps |
| bundle-analyzer | Bundle size and performance analysis                     | Read Glob Grep Bash            | Performance review, bundle optimization, dependency size audit    |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/code-reviewer.md` — read-only JS/TS code analysis agent
- `agents/test-writer.md` — test generation agent
- `agents/bundle-analyzer.md` — bundle size and performance agent
