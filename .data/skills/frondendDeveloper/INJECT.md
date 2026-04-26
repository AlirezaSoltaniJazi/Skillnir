# frondendDeveloper — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Stack**: TypeScript strict, React/Vue/Angular/Svelte, Next.js/Nuxt/Remix/Astro, Tailwind/CSS Modules/CSS-in-JS
- **Source**: `path/to/your/src/` — components/, pages/, hooks/, store/, styles/, lib/, types/
- **Key rules**: TypeScript strict (no `any`); typed props interfaces; one component per file; named exports; absolute imports with aliases; accessibility on every interactive element; error boundaries at route level
- **Never**: `any` for props/state; `dangerouslySetInnerHTML` with user data; secrets in client code; prop-drill 3+ levels; business logic in components; giant 300+ line components; suppress TS errors; skip keyboard accessibility
- **Sub-agents**: component-auditor (read-only audit), style-enforcer (design system), test-writer (tests)
- **Self-learning**: On correction → write to LEARNED.md. On ambiguity → check LEARNED.md first.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
