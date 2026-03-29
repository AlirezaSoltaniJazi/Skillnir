# Accessibility Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are accessibility-specific overrides.

```
ROLE:     Senior accessibility engineer auditing a codebase for WCAG compliance
GOAL:     Generate a production-grade accessibility skill directory
SCOPE:    Cross-platform accessibility analysis — examine web, iOS, and Android code for a11y issues
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Accessibility

This is a cross-cutting skill (like security). Scan ALL platform code for accessibility concerns:

**Platform & Rendering**

- Target platforms (web, iOS, Android, desktop, cross-platform)
- UI framework (React, Vue, Angular, SwiftUI, UIKit, Jetpack Compose, XML layouts, Flutter, React Native, etc.)
- Rendering approach (SSR, CSR, hybrid, native)
- Component library in use (MUI, Chakra, Radix, Ant Design, custom)
- Design system or token system (if any)

**Semantic Structure**

- HTML semantics (heading hierarchy, landmark regions, lists, tables)
- ARIA usage patterns (roles, states, properties — overuse or underuse)
- iOS accessibility traits and labels (accessibilityLabel, accessibilityHint, accessibilityTraits)
- Android content descriptions and semantics (contentDescription, importantForAccessibility, AccessibilityNodeInfo)
- Cross-platform abstraction layers (react-native-accessibility, Flutter Semantics widget)

**Keyboard & Focus**

- Tab order and focus management (tabIndex usage, focus trapping in modals/dialogs)
- Custom keyboard shortcuts and key event handlers
- Skip navigation links
- Focus indicators (visible focus ring, custom focus styles)
- iOS VoiceOver rotor support and focus groups
- Android TalkBack navigation order and focusable elements

**Visual Accessibility**

- Color contrast ratios (text, UI components, graphical objects)
- Color-only information indicators (error states, status, links)
- Text resizing and Dynamic Type support (iOS) / font scaling (Android)
- Responsive text and reflow at 400% zoom (web)
- Dark mode / high contrast mode support
- Icon-only buttons without text alternatives

**Motion & Animation**

- prefers-reduced-motion media query usage (web)
- UIAccessibility.isReduceMotionEnabled (iOS)
- AnimatorDurationScale / transition animations (Android)
- Auto-playing media, carousels, marquees
- Parallax and scroll-linked animations

**Forms & Interactive Elements**

- Form labels (explicit `<label>`, aria-label, aria-labelledby, placeholder-only anti-pattern)
- Error identification and description (aria-describedby, aria-errormessage, aria-invalid)
- Input purpose (autocomplete attributes for autofill)
- Touch target sizing (44x44pt iOS, 48x48dp Android, 24x24px web minimum)
- Custom controls (sliders, toggles, date pickers) with proper roles and states

**Testing & Tooling**

- Automated a11y testing tools configured (axe-core, Pa11y, Lighthouse, eslint-plugin-jsx-a11y)
- CI/CD accessibility gates (axe integration, Pa11y CLI)
- Manual testing evidence (VoiceOver, TalkBack, NVDA, JAWS)
- Accessibility Inspector / Xcode Accessibility audit usage
- Unit/integration tests for accessibility properties

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_accessibility.md`:

1. **Platform Patterns** — how this project targets accessibility across platforms
2. **Semantic Conventions** — ARIA, heading hierarchy, landmark, and label patterns in use
3. **Component A11y Patterns** — how reusable components handle accessibility
4. **Things to ALWAYS do** — non-negotiable accessibility patterns observed
5. **Things to NEVER do** — a11y anti-patterns explicitly avoided or commonly violated
6. **Framework-specific wisdom** — a11y patterns unique to the detected UI framework
7. **Testing conventions** — automated and manual a11y testing strategies in use

---

## PHASE 3: BEST PRACTICES

Integrate for the detected platform(s) and framework(s):

