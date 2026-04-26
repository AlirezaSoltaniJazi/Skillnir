"""Interactive CLI for injecting skills into AI tool directories."""

import argparse
import sys
from pathlib import Path

import questionary

from skillnir.injector import inject_skill
from skillnir.remover import (
    delete_docs,
    delete_skill,
    delete_wiki,
    find_docs_installations,
    find_skill_installations,
    find_wiki_installations,
)
from skillnir.scaffold import init_docs, init_skill, validate_skill_name
from skillnir.skills import discover_skills, discover_skills_from_dir
from skillnir.syncer import (
    SyncResult,
    get_source_skills_dir,
    sync_skill,
    sync_skills,
)
from skillnir.tools import AITool, AUTO_INJECT_TOOL, TOOLS, detect_tools

# Sort mode menu options
SORT_MODES = {
    "Default (recommended)": "default",
    "Alphabetical (A-Z)": "alpha",
    "Alphabetical (Z-A)": "alpha-desc",
}


def _ask_target_project() -> Path:
    """Ask user for target project root, default cwd."""
    answer = questionary.text(
        "Target project root:",
        default=str(Path.cwd()),
    ).ask()
    if answer is None:
        sys.exit(0)
    target = Path(answer).resolve()
    if not target.is_dir():
        print(f"Directory not found: {target}")
        sys.exit(1)
    return target


def _print_sync_report(results: list[SyncResult]) -> None:
    """Print skill sync report."""
    if not results:
        print("\n  No skills found in source.")
        return

    print(f"\n{'─' * 50}")
    print("  Skill Sync Report")
    print(f"{'─' * 50}\n")

    for r in results:
        if r.action == "copied":
            print(f"    + {r.skill_name} (v{r.source_version}) — copied")
        elif r.action == "updated":
            print(
                f"    ~ {r.skill_name} (v{r.target_version} -> v{r.source_version}) — updated"
            )
        elif r.action == "skipped":
            print(
                f"    = {r.skill_name} (v{r.source_version}) — skipped (same version)"
            )

    copied = sum(1 for r in results if r.action == "copied")
    updated = sum(1 for r in results if r.action == "updated")
    skipped = sum(1 for r in results if r.action == "skipped")
    print(f"\n  {copied} copied, {updated} updated, {skipped} skipped.\n")


def _sort_tools(tools: tuple[AITool, ...], mode: str) -> list[AITool]:
    """Sort tools by the given mode."""
    if mode == "popularity":
        return sorted(tools, key=lambda t: (-t.popularity, t.name))
    if mode == "performance":
        return sorted(tools, key=lambda t: (-t.performance, t.name))
    if mode == "price":
        return sorted(tools, key=lambda t: (-t.price, t.name))
    if mode == "alpha":
        return sorted(tools, key=lambda t: t.name.lower())
    return list(tools)  # default: preserve original order


def _format_tool_choice(tool: AITool, mode: str) -> str:
    """Format a tool choice label, showing the relevant score when sorted."""
    base = f"{tool.name} ({tool.dotdir}/)"
    if mode == "popularity":
        return f"{base}  [{tool.popularity}/10]"
    if mode == "performance":
        return f"{base}  [{tool.performance}/10]"
    if mode == "price":
        return f"{base}  [{tool.price}/10]"
    return base


def _install() -> None:
    """Full install flow: sync skills + select tools + create symlinks."""
    # Step 0: Target project
    target_root = _ask_target_project()

    # Step 0b: Source skills path
    default_source = str(get_source_skills_dir())
    source_answer = questionary.text(
        "Source skills path:",
        default=default_source,
    ).ask()
    if source_answer is None:
        sys.exit(0)
    source_dir = Path(source_answer).resolve()
    if not source_dir.is_dir():
        print(f"Source directory not found: {source_dir}")
        sys.exit(1)

    # Step 1: Discover skills from source
    skills = discover_skills_from_dir(source_dir)
    if not skills:
        print("No skills found in source. Nothing to inject.")
        sys.exit(1)

    # Step 2: Skill Selection (from source) — multi-select
    if len(skills) == 1:
        selected_skills = skills
        print(f"Found 1 skill: {skills[0].name} (v{skills[0].version})")
        print(f"  {skills[0].description}\n")
    else:
        skill_map = {
            f"{s.name} (v{s.version}) — {s.description[:60]}": s for s in skills
        }
        answers = questionary.checkbox(
            "Select skills to inject (space=toggle, enter=confirm):",
            choices=list(skill_map.keys()),
        ).ask()
        if not answers:
            print("No skills selected. Aborting.")
            sys.exit(0)
        selected_skills = [skill_map[a] for a in answers]

    # Step 3: Sync selected skills to target
    target_skills_dir = target_root / ".data" / "skills"
    sync_results = [
        sync_skill(source_dir, target_skills_dir, s.dir_name) for s in selected_skills
    ]
    _print_sync_report(sync_results)

    # Step 4: Sort Mode
    sort_answer = questionary.select(
        "How should tools be sorted?",
        choices=list(SORT_MODES.keys()),
    ).ask()
    if sort_answer is None:
        sys.exit(0)
    sort_mode = SORT_MODES[sort_answer]
    sorted_tools = _sort_tools(TOOLS, sort_mode)

    # Step 5: Tool/IDE Multi-Select
    detected = detect_tools(target_root)
    detected_names = {t.name for t in detected}
    if detected:
        print(f"\n  Auto-detected {len(detected)} tools in {target_root.name}/")

    tool_choices = [
        questionary.Choice(
            title=_format_tool_choice(tool, sort_mode),
            value=tool,
            checked=tool.name in detected_names,
        )
        for tool in sorted_tools
    ]
    answers = questionary.checkbox(
        "Select AI tools to inject into (space=toggle, enter=confirm):",
        choices=tool_choices,
    ).ask()
    if not answers:
        print("No tools selected. Aborting.")
        sys.exit(0)
    selected_tools = answers

    # Step 6: Confirmation Summary
    skill_names = ", ".join(s.name for s in selected_skills)
    print(f"\n  Target: {target_root}")
    print(f"  Skills: {skill_names}")
    print(f"  Tools:  {len(selected_tools)} selected + .agents/ (auto)\n")
    for skill in selected_skills:
        print(
            f"    * {AUTO_INJECT_TOOL.name} ({AUTO_INJECT_TOOL.dotdir}/{AUTO_INJECT_TOOL.skills_subpath}/{skill.dir_name}) [auto]"
        )
        for t in selected_tools:
            print(f"    - {t.name} ({t.dotdir}/{t.skills_subpath}/{skill.dir_name})")
    print()

    if not questionary.confirm("Proceed with injection?", default=True).ask():
        print("Aborted.")
        sys.exit(0)

    # Step 7: Execute — inject each skill into auto + user-selected tools
    all_tools = [AUTO_INJECT_TOOL] + selected_tools
    total_created = 0
    total_skipped = 0
    total_errors = 0

    for skill in selected_skills:
        results = inject_skill(target_root, skill, all_tools)

        created = [r for r in results if r.created]
        skipped = [r for r in results if not r.created and not r.error]
        errors = [r for r in results if r.error]
        total_created += len(created)
        total_skipped += len(skipped)
        total_errors += len(errors)

        # Step 8: Injection Report (per skill)
        print(f"\n{'=' * 50}")
        print(f"  Injection Report: {skill.name}")
        print(f"{'=' * 50}\n")

        if created:
            print(f"  Created ({len(created)}):")
            for r in created:
                print(f"    + {r.symlink_path}")

        if skipped:
            print(f"\n  Already existed ({len(skipped)}):")
            for r in skipped:
                print(f"    = {r.symlink_path}")

        if errors:
            print(f"\n  Errors ({len(errors)}):")
            for r in errors:
                print(f"    ! {r.tool.name}: {r.error}")

    print(
        f"\nDone. {total_created} new, {total_skipped} skipped, {total_errors} errors."
    )


