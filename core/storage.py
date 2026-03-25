# core/storage.py — All persistence: JSON DB + session save/load
# Merged from: core/persistence.py + database/json_db.py

import json
import os

# ─────────────────────────────────────────────
#  PATH SETUP
# ─────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(__file__))

# JSON data files live in data/
DATA_DIR     = os.path.join(_ROOT, "data")
USERS_FILE   = os.path.join(DATA_DIR, "users.json")
CHATS_FILE   = os.path.join(DATA_DIR, "chats.json")
STORIES_FILE = os.path.join(DATA_DIR, "stories.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

# Session files stay in sessions/
SESSION_DIR  = os.path.join(_ROOT, "sessions")
ACTIVE_FILE  = os.path.join(SESSION_DIR, "_active.txt")

# Keys we persist per user
_PERSIST_KEYS = [
    "logged_in", "auth_user_id", "auth_username", "auth_bio", "auth_pic",
    "_profile_synced", "user_profile",
    "chats", "active_chat", "active_story_id", "chat_counter", "current_page",
    "story_metadata", "story_title", "chapters", "chapter_order", "active_chapter",
    "model", "temperature", "length_mode",
    "genre", "tone", "writing_style",
    "story_context", "response_mode", "memory_mode", "auto_continue",
    "ui_theme", "font_size", "bubble_style",
    "split_draft", "outline", "chapter_count",
    "right_sidebar_open",
]

# In-memory cache to optimize performance and prevent UI freezing
_DB_CACHE = {}


# ─────────────────────────────────────────────
#  LOW-LEVEL JSON I/O  (from json_db.py)
# ─────────────────────────────────────────────

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    for file_path in [USERS_FILE, CHATS_FILE, STORIES_FILE, HISTORY_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)


def read_json(file_path):
    if file_path in _DB_CACHE:
        return _DB_CACHE[file_path]
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            _DB_CACHE[file_path] = data
            return data
    except Exception:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            import shutil
            shutil.copy2(file_path, file_path + ".bak")
        return {}


def write_json(file_path, data):
    _DB_CACHE[file_path] = data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ─────────────────────────────────────────────
#  USER CRUD
# ─────────────────────────────────────────────

def get_user(username):
    return read_json(USERS_FILE).get(username)


def save_user(username, user_data):
    users = read_json(USERS_FILE)
    users[username] = user_data
    write_json(USERS_FILE, users)


# ─────────────────────────────────────────────
#  CHAT CRUD
# ─────────────────────────────────────────────

def get_user_chats(username):
    return read_json(CHATS_FILE).get(username, {})


def save_user_chats(username, chat_data):
    chats = read_json(CHATS_FILE)
    chats[username] = chat_data
    write_json(CHATS_FILE, chats)


def add_chat_message(username, story_id, role, content, timestamp):
    chats = read_json(CHATS_FILE)
    user_chats = chats.get(username, {})
    story_chats = user_chats.get(str(story_id), [])
    story_chats.append({"role": role, "content": content, "timestamp": timestamp})
    user_chats[str(story_id)] = story_chats
    chats[username] = user_chats
    write_json(CHATS_FILE, chats)


# ─────────────────────────────────────────────
#  STORY CRUD
# ─────────────────────────────────────────────

def get_user_stories(username):
    return read_json(STORIES_FILE).get(username, {})


def get_story(username, story_id):
    return get_user_stories(username).get(str(story_id))


def save_story(username, story_id, story_data):
    stories = read_json(STORIES_FILE)
    user_stories = stories.get(username, {})
    user_stories[str(story_id)] = story_data
    stories[username] = user_stories
    write_json(STORIES_FILE, stories)


# ─────────────────────────────────────────────
#  HISTORY CRUD
# ─────────────────────────────────────────────

def get_user_history(username):
    return read_json(HISTORY_FILE).get(username, [])


def add_to_history(username, story_name, story_id, created_at):
    history = read_json(HISTORY_FILE)
    user_history = history.get(username, [])
    exists = False
    for item in user_history:
        if item.get("story_id") == str(story_id):
            item["story_name"] = story_name
            item["created_at"] = created_at
            exists = True
            break
    if not exists:
        user_history.append({"story_id": str(story_id), "story_name": story_name, "created_at": created_at})
    history[username] = user_history
    write_json(HISTORY_FILE, history)


def delete_story_cascade(username, story_id):
    story_id_str = str(story_id)
    chats = read_json(CHATS_FILE)
    if username in chats and story_id_str in chats[username]:
        del chats[username][story_id_str]
        write_json(CHATS_FILE, chats)
    stories = read_json(STORIES_FILE)
    if username in stories and story_id_str in stories[username]:
        del stories[username][story_id_str]
        write_json(STORIES_FILE, stories)
    history = read_json(HISTORY_FILE)
    if username in history:
        history[username] = [i for i in history[username] if i.get("story_id") != story_id_str]
        write_json(HISTORY_FILE, history)


# ─────────────────────────────────────────────
#  SESSION PERSISTENCE  (from persistence.py)
# ─────────────────────────────────────────────

def _ensure_session_dir():
    os.makedirs(SESSION_DIR, exist_ok=True)


def save_session(username: str):
    """Save the current session state to a JSON file for the given user."""
    import streamlit as st
    _ensure_session_dir()
    data = {}
    for key in _PERSIST_KEYS:
        val = st.session_state.get(key)
        if key == "auth_pic" and val is not None:
            continue
        if key == "user_profile" and isinstance(val, dict):
            val = {k: v for k, v in val.items() if k != "profile_pic"}
        data[key] = val
    path = os.path.join(SESSION_DIR, f"{username}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_session(username: str) -> dict | None:
    """Load a previously saved session for the given user. Returns None if not found."""
    path = os.path.join(SESSION_DIR, f"{username}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "user_profile" in data and isinstance(data["user_profile"], dict):
            data["user_profile"].setdefault("profile_pic", None)
        return data
    except (json.JSONDecodeError, IOError):
        return None


def save_active_user(username: str):
    """Remember who is currently logged in (survives page refresh)."""
    _ensure_session_dir()
    with open(ACTIVE_FILE, "w", encoding="utf-8") as f:
        f.write(username)


def load_active_user() -> str | None:
    """Return the last logged-in username, or None."""
    if not os.path.exists(ACTIVE_FILE):
        return None
    try:
        with open(ACTIVE_FILE, "r", encoding="utf-8") as f:
            name = f.read().strip()
        return name if name else None
    except IOError:
        return None


def clear_active_user():
    """Clear the active-user token (called on logout)."""
    if os.path.exists(ACTIVE_FILE):
        os.remove(ACTIVE_FILE)
