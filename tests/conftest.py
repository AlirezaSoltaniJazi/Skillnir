"""Shared fixtures for skillnir tests."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend, AppConfig
from skillnir.skills import Skill
from skillnir.tools import AITool

SAMPLE_FRONTMATTER = """\
---
name: test-skill
description: A test skill
metadata:
  version: "1.0.0"
---
# Test Skill
Some content here.
"""

SAMPLE_FRONTMATTER_V2 = """\
---
name: test-skill
description: A test skill
metadata:
  version: "2.0.0"
---
# Test Skill v2
Updated content.
"""


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temp project directory with .data/skills/ and tool dotdirs."""
    skills_dir = tmp_path / ".data" / "skills" / "my-skill"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text(SAMPLE_FRONTMATTER, encoding="utf-8")

    for dotdir in (".cursor", ".claude"):
        (tmp_path / dotdir).mkdir()

    return tmp_path


@pytest.fixture
def sample_skill(tmp_project: Path) -> Skill:
    return Skill(
        name="my-skill",
        description="A test skill",
        version="1.0.0",
        path=tmp_project / ".data" / "skills" / "my-skill",
    )


@pytest.fixture
def sample_tool() -> AITool:
    return AITool(name="TestTool", dotdir=".testtool", company="TestCo")


@pytest.fixture
def mock_config():
    """Patch load_config to return a controllable AppConfig."""
    cfg = AppConfig(backend=AIBackend.CLAUDE, model="sonnet", prompt_version="v1")
    with patch("skillnir.backends.load_config", return_value=cfg):
        yield cfg