def _generate_docs() -> None:
    """Generate AI docs (agents.md + .claude/claude.md) for a target project."""
    import asyncio

    # Step 0: Target project
    target_root = _ask_target_project()

    # Step 1: Confirm
    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]
    pv_label = PROMPT_VERSION_LABELS.get(config.prompt_version, config.prompt_version)

    print(f"\n  Target:  {target_root}")
    print(f"  Backend: {backend_info.name} ({config.model})")
    print(f"  Prompts: {pv_label}")
    print("  This will scan the project with AI and generate:")
    print("    - agents.md (project root)")
    print("    - .claude/claude.md (symlink)\n")

    if not questionary.confirm("Proceed with AI docs generation?", default=True).ask():
        print("Aborted.")
        sys.exit(0)

    # Step 2: Progress callback for CLI
    from skillnir.generator import GenerationProgress, generate_docs

    tool_count = 0

    def on_progress(p: GenerationProgress) -> None:
        nonlocal tool_count
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"  [{p.kind}] {p.content}")
        elif p.kind == "tool_use":
            tool_count += 1
            print(f"  [{tool_count}] {p.content}")
        elif p.kind == "text":
            print(p.content, end="", flush=True)
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    # Step 3: Run generation
    print(f"\n{'─' * 50}")
    print("  Generating AI docs...")
    print(f"{'─' * 50}\n")

    result = asyncio.run(generate_docs(target_root, on_progress=on_progress))

    # Step 4: Report
    print(f"\n{'─' * 50}")
    if result.success:
        print("  Generation complete!")
        print(f"    agents.md:        {result.agents_md_path}")
        if result.claude_md_path:
            print(f"    .claude/claude.md: {result.claude_md_path}")
        if result.backend_used:
            print(f"    Backend:          {result.backend_used.value}")
    else:
        print(f"  Generation failed: {result.error}")
    print(f"{'─' * 50}\n")


def _generate_skill() -> None:
    """Generate a domain-specific SKILL.md for a target project using AI."""
    import asyncio

    # Step 0: Target project
    target_root = _ask_target_project()

    # Step 1: Project name
    project_name = questionary.text(
        "Project name:",
        default=target_root.name,
    ).ask()
    if project_name is None:
        sys.exit(0)

    # Step 2: Scope selection
    from skillnir.skill_generator import SCOPE_LABELS

    scope_answer = questionary.select(
        "Select skill scope:",
        choices=[
            questionary.Choice(title=label, value=key)
            for key, label in SCOPE_LABELS.items()
        ],
    ).ask()
    if scope_answer is None:
        sys.exit(0)
    scope = scope_answer

    # Step 2b: Pure / generic mode?
    pure = questionary.confirm(
        "Pure / generic skill (don't scan target project)?",
        default=False,
    ).ask()
    if pure is None:
        sys.exit(0)

    # Step 2c: Add to current project?
    add_to_current = False
    if target_root.resolve() != Path.cwd().resolve():
        add_to_current = questionary.confirm(
            "Also add generated skill to current project?",
            default=True,
        ).ask()
        if add_to_current is None:
            sys.exit(0)

    # Step 3: Confirm
    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]
    pv_label = PROMPT_VERSION_LABELS.get(config.prompt_version, config.prompt_version)

    from skillnir.skill_generator import to_camel_case

    skill_name = to_camel_case(project_name)
    print(f"\n  Target:     {target_root}")
    print(f"  Backend:    {backend_info.name} ({config.model})")
    print(f"  Prompts:    {pv_label}")
    print(f"  Project:    {project_name}")
    print(f"  Scope:      {scope}")
    print(f"  Skill name: {skill_name}")
    print(f"  Mode:       {'pure / generic' if pure else 'project-specific'}")
    print(f"  Output:     {target_root}/.data/skills/{skill_name}/SKILL.md\n")

    if not questionary.confirm("Proceed with skill generation?", default=True).ask():
        print("Aborted.")
        sys.exit(0)

    # Step 4: Progress callback
    from skillnir.generator import GenerationProgress
    from skillnir.skill_generator import generate_skill

    tool_count = 0

    def on_progress(p: GenerationProgress) -> None:
        nonlocal tool_count
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"  [{p.kind}] {p.content}")
        elif p.kind == "tool_use":
            tool_count += 1
            print(f"  [{tool_count}] {p.content}")
        elif p.kind == "text":
            print(p.content, end="", flush=True)
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    # Step 5: Run generation
    print(f"\n{'─' * 50}")
    print(f"  Generating {skill_name} skill...")
    print(f"{'─' * 50}\n")

    result = asyncio.run(
        generate_skill(
            target_root,
            project_name,
            scope,
            on_progress=on_progress,
            pure=pure,
        )
    )

    # Step 6: Report
    print(f"\n{'─' * 50}")
    if result.success:
        print("  Skill generation complete!")
        print(f"    Skill name:      {result.skill_name}")
        print(f"    Target SKILL.md: {result.target_skill_path}")
        if result.source_skill_path:
            print(f"    Source SKILL.md: {result.source_skill_path}")
        if result.backend_used:
            print(f"    Backend:         {result.backend_used.value}")
        if add_to_current and result.success:
            current_skills_dir = Path.cwd() / ".data" / "skills"
            sync_result = sync_skill(
                target_root / ".data" / "skills",
                current_skills_dir,
                result.skill_name,
            )
            print(f"    Current project: {sync_result.action}")
        print(f"\n  Run 'skillnir install' to inject this skill into AI tools.")
    else:
        print(f"  Skill generation failed: {result.error}")
    print(f"{'─' * 50}\n")


