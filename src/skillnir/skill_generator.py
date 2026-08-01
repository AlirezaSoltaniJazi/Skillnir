"""Skill generation with multi-backend support (Claude, Gemini, Copilot)."""

import asyncio
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from skillnir.backends import (
    BACKENDS,
    AIBackend,
    build_claude_sdk_kwargs,
    build_subprocess_command,
    load_config,
    maybe_compress_prompt,
    run_streaming_command,
)
from skillnir.generator import (
    GenerationProgress,
    _emit,
    build_context_pack,
    get_prompts_dir,
)
from skillnir.skill_validator import validate_skill_dir
from skillnir.skills import parse_frontmatter
from skillnir.syncer import get_source_skills_dir


def to_camel_case(name: str) -> str:
    """Convert a name to camelCase for skill directory naming.

    'My Skill' -> 'mySkill'
    'my-skill' -> 'mySkill'
    'my_skill' -> 'mySkill'
    'MySkill'  -> 'mySkill'
    'my skill name' -> 'mySkillName'
    """
    # Split on spaces, hyphens, and underscores
    words = re.split(r"[\s\-_]+", name.strip())
    if not words:
        return name
    # First word lowercase, rest title-cased
    result = words[0].lower() + "".join(w.capitalize() for w in words[1:])
    # Handle PascalCase input: if first char was uppercase but no separators, lowercase first char
    if not result:
        return name
    return result


SKILL_SCOPES: tuple[str, ...] = (
    "backend",
    "frontend",
    "android",
    "ios",
    "infra",
    "testing",
    "js",
    "python",
    "security",
    "test-design",
    "general-system",
    "locator",
    "database",
    "api-design",
    "migration",
    "data-science",
    "go",
    "performance",
    "cross-platform-mobile",
    "observability",
    "accessibility",
    "chrome-extension",
    "playwright",
    "wdio",
    "selenium",
    "appium",
    "manual-tester",
    "project-manager",
    "devops-engineer",
    "ui-ux-designer",
    "financial-manager",
    "hr-manager",
    "django",
    "deep-researcher",
    "translator",
    "android-google",
    "automation-review",
)

SCOPE_LABELS: dict[str, str] = {
    "backend": "Backend (Python/Django/Go/Java/etc.)",
    "frontend": "Frontend (React/Vue/Angular/Svelte/etc.)",
    "android": "Android (Kotlin/Java)",
    "ios": "iOS (Swift/Obj-C)",
    "infra": "Infrastructure (Docker/CI/Terraform/K8s)",
    "testing": "Test Automation (E2E/API/Integration/Playwright/WDIO/etc.)",
    "js": "JavaScript/TypeScript (Node.js/React/Vue/Express/Next.js/etc.)",
    "python": "Python (FastAPI/Flask/scripts/data/CLI/etc.)",
    "security": "Security (OWASP/SAST/DAST/dependency audit across all platforms)",
    "test-design": "Test Case Design (test strategy, coverage, scenarios, edge cases)",
    "general-system": "General System (cross-cutting skill rules, LEARNED.md conventions, skill file management)",
    "locator": "Locator Extraction (element selectors, page objects, Playwright/Cypress/WDIO/Selenium/Robot)",
    "database": "Database (schema design/migrations/query optimization/ORM patterns/data modeling)",
    "api-design": "API Design (OpenAPI/Protobuf/GraphQL schemas/versioning/contract testing)",
    "migration": "Migration & Refactoring (framework upgrades/language migrations/architecture refactors)",
    "data-science": "Data Science & ML (notebooks/pandas/ML pipelines/experiment tracking/model serving)",
    "go": "Go (idioms/goroutines/channels/modules/table-driven tests/pprof)",
    "performance": "Performance (profiling/load testing/bundle analysis/caching/query optimization)",
    "cross-platform-mobile": "Cross-Platform Mobile (React Native/Flutter/KMP/native bridges)",
    "observability": "Observability (OpenTelemetry/tracing/metrics/logging/SLOs/alerting)",
    "accessibility": "Accessibility (WCAG/ARIA/screen readers/keyboard navigation/color contrast)",
    "chrome-extension": "Chrome Extension (Manifest V3/content scripts/service workers/chrome.* APIs)",
    "playwright": "Playwright (fixtures/POM/visual regression/API testing/tracing/sharding)",
    "wdio": "WebDriverIO (wdio.conf/custom commands/services/BiDi/reporters/visual testing)",
    "selenium": "Selenium (Selenium 4+/Grid/multi-language/PageFactory/Actions API/waits)",
    "appium": "Appium (Appium 2.0/XCUITest/UiAutomator2/gestures/hybrid apps/cloud testing)",
    "manual-tester": "Manual Tester (ISTQB/test cases/boundary values/equivalence/exploratory/test plans)",
    "project-manager": "Project Manager (PMBOK 7/PRINCE2 7/Scrum/Kanban/charters/RACI/risk register/OKRs/retros)",
    "devops-engineer": "DevOps Engineer (CI/CD, GitOps, IaC/Terraform, Kubernetes, SRE/DORA, on-call/incident response)",
    "ui-ux-designer": "UI/UX Designer (design systems, Figma, NN/g, Material 3/HIG, WCAG 2.2, user research, usability testing)",
    "financial-manager": "Financial Manager (budgets, P&L, FP&A, cash flow, runway, IFRS/GAAP, financial models, unit economics)",
    "hr-manager": "HR Manager (hiring loops, JDs, interview rubrics, performance reviews, leveling, comp bands, employment law)",
    "django": "Django (models/ORM/DRF/migrations/Celery/Channels/admin/security)",
    "deep-researcher": "Deep Researcher (methodology/source evaluation/synthesis/citations/fact-checking)",
    "translator": "Translator (i18n/l10n/ICU plurals/RTL/terminology management/CAT tools)",
    "android-google": "Android (Google Official Skills — Compose/Nav3/edge-to-edge/AGP9/Camera/Journeys/Glimmer XR)",
    "automation-review": "Automation Review (code review / test-plan & test-case review across languages & frameworks, self-extending, HTML report)",
}


