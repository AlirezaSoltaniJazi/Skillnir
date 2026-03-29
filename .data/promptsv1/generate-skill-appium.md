# Appium Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are Appium-specific overrides.

```
ROLE:     Senior Appium mobile test automation engineer analyzing a production mobile test suite
GOAL:     Generate a production-grade Appium mobile automation skill directory
SCOPE:    Appium test code only — tests/, pages/, capabilities, driver configs, app management utilities. Ignore application source code (covered by android/ios skills), web test automation (covered by Playwright/WDIO/Selenium skills)
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Appium Only

Ignore application source code and web test automation. Scan for:

**Appium Version & Architecture**

- Appium 1.x vs 2.0 architecture
- Installed drivers (appium driver list)
- Plugins
- appium doctor
- Server config (appiumArgs, port, basePath)

**Drivers**

- XCUITest (iOS)
- UiAutomator2 (Android)
- Espresso (Android)
- Mac2
- Windows
- Gecko (mobile Firefox)
- Driver installation and versioning

**Capabilities**

- W3C capabilities format (appium: prefix)
- platformName, automationName
- app vs bundleId/appPackage+appActivity
- noReset/fullReset
- newCommandTimeout
- Device-specific caps

**App Types**

- Native
- WebView (hybrid)
- Mobile browser (Safari/Chrome)
- Context switching (NATIVE_APP vs WEBVIEW_*)
- getContexts/switchContext patterns

**Locator Strategies**

- Accessibility ID (cross-platform primary)
- UiAutomator selector (Android: new UiSelector())
- iOS predicate string
- iOS class chain
- XPath (last resort)
- id, className
- mobile: locator strategies

**Gestures**

- W3C Actions API (pointer, key, wheel)
- mobile: commands (mobile:swipe, mobile:scroll, mobile:pinchOpen)
- Deprecated TouchAction/MultiTouch
- Gesture abstraction patterns

**App Lifecycle**

- installApp, activateApp, terminateApp, backgroundApp, removeApp, isAppInstalled
- App state management
- Reset strategies (noReset vs fullReset vs app state clearing)

**Device Management**

- Real device vs simulator/emulator
- UDID management
- Appium device farms
- Parallel on multiple devices
- Device selection strategies

**Deep Linking & Notifications**

- URL scheme testing (mobile:deepLink)
- Universal/app links
- Push notification mocking/testing
- Notification center interaction

**Permission Handling**

- Auto-grant permissions (autoGrantPermissions cap)
- Runtime permission dialogs
- Platform-specific strategies (iOS alert handling, Android permission APIs)

**Cloud Testing**

- BrowserStack App Automate
- Sauce Labs Real Devices
- LambdaTest
- AWS Device Farm
- Cloud capabilities
- App upload APIs

**CI/CD**

- Emulator/simulator setup in CI (GitHub Actions, Jenkins)
- App artifact management (.apk/.ipa)
- Parallel device matrix
- Appium server management in CI

**Performance**

- adb shell dumpsys (Android)
- instruments/Xcode (iOS)
- Battery/CPU/memory profiling during tests
- Network throttling

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_appium.md`:

1. **Architecture Patterns** — how this project structures Appium test code
2. **Coding Conventions** — style, naming, structure conventions
3. **Package Patterns** — key packages and idiomatic usage
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected driver/platform
7. **Mobile-specific conventions** — capability management, gesture patterns, context switching

---

## PHASE 3: BEST PRACTICES

Integrate for the detected language/platform:

1. Appium 2.0 driver architecture — use driver plugins, appium doctor for setup validation
2. W3C capabilities always — use appium: prefix, avoid deprecated JSON Wire Protocol capabilities
3. Accessibility ID as primary locator — cross-platform, stable, meaningful
4. W3C Actions over deprecated TouchAction — modern gesture API, platform-consistent
5. Explicit waits for mobile — elements load slower on mobile, never use implicit waits or Thread.sleep
6. Context switching discipline — always verify current context, switch back after WebView interaction
7. App state management — prefer noReset with selective cleanup over fullReset (faster)
8. Device-agnostic test design — abstract platform differences, conditional logic only for platform-specific features
9. Parallel execution on device grid — multiple emulators/real devices, cloud farms for coverage
10. Cloud testing for coverage breadth — real device coverage via BrowserStack/Sauce/LambdaTest
11. CI emulator management — pre-baked emulator snapshots, cold boot avoidance, parallel emulator startup
12. Gesture abstraction in page objects — encapsulate swipe/scroll/pinch in reusable methods

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Appium task — mobile test creation, page object design, capability configuration, gesture implementation, driver setup, context switching, app lifecycle management, device management, cloud testing, CI integration, locator strategy, permission handling.

**`allowed-tools`**: `Read Edit Write Bash(appium:*) Bash(adb:*) Bash(xcrun:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (locator skill for web-only locators, testing skill for generic strategy, android/ios skills for native app development not test automation, wdio skill for WDIO-specific config — though WDIO can drive Appium)
3. **Architecture** — project structure diagram, key directories, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Import order, naming conventions, formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/locator-strategies-guide.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for per-component verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with Appium-specific detection signals (e.g., "AppiumServerError" for Diagnostic, "another screen test like X" for Efficient, "what is UiAutomator selector" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/appium-config-patterns.md` — server config, driver setup, plugin management examples
- `references/capability-patterns.md` — W3C capabilities, platform-specific caps, cloud provider caps
- `references/gesture-patterns.md` — W3C Actions, mobile: commands, gesture abstraction patterns
- `references/page-object-template` (language-dependent) — mobile page object patterns per language
- `references/locator-strategies-guide.md` — Accessibility ID, UiAutomator, iOS predicate, class chain patterns
- `references/code-style.md` — import order, naming conventions, formatting with full examples
- `references/security-checklist.md` — credential handling, app signing, device security
- `references/common-issues.md` — troubleshooting common Appium pitfalls
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `assets/capabilities-example.json` — sample capabilities for Android and iOS
- `scripts/validate-appium.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent              | Role                                                        | Tools                     | Spawn When                                                             |
| ------------------ | ----------------------------------------------------------- | ------------------------- | ---------------------------------------------------------------------- |
| test-reviewer      | Read-only test analysis against SKILL.md patterns           | Read Glob Grep            | PR review, test audit, POM compliance check                           |
| capability-auditor | Capability configuration and compatibility analysis         | Read Glob Grep            | Capability review, driver version check, cloud config validation       |
| gesture-designer   | Gesture implementation and abstraction patterns             | Read Edit Write Glob Grep | Complex gesture creation, swipe/scroll optimization, multi-touch flows |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/test-reviewer.md` — read-only Appium test analysis agent
- `agents/capability-auditor.md` — capability configuration audit agent
- `agents/gesture-designer.md` — gesture implementation and abstraction agent