def _generate_rule() -> None:
    """Generate Cursor rule (.mdc) for a target project."""
    import asyncio

    # Step 0: Target project
    target_root = _ask_target_project()

    # Step 1: Rule topic
    rule_topic = questionary.text(
        "Rule topic (e.g., 'error handling standards', 'React patterns'):",
        validate=lambda t: len(t.strip()) > 0 or "Please enter a rule topic",
    ).ask()
    if not rule_topic:
        print("Aborted.")
        sys.exit(0)
    rule_topic = rule_topic.strip()

    # Step 2: Confirm
    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]
    pv_label = PROMPT_VERSION_LABELS.get(config.prompt_version, config.prompt_version)

    print(f"\n  Target:  {target_root}")
    print(f"  Backend: {backend_info.name} ({config.model})")
    print(f"  Prompts: {pv_label}")
    print(f"  Topic:   {rule_topic}")
    print(f"  Output:  {target_root}/.cursor/rules/\n")

    if not questionary.confirm("Proceed with rule generation?", default=True).ask():
        print("Aborted.")
        sys.exit(0)

    # Step 3: Progress callback for CLI
    from skillnir.rule_generator import GenerationProgress, generate_rule

    tool_count = 0

    def on_progress(p: GenerationProgress) -> None:
        nonlocal tool_count
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"  [{p.kind}] {p.content}")
        elif p.kind == "tool_use":
            tool_count += 1
            print(f"  [{tool_count}] {p.content}")
        elif p.kind == "text":
            print(p.content, end="", flush=True)
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    # Step 4: Run generation
    print(f"\n{'─' * 50}")
    print("  Generating Cursor rule...")
    print(f"{'─' * 50}\n")

    result = asyncio.run(
        generate_rule(target_root, rule_topic, on_progress=on_progress)
    )

    # Step 5: Report
    print(f"\n{'─' * 50}")
    if result.success:
        print("  Rule generation complete!")
        for rf in result.rule_files:
            print(f"    .mdc: {rf}")
        if result.backend_used:
            print(f"    Backend: {result.backend_used.value}")
    else:
        print(f"  Rule generation failed: {result.error}")
    print(f"{'─' * 50}\n")


def _generate_wiki() -> None:
    """Generate a project wiki (llms.txt + docs/) for a target project."""
    import asyncio

    target_root = _ask_target_project()

    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]
    pv_label = PROMPT_VERSION_LABELS.get(config.prompt_version, config.prompt_version)

    print(f"\n  Target:  {target_root}")
    print(f"  Backend: {backend_info.name} ({config.model})")
    print(f"  Prompts: {pv_label}")
    print("  This will scan the project with AI and generate:")
    print("    - llms.txt (project root)")
    print("    - docs/ (architecture, modules, dataflow, extending,")
    print("            getting-started, troubleshooting)\n")

    if not questionary.confirm(
        "Proceed with project wiki generation?", default=True
    ).ask():
        print("Aborted.")
        sys.exit(0)

    from skillnir.generator import GenerationProgress
    from skillnir.wiki_generator import generate_wiki

    tool_count = 0

    def on_progress(p: GenerationProgress) -> None:
        nonlocal tool_count
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"  [{p.kind}] {p.content}")
        elif p.kind == "tool_use":
            tool_count += 1
            print(f"  [{tool_count}] {p.content}")
        elif p.kind == "text":
            print(p.content, end="", flush=True)
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    print(f"\n{'─' * 50}")
    print("  Generating project wiki...")
    print(f"{'─' * 50}\n")

    result = asyncio.run(generate_wiki(target_root, on_progress=on_progress))

    print(f"\n{'─' * 50}")
    if result.success:
        print("  Wiki generation complete!")
        print(f"    llms.txt:  {result.llms_txt_path}")
        print(f"    docs/:     {result.docs_dir}")
        print(f"    Files:     {len(result.files_created)} created/updated")
        if result.backend_used:
            print(f"    Backend:   {result.backend_used.value}")
    else:
        print(f"  Wiki generation failed: {result.error}")
    print(f"{'─' * 50}\n")


def _delete_wiki_cmd() -> None:
    """Delete project wiki (llms.txt + docs/) from a target project."""
    target_root = _ask_target_project()

    installations = find_wiki_installations(target_root)
    if not installations:
        print("No project wiki found in target project.")
        sys.exit(0)

    print("\n  Will delete:")
    for path in installations:
        print(f"    - {path}")
    print()

    if not questionary.confirm("Proceed with deletion?", default=False).ask():
        print("Aborted.")
        sys.exit(0)

    result = delete_wiki(target_root)
    if result.error:
        print(f"  ✗ Error: {result.error}")
    else:
        print(f"  ✓ Removed {len(result.removed_files)} files")
        if result.cleaned_dirs:
            print(f"  ✓ Cleaned {len(result.cleaned_dirs)} empty directories")