# Category groupings for the scope picker — keeps the catalog scannable.
# Order here is the order categories appear in the dropdown / CLI menu.
SCOPE_CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Engineering Roles",
        (
            "backend",
            "frontend",
            "js",
            "python",
            "django",
            "go",
            "android",
            "android-google",
            "ios",
            "cross-platform-mobile",
            "chrome-extension",
            "data-science",
        ),
    ),
    (
        "Quality & Testing",
        (
            "testing",
            "test-design",
            "manual-tester",
            "locator",
            "playwright",
            "wdio",
            "selenium",
            "appium",
            "accessibility",
            "automation-review",
        ),
    ),
    (
        "Architecture & Platform",
        (
            "infra",
            "devops-engineer",
            "database",
            "api-design",
            "migration",
            "performance",
            "observability",
            "security",
            "general-system",
        ),
    ),
    ("Design", ("ui-ux-designer",)),
    (
        "Business & People",
        (
            "project-manager",
            "financial-manager",
            "hr-manager",
            "deep-researcher",
            "translator",
        ),
    ),
)


@dataclass
class SkillGenerationResult:
    success: bool
    skill_name: str
    target_skill_path: Path | None = None
    source_skill_path: Path | None = None
    error: str | None = None
    backend_used: AIBackend | None = None
    # Contract-gate failures (SKILL.md exists but violates the base-template
    # contract) — distinguishes repairable output from infrastructure errors.
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def load_skill_prompt(scope: str, version: str = "") -> str:
    """Load a scope-specific prompt, prepending the shared base instructions."""
    if scope not in SKILL_SCOPES:
        raise ValueError(f"Invalid scope '{scope}'. Must be one of: {SKILL_SCOPES}")
    prompts_dir = get_prompts_dir(version)
    prompt_file = prompts_dir / f"generate-skill-{scope}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}\n"
            f"Expected at {prompts_dir}/generate-skill-{scope}.md"
        )
    prompt_text = prompt_file.read_text(encoding="utf-8")

    # Every scope template opens with "Read _base-skill-generator.md first
    # for shared structure, quality gates, and execution order." The generator
    # runs with cwd=<target project>, so the AI can't open that file itself —
    # we must inline it. Prepend it whenever present, for ALL prompt versions
    # (the default version is v1, which previously skipped this).
    base_file = prompts_dir / "_base-skill-generator.md"
    if base_file.exists():
        base_text = base_file.read_text(encoding="utf-8")
        prompt_text = base_text + "\n\n---\n\n" + prompt_text

    return prompt_text


