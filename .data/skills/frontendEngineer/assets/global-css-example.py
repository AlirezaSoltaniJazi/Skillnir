"""Example _GLOBAL_CSS template showing the theme structure."""

# This is a reference template — the actual CSS lives in src/skillnir/ui/__init__.py
# Copy and adapt when adding new global styles.

_GLOBAL_CSS_TEMPLATE = """
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

/* ── Accent bar for cards ── */
.accent-bar { height: 3px; border-radius: 3px; }

/* ── Nav item active state ── */
.nav-active {
    background: rgba(99, 102, 241, 0.1) !important;
    color: #6366f1 !important;
    border-right: 3px solid #6366f1;
}

/* ── Fade in animation ── */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.3s ease-out; }

/* ── Left border accent ── */
.border-l-accent { border-left: 4px solid; border-radius: 12px !important; }

/* ── Theme-adaptive secondary text ── */
.text-secondary { color: #4f46e5; }
.body--dark .text-secondary { color: #a5b4fc; }
</style>
"""