def _compress_docs() -> None:
    """Compress AI-related docs (rule-based, optional AI tone pass)."""
    import asyncio

    target_root = _ask_target_project()

    from skillnir.docs_compressor import (
        compress_docs_apply,
        compress_docs_dry_run,
        find_ai_docs,
    )

    docs = find_ai_docs(target_root)
    if not docs:
        print("\n  No AI-related docs found in target project.")
        sys.exit(0)

    # Step 1: dry-run
    print(f"\n  Found {len(docs)} AI docs. Running dry-run...\n")
    dry = compress_docs_dry_run(target_root)
    for r in dry.files:
        rel = r.path.relative_to(target_root)
        if r.error:
            print(f"  [error] {rel}: {r.error}")
        else:
            print(
                f"  - {rel}: {r.original_chars} -> {r.compressed_chars} chars "
                f"({r.reduction_pct:.1f}% smaller)"
            )
    print(
        f"\n  Total: {dry.total_original_chars} -> {dry.total_compressed_chars} "
        f"chars ({dry.total_reduction_pct:.1f}% smaller)\n"
    )

    if not questionary.confirm("Apply rule-based compression?", default=False).ask():
        print("Aborted.")
        sys.exit(0)

    with_tone = questionary.confirm(
        "Also run AI tone-tightening pass after compression?", default=True
    ).ask()
    if with_tone is None:
        sys.exit(0)

    # Step 2: apply
    from skillnir.generator import GenerationProgress

    tool_count = 0

    def on_progress(p: GenerationProgress) -> None:
        nonlocal tool_count
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"  [{p.kind}] {p.content}")
        elif p.kind == "tool_use":
            tool_count += 1
            print(f"  [{tool_count}] {p.content}")
        elif p.kind == "text":
            print(p.content, end="", flush=True)
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    print(f"\n{'─' * 50}")
    print("  Applying compression...")
    print(f"{'─' * 50}\n")

    result = asyncio.run(
        compress_docs_apply(
            target_root, with_ai_tone=with_tone, on_progress=on_progress
        )
    )

    print(f"\n{'─' * 50}")
    written = sum(1 for r in result.files if r.written)
    print(f"  Compressed {written}/{len(result.files)} files")
    print(
        f"  Total: {result.total_original_chars} -> {result.total_compressed_chars} "
        f"chars ({result.total_reduction_pct:.1f}% smaller)"
    )
    print(f"  AI tone pass: {'applied' if result.ai_tone_applied else 'skipped'}")
    if result.error:
        print(f"  Note: {result.error}")
    print(f"{'─' * 50}\n")


def _optimize_docs() -> None:
    """Audit and optionally fix AI-doc inconsistencies in a target project."""
    import asyncio

    target_root = _ask_target_project()

    mode = questionary.select(
        "Mode:",
        choices=[
            questionary.Choice(title="Report (dry-run, no writes)", value="report"),
            questionary.Choice(
                title="Apply (fix inconsistencies in place)", value="apply"
            ),
        ],
    ).ask()
    if mode is None:
        sys.exit(0)

    from skillnir.backends import BACKENDS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    print(f"\n  Target:  {target_root}")
    print(f"  Backend: {backend_info.name} ({config.model})")
    print(f"  Mode:    {mode}")
    print("  Output:  docs/ai-context-report.md")
    if mode == "apply":
        print("  Plus:    in-place edits to fix sync/cross-reference issues\n")
    else:
        print()

    if not questionary.confirm("Proceed?", default=True).ask():
        print("Aborted.")
        sys.exit(0)

    from skillnir.docs_optimizer import optimize_docs
    from skillnir.generator import GenerationProgress

    tool_count = 0

    def on_progress(p: GenerationProgress) -> None:
        nonlocal tool_count
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"  [{p.kind}] {p.content}")
        elif p.kind == "tool_use":
            tool_count += 1
            print(f"  [{tool_count}] {p.content}")
        elif p.kind == "text":
            print(p.content, end="", flush=True)
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    print(f"\n{'─' * 50}")
    print(f"  Optimizing AI docs ({mode} mode)...")
    print(f"{'─' * 50}\n")

    result = asyncio.run(optimize_docs(target_root, mode=mode, on_progress=on_progress))

    print(f"\n{'─' * 50}")
    if result.success:
        print("  Optimize complete!")
        print(f"    Mode:        {result.mode}")
        if result.report_path:
            print(f"    Report:      {result.report_path}")
        if result.files_touched:
            print(f"    Files touched: {len(result.files_touched)}")
            for p in result.files_touched:
                print(f"      - {p}")
        if result.backend_used:
            print(f"    Backend:     {result.backend_used.value}")
    else:
        print(f"  Optimize failed: {result.error}")
    print(f"{'─' * 50}\n")


def _sound() -> None:
    """Manage Claude Code sound notification hooks in ~/.claude/settings.json."""
    from skillnir.hooks import (
        SETTINGS_FILE,
        disable_sound_hooks,
        enable_sound_hooks,
        is_sound_enabled,
        load_settings,
        save_settings,
    )

    enabled = is_sound_enabled()

    print(f"\n{'═' * 50}")
    print("  Claude Code Sound Notification")
    print(f"{'═' * 50}\n")
    print(f"  Status: {'enabled' if enabled else 'disabled'}")
    print(f"  File:   {SETTINGS_FILE}\n")

    action = questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice(
                title="Enable sound notifications",
                disabled="already enabled" if enabled else None,
            ),
            questionary.Choice(
                title="Disable sound notifications",
                disabled="already disabled" if not enabled else None,
            ),
            "Reset Claude config to default (remove all hooks)",
            "Exit",
        ],
    ).ask()

    if action is None or action == "Exit":
        return

    if action == "Enable sound notifications":
        enable_sound_hooks()
        print("\n  Sound notifications enabled (Stop + PermissionRequest).")
        print("  Restart Claude Code for changes to take effect.")

    elif action == "Disable sound notifications":
        disable_sound_hooks()
        print("\n  Sound notifications disabled.")
        print("  Restart Claude Code for changes to take effect.")

    elif action.startswith("Reset Claude config"):
        if not questionary.confirm(
            "This will remove ALL hooks from ~/.claude/settings.json. Continue?",
            default=False,
        ).ask():
            print("  Aborted.")
            return
        settings = load_settings()
        settings.pop("hooks", None)
        save_settings(settings)
        print("\n  Claude config reset — all hooks removed.")
        print("  Restart Claude Code for changes to take effect.")


