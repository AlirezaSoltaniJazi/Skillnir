# iOS Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are iOS-specific overrides.

```
ROLE:     Senior iOS engineer analyzing a production iOS codebase
GOAL:     Generate a production-grade iOS development skill directory
SCOPE:    iOS code only — ignore server/backend, Android (*.kt, *.java, build.gradle), web/frontend, infra
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — iOS Only

**Language & Build**

- Primary language (Swift/Objective-C — ratio)
- Swift version + language features (async/await, actors, macros, property wrappers)
- Package management (SPM/CocoaPods/Carthage — manifest contents)
- SPM plugins + build plugins (SwiftLint, SwiftFormat, sourcery)
- Deployment target (minimum iOS version)
- Xcode project structure (.xcodeproj, .xcworkspace, .xcconfig files)
- Build configurations + xcconfig hierarchy
- Key dependencies and roles

**Architecture**

- Pattern (MVVM/VIPER/Clean/TCA/MVC — which layers)
- Module/target structure (feature frameworks, SPM packages)
- Base classes/protocols (BaseViewController, BaseViewModel, AnyWidget)
- Navigation (Coordinator, NavigationStack, UINavigationController, Router)
- Dependency injection (Swinject, Factory, manual, protocol-based)
- Screen organization (storyboards, xibs, programmatic, SwiftUI views)

**UI Layer**

- Framework (SwiftUI/UIKit/mixed — ratio)
- If SwiftUI: view patterns, @State, @Observable, @Environment, preference keys
- If UIKit: VC patterns, auto layout approach (SnapKit, anchors, storyboard), custom views
- Design system/theme (custom, UIKit appearance, SwiftUI modifiers)
- State pattern (ObservableObject, @Observable, Combine publishers)
- Collection patterns (diffable data source, compositional layout, LazyVStack)

**Data Layer**

- Local storage (Core Data, SwiftData, UserDefaults, Keychain, Realm)
- Network layer (URLSession, Alamofire, custom — structure)
- Repository/service pattern usage
- Data models (Codable structs, separate layers, mappers)
- Serialization (JSONDecoder config, custom coding keys, date strategies)
- Caching strategy

**Concurrency**

- Model (async/await, Combine, GCD, OperationQueue)
- Actor usage + Sendable conformance
- Task management and cancellation
- MainActor/background patterns
- Combine publishers/subscribers (if used)

**Code Quality**

- Swift style (protocol-oriented? value vs reference types?)
- Naming conventions (types, functions, properties, files)
- Access control usage (public, internal, private, fileprivate)
- Error handling (throwing functions, Result type, custom errors)
- Logging (os.log, OSLog, Logger, custom)
- SwiftLint rules + SwiftFormat config

**Testing**

- Unit (XCTest, Quick/Nimble)
- UI testing (XCUITest, snapshot testing)
- Structure + naming conventions
- Mock/stub strategy (protocols, test doubles)
- Async testing patterns

**SDK & Platform Integration**

- Platform SDKs (HealthKit, CoreLocation, AVFoundation, StoreKit, CloudKit, ARKit)
- Custom SDK wrappers + abstraction layers
- Push notifications (APNs, Firebase Cloud Messaging)
- Deep link/Universal link handling
- App extensions (widgets, share, notification content, intents)
- App Clips

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_ios.md`:

1. **Architecture Patterns** — how this project structures iOS code
2. **UI Patterns** — SwiftUI/UIKit conventions and state management
3. **Data Flow** — network/storage to UI data path
4. **Coding Conventions** — Swift style, naming, file structure
5. **Things to ALWAYS do** — non-negotiable patterns
6. **Things to NEVER do** — anti-patterns explicitly avoided
7. **Platform-specific wisdom** — lifecycle gotchas, memory management, SDK patterns

---

## PHASE 3: BEST PRACTICES

Integrate for the detected architecture:

- Swift concurrency (structured concurrency, actor isolation, Sendable)
- Memory management (ARC, weak/unowned, retain cycle prevention)
- Protocol-oriented programming + value semantics (prefer structs, COW)
- SwiftUI best practices (view composition, environment, preferences, minimal body)
- UIKit best practices (lifecycle, auto layout performance, diffable data sources)
- App lifecycle and state restoration
- Accessibility (VoiceOver, Dynamic Type, UIAccessibility)
- Security (Keychain, App Transport Security, biometric auth, data protection)
- Performance (Instruments profiling, image optimization, lazy loading, startup time)
- Testing pyramid (unit > integration > UI)
- App Store guidelines compliance

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY iOS task — SwiftUI views, UIKit controllers, ViewModels, navigation, data persistence, networking, Combine/async-await, testing, SDK integration, accessibility, performance, App Store.

**`allowed-tools`**: `Read Edit Write Bash(swift:*) Bash(xcodebuild:*) Bash(xcrun:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend, Android, frontend, infra)
3. **Architecture** — module/target diagram, key directories, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Swift conventions, access control, imports details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for keychain, ATS, biometric verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, SDK docs, architecture decisions
12. **Adaptive Interaction Protocols** — interaction modes with iOS-specific detection signals (e.g., "how does @Observable work" for Teaching, "another view like X" for Efficient, "EXC_BAD_ACCESS" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, memory bridge

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/architecture-guide.md` — module/target structure, layer responsibilities
- `references/code-style.md` — Swift conventions, access control, imports with full examples
- `references/security-checklist.md` — keychain, ATS, biometric, data protection checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/swiftui-patterns.md` — SwiftUI view composition, state management (ALL code examples)
- `references/test-patterns.md` — testing patterns with full examples
- `references/viewmodel-template.swift` — copy-paste ViewModel boilerplate
- `references/common-issues.md` — troubleshooting common iOS pitfalls
- `scripts/validate-ios.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent         | Role                                                      | Tools                          | Spawn When                                                             |
| ------------- | --------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------- |
| code-reviewer | Read-only Swift code analysis and architecture compliance | Read Glob Grep                 | PR review, architecture compliance check, SwiftUI best practices audit |
| test-writer   | XCTest/Swift Testing generation                           | Read Edit Write Glob Grep Bash | "write tests for X", new view/feature creation, coverage gaps          |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/code-reviewer.md` — read-only Swift code analysis agent
- `agents/test-writer.md` — XCTest/Swift Testing generation agent
