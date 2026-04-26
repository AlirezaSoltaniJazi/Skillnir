# AI Interaction Guide — Frontend Developer

> Anti-dependency strategies, correction protocols, and interaction patterns for frontend development.

---

## Anti-Dependency Strategies

### Prevent Pattern Repetition Without Understanding

- After generating 3+ similar components, ask: "Should I create a shared base component or variant system?"
- After writing similar data-fetching hooks, point to existing hooks as patterns
- Reference `references/component-template.tsx` for standard boilerplate
- If the user keeps asking for the same kind of component, suggest abstracting a generic version

### Promote Self-Sufficiency

- In teaching mode, explain WHY a pattern works (React reconciliation, Vue reactivity, Angular change detection)
- After fixing a bug, explain the root cause and how to recognize it next time
- Reference specific project files as examples, not just abstract rules
- Encourage the user to run tests and check the browser DevTools themselves

### Avoid Cargo-Culting

- Don't blindly add `useMemo`/`useCallback` everywhere — explain when memoization actually helps
- Don't add `useEffect` as the first solution — consider if the logic belongs in an event handler
- If a pattern seems wrong for the framework, say so and suggest the idiomatic approach
- Always check LEARNED.md before applying a convention — it may have been corrected

---

## Correction Protocol

When the user corrects frontend code:

1. **Acknowledge** the specific mistake:
   - "I used `any` for the API response type — that bypasses TypeScript safety."

2. **Restate as a rule**:
   - "Understood: always type API responses with a proper interface, even if it requires defining the shape."

3. **Apply immediately** to all code in the current session.

4. **Write to LEARNED.md** under `## Corrections`:
   ```
   - 2026-04-26: Always type API responses — never use `any`. Define response interfaces in types/.
   ```

---

## Preference Elicitation Protocol

When encountering an undocumented convention:

1. Check LEARNED.md for prior preferences
2. Check existing project files for implicit patterns
3. Ask ONE targeted question: "I see components use CSS Modules. Should new components follow this, or is there a case for switching to Tailwind?"
4. Write the answer to LEARNED.md under `## Preferences`

---

## Mode-Specific Anti-Patterns

### Teaching Mode

- Don't just say "use `useEffect`" — explain the dependency array and cleanup function
- Don't reference backend patterns when explaining frontend concepts
- Point to actual project components as learning examples
- Explain framework-specific behavior (virtual DOM, signals, dirty checking)

### Efficient Mode

- Don't explain React basics when duplicating an existing component
- Don't ask about styling choices when the project already has a design system
- Copy the exact pattern from the most similar existing component
- Skip explanations unless the pattern deviates from existing code

### Diagnostic Mode

- Don't suggest "clear cache and restart" first — read the error message and code
- Check the component → its props → its hooks → its dependencies in that order
- For hydration errors: compare server vs client render paths
- For styling issues: check specificity, class conflicts, and load order
- For state issues: trace the data flow from source to consumer

### Review Mode

- Don't silently make changes — report findings without modifying code
- Check against the project's conventions (SKILL.md + LEARNED.md)
- Prioritize findings: accessibility > correctness > performance > style
- Provide severity levels: critical (must fix), warning (should fix), info (nice to have)

---

## Convention Surfacing

When discovering an implicit convention not documented in SKILL.md:

1. Verify it's consistent across 3+ files
2. Write to LEARNED.md under `## Discovered Conventions`
3. Example: "- 2026-04-26: All form components use React Hook Form with zodResolver — no custom validation logic"

---

## Common AI Mistakes to Avoid

| Mistake                                     | Better Approach                                      |
| ------------------------------------------- | ---------------------------------------------------- |
| Adding `useEffect` for derived state        | Use `useMemo` or compute inline during render        |
| Wrapping everything in `useCallback`        | Only memoize when passed to optimized child          |
| Using `any` to "fix" TypeScript errors      | Define the proper type, even if it requires effort   |
| Creating a new state manager for each feature| Use existing store patterns — don't reinvent         |
| Writing tests that test implementation       | Test behavior from the user's perspective            |
| Suggesting `// @ts-ignore` for type errors  | Fix the type definition — don't suppress             |
| Adding inline styles for static values       | Use CSS classes — inline only for runtime-dynamic    |
| Over-abstracting simple components           | Not everything needs to be generic — YAGNI applies   |
