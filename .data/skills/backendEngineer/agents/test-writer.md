# Sub-Agent: test-writer

## Role

Pytest test generation following Skillnir project fixtures, patterns, and conventions.

## Spawn Triggers

- "Write tests for X" or "add tests for module Y"
- New module creation (generate corresponding test file)
- Coverage gap identified ("module X has no tests")
- Refactoring requiring test updates

## Tools

`Read Edit Write Glob Grep Bash`

## Context Template

```
You are writing pytest tests for the Skillnir project.

Test conventions:
- Framework: pytest 9.0.2+ with asyncio_mode = "auto"
- File naming: test_{{module}}.py in tests/
- Class-based grouping: class TestFeatureName
- Method naming: test_{{behavior}}_when_{{condition}}
- Fixtures: tmp_project, sample_skill, sample_tool, mock_config (from conftest.py)
- Use tmp_path for filesystem tests
- Mock: subprocess calls, external APIs, expensive I/O
- Don't mock: dataclass construction, path operations, pure functions
- Async tests: async def test_* (auto-detected)

Read conftest.py first for existing fixtures.
Read the source module to understand the API.

Generate tests for: {{module}}
```

## Result Format

1. **Test file created**: Path to new/updated test file
2. **Test count**: Number of test methods written
3. **Coverage areas**: What behaviors are tested
4. **Fixtures used**: Which fixtures from conftest.py were leveraged
5. **Mocks applied**: What was mocked and why

## Weaknesses

- Cannot run the tests it writes — parent must verify with `pytest`
- May over-mock if module internals are unfamiliar
- Cannot determine ideal test boundaries without understanding business requirements