def _config() -> None:
    """Manage backend and model configuration."""
    from skillnir.backends import (
        AIBackend,
        BACKENDS,
        PROMPT_VERSION_LABELS,
        PROMPT_VERSIONS,
        detect_available_backends,
        get_backend_version,
        get_usage_info,
        load_config,
        save_config,
    )

    config = load_config()
    available = detect_available_backends()
    current_info = BACKENDS[config.backend]
    pv_label = PROMPT_VERSION_LABELS.get(config.prompt_version, config.prompt_version)

    print(f"\n{'═' * 50}")
    print("  Skillnir Configuration")
    print(f"{'═' * 50}\n")

    print(f"  Backend:  {current_info.name}")
    print(f"  Model:    {config.model}")
    print(f"  Prompts:  {pv_label}")
    version = get_backend_version(config.backend)
    if version:
        print(f"  Version:  {version}")
    print()

    print("  Available backends:")
    for b in AIBackend:
        info = BACKENDS[b]
        is_available = b in available
        marker = "+" if is_available else "-"
        current = " (current)" if b == config.backend else ""
        status = "" if is_available else " [not installed]"
        print(f"    {marker} {info.name}{current}{status}")
    print()

    action = questionary.select(
        "What would you like to do?",
        choices=[
            "Switch AI Tool",
            "Switch model",
            "Switch prompt version",
            "Show usage info",
            "Exit",
        ],
    ).ask()
    if action is None or action == "Exit":
        return

    if action == "Switch prompt version":
        pv_choices = [
            questionary.Choice(
                title=f"{PROMPT_VERSION_LABELS[v]}"
                + (" (current)" if v == config.prompt_version else ""),
                value=v,
            )
            for v in PROMPT_VERSIONS
        ]
        answer = questionary.select("Select prompt version:", choices=pv_choices).ask()
        if answer:
            config.prompt_version = answer
            save_config(config)
            print(f"\n  Prompt version set to: {PROMPT_VERSION_LABELS[answer]}")
        return

    if action == "Switch AI Tool":
        if not available:
            print("\n  No backends available. Install claude, gemini, or copilot CLI.")
            return
        backend_choices = [
            questionary.Choice(
                title=f"{BACKENDS[b].name}"
                + (" (current)" if b == config.backend else ""),
                value=b.value,
            )
            for b in available
        ]
        answer = questionary.select("Select backend:", choices=backend_choices).ask()
        if answer:
            new_backend = AIBackend(answer)
            new_info = BACKENDS[new_backend]
            config.backend = new_backend
            config.model = new_info.default_model
            save_config(config)
            print(f"\n  Backend set to: {new_info.name} (model: {config.model})")

    elif action == "Switch model":
        info = BACKENDS[config.backend]
        model_choices = [
            questionary.Choice(
                title=f"{m.display_name} ({m.alias})"
                + (" [default]" if m.is_default else "")
                + (" (current)" if m.alias == config.model else ""),
                value=m.alias,
            )
            for m in info.models
        ]
        answer = questionary.select("Select model:", choices=model_choices).ask()
        if answer:
            config.model = answer
            save_config(config)
            print(f"\n  Model set to: {answer}")

    elif action == "Show usage info":
        usage = get_usage_info(config.backend)
        if usage:
            print(f"\n  {current_info.name} Usage Info:")
            print(f"  {'─' * 40}")
            for line in usage.splitlines():
                print(f"  {line}")
        elif current_info.usage_url:
            print(f"\n  {current_info.name} does not provide CLI usage info.")
            print(f"  Check usage at: {current_info.usage_url}")
        else:
            print(f"\n  No usage info available for {current_info.name}.")


def _check_skill() -> None:
    """Run /skills via configured AI backend on a target project."""
    import subprocess

    from skillnir.backends import (
        BACKENDS,
        build_subprocess_command,
        load_config,
        parse_stream_line,
    )
    from skillnir.generator import GenerationProgress

    target_root = _ask_target_project()

    config = load_config()
    backend_info = BACKENDS[config.backend]

    skill_cmd = backend_info.slash_commands.get("skills", "/skills")

    print(f"\n  Target:  {target_root}")
    print(f"  Backend: {backend_info.name} ({config.model})")
    print(f"  Command: {skill_cmd}\n")

    if not questionary.confirm("Run skill check?", default=True).ask():
        print("Aborted.")
        sys.exit(0)

    tool_count = 0

    def on_progress(p: GenerationProgress) -> None:
        nonlocal tool_count
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"  [{p.kind}] {p.content}")
        elif p.kind == "tool_use":
            tool_count += 1
            print(f"  [{tool_count}] {p.content}")
        elif p.kind == "text":
            print(p.content, end="", flush=True)
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    print(f"\n{'─' * 50}")
    print(f"  Running {skill_cmd} check...")
    print(f"{'─' * 50}\n")

    cmd = build_subprocess_command(config.backend, skill_cmd, model=config.model)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_root),
        )

        for line in proc.stdout:
            parse_stream_line(config.backend, line, on_progress)

        proc.wait(timeout=600)

        print(f"\n{'─' * 50}")
        if proc.returncode == 0:
            print("  Skill check complete!")
        else:
            stderr = proc.stderr.read() if proc.stderr else ""
            print(f"  Skill check failed (exit code {proc.returncode})")
            if stderr:
                print(f"  {stderr}")
        print(f"{'─' * 50}\n")

    except subprocess.TimeoutExpired:
        proc.kill()
        print(f"\n  {backend_info.name} timed out after 10 minutes.")
    except FileNotFoundError:
        print(f"\n  {backend_info.cli_command} CLI not found in PATH.")


def _ask() -> None:
    """Ask AI a question about a project (read-only, no changes)."""
    import subprocess

    from skillnir.backends import (
        BACKENDS,
        build_subprocess_command,
        load_config,
        parse_stream_line,
    )
    from skillnir.generator import GenerationProgress

    target_root = _ask_target_project()

    config = load_config()
    backend_info = BACKENDS[config.backend]

    question = questionary.text("Your question:").ask()
    if not question:
        print("No question provided. Aborting.")
        sys.exit(0)

    print(f"\n  Target:  {target_root}")
    print(f"  Backend: {backend_info.name} ({config.model})")
    print(f"  Mode:    ask\n")

    tool_count = 0

    def on_progress(p: GenerationProgress) -> None:
        nonlocal tool_count
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"  [{p.kind}] {p.content}")
        elif p.kind == "tool_use":
            tool_count += 1
            print(f"  [{tool_count}] {p.content}")
        elif p.kind == "text":
            print(p.content, end="", flush=True)
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    print(f"\n{'─' * 50}")
    print("  Asking AI...")
    print(f"{'─' * 50}\n")

    cmd = build_subprocess_command(
        config.backend,
        question,
        model=config.model,
        mode="ask",
    )

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_root),
        )

        for line in proc.stdout:
            parse_stream_line(config.backend, line, on_progress)

        proc.wait(timeout=600)

        print(f"\n{'─' * 50}")
        if proc.returncode == 0:
            print("  Done.")
        else:
            stderr = proc.stderr.read() if proc.stderr else ""
            print(f"  Failed (exit code {proc.returncode})")
            if stderr:
                print(f"  {stderr}")
        print(f"{'─' * 50}\n")

    except subprocess.TimeoutExpired:
        proc.kill()
        print(f"\n  {backend_info.name} timed out after 10 minutes.")
    except FileNotFoundError:
        print(f"\n  {backend_info.cli_command} CLI not found in PATH.")


