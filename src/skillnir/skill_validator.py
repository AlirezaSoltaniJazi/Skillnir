"""Deterministic validation of generated skill directories.

Checks the contract that ``_base-skill-generator.md`` declares (frontmatter
schema, SKILL.md / INJECT.md budgets, LEARNED.md scaffold, references/
layout) so the pipeline can reject or repair non-conforming output instead
of reporting success on a bare SKILL.md.

Violations are hard failures worth a repair pass; warnings are quality
gaps reported but not fatal.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from skillnir.skills import parse_frontmatter

# Budgets from _base-skill-generator.md ("Placement Rules" / "Quality Gates").
SKILL_MD_MAX_LINES = 300
SKILL_MD_MAX_TOKENS = 3500
INJECT_MD_MIN_TOKENS = 50
INJECT_MD_MAX_TOKENS = 150
# optimize-docs.md flags INJECT.md over ~1000 chars (~250 tokens) as a
# hard budget violation; between 150 and 250 tokens is a warning.
INJECT_MD_HARD_MAX_TOKENS = 250
MAX_SUB_AGENTS = 4
MIN_REFERENCE_FILES = 5

_LEARNED_SECTIONS = ("Corrections", "Preferences", "Discovered Conventions")


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars per token) — enough for budget gates."""
    return len(text) // 4


@dataclass
class SkillValidationReport:
    """Result of validating one generated skill directory."""

    skill_dir: Path
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations

    def summary(self) -> str:
        lines = [f"- {v}" for v in self.violations]
        return "\n".join(lines)


def validate_skill_dir(
    skill_dir: Path, expected_name: str | None = None
) -> SkillValidationReport:
    """Validate a generated skill directory against the base-template contract."""
    report = SkillValidationReport(skill_dir=skill_dir)
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        report.violations.append(f"SKILL.md is missing at {skill_md}")
        return report

    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.violations.append(f"SKILL.md is unreadable: {exc}")
        return report

    try:
        meta = parse_frontmatter(skill_md)
    except Exception as exc:  # yaml.YAMLError and friends
        report.violations.append(f"SKILL.md frontmatter is not valid YAML: {exc}")
        meta = {}

    # yaml.safe_load can yield a list or scalar (e.g. "---\n- name: x\n---").
    if not isinstance(meta, dict):
        report.violations.append(
            "SKILL.md frontmatter is not a YAML mapping of key: value pairs"
        )
        meta = {}

    if meta:
        if not meta.get("name"):
            report.violations.append("SKILL.md frontmatter has no 'name'")
        elif expected_name and meta["name"] != expected_name:
            report.violations.append(
                f"SKILL.md frontmatter name is '{meta['name']}', "
                f"expected '{expected_name}'"
            )
        if not meta.get("description"):
            report.violations.append("SKILL.md frontmatter has no 'description'")
    elif not report.violations:
        report.violations.append(
            "SKILL.md has no YAML frontmatter between '---' markers"
        )

    line_count = len(text.splitlines())
    if line_count > SKILL_MD_MAX_LINES:
        report.violations.append(
            f"SKILL.md is {line_count} lines (budget: {SKILL_MD_MAX_LINES})"
        )
    token_estimate = estimate_tokens(text)
    if token_estimate >= SKILL_MD_MAX_TOKENS:
        report.violations.append(
            f"SKILL.md is ~{token_estimate} tokens (budget: <{SKILL_MD_MAX_TOKENS})"
        )

    _check_inject(skill_dir / "INJECT.md", report)
    _check_learned(skill_dir / "LEARNED.md", report)
    _check_references(skill_dir / "references", report)
    _check_agents(skill_dir, meta, report)

    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir() or not list(scripts_dir.glob("validate-*.sh")):
        report.warnings.append("scripts/ has no validate-*.sh script")

    return report


def _check_inject(inject_md: Path, report: SkillValidationReport) -> None:
    if not inject_md.is_file():
        report.violations.append("INJECT.md is missing (always-loaded summary)")
        return
    try:
        tokens = estimate_tokens(inject_md.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        report.violations.append(f"INJECT.md is unreadable: {exc}")
        return
    if tokens > INJECT_MD_HARD_MAX_TOKENS:
        report.violations.append(
            f"INJECT.md is ~{tokens} tokens "
            f"(hard budget: {INJECT_MD_HARD_MAX_TOKENS}; target: "
            f"{INJECT_MD_MIN_TOKENS}-{INJECT_MD_MAX_TOKENS})"
        )
    elif not INJECT_MD_MIN_TOKENS <= tokens <= INJECT_MD_MAX_TOKENS:
        report.warnings.append(
            f"INJECT.md is ~{tokens} tokens (target: "
            f"{INJECT_MD_MIN_TOKENS}-{INJECT_MD_MAX_TOKENS})"
        )


def _check_learned(learned_md: Path, report: SkillValidationReport) -> None:
    if not learned_md.is_file():
        report.violations.append("LEARNED.md is missing (self-learning scaffold)")
        return
    try:
        text = learned_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.violations.append(f"LEARNED.md is unreadable: {exc}")
        return
    missing = [
        section
        for section in _LEARNED_SECTIONS
        if not re.search(rf"^#+\s*{re.escape(section)}", text, re.MULTILINE)
    ]
    if missing:
        report.warnings.append("LEARNED.md is missing sections: " + ", ".join(missing))


def _check_references(references_dir: Path, report: SkillValidationReport) -> None:
    ref_files = (
        [p for p in references_dir.iterdir() if p.is_file()]
        if references_dir.is_dir()
        else []
    )
    if not ref_files:
        report.violations.append("references/ is missing or empty")
    elif len(ref_files) < MIN_REFERENCE_FILES:
        report.warnings.append(
            f"references/ has {len(ref_files)} files "
            f"(template asks for at least {MIN_REFERENCE_FILES})"
        )


def _check_agents(skill_dir: Path, meta: dict, report: SkillValidationReport) -> None:
    agents_dir = skill_dir / "agents"
    agent_files = list(agents_dir.glob("*.md")) if agents_dir.is_dir() else []
    if len(agent_files) > MAX_SUB_AGENTS:
        report.violations.append(
            f"agents/ defines {len(agent_files)} sub-agents (cap: {MAX_SUB_AGENTS})"
        )
    allowed_tools = str(meta.get("allowed-tools", ""))
    has_agent_tool = bool(re.search(r"\bAgent\b", allowed_tools))
    if agent_files and not has_agent_tool:
        report.warnings.append(
            "agents/ is non-empty but 'Agent' is not in allowed-tools"
        )
    elif not agent_files and has_agent_tool:
        report.warnings.append("'Agent' is in allowed-tools but agents/ is empty")
