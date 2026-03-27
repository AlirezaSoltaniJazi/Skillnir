# Android Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are Android-specific overrides.

```
ROLE:     Senior Android engineer analyzing a production Android codebase
GOAL:     Generate a production-grade Android development skill directory
SCOPE:    Android code only — ignore server/backend, iOS (*.swift, Sources/), web/frontend, infra
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Android Only

**Language & Build**

- Primary language (Kotlin/Java — ratio)
- Kotlin version + features (coroutines, sealed classes, value classes, context receivers)
- Build system (Gradle Kotlin DSL, Groovy, version catalogs)
- Min SDK / Target SDK / Compile SDK
- Key dependencies from build.gradle(.kts) + version catalog
- Multi-module structure (app + feature modules + library modules)
- Kotlin Multiplatform (KMP) usage (shared modules, expect/actual)

**Architecture**

- Pattern (MVVM/MVI/MVP/Clean Architecture — layers)
- Module structure (feature-based, layer-based, hybrid)
- Base classes/interfaces (BaseViewModel, BaseFragment, BaseActivity)
- Navigation (Navigation Component, manual fragments, Compose navigation)
- Dependency injection (Hilt/Koin/Dagger/manual)
- Screen organization (single activity + fragments, Compose destinations)

**UI Layer**

- Framework (Jetpack Compose, XML Views, mixed)
- If Compose: composable patterns, state hoisting, recomposition management, stability
- If XML: layout patterns, ViewBinding/DataBinding, custom views
- Design system/theme (Material 3, custom design system)
- Screen state pattern (sealed class, data class, StateFlow)
- UI event handling (SharedFlow, Channel, callbacks)

**Data Layer**

- Local storage (Room, DataStore, SharedPreferences, SQLite)
- Network layer (Retrofit/Ktor/OkHttp — configuration)
- Repository pattern usage
- Data models (separate domain/data/UI models, mappers)
- Serialization (Kotlinx Serialization, Gson, Moshi)
- Caching strategy

**Concurrency & Background**

- Coroutine patterns (viewModelScope, lifecycleScope, custom scopes)
- Flow patterns (StateFlow, SharedFlow, callbackFlow)
- WorkManager for background tasks
- Dispatcher usage (IO, Default, Main)

**Code Quality**

- Kotlin style (idiomatic, extension functions, scope functions)
- Naming conventions (classes, functions, packages, resources)
- Error handling (Result type, sealed classes, exceptions)
- Logging approach + lint rules/detekt configuration
- Code formatting (ktfmt, ktlint)

**Testing**

- Unit (JUnit 4/5, MockK, Mockito)
- UI testing (Compose testing, Espresso, Robolectric)
- Structure + naming conventions
- Fake/mock strategy + integration test patterns

**SDK & Platform Integration**

- Firebase (Analytics, Crashlytics, Cloud Messaging, Remote Config, Firestore)
- Google Play services (Maps, Auth, In-App Billing, Location)
- Other platform SDKs (Health Connect, CameraX, ML Kit)
- Custom SDK wrappers
- Permission handling patterns
- Deep link/URI handling + push notifications

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_android.md`:

1. **Architecture Patterns** — how this project structures Android code
2. **UI Patterns** — Compose/XML conventions and state management
3. **Data Flow** — network/DB to UI data path
4. **Coding Conventions** — Kotlin style, naming, file structure
5. **Things to ALWAYS do** — non-negotiable patterns
6. **Things to NEVER do** — anti-patterns explicitly avoided
7. **Platform-specific wisdom** — lifecycle gotchas, SDK patterns, ProGuard

---

## PHASE 3: BEST PRACTICES

Integrate for the detected architecture:

- Jetpack architecture guidelines (single activity, unidirectional data flow)
- Compose best practices (stability, recomposition, side effects, performance)
- Coroutine structured concurrency and cancellation
- Memory leak prevention (lifecycle awareness, scope management)
- Configuration change handling
- ProGuard/R8 rules and considerations
- App startup optimization (App Startup library, lazy init)
- Battery and network efficiency
- Accessibility (TalkBack, content descriptions, semantic properties, WCAG 2.1 AA mapping, touch target sizing, color contrast)
- Security (certificate pinning, EncryptedSharedPreferences, safe intents, OWASP Mobile Top 10)
- Testing pyramid (unit > integration > UI)
- KMP best practices (shared logic boundaries, platform-specific implementations)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Android task — feature modules, Compose UI, ViewModels, navigation, data layer, DI, Kotlin patterns, testing, Gradle config, SDK integration, performance, KMP.

**`allowed-tools`**: `Read Edit Write Bash(gradle:*) Bash(./gradlew:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend, iOS, frontend, infra)
3. **Architecture** — module diagram, key directories, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Kotlin conventions, imports, formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for storage, network, intent verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, SDK docs, architecture decision records
12. **Adaptive Interaction Protocols** — interaction modes with Android-specific detection signals (e.g., "what does this annotation do" for Teaching, "same pattern as X screen" for Efficient, "crash on rotation" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/architecture-guide.md` — module structure, layer responsibilities, data flow
- `references/code-style.md` — Kotlin conventions, imports, formatting with full examples
- `references/security-checklist.md` — storage encryption, network security, intent safety checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/compose-patterns.md` — Compose UI patterns, state hoisting, recomposition (ALL code examples)
- `references/test-patterns.md` — testing patterns with full examples
- `references/viewmodel-template.kt` — copy-paste ViewModel boilerplate
- `references/common-issues.md` — troubleshooting common Android pitfalls
- `scripts/validate-android.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent            | Role                                                            | Tools                          | Spawn When                                                                   |
| ---------------- | --------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------------- |
| code-reviewer    | Read-only Kotlin/Java code analysis and architecture compliance | Read Glob Grep                 | PR review, architecture compliance check, Compose best practices audit       |
| test-writer      | Android test generation (unit + instrumented)                   | Read Edit Write Glob Grep Bash | "write tests for X", new screen/feature creation, coverage gaps              |
| security-scanner | OWASP Mobile Top 10 audit and Android security analysis         | Read Glob Grep                 | Security review, pre-release audit, insecure storage/intent/IPC analysis     |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/code-reviewer.md` — read-only Android code analysis agent
- `agents/test-writer.md` — Android test generation agent
- `agents/security-scanner.md` — OWASP Mobile Top 10 security audit agent
