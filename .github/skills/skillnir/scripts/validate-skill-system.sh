#!/usr/bin/env bash
set -euo pipefail

# Validates skill system conventions for the skillnir project.
# Usage: ./validate-skill-system.sh [project-root]
#
# Checks:
# 1. Every skill directory has required files (SKILL.md, INJECT.md, LEARNED.md)
# 2. SKILL.md has YAML frontmatter with required fields
# 3. LEARNED.md has required sections (Corrections, Preferences, Discovered Conventions)
# 4. INJECT.md is within token budget (approximate line count check)
# 5. references/ has minimum required files
# 6. scripts/ has at least one validate-*.sh
# 7. SKILL.md contains "Read LEARNED.md" instruction
# 8. SKILL.md contains announcement rule

PROJECT_ROOT="${1:-.}"
SKILLS_DIR="$PROJECT_ROOT/.data/skills"

PASS=0
FAIL=0
WARN=0

pass() {
    echo "  ✅ PASS  $1"
    PASS=$((PASS + 1))
}

fail() {
    echo "  ❌ FAIL  $1"
    FAIL=$((FAIL + 1))
}

warn() {
    echo "  ⚠️  WARN  $1"
    WARN=$((WARN + 1))
}

echo "========================================="
echo "  Skill System Convention Validator"
echo "========================================="
echo ""

if [[ ! -d "$SKILLS_DIR" ]]; then
    fail "Skills directory not found: $SKILLS_DIR"
    echo ""
    echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
    exit 1
fi

# Iterate over each skill directory
for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    echo "--- Checking skill: $skill_name ---"

    # Check 1: Required files exist
    for required_file in SKILL.md INJECT.md LEARNED.md; do
        if [[ -f "$skill_dir/$required_file" ]]; then
            pass "$skill_name/$required_file exists"
        else
            fail "$skill_name/$required_file is missing"
        fi
    done

    # Check 2: SKILL.md has YAML frontmatter
    if [[ -f "$skill_dir/SKILL.md" ]]; then
        if head -1 "$skill_dir/SKILL.md" | grep -q "^---$"; then
            pass "$skill_name/SKILL.md has YAML frontmatter"
        else
            fail "$skill_name/SKILL.md missing YAML frontmatter"
        fi

        # Check required frontmatter fields
        for field in name description compatibility allowed-tools; do
            if grep -q "^${field}:" "$skill_dir/SKILL.md"; then
                pass "$skill_name/SKILL.md has '$field' field"
            else
                fail "$skill_name/SKILL.md missing '$field' field"
            fi
        done

        # Check 7: Contains "Read LEARNED.md" instruction
        if grep -qi "Read.*LEARNED.md" "$skill_dir/SKILL.md"; then
            pass "$skill_name/SKILL.md contains 'Read LEARNED.md' instruction"
        else
            fail "$skill_name/SKILL.md missing 'Read LEARNED.md' instruction"
        fi

        # Check 8: Contains announcement rule
        if grep -qi "Announce skill usage\|Using:.*skill" "$skill_dir/SKILL.md"; then
            pass "$skill_name/SKILL.md contains announcement rule"
        else
            fail "$skill_name/SKILL.md missing announcement rule"
        fi

        # Check line count
        line_count=$(wc -l < "$skill_dir/SKILL.md")
        if [[ $line_count -le 300 ]]; then
            pass "$skill_name/SKILL.md is within budget ($line_count lines)"
        else
            fail "$skill_name/SKILL.md exceeds 300 lines ($line_count lines)"
        fi
    fi

    # Check 3: LEARNED.md has required sections
    if [[ -f "$skill_dir/LEARNED.md" ]]; then
        for section in "## Corrections" "## Preferences" "## Discovered Conventions"; do
            if grep -q "$section" "$skill_dir/LEARNED.md"; then
                pass "$skill_name/LEARNED.md has '$section' section"
            else
                fail "$skill_name/LEARNED.md missing '$section' section"
            fi
        done
    fi

    # Check 4: INJECT.md line count (proxy for token budget)
    if [[ -f "$skill_dir/INJECT.md" ]]; then
        inject_lines=$(wc -l < "$skill_dir/INJECT.md")
        if [[ $inject_lines -le 20 ]]; then
            pass "$skill_name/INJECT.md is compact ($inject_lines lines)"
        else
            warn "$skill_name/INJECT.md may exceed token budget ($inject_lines lines)"
        fi
    fi

    # Check 5: references/ has files
    if [[ -d "$skill_dir/references" ]]; then
        ref_count=$(find "$skill_dir/references" -maxdepth 1 -type f | wc -l)
        if [[ $ref_count -ge 5 ]]; then
            pass "$skill_name/references/ has $ref_count files (≥5 required)"
        else
            warn "$skill_name/references/ has only $ref_count files (≥5 recommended)"
        fi
    else
        warn "$skill_name/references/ directory not found"
    fi

    # Check 6: scripts/ has validate script
    if [[ -d "$skill_dir/scripts" ]]; then
        if ls "$skill_dir/scripts"/validate-*.sh >/dev/null 2>&1; then
            pass "$skill_name/scripts/ has validation script"
        else
            warn "$skill_name/scripts/ has no validate-*.sh"
        fi
    else
        warn "$skill_name/scripts/ directory not found"
    fi

    # Check: agents/ consistency with allowed-tools
    if [[ -d "$skill_dir/agents" ]]; then
        agent_count=$(find "$skill_dir/agents" -maxdepth 1 -name "*.md" -type f | wc -l)
        if [[ $agent_count -gt 0 ]]; then
            if grep -q "Agent" "$skill_dir/SKILL.md" 2>/dev/null; then
                pass "$skill_name has agents/ and 'Agent' in allowed-tools"
            else
                fail "$skill_name has agents/ but 'Agent' not in allowed-tools"
            fi
            if [[ $agent_count -le 4 ]]; then
                pass "$skill_name has $agent_count sub-agents (≤4 max)"
            else
                fail "$skill_name has $agent_count sub-agents (max 4 allowed)"
            fi
        fi
    fi

    echo ""
done

echo "========================================="
echo "  Results: $PASS passed, $FAIL failed, $WARN warnings"
echo "========================================="

if [[ $FAIL -gt 0 ]]; then
    exit 1
else
    exit 0
fi
