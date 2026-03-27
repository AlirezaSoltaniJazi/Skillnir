# Cross-Platform Mobile Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are cross-platform mobile-specific overrides.

```
ROLE:     Senior cross-platform mobile engineer analyzing a hybrid mobile codebase
GOAL:     Generate a production-grade cross-platform mobile skill directory
SCOPE:    Cross-platform mobile code only (React Native, Flutter, KMP) — ignore pure native Android/iOS, backend, web
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Cross-Platform Mobile Only

Ignore pure native Android/iOS, backend, and web code. Scan for:

**Framework & Toolchain**

- Primary framework (React Native, Flutter, KMP/Compose Multiplatform)
- Architecture variant (React Native New Architecture vs Old, Flutter 3.x, KMP with shared module)
- Package manager + dependency file (package.json, pubspec.yaml, build.gradle.kts, libs.versions.toml)
- JS engine (Hermes, JSC, V8) or Dart/Kotlin compiler configuration
- Key dependencies and usage patterns
- Version pinning strategy
- Build tooling (Metro, Gradle, Xcode build phases, Fastlane, EAS)

**Architecture**

- Project structure (monorepo vs standalone, shared module boundaries)
- Navigation pattern (React Navigation, Expo Router, go_router, Navigator 2.0, Voyager)
- State management (Redux/Zustand/Jotai for RN, Riverpod/Bloc/Provider for Flutter, StateFlow/MVI for KMP)
- Data layer (repositories, data sources, API clients)
- Dependency injection (Hilt for KMP, get_it/injectable for Flutter, context/providers for RN)
- Platform-specific code branching (Platform.OS, Platform.select, defaultTargetPlatform, expect/actual)
- Feature module organization (by feature vs by layer)
- Configuration/flavor/scheme structure (dev, staging, prod)

**Native Bridge & Interop**

- Native module pattern (Turbo Modules, JSI, platform channels, expect/actual)
- Fabric components (New Architecture) or Platform Views
- Native dependency linking (autolinking, CocoaPods, Gradle)
- FFI or direct native calls
- Event emitters / method channels / streams

**UI & Rendering**

- Component/widget library (custom design system, Material, Cupertino, NativeBase, Tamagui)
- Styling approach (StyleSheet, styled-components, ThemeData, Compose theming)
- Animation patterns (Reanimated, LayoutAnimation, implicit/explicit animations, Lottie)
- Rendering engine (Skia, Impeller, Fabric renderer)
- Responsive/adaptive layout strategy
- Accessibility patterns (semantics, accessibilityLabel, TalkBack/VoiceOver)

**Code Quality**

- Type system usage (TypeScript strictness, Dart strict-mode, Kotlin null safety)
- Linting and formatting (ESLint, dart analyze, ktlint, Prettier)
- Error handling (ErrorBoundary, FlutterError, runZonedGuarded, Result types)
- Logging (console, crashlytics, custom logger)
- Constants/enums management
- Code generation (freezed, json_serializable, graphql_codegen, Moshi)

**Testing**

- Framework (Jest/Detox for RN, flutter_test/integration_test for Flutter, kotlin.test for KMP)
- Structure (unit/widget/integration split, golden tests, snapshot tests)
- Mocking approach (mockito, mocktail, jest mocks)
- E2E/device testing (Detox, Maestro, Patrol, Appium)
- Naming conventions + coverage tooling

**Performance**

- Frame rate monitoring (Perf Monitor, DevTools timeline, Flipper)
- Bundle/app size optimization (tree shaking, code splitting, deferred components)
- Image handling (caching, lazy loading, resolution-aware)
- List virtualization (FlatList, ListView.builder, LazyColumn)
- Startup optimization (Hermes bytecode, deferred loading, splash screen)
- Memory leak prevention patterns

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_cross_platform_mobile.md`:

1. **Architecture Patterns** — how this project structures cross-platform mobile code
2. **Coding Conventions** — style, naming, structure conventions
3. **Package Patterns** — key packages and idiomatic usage
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected framework (RN/Flutter/KMP)
7. **Navigation & state conventions** — navigation structure, state flow, platform branching rules

---

## PHASE 3: BEST PRACTICES

Integrate for the detected framework:

- Cross-platform architecture principles relevant to this project
- Navigation patterns (deep linking, nested navigators, route guards)
- State management best practices (unidirectional data flow, state scoping, persistence)
- Native bridge safety (thread safety, type marshalling, error propagation across bridge)
- Platform-specific code isolation (minimize platform-specific surface area, shared-first approach)
- UI consistency vs platform fidelity trade-offs
- Performance optimization (60fps rendering, minimize bridge calls, efficient re-renders)
- Testing discipline (widget/component tests, integration tests, golden tests, what to mock)
- Security: secure storage (Keychain/Keystore), certificate pinning, obfuscation, classify by severity (Critical/High/Medium/Low)
- Accessibility compliance (WCAG mobile, screen reader support, dynamic type)
- App size optimization (tree shaking, asset compression, split APKs/app thinning)
- Offline-first patterns (local DB, sync strategies, optimistic updates)
- CI/CD for mobile (code signing, OTA updates, store deployment)
- Crash reporting and error boundary strategies

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY cross-platform mobile task — screen development, widget/component creation, navigation, state management, native bridge, platform channels, animations, testing, performance tuning, build configuration, app store deployment.

**`allowed-tools`**: `Read Edit Write Bash(npx:*) Bash(flutter:*) Bash(dart:*) Bash(gradle:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend, pure native, infra, web)
3. **Architecture** — project structure diagram, shared vs platform-specific directories, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Import order, component/widget structure, formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for per-component verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with cross-platform mobile-specific detection signals (e.g., "red screen" for Diagnostic, "add a new screen" for Efficient, "how does this bridge work" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/navigation-patterns.md` — navigation structure, deep linking, route examples (ALL code examples go here)
- `references/code-style.md` — import order, component/widget structure, formatting with full examples
- `references/security-checklist.md` — per-screen, per-bridge, per-storage verification checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/component-template.{{ext}}` — copy-paste screen/widget template (use detected framework extension)
- `references/test-patterns.md` — testing patterns with full examples
- `references/common-issues.md` — troubleshooting common cross-platform pitfalls
- `assets/env-example` — environment variable template
- `scripts/validate-mobile.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent                  | Role                                                        | Tools                          | Spawn When                                                       |
| ---------------------- | ----------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------- |
| code-reviewer          | Read-only code analysis against SKILL.md patterns           | Read Glob Grep                 | PR review, code audit, architecture compliance check             |
| platform-bridge-auditor | Audit native bridge safety, thread handling, type marshalling | Read Glob Grep                 | Native module changes, bridge code review, platform channel audit |
| test-writer            | Test generation following project conventions               | Read Edit Write Glob Grep Bash | "write tests for X", new screen/widget creation, coverage gaps   |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/code-reviewer.md` — read-only cross-platform mobile code analysis agent
- `agents/platform-bridge-auditor.md` — native bridge safety audit agent
- `agents/test-writer.md` — test generation agent
