"""NiceGUI web interface for skillnir."""

from pathlib import Path

_GLOBAL_CSS = """
<style>
/* ── Dark mode surfaces ── */
.body--dark { background: #0f0f17 !important; }
.body--dark .q-card { background: #1a1a2e !important; }
.body--dark .q-drawer { background: #12121e !important; }
.body--dark .q-header { background: #12121e !important; }

/* ── Light mode surfaces ── */
.body--light { background: #f8fafc !important; }
.body--light .q-card { background: #ffffff !important; }
.body--light .q-drawer { background: #f1f5f9 !important; }
.body--light .q-header { background: #ffffff !important; border-bottom: 1px solid #e2e8f0; }
.body--light .nav-active { background: rgba(99, 102, 241, 0.08) !important; }

/* ── Card border-radius (both modes) ── */
.q-card { border-radius: 12px !important; }

/* ── Gradient text ── */
.gradient-text {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Card interactions ── */
.card-hover { transition: all 0.2s ease; }
.card-hover:hover {
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.08);
    transform: translateY(-1px);
}

/* ── Model picker card hover ── */
.model-card {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid transparent;
}
.model-card:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.2);
    border-color: rgba(99, 102, 241, 0.4);
}
.body--dark .model-card:hover {
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.25);
    background: #1e1e3a !important;
}

/* ── Accent bar for cards ── */
.accent-bar { height: 3px; border-radius: 3px; }

/* ── Scrollbar (dark) ── */
.body--dark ::-webkit-scrollbar { width: 6px; height: 6px; }
.body--dark ::-webkit-scrollbar-track { background: transparent; }
.body--dark ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
.body--dark ::-webkit-scrollbar-thumb:hover { background: #555; }

/* ── Nav item active state ── */
.nav-active { background: rgba(99, 102, 241, 0.1) !important; color: #6366f1 !important;
    border-right: 3px solid #6366f1; }

/* ── Fade in ── */
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); } }
.fade-in { animation: fadeIn 0.3s ease-out; }

/* ── Left border accent ── */
.border-l-accent { border-left: 4px solid; border-radius: 12px !important; }

/* ── Theme-adaptive secondary text ── */
.text-secondary { color: #4f46e5; }  /* indigo-600 for light */
.body--dark .text-secondary { color: #a5b4fc; }  /* indigo-300 for dark */
</style>
"""


def run_ui(port: int = 8080) -> None:
    """Start the NiceGUI web server."""
    from nicegui import app, ui

    # ── Static assets (notification sound) ────────────────────
    _assets_dir = Path(__file__).resolve().parent.parent / "assets"
    app.add_static_files("/static", str(_assets_dir))

    # ── Research files (landing page + articles) ──────────────
    _research_dir = (
        Path(__file__).resolve().parent.parent.parent.parent / ".data" / "research"
    )
    if _research_dir.is_dir():
        app.add_static_files("/research-files", str(_research_dir))

    # ── Events files (landing page + event pages) ────────────
    _events_dir = (
        Path(__file__).resolve().parent.parent.parent.parent / ".data" / "events"
    )
    _events_dir.mkdir(parents=True, exist_ok=True)
    app.add_static_files("/events-files", str(_events_dir))

    # ── Import page modules to register @ui.page routes ───────
    from skillnir.ui.pages import (  # noqa: F401
        ai_context,
        ai_extra,
        delete_skill,
        events,
        generate_skill,
        home,
        ignore,
        research,
        settings,
        skill,
        supported,
        templates,
        usage_page,
    )

    # ── Start server ─────────────────────────────────────────
    ui.run(
        title="Skillnir",
        port=port,
        reload=False,
        show=True,
        storage_secret="skillnir-local",
    )
