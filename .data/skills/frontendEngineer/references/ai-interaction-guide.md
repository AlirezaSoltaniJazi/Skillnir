# AI Interaction Guide — Frontend Engineer

> Anti-dependency strategies, correction protocols, and interaction patterns for NiceGUI frontend development.

---

## Anti-Dependency Strategies

### Prevent Pattern Repetition Without Understanding

- After generating 3+ similar components, ask: "Should I create a shared base component?"
- After writing similar page layouts, point to existing page patterns in `pages/`
- Reference `references/component-template.py` for standard component boilerplate

### Promote Self-Sufficiency

- In teaching mode, explain WHY a NiceGUI pattern works (context managers, reactivity)
- After fixing a styling issue, explain the project's CSS class conventions
- Reference specific project components as examples, not just abstract rules

### Avoid Cargo-Culting

- Don't blindly copy React/Vue patterns — NiceGUI has its own idioms
- If a pattern seems wrong for NiceGUI, say so and suggest alternatives
- Always check LEARNED.md before applying a convention — it may have been corrected

---

## Correction Protocol

When the user corrects frontend code:

1. **Acknowledge** the specific mistake:
   - "I used raw HTML instead of NiceGUI elements — that breaks reactivity."

2. **Restate as a rule**:
   - "Understood: always use `ui.label()` / `ui.card()`, never `ui.html()` with content."

3. **Apply immediately** to all code in the current session.

4. **Write to LEARNED.md** under `## Corrections`:
   ```
   - 2026-03-31: Never use ui.html() for content — use NiceGUI elements for reactivity
   ```

---

## Preference Elicitation Protocol

When encountering an undocumented UI convention:

1. Check LEARNED.md for prior preferences
2. Check existing components for implicit patterns
3. Ask ONE targeted question: "I see components use `p-5` padding. Should new components match this, or is there a case for `p-6`?"
4. Write the answer to LEARNED.md under `## Preferences`

---

## Mode-Specific Anti-Patterns

### Teaching Mode

- ❌ Don't just say "use .classes()" — explain how NiceGUI's context manager creates the element
- ❌ Don't reference React hooks or Vue directives — this is NiceGUI/Python
- ✅ Point to actual project components as learning examples

### Efficient Mode

- ❌ Don't explain Tailwind basics when duplicating an existing component
- ❌ Don't ask about color choices when `_COLOR_HEX` already defines the palette
- ✅ Copy the exact pattern from the most similar existing component

### Diagnostic Mode

- ❌ Don't suggest "check the browser console" first — check Python code
- ❌ Don't assume JavaScript issues — NiceGUI problems are Python-side
- ✅ Trace the styling chain: `_GLOBAL_CSS` → `.classes()` → `.props()` → `.style()`

---

## Convention Surfacing

When discovering an implicit convention not documented in SKILL.md:

1. Verify it's consistent across 3+ files
2. Write to LEARNED.md under `## Discovered Conventions`
3. Example: "- 2026-03-31: All form inputs use `.props('outlined dense rounded')` consistently"