def _name_tokens(name: str) -> set[str]:
    """Split a camelCase/kebab/snake name into lowercase word tokens."""
    tokens: set[str] = set()
    for part in re.split(r"[\s\-_.]+", name):
        for word in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", part):
            tokens.add(word.lower())
    return tokens


def _find_reference_skill(scope: str) -> tuple[Path | None, bool]:
    """Find an existing skill to use as format reference for the AI.

    Returns ``(path, same_scope)``. Keywords match whole tokens of the
    skill directory name and its frontmatter description — substring
    matching made scope 'go' pick any 'django*' skill. When nothing
    matches, falls back to the first skill of ANY scope with
    ``same_scope=False`` so the prompt can mark it structure-only.
    """
    source_dir = get_source_skills_dir()
    if not source_dir.is_dir():
        return None, False

    scope_keywords = {
        "backend": ("server", "backend", "django", "api"),
        "frontend": ("web", "frontend", "react", "angular", "vue"),
        "android": ("android",),
        "ios": ("ios",),
        "infra": ("infra", "devops", "deploy"),
        "testing": ("test", "e2e", "wdio", "playwright", "cypress", "selenium", "spec"),
        "js": (
            "javascript",
            "typescript",
            "node",
            "npm",
            "react",
            "vue",
            "next",
            "express",
        ),
        "python": ("python", "fastapi", "flask", "pip", "poetry", "script"),
        "security": ("security", "auth", "owasp", "vulnerability", "pentest", "audit"),
        "test-design": (
            "test-case",
            "test-design",
            "test-plan",
            "test-strategy",
            "scenario",
        ),
        "general-system": (
            "general",
            "system",
            "meta",
            "skill-system",
            "cross-cutting",
        ),
        "locator": (
            "locator",
            "selector",
            "page-object",
            "element",
            "wdio",
            "playwright",
            "cypress",
            "selenium",
        ),
        "database": ("database", "schema", "migration", "sql", "orm", "query"),
        "api-design": ("api", "openapi", "swagger", "protobuf", "graphql", "contract"),
        "migration": ("migration", "upgrade", "refactor", "compat"),
        "data-science": ("data", "ml", "notebook", "jupyter", "pandas", "model"),
        "go": ("go", "golang", "goroutine"),
        "performance": ("performance", "profiling", "benchmark", "load-test"),
        "cross-platform-mobile": ("react-native", "flutter", "kmp", "expo"),
        "observability": (
            "observability",
            "tracing",
            "metrics",
            "opentelemetry",
            "slo",
        ),
        "accessibility": ("accessibility", "a11y", "wcag", "aria", "screen-reader"),
        "chrome-extension": (
            "chrome",
            "extension",
            "manifest",
            "content-script",
            "service-worker",
            "popup",
        ),
        "playwright": ("playwright", "pw", "fixture", "visual-regression", "trace"),
        "wdio": ("wdio", "webdriverio", "webdriver-io"),
        "selenium": ("selenium", "webdriver", "grid", "pagefactory"),
        "appium": ("appium", "mobile-test", "xcuitest", "uiautomator", "espresso"),
        "devops-engineer": (
            "devops",
            "infra",
            "ci",
            "cd",
            "gitops",
            "terraform",
            "kubernetes",
            "k8s",
            "sre",
        ),
        "ui-ux-designer": (
            "ui",
            "ux",
            "design",
            "figma",
            "wireframe",
            "design-system",
            "designer",
        ),
        "financial-manager": (
            "finance",
            "financial",
            "budget",
            "accounting",
            "fpa",
            "treasury",
        ),
        "hr-manager": (
            "hr",
            "people",
            "recruiting",
            "hiring",
            "talent",
            "human-resources",
        ),
        "django": (
            "django",
            "drf",
            "django-rest-framework",
            "manage.py",
            "settings.py",
            "models.py",
            "views.py",
            "asgi",
            "wsgi",
            "celery",
            "channels",
        ),
        "deep-researcher": (
            "research",
            "researcher",
            "methodology",
            "citation",
            "source",
            "synthesis",
            "literature-review",
            "intel",
            "brief",
        ),
        "translator": (
            "translator",
            "translation",
            "i18n",
            "l10n",
            "locale",
            "localization",
            "gettext",
            "xliff",
            "icu",
            "crowdin",
            "lokalise",
            "phrase",
        ),
        "android-google": (
            "android",
            "jetpack-compose",
            "compose",
            "navigation3",
            "edge-to-edge",
            "agp",
            "camerax",
            "appfunctions",
            "glimmer",
            "perfetto",
            "journeys",
            "agent-mode",
            "android-skills",
        ),
        "automation-review": (
            "review",
            "audit",
            "code-review",
            "test-review",
            "quality-gate",
            "lint",
            "flaky",
            "test-automation",
            "qa",
        ),
    }

    keywords = scope_keywords.get(scope, ())
    candidates = [
        entry
        for entry in sorted(source_dir.iterdir())
        if entry.is_dir() and (entry / "SKILL.md").exists()
    ]

    for entry in candidates:
        tokens = _name_tokens(entry.name)
        try:
            description = str(
                parse_frontmatter(entry / "SKILL.md").get("description", "")
            )
        except Exception:
            description = ""
        tokens |= _name_tokens(description)
        for kw in keywords:
            if _name_tokens(kw) <= tokens:
                return entry, True

    # Fallback: the first skill of any scope — usable for structure only.
    if candidates:
        return candidates[0], False

    return None, False