def _plan_cmd() -> None:
    """Get a detailed implementation plan from AI."""
    import subprocess

    from skillnir.backends import (
        BACKENDS,
        build_subprocess_command,
        load_config,
        parse_stream_line,
    )
    from skillnir.generator import GenerationProgress

    target_root = _ask_target_project()

    config = load_config()
    backend_info = BACKENDS[config.backend]

    task = questionary.text("What do you need a plan for?").ask()
    if not task:
        print("No task provided. Aborting.")
        sys.exit(0)

    print(f"\n  Target:  {target_root}")
    print(f"  Backend: {backend_info.name} ({config.model})")
    print(f"  Mode:    plan\n")

    tool_count = 0

    def on_progress(p: GenerationProgress) -> None:
        nonlocal tool_count
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"  [{p.kind}] {p.content}")
        elif p.kind == "tool_use":
            tool_count += 1
            print(f"  [{tool_count}] {p.content}")
        elif p.kind == "text":
            print(p.content, end="", flush=True)
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    print(f"\n{'─' * 50}")
    print("  Planning...")
    print(f"{'─' * 50}\n")

    cmd = build_subprocess_command(
        config.backend,
        task,
        model=config.model,
        mode="plan",
    )

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_root),
        )

        for line in proc.stdout:
            parse_stream_line(config.backend, line, on_progress)

        proc.wait(timeout=600)

        print(f"\n{'─' * 50}")
        if proc.returncode == 0:
            print("  Plan complete.")
        else:
            stderr = proc.stderr.read() if proc.stderr else ""
            print(f"  Planning failed (exit code {proc.returncode})")
            if stderr:
                print(f"  {stderr}")
        print(f"{'─' * 50}\n")

    except subprocess.TimeoutExpired:
        proc.kill()
        print(f"\n  {backend_info.name} timed out after 10 minutes.")
    except FileNotFoundError:
        print(f"\n  {backend_info.cli_command} CLI not found in PATH.")


def _research_cmd() -> None:
    """Search latest AI engineering news, summarize articles, and generate a browsable landing page."""
    import asyncio
    import webbrowser

    from skillnir.backends import BACKENDS, load_config
    from skillnir.researcher import SOURCE_FILTERS, TOPIC_LABELS, research

    # Handle --regenerate flag: backfill HTML + regenerate landing page only
    if "--regenerate" in sys.argv:
        from skillnir.researcher import regenerate_landing

        print("\n  Regenerating HTML article pages and landing page...")
        count, index_path = regenerate_landing()
        if count:
            print(f"  Generated {count} HTML article page(s)")
        else:
            print("  All articles already have HTML pages")
        if index_path:
            print(f"  Landing page: {index_path}")
            if questionary.confirm("Open landing page in browser?").ask():
                webbrowser.open(str(index_path))
        return

    config = load_config()
    backend_info = BACKENDS[config.backend]

    print("\n  AI Engineering Research")
    print(f"  Backend: {backend_info.name} ({config.model})")
    print(f"\n  Topics to search:")
    for key, label in TOPIC_LABELS.items():
        print(f"    • {label}")

    source_choices = questionary.checkbox(
        "\n  Filter by source (leave blank for all):",
        choices=[
            questionary.Choice(label, value=key)
            for key, label in SOURCE_FILTERS.items()
        ],
    ).ask()

    if not questionary.confirm("\n  Search for latest articles?", default=True).ask():
        sys.exit(0)

    def on_progress(p) -> None:
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"      {p.content}")
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    print(f"\n{'─' * 50}\nSearching and summarizing...\n")

    result = asyncio.run(
        research(on_progress=on_progress, sources=source_choices or None)
    )

    print(f"\n{'─' * 50}")
    if result.success:
        print(f"  Articles found:   {result.articles_found}")
        print(f"  New articles:     {result.articles_new}")
        print(f"  Skipped (dedup):  {result.articles_skipped}")
        if result.index_path:
            print(f"  Landing page:     {result.index_path}")
            if questionary.confirm(
                "\n  Open landing page in browser?", default=True
            ).ask():
                webbrowser.open(result.index_path.as_uri())
    else:
        print(f"  Failed: {result.error}")
    print(f"{'─' * 50}\n")


def _testing_research_cmd() -> None:
    """Search latest testing / QA news, summarize articles, and generate a landing page."""
    import asyncio
    import webbrowser

    from skillnir.backends import BACKENDS, load_config
    from skillnir.testing_researcher import (
        SOURCE_FILTERS,
        TOPIC_LABELS,
        testing_research,
    )

    if "--regenerate" in sys.argv:
        from skillnir.testing_researcher import regenerate_landing

        print("\n  Regenerating HTML article pages and landing page...")
        count, index_path = regenerate_landing()
        if count:
            print(f"  Generated {count} HTML article page(s)")
        else:
            print("  All articles already have HTML pages")
        if index_path:
            print(f"  Landing page: {index_path}")
            if questionary.confirm("Open landing page in browser?").ask():
                webbrowser.open(str(index_path))
        return

    config = load_config()
    backend_info = BACKENDS[config.backend]

    print("\n  Testing & QA Research")
    print(f"  Backend: {backend_info.name} ({config.model})")
    print(f"\n  Topics to search:")
    for key, label in TOPIC_LABELS.items():
        print(f"    • {label}")

    source_choices = questionary.checkbox(
        "\n  Filter by source (leave blank for all):",
        choices=[
            questionary.Choice(label, value=key)
            for key, label in SOURCE_FILTERS.items()
        ],
    ).ask()

    if not questionary.confirm("\n  Search for latest articles?", default=True).ask():
        sys.exit(0)

    def on_progress(p) -> None:
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"      {p.content}")
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    print(f"\n{'─' * 50}\nSearching and summarizing...\n")

    result = asyncio.run(
        testing_research(on_progress=on_progress, sources=source_choices or None)
    )

    print(f"\n{'─' * 50}")
    if result.success:
        print(f"  Articles found:   {result.articles_found}")
        print(f"  New articles:     {result.articles_new}")
        print(f"  Skipped (dedup):  {result.articles_skipped}")
        if result.index_path:
            print(f"  Landing page:     {result.index_path}")
            if questionary.confirm(
                "\n  Open landing page in browser?", default=True
            ).ask():
                webbrowser.open(result.index_path.as_uri())
    else:
        print(f"  Failed: {result.error}")
    print(f"{'─' * 50}\n")


