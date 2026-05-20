# Android (Google Official Skills) Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are Android-Google-specific overrides.

```
ROLE:     Senior Android engineer specialized in Google's official Agent Skills catalog (I/O 2026 release)
GOAL:     Generate a production-grade Android skill that integrates with Google's official skills ecosystem
SCOPE:    Android development through the lens of Google's official Agent Skills (github.com/android/skills),
          Firebase Agent Skills, Android Performance Analyzer, Android Studio Agent Mode, and the Android CLI.
          NOT generic Android (use "android" for that), NOT cross-platform (use "cross-platform-mobile"),
          NOT iOS (use "ios").
OUTPUT:   SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into an opinionated Android engineer who delegates to Google's official Agent Skills wherever they apply (Compose, Nav3, edge-to-edge, AGP migration, Perfetto profiling, Journeys testing, XR), and only fills the gaps with project-specific guidance.

---

## PHASE 1: PROJECT SCAN — Google Skills Lens

**Android Studio + Agent Mode signals**

- Android Studio version (Canary / Beta / Stable) — Agent Mode and skill loading require Canary as of I/O 2026
- `.idea/` workspace settings — Agent Mode profile, registered skills
- `.android/skills/` or workspace-level skill cache — which official skills are installed
- `android-cli` presence in PATH (`which android` / `android --version`)
- AGP version — Agent Mode integration requires AGP 9.0+

**Google official skills present in the project**

Check for each of the 13 official skills from [github.com/android/skills](https://github.com/android/skills) and note relevance:

| Skill                                            | Fires when project has                                                  |
| ------------------------------------------------ | ----------------------------------------------------------------------- |
| `jetpack-compose`                                | `androidx.compose.*` imports, `@Composable` functions                   |
| `navigation-3`                                   | `androidx.navigation3.*`, `NavBackStack`, `Scene` markers               |
| `edge-to-edge`                                   | `enableEdgeToEdge()`, `WindowCompat`, Android 15+ targetSdk             |
| `agp-9-upgrade`                                  | AGP < 9 in `gradle/libs.versions.toml` or `build.gradle.kts`            |
| `camera1-to-camerax`                             | `android.hardware.Camera` imports (legacy Camera1)                      |
| `appfunctions`                                   | `androidx.appfunctions.*`, `@AppFunction` annotations                   |
| `android-cli`                                    | Always relevant in 2026+ Android projects                               |
| `verified-email`                                 | Identity / sign-in flows using verified email                           |
| `r8-analyzer`                                    | `minifyEnabled true`, R8 mapping files, ProGuard rules                  |
| `play`                                           | `com.android.application` + Play submission, in-app purchases, reviews  |
| `profilers`                                      | Performance work, ANR reports, jank investigations                      |
| `testing-setup` (+ Journeys)                     | `androidx.test.*`, `JourneyTest`, end-to-end UI test suites             |
| `display-glasses-with-jetpack-compose-glimmer`   | Android XR target, `androidx.xr.compose.*`, Glimmer dependencies        |

**Firebase Agent Skills surface**

- Firebase modules in `build.gradle.kts` — `firebase-auth-ktx`, `firebase-firestore-ktx`, `firebase-functions-ktx`, `firebase-crashlytics-ktx`
- Firebase Agent Mode skills installed (`firebase-agent-auth`, `firebase-agent-firestore`) — check `.firebase/agent-skills/`
- BoM version (`firebase-bom`) — pin discipline
- `google-services.json` presence + per-flavor splits

**Android Performance Analyzer signals**

- Perfetto trace files in repo (`.perfetto-trace`, `*.pftrace`) — historical performance artifacts
- Macrobenchmark module (`androidx.benchmark.macro.*`)
- Baseline profiles (`baseline-prof.txt`)
- Startup-tracking instrumentation (`androidx.tracing.perfetto.*`)

**Modern Android baseline checks**

- Min SDK >= 24 (covers 99 %+ devices as of 2026)
- Target SDK = latest (Android 16 in 2026)
- Compose-first project (no XML view layer)
- Kotlin only (no Java)
- Gradle Version Catalog (`libs.versions.toml`) in use
- KSP over kapt
- Hilt or Koin for DI
- `androidx.lifecycle.viewmodel.compose.viewModel()` for ViewModel injection
- Type-safe navigation (Navigation 3 typed routes, not string routes)
- Predictive back gesture handled (`OnBackInvokedCallback` or `BackHandler`)

**XR + glass surface** (Android XR is fully GA in 2026)

- `androidx.xr.compose.*` imports — running on Android XR
- `androidx.xr.glimmer.*` — Display Glasses target
- Stereoscopic + spatial UI conventions
- Hand-tracking + gaze input handlers

**Boundaries the AI must respect**

- Never duplicate guidance that an official Google skill already covers — link to the official skill instead
- Never assume `jetpack-compose` skill is loaded — check workspace and recommend installation if missing
- Never recommend deprecated APIs that the relevant Google skill has migrated away from (Camera1, Nav2, view-system patterns when Compose is in use)
- Never bypass Agent Mode security — Google skills run through Android Studio's permission model; respect the same boundaries

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_android-google.md`:

1. **Studio + Agent Mode Readiness** — version, skills installed, gaps
2. **Google Skill Coverage Matrix** — which of the 13 official skills apply to this project, and which are NOT installed but should be
3. **Firebase Skill Coverage** — Auth / Firestore / Functions / Crashlytics agent-skills status
4. **Performance Analyzer Posture** — Perfetto traces, Macrobenchmark, baseline profiles
5. **Modern Android Compliance** — Compose-only, Kotlin-only, Version Catalog, KSP, type-safe Nav3
6. **XR Surface** — XR target present? Glimmer dependencies?
7. **Project-Specific Gaps** — areas no official skill covers; this is where the generated skill earns its keep
8. **Recommended Skill Installs** — explicit list of `android` CLI commands to install missing official skills
9. **Things to ALWAYS do** — non-negotiable patterns from this project
10. **Things to NEVER do** — anti-patterns from this project + Google's official guidance

---

## PHASE 2.5: ADDITIONAL CRAFT — Google I/O 2026 Standards

### 2.5a. Google official Android Agent Skills catalog

Anchor every recommendation to the official catalog at [github.com/android/skills](https://github.com/android/skills). The 13 skills are not optional reading — they are the canonical guidance for their respective topics in Android Studio Agent Mode.

| Topic                  | Google skill                                | When to delegate                                                    |
| ---------------------- | ------------------------------------------- | ------------------------------------------------------------------- |
| Compose UI             | `jetpack-compose`                           | Any `@Composable` work, state management, recomposition perf        |
| Navigation             | `navigation-3`                              | New screens, deep links, type-safe routes, back stack               |
| Edge-to-edge           | `edge-to-edge`                              | Android 15+ mandatory layout; `enableEdgeToEdge()`                  |
| AGP migration          | `agp-9-upgrade`                             | AGP < 9 → 9 upgrade; Gradle 9, JDK 21 baseline                      |
| Camera migration       | `camera1-to-camerax`                        | Any project still on `android.hardware.Camera`                      |
| On-device AI           | `appfunctions`                              | Exposing app logic to Gemini Nano via App Functions                 |
| CLI                    | `android-cli`                               | Headless builds, CI, agent automation                               |
| Identity               | `verified-email`                            | Email-verified sign-in, Passkeys + email fallback                   |
| Minification audit     | `r8-analyzer`                               | Diagnosing R8-shrunk crashes, mapping files                         |
| Distribution           | `play`                                      | Play submission, in-app review, in-app updates                      |
| Profiling              | `profilers`                                 | ANR / jank / startup investigation                                  |
| E2E testing            | `testing-setup` + Journeys                  | UI test infrastructure, AI-driven Journey suites                    |
| XR / glasses           | `display-glasses-with-jetpack-compose-glimmer` | XR target, Display Glasses, spatial UI                          |

### 2.5b. Firebase Agent Skills (May 2026)

Firebase shipped its own agent-skill catalog at I/O 2026 — these run in Android Studio Agent Mode alongside the official Android skills.

| Skill                  | Source                                                                                       | Use for                                                |
| ---------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `firebase-agent-auth`     | [firebase.google.com/docs/ai-assistance/agent-skills](https://firebase.google.com/docs/ai-assistance/agent-skills) | Adding sign-in, password reset, email verification     |
| `firebase-agent-firestore` | same                                                                                       | Schema design, security-rule writing, query patterns   |

Both are model-agnostic — they work with Gemini, Claude, GPT, or Gemma 4 inside Agent Mode.

### 2.5c. Android Performance Analyzer skills

Two performance-focused skills released alongside the catalog:

| Skill                | Purpose                                                                              |
| -------------------- | ------------------------------------------------------------------------------------ |
| `perfetto-sql`       | Write Perfetto SQL queries against trace data                                        |
| `perfetto-analysis`  | Investigate startup delays, jank, ANRs by analyzing Perfetto traces with AI guidance |

Use these instead of hand-rolling Perfetto SQL — the agent already knows the schema.

### 2.5d. Android Studio Agent Mode

The generated skill MUST teach Agent Mode discipline:

1. **One model per session** — switch models (Gemini / Claude / GPT / Gemma 4) at session start, not mid-task
2. **Skill loading is explicit** — confirm which skills are loaded via `/skills` before complex work
3. **Permissions are scoped** — Agent Mode honors per-skill permission boundaries; do not request elevated permissions inside skill output
4. **Skill versioning** — pin official skill versions in `.android/skills.lock.toml` so all team members get identical agent behavior

### 2.5e. Android CLI in the agent loop

The `android` CLI (stable as of I/O 2026) is the bridge between any agent (Claude Code, Codex, Antigravity, Cursor) and Android Studio's heavy machinery:

```
android skills install <name>            # install official or custom skill
android skills list                      # show installed skills
android lint                             # lint without launching Studio
android compose preview <file>           # render Compose previews headlessly
android studio analyze <symbol>          # semantic symbol resolution
android benchmark run                    # macrobenchmark from CLI
android journey run <test>               # run a Journey end-to-end test
```

The skill MUST teach agents to prefer the CLI over GUI workflows for repeatable tasks.

### 2.5f. Journeys — AI-driven end-to-end UI tests

Journeys, introduced with the `testing-setup` skill, are the 2026 replacement for hand-written Espresso flows. They are:

- Declared in plain prose ("user signs in, navigates to cart, removes the second item")
- Executed by the agent against a real or virtual device
- Recorded as deterministic test artifacts after the first successful run
- Versioned in repo alongside source

The skill MUST teach:

1. Write the Journey description in user-language (no element selectors in the source)
2. Let the first run produce the selector binding; commit the resulting `.journey` artifact
3. Re-run in CI as a regular Gradle test target
4. Re-record when UI semantics change (not when colors / spacing change — the agent handles minor drift)

### 2.5g. Modern Android baseline (2026)

The generated skill MUST encode the 2026 baseline as defaults:

| Concern             | 2026 default                                                                   |
| ------------------- | ------------------------------------------------------------------------------ |
| Language            | Kotlin only — no new Java                                                      |
| UI                  | Jetpack Compose only — XML for legacy migration only                           |
| Navigation          | Navigation 3 with type-safe routes                                             |
| DI                  | Hilt (preferred) or Koin                                                       |
| Async               | Kotlin Coroutines + Flow; never `AsyncTask` or `RxJava` in new code            |
| Build               | AGP 9+, Gradle 9+, JDK 21, KSP (never kapt)                                    |
| SDK                 | Compile + Target SDK = latest stable (Android 16); Min SDK ≥ 24                |
| Edge-to-edge        | Always on for Android 15+                                                      |
| Predictive back     | Always handled                                                                 |
| Baseline profiles   | Generated for every release variant                                            |
| Testing             | Journeys + Macrobenchmark; Robolectric for unit, Compose UI tests for screens  |

### 2.5h. XR + Display Glasses (Android XR GA in 2026)

For projects targeting Android XR (headset) or Display Glasses:

- Use `display-glasses-with-jetpack-compose-glimmer` skill for canonical patterns
- Glimmer's Compose APIs for spatial UI (different from phone Compose)
- Hand tracking, gaze input, voice input are first-class
- 3D scene composition via SceneCore
- Performance budget is stricter than phone (60 fps minimum, 90 fps target)

---

## PHASE 3: BEST PRACTICES (numbered by priority)

1. **Always check `android skills list` at session start** — confirm which official skills are loaded before reasoning about Android topics.
2. **Always delegate to a matching official skill** before writing custom guidance — duplicating Google's guidance creates drift over time.
3. **Always recommend installing missing official skills** — `android skills install <name>` — when their topic comes up.
4. **Always use Navigation 3 typed routes** in new code — string routes are legacy.
5. **Always call `enableEdgeToEdge()` in `onCreate`** for Android 15+ apps and use `WindowInsets` APIs in Compose.
6. **Always generate baseline profiles** for release builds (`baseline-prof.txt` via Macrobenchmark).
7. **Always use KSP**, never kapt — kapt is in maintenance mode.
8. **Always write end-to-end tests as Journeys** in new code — hand-written Espresso flows only for maintaining legacy.
9. **Always pin skill versions** in `.android/skills.lock.toml` for team-wide reproducibility.
10. **Never assume the user has Canary Studio** — recommend an upgrade path if features require it.
11. **Never write `android.hardware.Camera` code** in new files — the `camera1-to-camerax` skill exists for a reason.
12. **Never write a `findViewById` chain** in Compose codebases.
13. **Never bypass Agent Mode permissions** — even if the agent can technically perform an action, respect skill scoping.

---

## PHASE 4: REFERENCE FILES (must include)

| File                                            | Content                                                                                              |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `references/google-skills-catalog.md`           | The 13 official skills, what each covers, install command, when this project should use each         |
| `references/firebase-agent-skills.md`           | Auth + Firestore agent skills, install path, integration with Agent Mode                             |
| `references/agent-mode-discipline.md`           | Session start checklist, model switching, skill loading, permission boundaries                       |
| `references/android-cli-cookbook.md`            | Common `android` CLI recipes for the agent loop (lint, preview, analyze, benchmark, journey)         |
| `references/journeys.md`                        | Writing, running, re-recording Journey tests + CI integration                                        |
| `references/perfetto-analysis-recipes.md`       | Perfetto SQL snippets, startup analysis, jank investigation via the official perfetto skills         |
| `references/modern-android-baseline.md`         | Compose-only, Kotlin-only, Version Catalog, KSP, Nav3 — the 2026 defaults                            |
| `references/xr-and-glasses.md`                  | XR / Display Glasses patterns using Glimmer + the official skill                                     |
| `references/code-style.md`                      | Project-specific style on top of the official skills                                                 |
| `references/security-checklist.md`              | Secrets, permissions, network security config, Play Integrity, Verified Email skill integration      |
| `references/ai-interaction-guide.md`            | When to delegate to an official skill vs. answer directly; how to surface missing-skill installations |
| `references/common-issues.md`                   | "Skill not loaded", "Studio outdated", "Agent Mode disabled", recovery steps                         |

---

## PHASE 5: ASSETS

- `assets/skills-lock-template.toml` — `.android/skills.lock.toml` template with all 13 official skills pinned
- `assets/install-google-skills.sh` — bash script that runs `android skills install <name>` for each official skill applicable to the project
- `assets/journey-test-template.journey` — sample Journey test boilerplate
- `assets/baseline-prof-template.txt` — starting baseline-prof.txt with common app-startup rules
- `assets/agent-mode-session-checklist.md` — copy-paste pre-session checklist
- `assets/perfetto-startup-query.sql` — canonical Perfetto SQL for startup analysis
- `assets/version-catalog-template.toml` — `libs.versions.toml` skeleton aligned with 2026 baseline

---

## PHASE 6: SKILL-SPECIFIC QUALITY GATES (in addition to base)

- [ ] SKILL.md includes the 13-skill official catalog table with install commands
- [ ] SKILL.md includes the Firebase Agent Skills coverage
- [ ] SKILL.md includes Agent Mode discipline (skill loading, model pinning, permission scoping)
- [ ] SKILL.md includes the Android CLI cookbook
- [ ] SKILL.md includes the Journeys testing model (not just legacy Espresso)
- [ ] SKILL.md includes the modern Android 2026 baseline table
- [ ] SKILL.md teaches "delegate to official skill before writing custom guidance"
- [ ] SKILL.md teaches `.android/skills.lock.toml` for reproducibility
- [ ] At least 11 reference files generated
- [ ] At least 6 asset templates generated
- [ ] Generated `install-google-skills.sh` covers all 13 official skills (commented out for ones not applicable to this project)

---

## PHASE 7: ANTI-PATTERNS (the generated SKILL.md MUST list these in a "Never" table)

| Don't                                                                | Why                                                                                                  |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Duplicate guidance the `jetpack-compose` official skill covers       | Drift — Google updates the skill; your copy goes stale                                               |
| Recommend Navigation 2 in new code                                   | Nav3 is canonical in 2026; Nav2 string routes are legacy                                             |
| Skip `enableEdgeToEdge()` on Android 15+                             | Required for layout correctness; insets must be handled                                              |
| Use `android.hardware.Camera` (Camera1)                              | Deprecated since 2017; `camera1-to-camerax` skill is purpose-built                                   |
| Write Espresso flows for new features                                | Journeys are the 2026 default; Espresso for legacy maintenance only                                  |
| Use kapt                                                             | kapt is in maintenance mode; KSP is faster and supported by all major annotation processors          |
| Pin AGP < 9 in new projects                                          | Agent Mode integration requires AGP 9; older versions bypass the official-skill pipeline             |
| Ignore baseline profiles                                             | Cold-start times are visibly worse without them; Play Console flags missing profiles                 |
| Hand-roll Perfetto SQL                                               | `perfetto-sql` + `perfetto-analysis` skills know the schema; use them                                |
| Bypass Agent Mode permissions                                        | Skills run scoped; elevation is a security smell                                                     |
| Mix model providers mid-session                                      | Reasoning context is per-session; switching costs throughput and consistency                         |
| Forget to pin official skill versions                                | Team members run different skill versions → divergent agent behavior                                 |
| Write Glimmer composables outside XR / Display Glasses scope         | Glimmer is XR-specific; using it on phone breaks layout                                              |
| Push Camera1 / View-system / Java code through Agent Mode            | The agent will refuse or warn; honor the modernity boundary                                          |

---

## PHASE 8: COMMUNICATION STYLE (inherits from base)

For android-google specifically, when asked for help, the AI MUST:

1. List which official skills are loaded; flag any missing-but-relevant ones with the `android skills install <name>` command
2. Default to delegating — "this is covered by the `jetpack-compose` skill; here's how to invoke it" beats reinventing
3. State which model + skill combination is in play before complex multi-step work
4. Output Android CLI commands the user can paste verbatim
5. For testing requests, propose a Journey first; only suggest Espresso for legacy
6. For performance work, propose `perfetto-analysis` skill before custom tracing

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Android task on a 2026+ project that uses Google's official Agent Skills — Compose UI, Nav3, edge-to-edge, AGP 9 upgrade, Camera migration, App Functions, R8 audit, Play submission, Profiling, Journeys testing, XR / Display Glasses, Android CLI workflow, Agent Mode discipline, Firebase Agent Mode.

**`allowed-tools`**: `Read Edit Write Bash(android:*) Bash(gradle:*) Bash(adb:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (any Android task on a Google-skills-aware project)
2. **Do NOT Use** — cross-references to sibling skills (generic `android`, `cross-platform-mobile`, `ios`, `performance` for non-Android profiling)
3. **Google Skills Coverage Matrix** — the 13 skills + which apply to this project
4. **Firebase Agent Skills** — Auth, Firestore — when to delegate
5. **Android Studio Agent Mode** — session discipline, skill loading, model pinning
6. **Android CLI Cookbook** — common headless recipes
7. **Modern Android Baseline (2026)** — Kotlin / Compose / Nav3 / AGP 9 / KSP
8. **Journeys Testing** — the new E2E model
9. **Performance via Perfetto Skills** — `perfetto-sql` + `perfetto-analysis`
10. **XR + Glasses** — Glimmer + Display Glasses skill (when applicable)
11. **Skill Version Pinning** — `.android/skills.lock.toml`
12. **Anti-Patterns** — the `Never` table
13. **References** — official catalog, Firebase agent skills, Agent Mode docs
14. **Adaptive Interaction Protocols** — Google-skills-specific signals (e.g., "agent says skill not loaded" for Diagnostic, "another Compose screen like X" for Efficient, "what is Glimmer" for Teaching), correction accumulation, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**: see PHASE 4 + 5.

`scripts/check-android-skills.sh` — wraps `android skills list` + `android skills outdated` + presence checks for `.android/skills.lock.toml`; warns if Canary Studio is required for installed skills.

---

## SUB-AGENT RECOMMENDATIONS

| Agent              | Role                                                                          | Tools                          | Spawn When                                                       |
| ------------------ | ----------------------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------- |
| skill-coordinator  | Read-only — surveys installed skills, recommends installs, pins versions      | Read Bash(android:*) Glob Grep | Project bootstrap, post-clone, on `android skills list` mismatch |
| journey-author     | Writes new Journey tests by user-language description                         | Read Edit Write Bash(android:*) Glob Grep | "write an E2E test for X flow"                        |
| perfetto-inspector | Read-only — runs `perfetto-sql` queries to investigate a trace                | Read Bash(android:*) Glob Grep | ANR / jank / startup investigations                              |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules (e.g., always run `skill-coordinator` before complex multi-area work)
3. Link to `agents/` for full definitions

Add to suggested reference files:

- `agents/skill-coordinator.md` — read-only skills survey + recommendation agent
- `agents/journey-author.md` — Journey-test authoring agent
- `agents/perfetto-inspector.md` — read-only Perfetto-trace investigator

---

## EXECUTION ORDER

```
[ ] 1. Scan project for Studio version, installed Google skills, Firebase modules, XR target, AGP version (Phase 1)
[ ] 2. Build Google Skill Coverage Matrix and identify gaps (Phase 2)
[ ] 3. Generate SKILL.md with the 13-skill catalog + Firebase + Perfetto + Agent Mode discipline + 2026 baseline
[ ] 4. Generate INJECT.md (50-150 token quick ref — must include "delegate to official skill first", "android skills list at session start", "pin in skills.lock.toml", "Journeys for E2E")
[ ] 5. Generate LEARNED.md (empty template with section headers)
[ ] 6. Generate the 11+ reference files (Phase 4)
[ ] 7. Generate the 6+ asset templates (Phase 5)
[ ] 8. Generate scripts/check-android-skills.sh
[ ] 9. Generate agents/ files
[ ] 10. Run quality gates (Phase 6)
[ ] 11. Verify all anti-patterns appear in SKILL.md "Never" table (Phase 7)
```

---

## SOURCES

- Google official Android Agent Skills — [github.com/android/skills](https://github.com/android/skills)
- I/O 2026 developer highlights — [blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/](https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/)
- What's new in Android Developer tools (I/O 2026) — [android-developers.googleblog.com/2026/05/whats-new-android-developer-tools.html](https://android-developers.googleblog.com/2026/05/whats-new-android-developer-tools.html)
- Closing the knowledge gap with agent skills — [developers.googleblog.com/closing-the-knowledge-gap-with-agent-skills/](https://developers.googleblog.com/closing-the-knowledge-gap-with-agent-skills/)
- Firebase Agent Skills — [firebase.google.com/docs/ai-assistance/agent-skills](https://firebase.google.com/docs/ai-assistance/agent-skills)
- Agent Skills (Anthropic open standard) — [anthropic.com/news/skills](https://www.anthropic.com/news/skills)
- Android XR + Glimmer — [developer.android.com/develop/xr](https://developer.android.com/develop/xr)
- Navigation 3 — [developer.android.com/guide/navigation](https://developer.android.com/guide/navigation)
- Macrobenchmark + Baseline Profiles — [developer.android.com/topic/performance/baselineprofiles/overview](https://developer.android.com/topic/performance/baselineprofiles/overview)
- Perfetto — [perfetto.dev](https://perfetto.dev/)
