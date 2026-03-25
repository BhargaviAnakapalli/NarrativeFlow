# ui/editor.py — Story editor and split editor
# Merged from: ui/story_editor.py + ui/split_editor.py

import streamlit as st

from core.engine import call_ollama, add_message, get_flat_history
from core.export import create_pdf_bytes, create_docx_bytes


# ─────────────────────────────────────────────
#  STORY EDITOR  (from story_editor.py)
# ─────────────────────────────────────────────

def _get_chapters():
    return st.session_state.get("chapter_order", ["Chapter 1"])


def _get_chapter_content():
    return st.session_state.chapters.get(st.session_state.active_chapter, "")


def render_story_editor():
    """Render the center story editor with title, chapter nav, and editor area."""

    # ── Story Title ──
    col_title, col_spacer = st.columns([4, 1])
    with col_title:
        new_title = st.text_input(
            "Story Title",
            value=st.session_state.story_title,
            placeholder="Story Title…",
            label_visibility="collapsed",
            key="story_title_input",
        )
        if new_title != st.session_state.story_title:
            import re
            clean_title = re.sub(r'<[^>]*>', '', new_title).strip() or "Untitled Story"
            st.session_state.story_title = clean_title
            st.session_state.pop("story_title_input", None)

            story_id = st.session_state.get("active_story_id")
            if story_id and getattr(st.session_state, "logged_in", False):
                from core.storage import save_story, add_to_history
                from datetime import datetime
                username = getattr(st.session_state, "auth_username", "")
                if username:
                    full_content = "\n\n".join([st.session_state.chapters.get(c, "") for c in st.session_state.chapter_order])
                    now = datetime.now().strftime("%b %d, %H:%M")
                    save_story(username, story_id, {"title": clean_title, "content": full_content, "updated_at": now})
                    add_to_history(username, clean_title, story_id, now)
            st.session_state.story_metadata[st.session_state.active_chat]["title"] = clean_title
            st.rerun()

    # ── Chapter Navigation Bar ──
    chapters = _get_chapters()
    st.markdown('<div class="chapter-nav">', unsafe_allow_html=True)
    ch_cols = st.columns(len(chapters) + 1)
    for i, ch_name in enumerate(chapters):
        with ch_cols[i]:
            is_active_ch = ch_name == st.session_state.active_chapter
            btn_type = "primary" if is_active_ch else "secondary"
            if st.button(f"Ch{i+1}", key=f"ch_nav_{i}", help=ch_name, type=btn_type, use_container_width=True):
                st.session_state.active_chapter = ch_name
                st.rerun()
    with ch_cols[-1]:
        if st.button("＋ Chapter", key="add_chapter_btn", use_container_width=True):
            st.session_state.chapter_counter += 1
            new_ch = f"Chapter {st.session_state.chapter_counter}"
            st.session_state.chapters[new_ch] = ""
            st.session_state.chapter_order.append(new_ch)
            st.session_state.active_chapter = new_ch
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="chapter-label">✍ {st.session_state.active_chapter}</div>', unsafe_allow_html=True)

    # ── Main Story Editor ──
    ch = st.session_state.active_chapter
    if "editor_sync_key" not in st.session_state:
        st.session_state.editor_sync_key = 0
    widget_key = f"editor_{ch}_{st.session_state.editor_sync_key}"

    def _sync_editor():
        if widget_key in st.session_state:
            st.session_state.chapters[ch] = st.session_state[widget_key]
            if getattr(st.session_state, "logged_in", False):
                from core.storage import save_story, add_to_history
                from datetime import datetime
                username = getattr(st.session_state, "auth_username", "")
                story_title = st.session_state.story_title
                full_content = "\n\n".join([st.session_state.chapters.get(c, "") for c in st.session_state.chapter_order])
                story_id = st.session_state.get("active_story_id") or st.session_state.active_chat
                if username:
                    st.session_state.active_story_id = story_id
                    now = datetime.now().strftime("%b %d, %H:%M")
                    save_story(username, story_id, {"title": story_title, "content": full_content, "updated_at": now})
                    add_to_history(username, story_title, story_id, now)

    st.text_area(
        "Story Chapter Editor",
        value=st.session_state.chapters.get(ch, ""),
        height=420,
        placeholder="Begin your story here… write scenes, paragraphs, and let the narrative flow.",
        label_visibility="collapsed",
        key=widget_key,
        on_change=_sync_editor
    )

    updated_content = st.session_state.chapters.get(ch, "")
    words = len(updated_content.split()) if updated_content.strip() else 0
    reading_mins = max(1, round(words / 200))
    st.markdown(
        f'<div class="editor-stats">'
        f'<span>📝 {words} words</span>'
        f'<span>⏱ ~{reading_mins} min read</span>'
        f'<span>📖 {st.session_state.active_chapter}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Bottom Story Controls ──
    bc1, bc2, bc3, bc4 = st.columns(4)

    with bc1:
        try:
            pdf_bytes = create_pdf_bytes(st.session_state.story_title, st.session_state.chapter_order, st.session_state.chapters)
            st.download_button("📄 Export PDF", data=pdf_bytes,
                file_name=f"{st.session_state.story_title.replace(' ','_')}.pdf",
                mime="application/pdf", use_container_width=True)
        except Exception:
            st.button("📄 Export PDF", disabled=True, use_container_width=True, help="Error generating PDF")

    with bc2:
        try:
            docx_bytes = create_docx_bytes(st.session_state.story_title, st.session_state.chapter_order, st.session_state.chapters)
            st.download_button("📝 Export DOCX", data=docx_bytes,
                file_name=f"{st.session_state.story_title.replace(' ','_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True)
        except Exception:
            st.button("📝 Export DOCX", disabled=True, use_container_width=True, help="Error generating DOCX")

    with bc3:
        if st.button("✨ Format Story", key="format_story_btn", use_container_width=True):
            raw = _get_chapter_content()
            if raw.strip():
                with st.spinner("Formatting…"):
                    formatted = call_ollama(
                        [{"role": "user", "content": raw}],
                        "Format and polish this story passage. Fix punctuation, paragraph breaks, and improve prose flow. Return only the improved text."
                    )
                if not formatted.startswith("⚠️"):
                    st.session_state.chapters[ch] = formatted
                    st.session_state.editor_sync_key += 1
                    st.rerun()

    with bc4:
        if st.button("🗑 Clear Chat", key="clear_chat_btn", use_container_width=True, type="primary"):
            st.session_state.chats[st.session_state.active_chat] = []
            st.session_state.last_ai_suggestion = ""
            st.rerun()


def _build_full_story() -> str:
    lines = [f"# {st.session_state.story_title}\n"]
    for ch in st.session_state.chapter_order:
        content = st.session_state.chapters.get(ch, "")
        if content.strip():
            lines.append(f"\n## {ch}\n\n{content}")
    return "\n".join(lines) if len(lines) > 1 else "No story content yet."


# ─────────────────────────────────────────────
#  SPLIT EDITOR  (from split_editor.py)
# ─────────────────────────────────────────────

def render_split_editor():
    st.markdown("#### ✏️ Split Editor — Write & Refine Side by Side")

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown('<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:.1em;'
                    'color:var(--muted);margin-bottom:4px;">📝 YOUR DRAFT</div>', unsafe_allow_html=True)
        draft = st.text_area(
            "draft",
            value=st.session_state.split_draft,
            height=400,
            placeholder="Write or paste your draft here…",
            label_visibility="collapsed",
            key="draft_area",
        )
        st.session_state.split_draft = draft

        split_action = st.selectbox("AI Action", [
            "Improve prose style",
            "Add vivid sensory detail",
            "Tighten and remove filler",
            "Rewrite in current tone & style",
            "Punch up the dialogue",
            "Fix pacing issues",
            "Suggest a natural continuation",
            "Convert to different perspective",
        ], key="split_act")

        run_ai = st.button("⚡ Run AI on Draft", use_container_width=True)

    with right_col:
        st.markdown('<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:.1em;'
                    'color:var(--muted);margin-bottom:4px;">🤖 AI SUGGESTIONS</div>', unsafe_allow_html=True)

        if run_ai and draft.strip():
            h = [{"role": "user", "content": f"{split_action}:\n\n{draft}"}]
            with st.spinner(f"Running: {split_action}…"):
                suggestion = call_ollama(h, split_action)
            st.session_state["last_suggestion"] = suggestion

        sugg = st.session_state.get("last_suggestion", "")
        if sugg:
            st.markdown(f"""
            <div class="editor-panel">
                {sugg.replace(chr(10),"<br>")}
            </div>
            """, unsafe_allow_html=True)
            st.download_button("⬇ Download AI Version", data=sugg, file_name="ai_suggestion.txt", mime="text/plain")
            if st.button("➕ Send AI version to Chat"):
                add_message("assistant", sugg)
                st.success("Added to story chat!")
        else:
            st.markdown("""
            <div class="editor-panel" style="display:flex;align-items:center;justify-content:center;min-height:380px;">
                <div style='text-align:center;color:var(--muted);'>
                    <div style='font-size:1.8rem;margin-bottom:6px;'>🪄</div>
                    <div>AI suggestions appear here</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