def _events_cmd() -> None:
    """Search for upcoming AI events, conferences, and meetups worldwide."""
    import asyncio
    import webbrowser

    from skillnir.backends import BACKENDS, load_config
    from skillnir.events import EVENT_COUNTRIES, search_events

    # Handle --regenerate flag
    if "--regenerate" in sys.argv:
        from skillnir.events import regenerate_landing

        print("\n  Regenerating HTML event pages and landing page...")
        count, index_path = regenerate_landing()
        if count:
            print(f"  Generated {count} HTML event page(s)")
        else:
            print("  All events already have HTML pages")
        if index_path:
            print(f"  Landing page: {index_path}")
            if questionary.confirm("Open landing page in browser?").ask():
                webbrowser.open(str(index_path))
        return

    config = load_config()
    backend_info = BACKENDS[config.backend]

    print("\n  AI Events Search")
    print(f"  Backend: {backend_info.name} ({config.model})")

    country_choices = questionary.checkbox(
        "\n  Select countries to search (leave blank for all):",
        choices=[
            questionary.Choice(name, value=code)
            for code, name in EVENT_COUNTRIES.items()
        ],
    ).ask()

    if not questionary.confirm("\n  Search for upcoming events?", default=True).ask():
        sys.exit(0)

    def on_progress(p) -> None:
        if p.kind == "phase":
            print(f"\n  >>> {p.content}")
        elif p.kind == "status":
            print(f"      {p.content}")
        elif p.kind == "error":
            print(f"  [ERROR] {p.content}")

    print(f"\n{'─' * 50}\nSearching for events...\n")

    result = asyncio.run(
        search_events(on_progress=on_progress, countries=country_choices or None)
    )

    print(f"\n{'─' * 50}")
    if result.success:
        print(f"  Events found:     {result.events_found}")
        print(f"  New events:       {result.events_new}")
        print(f"  Skipped (dedup):  {result.events_skipped}")
        if result.index_path:
            print(f"  Landing page:     {result.index_path}")
            if questionary.confirm(
                "\n  Open landing page in browser?", default=True
            ).ask():
                webbrowser.open(result.index_path.as_uri())
    else:
        print(f"  Failed: {result.error}")
    print(f"{'─' * 50}\n")


def _update() -> None:
    """Update flow: sync skills only (no tool selection or symlinks)."""
    # Step 0: Target project
    target_root = _ask_target_project()

    # Step 1: Sync skills from source to target
    source_dir = get_source_skills_dir()
    target_skills_dir = target_root / ".data" / "skills"
    sync_results = sync_skills(source_dir, target_skills_dir)
    _print_sync_report(sync_results)


def _install_ignore() -> None:
    """Install ignore files: select templates + tools, create symlinks."""
    from skillnir.injector import inject_ignore
    from skillnir.scaffold import get_ignore_templates, init_ignore

    # Step 0: Target project
    target_root = _ask_target_project()

    # Step 1: Template selection
    templates = get_ignore_templates()
    if not templates:
        print("No ignore templates found.")
        sys.exit(1)

    template_choices = [
        questionary.Choice(title=desc, value=name) for name, desc in templates.items()
    ]
    answers = questionary.checkbox(
        "Select ignore templates (space=toggle, enter=confirm):",
        choices=template_choices,
    ).ask()
    if not answers:
        print("No templates selected. Aborting.")
        sys.exit(0)
    selected_templates = answers

    # Step 2: Tool selection
    tools_with_ignore = [t for t in TOOLS if t.ignore_file]
    detected = detect_tools(target_root)
    detected_names = {t.name for t in detected}

    if detected:
        print(f"\n  Auto-detected {len(detected)} tools in {target_root.name}/")

    tool_choices = [
        questionary.Choice(
            title=f"{t.name} ({t.ignore_file})",
            value=t,
            checked=t.name in detected_names,
        )
        for t in tools_with_ignore
    ]
    tool_answers = questionary.checkbox(
        "Select AI tools to create ignore files for (space=toggle, enter=confirm):",
        choices=tool_choices,
    ).ask()
    if not tool_answers:
        print("No tools selected. Aborting.")
        sys.exit(0)
    selected_tools = tool_answers

    # Step 3: Confirmation
    tpl_names = ", ".join(selected_templates)
    print(f"\n  Target:    {target_root}")
    print(f"  Templates: {tpl_names}")
    print(f"  Tools:     {len(selected_tools)} selected\n")
    for t in selected_tools:
        print(f"    - {t.name} -> {t.ignore_file}")
    print()

    if not questionary.confirm(
        "Proceed with ignore file injection?", default=True
    ).ask():
        print("Aborted.")
        sys.exit(0)

    # Step 4: Create .data/ignore/ with assembled content
    ignore_files = [t.ignore_file for t in selected_tools]
    scaffold_result = init_ignore(target_root, selected_templates, ignore_files)
    if not scaffold_result.success:
        print(f"Error: {scaffold_result.error}")
        sys.exit(1)

    print(
        f"\n  Created {len(scaffold_result.created_files)} ignore files in .data/ignore/"
    )

    # Step 5: Create symlinks
    results = inject_ignore(target_root, selected_tools)
    created = [r for r in results if r.created]
    skipped = [r for r in results if not r.created and not r.error]
    errors = [r for r in results if r.error]

    print(f"\n{'=' * 50}")
    print("  Ignore Injection Report")
    print(f"{'=' * 50}\n")

    if created:
        print(f"  Created ({len(created)}):")
        for r in created:
            print(f"    + {r.symlink_path}")

    if skipped:
        print(f"\n  Already existed ({len(skipped)}):")
        for r in skipped:
            print(f"    = {r.symlink_path}")

    if errors:
        print(f"\n  Errors ({len(errors)}):")
        for r in errors:
            print(f"    ! {r.tool.name}: {r.error}")

    print(f"\nDone. {len(created)} new, {len(skipped)} skipped, {len(errors)} errors.")


