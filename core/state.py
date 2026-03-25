# core/state.py — Session state initialization
import streamlit as st


def init_state():
    """Initialize all Streamlit session state defaults (idempotent).
    On first load, checks for a previously active user and restores their session."""
    import uuid
    default_id = str(uuid.uuid4())
    defaults = {
        # ── Chat ──
        "chats":        {default_id: []},
        "active_chat":  default_id,
        "active_story_id": default_id,
        "chat_counter": 1,

        # ── Ollama Model Settings ──
        "model":        "llama3:latest",
        "temperature":  0.7,
        "length_mode":  "Medium",

        # ── User Profile ──
        "user_profile": {
            "username":    "Guest User",
            "password":    "password",
            "bio":         "I love creating amazing stories.",
            "profile_pic": None,
        },
        "current_page": "💬 Story Chat",

        # ── Story Customization ──
        "genre":         "Fantasy",
        "tone":          "Dramatic",
        "writing_style": "Descriptive",

        # ── Character & World ──
        "story_context": {
            "title":             "",
            "char_name":         "",
            "char_personality":  ["Brave"],
            "perspective":       "Third person",
            "setting":           "",
        },

        # ── Chat Behavior ──
        "response_mode": "Detailed narration",
        "memory_mode":   "Session only",
        "auto_continue": False,

        # ── UI Preferences ──
        "ui_theme":    "Dark",
        "font_size":   15,
        "bubble_style":"Glass style",

        # ── Tools ──
        "split_draft":   "",
        "outline":       [],
        "chapter_count": 1,

        # ── Future Hooks ──
        "voice_input_enabled": False,
        "tts_enabled":         False,

        # ── Right Sidebar ──
        "right_sidebar_open": False,

        # ── Auth ──
        "logged_in":       False,
        "auth_user_id":    None,
        "auth_username":   "",
        "auth_bio":        "",
        "auth_pic":        None,
        "_profile_synced": False,

        # ── Chapter-based Story Editor ──
        "story_title":       "New Story",
        "chapters":          {"Chapter 1": ""},   # chapter_name -> content
        "active_chapter":    "Chapter 1",
        "chapter_order":     ["Chapter 1"],       # ordered list
        "chapter_counter":   1,

        # ── Story Search & Tags ──
        "search_story":      "",
        "story_tags":        {},                  # story_name -> list of tags

        # ── AI Suggestion (latest) ──
        "last_ai_suggestion": "",
        # ── Story Metadata (Title, Pinned) ──
        "story_metadata":    {default_id: {"title": "New Story", "pinned": False, "db_id": default_id}},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Ensure all existing chats have metadata
    if "story_metadata" not in st.session_state:
        st.session_state.story_metadata = {}
    for chat_name in st.session_state.chats:
        if chat_name not in st.session_state.story_metadata:
            st.session_state.story_metadata[chat_name] = {"title": "New Story", "pinned": False, "db_id": chat_name}

    # ── RESTORE PERSISTED SESSION ──
    # Only attempt restore once per Streamlit session
    if "_session_restored" not in st.session_state:
        st.session_state._session_restored = True
        try:
            from core.storage import load_active_user, load_session
            active_user = load_active_user()
            if active_user:
                saved = load_session(active_user)
                if saved and saved.get("logged_in"):
                    for key, val in saved.items():
                        st.session_state[key] = val
                    # Ensure profile_pic placeholder exists
                    if "user_profile" in saved and isinstance(saved["user_profile"], dict):
                        st.session_state.user_profile.setdefault("profile_pic", None)
        except Exception:
            pass  # If persistence fails, fall back to fresh state


def _load_stories_and_chats_from_db(username: str):
    from core.storage import get_user_stories, get_user_chats
    import datetime

    stories = get_user_stories(username)
    chats = get_user_chats(username)
    
    if stories:
        new_chats = {}
        new_metadata = {}
        
        # Load stories
        for story_id, story_data in stories.items():
            name = str(story_id)
            flat_chats = []
            
            # Load chats for this story
            story_chats = chats.get(str(story_id), [])
            for c in story_chats:
                flat_chats.append({
                    "role": c.get("role", ""),
                    "content": c.get("content", ""),
                    "ts": c.get("timestamp", "")
                })
            
            new_chats[name] = flat_chats
            last_up = story_data.get("updated_at", "")
            
            pinned = st.session_state.get("story_metadata", {}).get(name, {}).get("pinned", False)
            new_metadata[name] = {
                "title":        story_data.get("title", "New Story"),
                "pinned":       pinned,
                "db_id":        story_id,
                "last_updated": last_up,
            }
            
        st.session_state.chats = new_chats
        st.session_state.story_metadata = new_metadata
        
        active_chat = st.session_state.get("active_chat", "")
        if active_chat not in new_chats:
            active_chat = list(new_chats.keys())[-1] if new_chats else list(st.session_state.chats.keys())[0]
            
        st.session_state.active_chat = active_chat
        
        # Load active story content
        active_story_id = active_chat
        active_story_data = stories.get(active_story_id, {})
        
        st.session_state.story_title = active_story_data.get("title", "New Story")
        st.session_state.chapters = {"Chapter 1": active_story_data.get("content", "")}
        st.session_state.chapter_order = ["Chapter 1"]
        st.session_state.active_chapter = "Chapter 1"
        st.session_state.active_story_id = active_story_id
        st.session_state.chat_counter = max(
            st.session_state.get("chat_counter", 0), len(stories) + 1
        )

def sync_profile_after_login():
    """Copy auth data into user_profile on the first run after login, and load stories+chats from DB."""
    if not getattr(st.session_state, "_profile_synced", False):
        st.session_state.user_profile["username"]    = st.session_state.auth_username
        st.session_state.user_profile["bio"]         = st.session_state.auth_bio or "I love creating amazing stories."
        st.session_state.user_profile["profile_pic"] = st.session_state.auth_pic
        
        username = getattr(st.session_state, "auth_username", "")
        if username and getattr(st.session_state, "logged_in", False):
            _load_stories_and_chats_from_db(username)
        
        st.session_state._profile_synced = True