- WCAG 2.1 AA compliance as minimum baseline, AAA where feasible
- ARIA Authoring Practices Guide (APG) patterns for custom widgets
- Semantic HTML over ARIA (first rule of ARIA: don't use ARIA if native HTML works)
- Keyboard accessibility for all interactive elements (no mouse-only interactions)
- Focus management for SPAs, modals, route changes, dynamic content
- Color contrast: 4.5:1 for normal text, 3:1 for large text and UI components
- Touch target minimum sizing per platform guidelines (44pt iOS, 48dp Android, 24px web)
- Dynamic Type and font scaling (never fixed font sizes that prevent scaling)
- Reduced motion: respect user preferences, provide alternatives to motion-based UI
- Form accessibility: visible labels, grouped fields, descriptive errors, input purpose
- Live regions for dynamic content updates (aria-live, aria-atomic, aria-relevant)
- Screen reader testing across platforms (VoiceOver, TalkBack, NVDA, JAWS)
- Automated testing: axe-core for unit/integration, Lighthouse for audits, Pa11y for CI
- Image accessibility: alt text quality (descriptive, not redundant), decorative image handling
- Media accessibility: captions, transcripts, audio descriptions
- Classify issues by WCAG conformance level and impact severity (Critical/High/Medium/Low)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY accessibility task — WCAG audit, ARIA review, screen reader compatibility, keyboard navigation, color contrast check, focus management, touch target sizing, form accessibility, Dynamic Type support, reduced motion, a11y testing setup, accessibility remediation guidance.

**`allowed-tools`**: `Read Glob Grep Bash(npx:*)`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (a11y audit, WCAG compliance check, screen reader issues, keyboard navigation problems, contrast failures, new component a11y review)
2. **Do NOT Use** — cross-references to sibling skills (general frontend styling, backend logic, performance optimization unrelated to a11y)
3. **WCAG Compliance Map** — summary table mapping project areas to WCAG success criteria (Perceivable, Operable, Understandable, Robust), conformance level (A/AA/AAA), and current status
4. **Key Patterns** — summary table only (pattern name, platform, WCAG criterion, key rule). Full code examples in references/ only
5. **Semantic & ARIA Rules** — rules table only. Landmark structure, heading hierarchy, ARIA role conventions, labeling strategy in references/aria-patterns.md
6. **Common Remediation Recipes** — numbered step lists only, no code blocks (how to fix contrast, add labels, manage focus, etc.)
7. **Testing Standards** — rules list for automated + manual testing + link to references/test-patterns.md
8. **Platform-Specific Rules** — bullet list per platform (web, iOS, Android), no code examples
9. **Screen Reader Compatibility** — summary + link to references/screen-reader-checklist.md for per-component verification
10. **Anti-Patterns** — what NOT to do (with WCAG violation reference and why)
11. **References** — key files, docs, resources (WCAG spec, APG, platform guidelines)
12. **Adaptive Interaction Protocols** — interaction modes with accessibility-specific detection signals (e.g., "failing audit" for Diagnostic, "check this component" for Efficient, "what does aria-live do" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/aria-patterns.md` — ARIA role, state, and property usage patterns with full examples
- `references/wcag-checklist.md` — per-component WCAG success criteria verification checklist
- `references/screen-reader-checklist.md` — VoiceOver, TalkBack, NVDA, JAWS testing checklists per component type
- `references/color-contrast-guide.md` — contrast ratio requirements, tools, and remediation examples
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/keyboard-navigation.md` — focus order, focus trap, skip links, shortcut patterns with examples
- `references/test-patterns.md` — automated and manual a11y testing patterns with full examples
- `references/common-issues.md` — troubleshooting common accessibility pitfalls per platform
- `assets/a11y-audit-template.md` — accessibility audit report template
- `scripts/validate-accessibility.sh` — automated WCAG check runner (axe, Lighthouse, Pa11y)

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent                  | Role                                                     | Tools               | Spawn When                                                              |
| ---------------------- | -------------------------------------------------------- | ------------------- | ----------------------------------------------------------------------- |
| wcag-auditor           | WCAG checklist verification against codebase             | Read Glob Grep      | Full a11y audit, compliance check, pre-release review                   |
| screen-reader-tester   | Screen reader compatibility analysis per component       | Read Glob Grep      | New component review, screen reader bug report, VoiceOver/TalkBack test |
| color-contrast-checker | Automated contrast ratio verification across the project | Read Glob Grep Bash | Contrast audit, theme change review, dark mode verification             |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/wcag-auditor.md` — read-only WCAG compliance verification agent
- `agents/screen-reader-tester.md` — screen reader compatibility analysis agent
- `agents/color-contrast-checker.md` — automated contrast ratio verification agent
