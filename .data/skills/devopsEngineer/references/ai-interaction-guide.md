# AI Interaction Guide — Infrastructure Domain

## Anti-Dependency Strategies

### Problem
AI-assisted infrastructure work carries unique risks: misconfigured pipelines can break all PRs, security misconfigurations can expose repositories, and infrastructure changes are harder to review than application code.

### Strategies

1. **Explain before generating** — For CI/CD changes, explain what will change and why before writing YAML. Infrastructure mistakes propagate to all developers.

2. **Validate after generating** — Always run `scripts/validate-infra.sh` after infrastructure changes. Pre-commit hooks and CI checks are interconnected — changing one may require updating the other.

3. **Link to documentation** — When explaining GitHub Actions features, link to official docs. YAML configuration has many gotchas that aren't obvious from examples.

4. **Suggest dry runs** — For pre-commit changes: `pre-commit run --all-files`. For workflow changes: create a draft PR to trigger CI.

5. **Template after repetition** — If generating similar workflow patterns 3+ times, suggest creating a composite action or reusable workflow.

## Infrastructure-Specific Anti-Patterns in AI Interaction

### Don't blindly copy workflow patterns
Each workflow has specific trigger, permission, and timeout requirements. Copying a workflow and changing the command is insufficient — review all fields.

### Don't ignore the CI ↔ pre-commit parity
Changes to one must be evaluated for impact on the other. The AI should always check both when modifying quality gates.

### Don't generate secrets management without context
Never suggest hardcoding secrets. Always ask about the project's secret management approach first (this project has none — it's a CLI tool with no deployment secrets).

### Don't over-engineer infrastructure
This project is a Python CLI tool, not a cloud service. Suggestions for Docker, Kubernetes, Terraform, or cloud provisioning are inappropriate unless explicitly requested.

## Correction Protocol for Infrastructure

When corrected on infrastructure patterns:

1. Acknowledge the specific mistake (e.g., "I used `@main` instead of `@v4` for the action version")
2. Restate as a rule (e.g., "Understood: always pin GitHub Actions to major versions, never use branch references")
3. Apply to all subsequent workflow/config generation
4. Write to LEARNED.md under `## Corrections`

## Common AI Mistakes in This Project

| Mistake                              | Correct Approach                            |
| ------------------------------------ | ------------------------------------------- |
| Suggesting Docker for deployment     | Project is a CLI tool — no containerization |
| Using `@latest` for actions          | Pin to `@v4`, `@v5`, etc.                   |
| Forgetting `timeout-minutes`         | Every job MUST have a timeout               |
| Not excluding `.data/` from hooks    | Add `exclude: ^\.data/` to code hooks       |
| Suggesting `requirements.txt`        | Use `pyproject.toml` exclusively            |
| Adding deploy/release workflows      | Only add when explicitly requested          |
