# core/engine.py — Ollama API, prompt building, and chat helpers
# Merged from: core/ollama.py + core/prompts.py + core/chat_utils.py

import requests
import streamlit as st
from datetime import datetime

from config.config import OLLAMA_URL, OLLAMA_TAGS, MODELS, LENGTH_MAP


# ─────────────────────────────────────────────
#  OLLAMA HELPERS  (from ollama.py)
# ─────────────────────────────────────────────

def check_ollama() -> tuple[bool, list[str]]:
    """Returns (running: bool, available_model_names: list)."""
    try:
        r = requests.get(OLLAMA_TAGS, timeout=2)
        if r.ok:
            tags = [m["name"].split(":")[0] for m in r.json().get("models", [])]
            return True, tags
    except Exception:
        pass
    return False, []


def call_ollama(messages: list[dict], extra_instruction: str = "") -> str:
    """
    Call Ollama /api/generate with the current model + settings.
    messages = [{"role": "user"|"assistant", "content": str}]
    """
    system = build_system_prompt()
    if extra_instruction:
        system += f"\n\nSPECIAL TASK FOR THIS RESPONSE: {extra_instruction}"

    convo = ""
    for m in messages:
        role_label = "User" if m["role"] == "user" else "NarrativeFlow"
        convo += f"\n{role_label}: {m['content']}"
    convo += "\nNarrativeFlow:"

    full_prompt = f"<system>\n{system}\n</system>\n{convo}"

    payload = {
        "model":  st.session_state.model,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": st.session_state.temperature,
            "num_predict": LENGTH_MAP.get(st.session_state.length_mode, 500),
        },
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        err_text = e.response.text
        return f"⚠️ Ollama {status} Error: {err_text}"
    except requests.exceptions.ConnectionError:
        return "⚠️ Cannot connect to Ollama. Make sure `ollama serve` is running."
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. Try a shorter response length or a faster model."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Network Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ─────────────────────────────────────────────
#  PROMPT BUILDING  (from prompts.py)
# ─────────────────────────────────────────────

def build_system_prompt() -> str:
    """Builds the system prompt based on user settings in session state."""
    genre = st.session_state.get("genre", "Fantasy")
    tone = st.session_state.get("tone", "Dramatic")
    style = st.session_state.get("writing_style", "Descriptive")

    context = st.session_state.get("story_context", {})
    char_name = context.get("char_name", "")
    char_traits = ", ".join(context.get("char_personality", []))
    setting = context.get("setting", "")
    perspective = context.get("perspective", "Third person")
    response_mode = st.session_state.get("response_mode", "Detailed narration")

    prompt = "You are NarrativeFlow, an expert AI Story Co-Writer.\n\n"
    prompt += "Writing Guidelines:\n"
    prompt += f"- Genre: {genre}\n"
    prompt += f"- Tone: {tone}\n"
    prompt += f"- Style: {style}\n"
    prompt += f"- Perspective: {perspective}\n"
    prompt += f"- Pacing/Detail: {response_mode}\n\n"

    if char_name:
        prompt += f"Protagonist: {char_name}\n"
    if char_traits:
        prompt += f"Traits: {char_traits}\n"
    if setting:
        prompt += f"Setting: {setting}\n"

    prompt += "\n"
    prompt += "MANDATORY RULES & GUARDRAILS:\n"
    prompt += "1. ROLE: You are an Interactive Story Co-Writer. You exist ONLY to help create, develop, edit, or continue stories (e.g., plot, characters, dialogue, chapters, world-building).\n"
    prompt += "2. REJECT NON-STORY TOPICS: If the user asks about ANYTHING unrelated to storytelling (e.g., coding help, math, general knowledge, real-world current events), you MUST refuse politely by stating: \"I am designed only for interactive story writing and story development. Please provide a story prompt or idea to continue.\"\n"
    prompt += "3. GREETINGS: If the user simply says 'hi', 'hello', 'hey', or a similar greeting, you MUST reply exactly with: \"Hello! I'm your NarrativeFlow story co-writer. What story would you like to create today? You can start with a genre, character, or plot idea.\"\n"
    prompt += "4. NATIVE RESPONSE: Respond natively in the story when continuing the plot. Do not break character unless asked for feedback.\n"

    return prompt


# ─────────────────────────────────────────────
#  CHAT UTILITIES  (from chat_utils.py)
# ─────────────────────────────────────────────

def get_history() -> list[dict]:
    return st.session_state.chats.get(st.session_state.active_chat, [])


def add_message(role: str, content: str):
    chat = st.session_state.chats.setdefault(st.session_state.active_chat, [])
    ts = datetime.now().strftime("%H:%M")
    chat.append({"role": role, "content": content, "ts": ts})

    # Auto-save to JSON DB
    try:
        if st.session_state.get("logged_in") and st.session_state.get("auth_username"):
            username = st.session_state.auth_username
            story_id = st.session_state.get("active_story_id", st.session_state.active_chat)
            from core.storage import add_chat_message
            add_chat_message(username, story_id, role, content, ts)
    except Exception:
        pass

    # Auto-save active session backup
    try:
        from core.storage import save_session
        if st.session_state.get("auth_username"):
            save_session(st.session_state.auth_username)
    except Exception:
        pass


def all_ai_text() -> str:
    return "\n\n".join(
        m["content"] for m in get_history() if m["role"] == "assistant"
    )


def word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def reading_time(wc: int) -> int:
    return max(1, round(wc / 200))


def get_flat_history() -> list[dict]:
    return [{"role": m["role"], "content": m["content"]} for m in get_history()]