def _learned_feedback_section(output_dir: Path) -> str:
    """Inline an existing LEARNED.md so regeneration keeps its corrections."""
    learned_file = output_dir / "LEARNED.md"
    if not learned_file.is_file():
        return ""
    try:
        learned_text = learned_file.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return ""
    if not any(line.lstrip().startswith("- ") for line in learned_text.splitlines()):
        return ""
    return (
        "\n\nEXISTING LEARNED.md — corrections and preferences accumulated in "
        "prior sessions. These rules OVERRIDE any conflicting defaults: bake "
        "every entry into the regenerated skill content. Do NOT overwrite, "
        "truncate, or regenerate LEARNED.md itself.\n\n" + learned_text[:4000]
    )


def _build_user_prompt(
    target_project: Path,
    project_name: str,
    scope: str,
    pure: bool = False,
    extra_instructions: str = "",
) -> str:
    """Construct the runtime user prompt with project-specific details.

    When ``pure`` is True, the prompt instructs the AI to skip the
    project-scan phases and produce a generic, reusable skill grounded
    only in the system prompt's best-practice patterns. The output
    directory still lives under ``target_project/.data/skills/`` so the
    user can install the skill into a real project, but the skill body
    references no project-specific paths.

    ``extra_instructions`` is appended verbatim — used by the validation
    repair pass to feed concrete contract violations back to the AI.
    """
    skill_name = to_camel_case(project_name)
    output_dir = target_project / ".data" / "skills" / skill_name
    output_file = output_dir / "SKILL.md"

    ref_skill, same_scope = _find_reference_skill(scope)
    ref_section = ""
    if ref_skill:
        ref_section = (
            f"\n\nReference skill for format guidance: {ref_skill}\n"
            f"Read {ref_skill / 'SKILL.md'} before generating to match the style."
        )
        if not same_scope:
            ref_section += (
                "\nNOTE: this reference is from a DIFFERENT domain — copy its "
                "structure and formatting only, never its content or terminology."
            )

    learned_section = _learned_feedback_section(output_dir)
    tail = f"{ref_section}{learned_section}"
    if extra_instructions:
        tail += f"\n\n{extra_instructions}"

    if pure:
        return (
            f"PURE MODE — generate a generic, reusable {scope} skill.\n\n"
            "Do NOT scan or read the target project. Skip every project-scan / "
            "synthesis phase in the system prompt. Generate the skill grounded "
            "ONLY in the system prompt's best-practice patterns and templates.\n\n"
            "Use these placeholders where project specifics would normally go:\n"
            "- File paths: write `path/to/your/file.ext` (never invent real paths)\n"
            "- Project name: write `YOUR_PROJECT`\n"
            "- Stack / framework: list common options for the scope, not a specific choice\n"
            "- Examples: synthetic / canonical (not derived from any real codebase)\n\n"
            f"The skill name is \"{skill_name}\".\n"
            f"Use \"{skill_name}\" as the 'name' field in YAML frontmatter.\n"
            f"Create the output directory if needed: mkdir -p {output_dir}\n"
            f"Write the final SKILL.md to: {output_file}"
            f"{tail}"
        )

    prompt = (
        f"Generate a {scope} skill for the project at {target_project}.\n"
        f"The project name is \"{project_name}\".\n"
        f"The skill name is \"{skill_name}\".\n"
        f"Use \"{skill_name}\" as the 'name' field in YAML frontmatter.\n"
        f"\nFollow all phases in the system prompt.\n"
        f"Create the output directory if needed: mkdir -p {output_dir}\n"
        f"Write the final SKILL.md to: {output_file}"
        f"{tail}"
    )
    pack = build_context_pack(target_project)
    if pack:
        prompt += "\n\n" + pack
    return prompt


