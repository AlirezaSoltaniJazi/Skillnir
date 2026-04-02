"""Registry of supported AI coding tools."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AITool:
    name: str
    dotdir: str
    company: str
    skills_subpath: str = "skills"
    popularity: int = 0  # 1-10 (GitHub stars, user base, market share)
    performance: int = 0  # 1-10 (SWE-bench, coding quality, capabilities)
    price: int = 0  # 1-10 (10 = cheapest / most free)
    icon_url: str = (
        ""  # GitHub org avatar URL (e.g. https://github.com/org.png?size=32)
    )
    ignore_file: str = ""  # Ignore file name (e.g. .claudeignore), empty if unsupported


# .data/ is our central skill storage (source of truth)
SOURCE_DOTDIR = ".data"

# .agents/ is always auto-injected (Codex skills standard)
AUTO_INJECT_TOOL = AITool("Codex CLI (agents)", ".agents", "OpenAI")

# All tools that the user can select (popular tools first)
_GH = "https://github.com/{}.png?size=32"

TOOLS: tuple[AITool, ...] = (
    # ── Top tier ──────────────────────────────────────────────
    AITool(
        "Claude Code",
        ".claude",
        "Anthropic",
        popularity=9,
        performance=10,
        price=5,
        icon_url="https://claude.ai/images/claude_app_icon.png",
        ignore_file=".claudeignore",
    ),
    AITool(
        "Cursor",
        ".cursor",
        "Anysphere",
        popularity=9,
        performance=9,
        price=6,
        icon_url="https://static.cdnlogo.com/logos/c/23/cursor.svg",
        ignore_file=".cursorignore",
    ),
    AITool(
        "Windsurf",
        ".windsurf",
        "Codeium",
        popularity=7,
        performance=7,
        price=7,
        icon_url=_GH.format("Exafunction"),
        ignore_file=".codeiumignore",
    ),
    AITool(
        "GitHub Copilot",
        ".github",
        "GitHub",
        popularity=10,
        performance=8,
        price=7,
        icon_url=_GH.format("github"),
        ignore_file=".copilotignore",
    ),
    AITool(
        "Cline",
        ".cline",
        "Cline",
        popularity=8,
        performance=7,
        price=9,
        icon_url=_GH.format("cline"),
        ignore_file=".clineignore",
    ),
    AITool(
        "Roo Code",
        ".roo",
        "Roo Code",
        popularity=6,
        performance=7,
        price=9,
        icon_url=_GH.format("RooVetGit"),
        ignore_file=".rooignore",
    ),
    AITool(
        "Codex CLI",
        ".codex",
        "OpenAI",
        popularity=8,
        performance=8,
        price=6,
        icon_url=_GH.format("openai"),
        ignore_file=".codexignore",
    ),
    AITool(
        "Gemini CLI",
        ".gemini",
        "Google",
        popularity=8,
        performance=8,
        price=10,
        icon_url=_GH.format("google-gemini"),
        ignore_file=".geminiignore",
    ),
    AITool(
        "Continue.dev",
        ".continue",
        "Continue",
        popularity=5,
        performance=6,
        price=9,
        icon_url=_GH.format("continuedev"),
        ignore_file=".continueignore",
    ),
    AITool(
        "Amp",
        ".amp",
        "Sourcegraph",
        popularity=4,
        performance=7,
        price=4,
        icon_url=_GH.format("sourcegraph"),
        ignore_file=".ampignore",
    ),
    AITool(
        "Kiro",
        ".kiro",
        "Amazon AWS",
        popularity=5,
        performance=7,
        price=5,
        icon_url=_GH.format("aws"),
        ignore_file=".kiroignore",
    ),
    AITool(
        "Trae",
        ".trae",
        "ByteDance",
        popularity=6,
        performance=7,
        price=8,
        icon_url=_GH.format("bytedance"),
        ignore_file=".traeignore",
    ),
    AITool(
        "Junie AI Agent",
        ".junie",
        "JetBrains",
        popularity=4,
        performance=7,
        price=5,
        icon_url=_GH.format("JetBrains"),
        ignore_file=".aiignore",
    ),
    AITool(
        "Augment Code",
        ".augment",
        "Augment",
        popularity=3,
        performance=7,
        price=4,
        icon_url=_GH.format("augmentcode"),
        ignore_file=".augmentignore",
    ),
    # ── Others (alphabetical) ────────────────────────────────
    AITool("AdaL CLI", ".adal", "SylphAI", popularity=2, performance=5, price=7),
    AITool(
        "Google Antigravity IDE",
        ".agent",
        "Google",
        popularity=3,
        performance=6,
        price=6,
        icon_url=_GH.format("google"),
        ignore_file=".geminiignore",
    ),
    AITool(
        "CodeBuddy",
        ".codebuddy",
        "Tencent",
        popularity=3,
        performance=6,
        price=6,
        icon_url=_GH.format("Tencent"),
    ),
    AITool(
        "Command Code",
        ".commandcode",
        "CommandCode AI",
        popularity=2,
        performance=5,
        price=7,
    ),
    AITool(
        "Cortex Code CLI",
        ".cortex",
        "Snowflake",
        popularity=3,
        performance=6,
        price=6,
        icon_url=_GH.format("Snowflake-Labs"),
    ),
    AITool(
        "Crush",
        ".crush",
        "Charmbracelet",
        popularity=5,
        performance=6,
        price=8,
        icon_url=_GH.format("charmbracelet"),
        ignore_file=".crushignore",
    ),
    AITool(
        "Factory (Droids)",
        ".factory",
        "Factory AI",
        popularity=3,
        performance=6,
        price=5,
        icon_url=_GH.format("Factory-AI"),
    ),
    AITool(
        "Goose",
        ".goose",
        "Block",
        popularity=6,
        performance=6,
        price=10,
        icon_url=_GH.format("block"),
        ignore_file=".gooseignore",
    ),
    AITool("iFlow CLI", ".iflow", "iFlow AI", popularity=2, performance=5, price=7),
    AITool(
        "Kilo Code",
        ".kilocode",
        "Kilo",
        popularity=4,
        performance=6,
        price=9,
        icon_url=_GH.format("Kilo-Org"),
        ignore_file=".kilocodeignore",
    ),
    AITool(
        "Kimi Code CLI",
        ".kimi",
        "Moonshot AI",
        popularity=3,
        performance=6,
        price=7,
        icon_url=_GH.format("MoonshotAI"),
    ),
    AITool("Kode CLI", ".kode", "shareAI-lab", popularity=2, performance=5, price=8),
    AITool("MCPJam", ".mcpjam", "MCPJam", popularity=2, performance=5, price=7),
    AITool(
        "Mux",
        ".mux",
        "Coder",
        popularity=3,
        performance=6,
        price=7,
        icon_url=_GH.format("coder"),
    ),
    AITool(
        "Neovate Code", ".neovate", "NeovateAI", popularity=2, performance=5, price=7
    ),
    AITool(
        "OpenCode",
        ".opencode",
        "SST",
        popularity=3,
        performance=6,
        price=8,
        icon_url=_GH.format("sst-inc"),
        ignore_file=".opencodeignore",
    ),
    AITool(
        "OpenHands",
        ".openhands",
        "All Hands AI",
        popularity=7,
        performance=8,
        price=9,
        icon_url=_GH.format("All-Hands-AI"),
        ignore_file=".openhandsignore",
    ),
    AITool(
        "Pi Coding Agent",
        ".pi",
        "badlogic",
        popularity=2,
        performance=5,
        price=8,
        icon_url=_GH.format("badlogic"),
    ),
    AITool(
        "Pochi",
        ".pochi",
        "TabbyML",
        popularity=2,
        performance=5,
        price=7,
        icon_url=_GH.format("TabbyML"),
    ),
    AITool(
        "Qoder IDE",
        ".qoder",
        "Alibaba",
        popularity=3,
        performance=6,
        price=6,
        icon_url=_GH.format("alibaba"),
        ignore_file=".qoderignore",
    ),
    AITool(
        "Qwen Coding",
        ".qwen",
        "Alibaba",
        popularity=4,
        performance=7,
        price=8,
        icon_url=_GH.format("QwenLM"),
        ignore_file=".qwenignore",
    ),
    AITool(
        "Vibe",
        ".vibe",
        "Mistral AI",
        popularity=3,
        performance=7,
        price=7,
        icon_url=_GH.format("mistralai"),
    ),
    AITool(
        "Zencoder", ".zencoder", "Zencoder AI", popularity=2, performance=5, price=6
    ),
)


def detect_tools(target_root: Path) -> list[AITool]:
    """Return tools whose dotdir already exists in target_root."""
    return [t for t in TOOLS if (target_root / t.dotdir).is_dir()]
