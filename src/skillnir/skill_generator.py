"""Skill generation with multi-backend support (Claude, Gemini, Copilot)."""

import asyncio
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from skillnir.backends import (
    BACKENDS,
    AIBackend,
    build_claude_sdk_kwargs,
    build_subprocess_command,
    load_config,
    parse_stream_line,
)
from skillnir.generator import GenerationProgress, _emit, get_prompts_dir
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
}


@dataclass
class SkillGenerationResult:
    success: bool
    skill_name: str
    target_skill_path: Path | None = None
    source_skill_path: Path | None = None
    error: str | None = None
    backend_used: AIBackend | None = None


def load_skill_prompt(scope: str, version: str = "") -> str:
    """Load a scope-specific prompt, prepending the shared base for v2."""
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

    if version != "v1":
        base_file = prompts_dir / "_base-skill-generator.md"
        if base_file.exists():
            base_text = base_file.read_text(encoding="utf-8")
            prompt_text = base_text + "\n\n---\n\n" + prompt_text

    return prompt_text


def _find_reference_skill(scope: str) -> Path | None:
    """Find an existing skill to use as format reference for the AI."""
    source_dir = get_source_skills_dir()
    if not source_dir.is_dir():
        return None

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
    }

    keywords = scope_keywords.get(scope, ())
    for entry in sorted(source_dir.iterdir()):
        if entry.is_dir() and (entry / "SKILL.md").exists():
            name_lower = entry.name.lower()
            if any(kw in name_lower for kw in keywords):
                return entry

    # Fallback: return the first skill found (any scope is better than none)
    for entry in sorted(source_dir.iterdir()):
        if entry.is_dir() and (entry / "SKILL.md").exists():
            return entry

    return None


def _build_user_prompt(
    target_project: Path,
    project_name: str,
    scope: str,
    pure: bool = False,
) -> str:
    """Construct the runtime user prompt with project-specific details.

    When ``pure`` is True, the prompt instructs the AI to skip the
    project-scan phases and produce a generic, reusable skill grounded
    only in the system prompt's best-practice patterns. The output
    directory still lives under ``target_project/.data/skills/`` so the
    user can install the skill into a real project, but the skill body
    references no project-specific paths.
    """
    skill_name = to_camel_case(project_name)
    output_dir = target_project / ".data" / "skills" / skill_name
    output_file = output_dir / "SKILL.md"

    ref_skill = _find_reference_skill(scope)
    ref_section = ""
    if ref_skill:
        ref_section = (
            f"\n\nReference skill for format guidance: {ref_skill}\n"
            f"Read {ref_skill / 'SKILL.md'} before generating to match the style."
        )

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
            f"{ref_section}"
        )

    return (
        f"Generate a {scope} skill for the project at {target_project}.\n"
        f"The project name is \"{project_name}\".\n"
        f"The skill name is \"{skill_name}\".\n"
        f"Use \"{skill_name}\" as the 'name' field in YAML frontmatter.\n"
        f"\nFollow all phases in the system prompt.\n"
        f"Create the output directory if needed: mkdir -p {output_dir}\n"
        f"Write the final SKILL.md to: {output_file}"
        f"{ref_section}"
    )


async def generate_skill_sdk(
    target_project: Path,
    project_name: str,
    scope: str,
    prompt_text: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    pure: bool = False,
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
        system_prompt=prompt_text,
        max_turns=20,
        allowed_tools=["Read", "Glob", "Grep", "Bash", "Write"],
        permission_mode="acceptEdits",
        cwd=str(target_project),
        **build_claude_sdk_kwargs(),
    )

    user_prompt = _build_user_prompt(target_project, project_name, scope, pure=pure)

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
) -> SkillGenerationResult:
    """Generate skill using any backend CLI subprocess with real-time streaming."""
    skill_name = to_camel_case(project_name)
    info = BACKENDS[backend]
    _emit(on_progress, "phase", f"Starting {info.name}...")

    user_prompt = _build_user_prompt(target_project, project_name, scope, pure=pure)
    full_prompt = prompt_text + "\n\n---\n\n" + user_prompt
    cmd = build_subprocess_command(backend, full_prompt, model=model, max_turns=20)

    try:
        phase_label = (
            f"Generating generic ({scope}) skill..."
            if pure
            else f"Scanning project ({scope})..."
        )
        _emit(on_progress, "phase", phase_label)

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_project),
        )

        import threading

        stderr_chunks: list[str] = []

        def _drain_stderr() -> None:
            for err_line in proc.stderr:
                stderr_chunks.append(err_line)

        stderr_thread = threading.Thread(target=_drain_stderr, daemon=True)
        stderr_thread.start()

        for line in proc.stdout:
            parse_stream_line(backend, line, on_progress)

        proc.wait(timeout=600)
        stderr_thread.join(timeout=5)
        stderr = ''.join(stderr_chunks)

        if proc.returncode != 0:
            return SkillGenerationResult(
                success=False,
                skill_name=skill_name,
                error=f"{info.name} exited with code {proc.returncode}: {stderr}",
                backend_used=backend,
            )

    except subprocess.TimeoutExpired:
        proc.kill()
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            error=f"{info.name} timed out after 10 minutes.",
            backend_used=backend,
        )
    except FileNotFoundError:
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            error=f"{info.cli_command} CLI not found in PATH.",
            backend_used=backend,
        )

    _emit(on_progress, "phase", "Verifying outputs...")
    return _check_skill_outputs(target_project, skill_name, backend)


def _check_skill_outputs(
    target_project: Path,
    skill_name: str,
    backend: AIBackend,
) -> SkillGenerationResult:
    """Verify that SKILL.md was created and has valid frontmatter."""
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

    # Validate frontmatter
    try:
        meta = parse_frontmatter(skill_md)
        if not meta.get("name"):
            return SkillGenerationResult(
                success=False,
                skill_name=skill_name,
                error="SKILL.md was created but has no 'name' in frontmatter.",
                backend_used=backend,
            )
    except Exception:
        pass  # Don't fail on frontmatter issues — the file exists

    return SkillGenerationResult(
        success=True,
        skill_name=skill_name,
        target_skill_path=skill_md,
        source_skill_path=skill_md,
        backend_used=backend,
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

    # For Claude, try SDK first if available
    if backend == AIBackend.CLAUDE and _claude_sdk_available():
        _emit(on_progress, "status", "Using Claude SDK")
        return await generate_skill_sdk(
            target_project,
            project_name,
            scope,
            prompt_text,
            on_progress,
            pure=pure,
        )

    if not cli_available:
        return SkillGenerationResult(
            success=False,
            skill_name=skill_name,
            error=f"{info.name} CLI ({info.cli_command}) not found in PATH.",
            backend_used=backend,
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
    )