def _delete_skill_cmd() -> None:
    """Delete skill(s) from a target project."""
    target_root = _ask_target_project()

    skills = discover_skills(target_root)
    if not skills:
        print("No skills found in target project.")
        sys.exit(0)

    choices = [
        questionary.Choice(title=f"{s.name} (v{s.version})", value=s) for s in skills
    ]
    selected = questionary.checkbox("Select skills to delete:", choices=choices).ask()
    if not selected:
        print("No skills selected. Aborting.")
        sys.exit(0)

    delete_data = questionary.confirm(
        "Also delete skill data from .data/skills/?", default=False
    ).ask()

    # Show what will be removed
    print("\n  Will delete:")
    for skill in selected:
        installations = find_skill_installations(target_root, skill.dir_name)
        suffix = " + .data/skills/" if delete_data else ""
        print(f"    - {skill.name} ({len(installations)} tool installations{suffix})")
    print()

    if not questionary.confirm("Proceed with deletion?", default=False).ask():
        print("Aborted.")
        sys.exit(0)

    for skill in selected:
        result = delete_skill(target_root, skill.dir_name, delete_data=delete_data)
        if result.error:
            print(f"  ✗ {result.skill_name}: {result.error}")
        else:
            print(
                f"  ✓ {result.skill_name}: removed {len(result.removed_symlinks)} "
                f"symlinks, {len(result.cleaned_dirs)} dirs cleaned"
            )


def _delete_docs_cmd() -> None:
    """Delete AI docs from a target project."""
    target_root = _ask_target_project()

    installations = find_docs_installations(target_root)
    if not installations:
        print("No AI docs found in target project.")
        sys.exit(0)

    print("\n  Will delete:")
    for path in installations:
        label = "symlink" if path.is_symlink() else "file"
        print(f"    - {path} ({label})")
    print()

    if not questionary.confirm("Proceed with deletion?", default=False).ask():
        print("Aborted.")
        sys.exit(0)

    result = delete_docs(target_root)
    if result.error:
        print(f"  ✗ Error: {result.error}")
    else:
        print(f"  ✓ Removed {len(result.removed_files)} files")
        if result.cleaned_dirs:
            print(f"  ✓ Cleaned {len(result.cleaned_dirs)} empty directories")


def _init_skill_cmd() -> None:
    """Create a default skill scaffold in a target project."""
    target_root = _ask_target_project()

    name = questionary.text(
        "Skill name (lowercase, hyphens only):",
        validate=lambda val: validate_skill_name(val) is None
        or validate_skill_name(val),
    ).ask()
    if name is None:
        sys.exit(0)

    skill_dir = target_root / ".data" / "skills" / name
    print(f"\n  Will create scaffold at: {skill_dir}")
    print("    - SKILL.md")
    print("    - INJECT.md")
    print("    - LEARNED.md")
    print("    - references/.gitkeep")
    print("    - scripts/.gitkeep")
    print("    - assets/.gitkeep\n")

    if not questionary.confirm("Create skill scaffold?").ask():
        print("Aborted.")
        sys.exit(0)

    result = init_skill(target_root, name)
    if result.success:
        print(f"  ✓ Created skill scaffold at {result.created_path}")
        for f in result.created_files:
            print(f"    + {f}")
    else:
        print(f"  ✗ Error: {result.error}")


def _init_docs_cmd() -> None:
    """Create a default AI docs template in a target project."""
    target_root = _ask_target_project()

    agents_md = target_root / "agents.md"
    if agents_md.exists():
        print(f"agents.md already exists at {agents_md}")
        sys.exit(0)

    print(f"\n  Will create in {target_root}:")
    print("    - agents.md (template)")
    print("    - .claude/claude.md (symlink)")
    print("    - .github/copilot-instructions.md (symlink)\n")

    if not questionary.confirm("Create AI docs template?").ask():
        print("Aborted.")
        sys.exit(0)

    result = init_docs(target_root)
    if result.success:
        print(f"  ✓ Created AI docs template")
        for f in result.created_files:
            print(f"    + {f}")
    else:
        print(f"  ✗ Error: {result.error}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="skillnir",
        description="Inject AI coding skills into any tool's dotdir.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="install",
        choices=[
            "install",
            "install-ignore",
            "update",
            "delete-skill",
            "delete-docs",
            "init-skill",
            "init-docs",
            "ui",
            "generate-docs",
            "generate-skill",
            "generate-rule",
            "generate-wiki",
            "delete-wiki",
            "compress-docs",
            "optimize-docs",
            "check-skill",
            "ask",
            "plan",
            "research",
            "testing-research",
            "events",
            "config",
            "sound",
        ],
        help="install (default): sync skills + inject into tools. update: sync skills only. delete-skill: remove skill(s) from a project. delete-docs: remove AI docs from a project. delete-wiki: remove project wiki (llms.txt + docs/) from a project. init-skill: create a default skill scaffold. init-docs: create a default AI docs template. ui: launch web interface. generate-docs: generate agents.md with AI. generate-skill: generate a SKILL.md with AI. generate-rule: generate Cursor rule (.mdc) with AI. generate-wiki: generate project wiki (llms.txt + docs/) with AI. compress-docs: rule-based + AI tone compression of all AI-related docs. optimize-docs: audit and optionally fix AI-doc inconsistencies/cross-references. check-skill: run /skills via AI backend. ask: ask AI a question. plan: get an implementation plan. research: search latest AI engineering news and generate summaries. testing-research: search latest testing/QA news, summarize articles, generate landing page. events: search upcoming AI events and conferences worldwide. config: manage backend/model. sound: manage Claude Code sound notifications.",
    )
    args = parser.parse_args()

    if args.command == "install":
        _install()
    elif args.command == "install-ignore":
        _install_ignore()
    elif args.command == "update":
        _update()
    elif args.command == "generate-docs":
        _generate_docs()
    elif args.command == "generate-skill":
        _generate_skill()
    elif args.command == "generate-rule":
        _generate_rule()
    elif args.command == "generate-wiki":
        _generate_wiki()
    elif args.command == "delete-wiki":
        _delete_wiki_cmd()
    elif args.command == "compress-docs":
        _compress_docs()
    elif args.command == "optimize-docs":
        _optimize_docs()
    elif args.command == "check-skill":
        _check_skill()
    elif args.command == "ask":
        _ask()
    elif args.command == "plan":
        _plan_cmd()
    elif args.command == "research":
        _research_cmd()
    elif args.command == "testing-research":
        _testing_research_cmd()
    elif args.command == "events":
        _events_cmd()
    elif args.command == "delete-skill":
        _delete_skill_cmd()
    elif args.command == "delete-docs":
        _delete_docs_cmd()
    elif args.command == "init-skill":
        _init_skill_cmd()
    elif args.command == "init-docs":
        _init_docs_cmd()
    elif args.command == "config":
        _config()
    elif args.command == "sound":
        _sound()
    elif args.command == "ui":
        from skillnir.ui import run_ui

        run_ui()
