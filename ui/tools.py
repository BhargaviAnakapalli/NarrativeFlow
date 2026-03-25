# ui/tools.py — Writer Tools and World Builder tabs
# Merged from: ui/writer_tools.py + ui/world_builder.py

import streamlit as st

from core.engine import (
    call_ollama, add_message, get_flat_history,
    get_history, all_ai_text, word_count, reading_time,
    build_system_prompt,
)
from config.config import PERSONALITIES


def render_writer_tools():
    st.markdown("#### 🔧 Writer Tools")

    ai_text = all_ai_text()
    wc      = word_count(ai_text)
    rt      = reading_time(wc)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Words",  wc)
    m2.metric("Reading Time", f"~{rt} min")
    m3.metric("AI Passages",  sum(1 for m in get_history() if m["role"] == "assistant"))

    st.divider()

    st.markdown("#### 📚 Chapter Builder")
    chap_num     = st.number_input("Chapter #", 1, 50, st.session_state.chapter_count)
    chap_title   = st.text_input("Chapter Title (optional):")
    chap_premise = st.text_area("What happens in this chapter?", height=90)
    if st.button("✍ Write Chapter", use_container_width=True) and chap_premise:
        title_part = f" — {chap_title}" if chap_title else ""
        prompt = f"Write Chapter {chap_num}{title_part}. Events: {chap_premise}"
        prev = ai_text[-400:] if ai_text else ""
        if prev:
            prompt += f"\n[Story so far ends with: …{prev}]"
        add_message("user", prompt)
        h = get_flat_history()
        old_len = st.session_state.length_mode
        st.session_state.length_mode = "Chapter Mode"
        with st.spinner(f"Writing Chapter {chap_num}…"):
            reply = call_ollama(h)
        st.session_state.length_mode = old_len
        add_message("assistant", reply)
        st.session_state.chapter_count = chap_num + 1
        st.success(f"Chapter {chap_num} written! Check Story Chat.")

    st.divider()

    st.markdown("#### 🔄 Paragraph Rewriter")
    para  = st.text_area("Paste paragraph to rewrite:", height=100)
    instr = st.text_input("How to rewrite it:", placeholder="e.g., make it more poetic…")
    if st.button("🔄 Rewrite") and para and instr:
        with st.spinner("Rewriting…"):
            rewritten = call_ollama([{"role": "user", "content": f"Rewrite this paragraph — {instr}:\n\n{para}"}], instr)
        st.markdown(f'<div class="editor-panel" style="min-height:auto;">{rewritten.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Save rewritten paragraph", data=rewritten, file_name="rewrite.txt", mime="text/plain")

    st.divider()

    st.markdown("#### 📤 Export")
    if ai_text:
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button("📄 Export Story (.txt)", data=ai_text,
                file_name=f"{st.session_state.active_chat.replace(' ','_')}_story.txt",
                mime="text/plain", use_container_width=True)
        with dl2:
            full = "\n\n".join(f"[{m['role'].upper()}] {m['ts']}\n{m['content']}" for m in get_history())
            st.download_button("📋 Export Full Session (.txt)", data=full,
                file_name=f"{st.session_state.active_chat.replace(' ','_')}_session.txt",
                mime="text/plain", use_container_width=True)
        st.markdown("**Preview (copy manually):**")
        st.code(ai_text[:1000] + ("…" if len(ai_text) > 1000 else ""), language=None)
    else:
        st.info("No story generated yet. Start in Story Chat.")

    st.divider()

    st.markdown("#### 🔮 Future Feature Stubs")
    with st.expander("Architecture Placeholders"):
        st.markdown("**Voice Input** → `streamlit-webrtc` + `whisper`\n**TTS** → `pyttsx3`\n**PDF** → `fpdf2`")


def render_world_builder():
    st.markdown("#### 🗺 World & Character Builder")
    st.caption("Everything here is injected into every llama3 generation call.")

    ctx = st.session_state.story_context

    col_a, col_b = st.columns(2)
    with col_a:
        ctx["title"]     = st.text_input("Story Title", value=ctx.get("title",""), placeholder="Leave blank for untitled")
        ctx["char_name"] = st.text_input("Main Character Name", value=ctx.get("char_name",""), placeholder="e.g., Elara Voss")
        ctx["perspective"] = st.selectbox(
            "Story Perspective",
            ["Third person","First person","Second person (experimental)"],
            index=["Third person","First person","Second person (experimental)"].index(ctx.get("perspective","Third person")),
        )
    with col_b:
        ctx["setting"] = st.text_area("World / Setting Description", value=ctx.get("setting",""), height=110,
            placeholder="Describe the world, era, location, atmosphere…")
        ctx["char_personality"] = st.multiselect("Character Personality", PERSONALITIES,
            default=ctx.get("char_personality",["Brave"]))

    st.session_state.story_context = ctx

    if st.button("✅ Save World Context", use_container_width=True):
        st.success("Context saved! All future llama3 calls will use this world.")

    with st.expander("👁 Preview: What llama3 receives as system prompt"):
        st.code(build_system_prompt(), language=None)

    st.divider()

    st.markdown("#### 🧬 AI Character Generator")
    char_concept = st.text_input("Describe a character concept:", placeholder="e.g., a weary detective haunted by one case")
    if st.button("🧬 Generate Character Profile") and char_concept:
        prompt = (f"Generate a detailed character profile for: {char_concept}\n\n"
                  "Format as: NAME / AGE / APPEARANCE / PERSONALITY / BACKSTORY / GOAL / FATAL FLAW / FIRST LINE OF DIALOGUE")
        with st.spinner("Generating character…"):
            profile = call_ollama([{"role": "user", "content": prompt}], "Create a rich, vivid character profile.")
        st.markdown(f'<div class="editor-panel" style="min-height:auto;margin-top:0.75rem;">{profile.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Save Character", data=profile, file_name="character.txt", mime="text/plain")

    st.divider()

    st.markdown("#### 📋 Outline Builder")
    new_beat = st.text_input("Add a story beat:", placeholder="e.g., Hero discovers the map is a lie")
    if st.button("Add Beat") and new_beat:
        st.session_state.outline.append(new_beat)
        st.rerun()

    if st.session_state.outline:
        for j, beat in enumerate(st.session_state.outline):
            bca, bcb, bcc = st.columns([6,1,1])
            with bca:
                st.markdown(f"**{j+1}.** {beat}")
            with bcb:
                if st.button("✍", key=f"wb_{j}", help="Write this beat"):
                    add_message("user", f"Write a scene for: {beat}")
                    with st.spinner("Writing scene…"):
                        reply = call_ollama(get_flat_history())
                    add_message("assistant", reply)
            with bcc:
                if st.button("🗑", key=f"db_{j}"):
                    st.session_state.outline.pop(j)
                    st.rerun()

        if st.button("🚀 Generate Full Story from Outline"):
            outline_str = "\n".join(f"{i+1}. {b}" for i,b in enumerate(st.session_state.outline))
            add_message("user", f"Write a complete story following this outline:\n{outline_str}")
            old_len = st.session_state.length_mode
            st.session_state.length_mode = "Chapter Mode"
            with st.spinner("Generating full story from outline…"):
                reply = call_ollama(get_flat_history())
            st.session_state.length_mode = old_len
            add_message("assistant", reply)
            st.success("Story generated! Switch to Story Chat to read it.")
