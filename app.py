"""
NarrativeFlow — Main Entry Point
Run: streamlit run app.py
Requires: ollama serve + ollama pull llama3
"""

import streamlit as st

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be FIRST Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="NarrativeFlow – AI Story Co-Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CORE BOOTSTRAP
# ─────────────────────────────────────────────
from core.storage import init_db
init_db()

from core.state import init_state, sync_profile_after_login
from login import show_login_page

init_state()

# ─────────────────────────────────────────────
#  AUTH GATE
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    show_login_page()
    st.stop()

sync_profile_after_login()

# Persist session so it survives page refresh
try:
    from core.storage import save_active_user, save_session
    if st.session_state.auth_username:
        save_active_user(st.session_state.auth_username)
        save_session(st.session_state.auth_username)
except Exception:
    pass

# ─────────────────────────────────────────────
#  THEME / CSS
# ─────────────────────────────────────────────
from ui.styles import inject_theme
inject_theme()

# ─────────────────────────────────────────────
#  LEFT SIDEBAR
# ─────────────────────────────────────────────
from ui.layout import render_sidebar
render_sidebar()

# ─────────────────────────────────────────────
#  TWO-COLUMN MAIN LAYOUT
#  col_editor (story editor) | col_chat (AI panel)
# ─────────────────────────────────────────────
col_editor, col_chat = st.columns([5, 3])

# ── CENTER: Story Editor ──
with col_editor:
    st.markdown(f"""
    <div class="hero-compact">
        <h1>Narrative<span>Flow</span></h1>
        <p>{st.session_state.model} · {st.session_state.genre} · {st.session_state.tone}</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.session_state.current_page

    if page == "💬 Story Chat":
        from ui.editor import render_story_editor
        render_story_editor()

    elif page == "🗺 World Builder":
        from ui.tools import render_world_builder
        render_world_builder()

    elif page == "🔧 Writer Tools":
        from ui.tools import render_writer_tools
        render_writer_tools()

    elif page == "✏️ Split Editor":
        from ui.editor import render_split_editor
        render_split_editor()

# ── RIGHT: AI Chat Panel ──
with col_chat:
    from ui.chat import render_ai_chat_panel
    render_ai_chat_panel()