async def generate_skill_sdk(
    target_project: Path,
    project_name: str,
    scope: str,
    prompt_text: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    pure: bool = False,
    extra_instructions: str = "",
) -> SkillGenerationResult:
    """Generate skill using claude-agent-sdk (async, streaming). Claude only."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        query,
    )

    from skillnir.usage import session_tracker

    skill_name = to_camel_case(project_name)
    _emit(on_progress, "phase", "Connecting to Claude SDK...")

    options = ClaudeAgentOptions(
        system_prompt=maybe_compress_prompt(prompt_text),
        max_turns=20,
        allowed_tools=["Read", "Glob", "Grep", "Bash", "Edit", "Write"],
        permission_mode="acceptEdits",
        cwd=str(target_project),
        **build_claude_sdk_kwargs(),
    )

    user_prompt = _build_user_prompt(
        target_project,
        project_name,
        scope,
        pure=pure,
        extra_instructions=extra_instructions,
    )

    try:
        async for message in query(prompt=user_prompt, options=options):
            if isinstance(message, AssistantMessage) and on_progress:
                for block in message.content:
                    if isinstance(block, TextBlock):
                        _emit(on_progress, "text", block.text)
                    elif isinstance(block, ToolUseBlock):
                        _emit(
                            on_progress,
                            "tool_use",
                            f"Using {block.name}...",
                            tool_name=block.name,
                        )
            elif isinstance(message, ResultMessage):
                if message.usage:
                    session_tracker.record(
                        'claude',
                        message.usage,
                        getattr(message, 'total_cost_usd', None),
                    )
    except Exception as e:
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            error=str(e),
            backend_used=AIBackend.CLAUDE,
        )

    return _check_skill_outputs(target_project, skill_name, AIBackend.CLAUDE)


def generate_skill_subprocess(
    target_project: Path,
    project_name: str,
    scope: str,
    prompt_text: str,
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    pure: bool = False,
    extra_instructions: str = "",
) -> SkillGenerationResult:
    """Generate skill using any backend CLI subprocess with real-time streaming."""
    skill_name = to_camel_case(project_name)
    info = BACKENDS[backend]
    _emit(on_progress, "phase", f"Starting {info.name}...")

    user_prompt = _build_user_prompt(
        target_project,
        project_name,
        scope,
        pure=pure,
        extra_instructions=extra_instructions,
    )
    full_prompt = prompt_text + "\n\n---\n\n" + user_prompt
    cmd = build_subprocess_command(backend, full_prompt, model=model, max_turns=20)

    phase_label = (
        f"Generating generic ({scope}) skill..."
        if pure
        else f"Scanning project ({scope})..."
    )
    _emit(on_progress, "phase", phase_label)

    try:
        run = run_streaming_command(
            cmd, backend, target_project, on_progress, timeout=600
        )
    except FileNotFoundError:
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            error=f"{info.cli_command} CLI not found in PATH.",
            backend_used=backend,
        )

    if run.timed_out:
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            error=f"{info.name} timed out after 10 minutes.",
            backend_used=backend,
        )
    if run.returncode != 0:
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            error=f"{info.name} exited with code {run.returncode}: {run.stderr}",
            backend_used=backend,
        )

    _emit(on_progress, "phase", "Verifying outputs...")
    return _check_skill_outputs(target_project, skill_name, backend)


def _check_skill_outputs(
    target_project: Path,
    skill_name: str,
    backend: AIBackend,
) -> SkillGenerationResult:
    """Validate the generated skill against the base-template contract."""
    skill_dir = target_project / ".data" / "skills" / skill_name
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            error=(
                f"SKILL.md was not created at {skill_md}. "
                "The AI may need more turns or the project may be too complex."
            ),
            backend_used=backend,
        )

    report = validate_skill_dir(skill_dir, expected_name=skill_name)
    if not report.ok:
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            target_skill_path=skill_md,
            source_skill_path=skill_md,
            error="Generated skill violates the contract:\n" + report.summary(),
            backend_used=backend,
            violations=report.violations,
            warnings=report.warnings,
        )

    return SkillGenerationResult(
        success=True,
        skill_name=skill_name,
        target_skill_path=skill_md,
        source_skill_path=skill_md,
        backend_used=backend,
        warnings=report.warnings,
    )


def _claude_sdk_available() -> bool:
    """Check if claude-agent-sdk is importable."""
    try:
        import claude_agent_sdk  # noqa: F401

        return True
    except ImportError:
        return False


async def generate_skill(
    target_project: Path,
    project_name: str,
    scope: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    prompt_version_override: str | None = None,
    pure: bool = False,
) -> SkillGenerationResult:
    """Main entry point: load prompt, use configured backend, generate skill.

    When ``pure`` is True the AI is told to skip the project scan and
    produce a generic, reusable skill grounded only in the system prompt.
    """
    skill_name = to_camel_case(project_name)
    _emit(on_progress, "phase", "Loading skill prompt...")

    config = load_config()
    version = prompt_version_override or config.prompt_version

    try:
        prompt_text = load_skill_prompt(scope, version)
    except (FileNotFoundError, ValueError) as e:
        return SkillGenerationResult(success=False, skill_name=skill_name, error=str(e))
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    _emit(on_progress, "phase", f"Using {info.name}...")

    # Check CLI availability
    cli_available = bool(shutil.which(info.cli_command))

    use_sdk = backend == AIBackend.CLAUDE and _claude_sdk_available()
    if not use_sdk and not cli_available:
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            error=f"{info.name} CLI ({info.cli_command}) not found in PATH.",
            backend_used=backend,
        )

    async def _run(extra_instructions: str = "") -> SkillGenerationResult:
        if use_sdk:
            _emit(on_progress, "status", "Using Claude SDK")
            return await generate_skill_sdk(
                target_project,
                project_name,
                scope,
                prompt_text,
                on_progress,
                pure=pure,
                extra_instructions=extra_instructions,
            )
        _emit(on_progress, "status", f"Using {info.name} ({model})")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            generate_skill_subprocess,
            target_project,
            project_name,
            scope,
            prompt_text,
            backend,
            model,
            on_progress,
            pure,
            extra_instructions,
        )

    result = await _run()

    # One bounded repair pass: the skill exists but violates contract gates,
    # so re-invoke with the concrete violations instead of failing outright.
    if not result.success and result.violations:
        _emit(
            on_progress,
            "phase",
            "Repairing contract violations: " + "; ".join(result.violations),
        )
        repair_instructions = (
            "REPAIR PASS — a previous run already generated this skill at "
            f"{target_project / '.data' / 'skills' / skill_name}, but it "
            "violates these contract gates:\n"
            + "\n".join(f"- {v}" for v in result.violations)
            + "\nFix ONLY these violations by editing the existing files in "
            "place. Do not regenerate unaffected files from scratch."
        )
        result = await _run(extra_instructions=repair_instructions)

    return result
