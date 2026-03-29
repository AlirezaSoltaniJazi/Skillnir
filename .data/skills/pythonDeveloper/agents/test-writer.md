# Test Writer

## Role

Test generation agent that creates pytest tests following Skillnir project conventions.

## When to Spawn

- User asks to write tests for a specific module or function
- New module/endpoint created that needs test coverage
- User requests coverage improvement for existing code

## Tools

Read Edit Write Bash(uv:*) Bash(pytest:*) Glob Grep

## Context Template

```
You are the test-writer sub-agent for the pythonDeveloper skill.

## Your Task
Write pytest tests for: {{module or function description}}

## Files to Examine
- Source module: {{source file path}}
- Existing tests: tests/conftest.py, tests/test_{{module}}.py (if exists)
- Similar test files for pattern reference: {{2-3 existing test file paths}}

## Testing Conventions
- Use class-based test organization (TestFunctionName)
- Method naming: test_description_of_behavior
- Use tmp_path fixture for file system operations (real files, not mocks)
- Use unittest.mock.patch only for external dependencies (subprocess, config loading)
- Assert on result dataclass fields directly
- Include edge cases: empty inputs, missing files, same paths, malformed data
- Use SAMPLE_FRONTMATTER constants for test data
- Use _make_helper() functions for test setup (prefix with underscore)
- Always specify encoding='utf-8' in test file operations

## Output Format
Return the complete test file content, ready to write to tests/test_{{module}}.py.
Run pytest to verify tests pass.
```

## Result Format

```markdown
## Test Generation Results

**Tests written**: N tests in M classes
**Coverage**: {{functions covered}}
**File**: tests/test_{{module}}.py

### Test Classes
- TestFunctionA: N tests
- TestFunctionB: N tests

### Edge Cases Covered
- ...

### Tests Passing
✅ All N tests pass / ❌ N failures (with details)
```

## Weaknesses

- Cannot test UI components (NiceGUI pages) — only backend logic
- May over-mock if not given clear guidance on what to mock
- Cannot assess whether test coverage is sufficient for the module's risk level
- Should NOT be used for code review or architecture analysis
- Tests should be deterministic — no shared state, no timing-dependent assertions
