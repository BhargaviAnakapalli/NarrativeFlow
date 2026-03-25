# ui/chat.py — AI assistant chat panel (renamed from ui/ai_chat_panel.py)
import streamlit as st

from core.engine import call_ollama, add_message, get_history, get_flat_history, check_ollama
from ui.layout import render_icon_nav


def render_ai_chat_panel():
    """Render the right AI assistant chat panel."""

    # ── Top Navigation Icons ──
    render_icon_nav()

    # ── Header ──
    st.markdown("""
    <div class="ai-panel-header">
        <span class="ai-panel-icon">✍️</span>
        <span class="ai-panel-title">AI Assistant</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Ollama status dot ──
    online, _ = check_ollama()
    dot = "🟢" if online else "🔴"
    st.markdown(
        f'<div class="ai-status">{dot} {"Online · " + st.session_state.model if online else "Ollama offline"}</div>',
        unsafe_allow_html=True,
    )

    # ── Chat History ──
    with st.container(height=550, border=False):
        st.markdown('<div class="ai-chat-messages">', unsafe_allow_html=True)

        history = get_history()
        if not history:
            st.markdown("""
            <div class="ai-empty-state">
                <div style="font-size:2rem;margin-bottom:0.5rem;">✨</div>
                <div>Ask your AI co-writer anything.<br>Build characters, expand scenes, or continue the story.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i, msg in enumerate(history):
                role = msg["role"]
                content = msg["content"]
                ts = msg.get("ts", "")
                if role == "user":
                    st.markdown(f"""
                    <div class="ai-msg-user">
                        <div class="ai-msg-bubble user">{content}</div>
                        <div class="ai-msg-meta">{ts}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="ai-msg-ai">
                        <div class="ai-avatar">✍️</div>
                        <div style="flex:1;min-width:0;">
                            <div class="ai-suggestion-card">{content}</div>
                            <div class="ai-msg-meta">{ts} · {st.session_state.model}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        if st.button("＋ Add", key=f"add_story_{i}", use_container_width=True, help="Add to Story"):
                            ch = st.session_state.active_chapter
                            current = st.session_state.chapters.get(ch, "")
                            separator = "\n\n" if current.strip() else ""
                            st.session_state.chapters[ch] = current + separator + content
                            st.session_state.editor_sync_key = st.session_state.get("editor_sync_key", 0) + 1
                            st.success("✅ Added to story!")
                            st.rerun()
                    with btn_col2:
                        if st.button("↩ Rewrite", key=f"rewrite_{i}", use_container_width=True, help="Rewrite this"):
                            with st.spinner("Rewriting…"):
                                reply = call_ollama([{"role": "user", "content": content}],
                                    "Rewrite this passage in a completely different style, keeping the same story ideas.")
                            add_message("assistant", reply)
                            st.rerun()
                    with btn_col3:
                        if st.button("⤢ Expand", key=f"expand_{i}", use_container_width=True, help="Expand this"):
                            with st.spinner("Expanding…"):
                                reply = call_ollama([{"role": "user", "content": content}],
                                    "Expand this passage into a longer, more detailed and immersive version.")
                            add_message("assistant", reply)
                            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Chat Input ──
    user_input = st.chat_input(f"Ask your co-writer… {st.session_state.model}", key="ai_panel_chat_input")

    if user_input:
        is_first_msg = len(get_history()) == 0
        add_message("user", user_input)
        h = get_flat_history()
        with st.spinner("Writing…"):
            reply = call_ollama(h)
        add_message("assistant", reply)
        st.session_state.last_ai_suggestion = reply

        # ── Auto-generate title from first message ──
        active_chat = st.session_state.active_chat
        import re
        from datetime import datetime as _dt
        _now = _dt.now().strftime("%b %d, %H:%M")

        if active_chat not in st.session_state.story_metadata:
            st.session_state.story_metadata[active_chat] = {"title": "New Story", "pinned": False, "db_id": active_chat}

        _default_titles = {"new story", "untitled story", "untitled", ""}
        if is_first_msg and st.session_state.story_title.strip().lower() in _default_titles:
            clean_input = re.sub(r'<[^>]*>', '', user_input).strip() or "New Story"
            new_title = clean_input[:40].strip()
            if len(clean_input) > 40:
                new_title += "…"
            st.session_state.story_title = new_title
            st.session_state.story_metadata[active_chat]["title"] = new_title
            st.session_state.pop("story_title_input", None)

        st.session_state.story_metadata[active_chat]["last_updated"] = _now

        if getattr(st.session_state, "logged_in", False):
            from core.storage import save_story, add_to_history, get_story
            username = getattr(st.session_state, "auth_username", "")
            if username:
                story_id = st.session_state.get("active_story_id") or st.session_state.active_chat
                st.session_state.active_story_id = story_id
                now = _dt.now().strftime("%b %d, %H:%M")
                story_title = re.sub(r'<[^>]*>', '', st.session_state.story_title).strip()
                existing_story = get_story(username, story_id) or {}
                save_story(username, story_id, {"title": story_title, "content": existing_story.get("content", ""), "updated_at": now})
                add_to_history(username, story_title, story_id, now)
                st.session_state.story_metadata[active_chat]["title"] = story_title
                st.session_state.story_metadata[active_chat]["last_updated"] = now
                st.session_state.story_metadata[active_chat]["db_id"] = story_id

        if st.session_state.auto_continue and not reply.startswith("⚠️"):
            h2 = get_flat_history()
            with st.spinner("Auto-continuing…"):
                continuation = call_ollama(h2, "Continue the story naturally from where it left off.")
            add_message("assistant", continuation)

        st.rerun()
