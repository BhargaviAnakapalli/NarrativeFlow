"""
login.py — Auth module for NarrativeFlow
Import in app.py — do NOT call st.set_page_config here.
"""
import streamlit as st
import re

def validate_password(password: str):
    """Returns an error string, or None if valid."""
    if len(password) < 8:
        return "⚠️ Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "⚠️ Must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "⚠️ Must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "⚠️ Must contain at least one number."
    if not re.search(r"[!@#$%^&+=]", password):
        return "⚠️ Must contain a special character (!@#$%^&+=)."
    return None


# ─────────────────────────────────────────────
#  MAIN LOGIN PAGE
# ─────────────────────────────────────────────
def show_login_page():
    """
    Renders the login/register UI (called from app.py before the main UI).
    On success sets:
        st.session_state.logged_in       = True
        st.session_state.auth_username   = <username>
        st.session_state.auth_bio        = <bio>
        st.session_state.auth_pic        = None (or bytes)
    then calls st.rerun().
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background: #0c1222 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    [data-testid="stHeader"]  { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .block-container {
        max-width: 480px !important;
        padding-top: 5vh !important;
    }
    .auth-logo {
        text-align: center;
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.8rem;
        font-weight: 300;
        color: #c9a96e;
        letter-spacing: 0.04em;
        margin-bottom: 0.25rem;
    }
    .auth-logo span { color: #fff; }
    .auth-sub {
        text-align: center;
        color: #6b7280;
        font-size: 0.82rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }
    [data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e5e7eb !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #c9a96e !important;
        box-shadow: 0 0 0 2px rgba(201,169,110,0.2) !important;
    }
    [data-testid="stTextInput"] label { color: #9ca3af !important; font-size: 0.85rem !important; }
    .stButton > button {
        background: linear-gradient(135deg, #c9a96e, #b8860b) !important;
        border: none !important;
        color: #0c1222 !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
    }
    .stTabs [data-baseweb="tab"]   { color: #9ca3af !important; border-radius: 8px !important; }
    .stTabs [aria-selected="true"] { background: rgba(201,169,110,0.18) !important; color: #c9a96e !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-logo">Narrative<span>Flow</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">AI Story Co-Writer ✨</div>', unsafe_allow_html=True)

    tab_login, tab_reg = st.tabs(["Login", "Register"])

    with tab_login:
        st.markdown("#### Welcome back")
        login_user = st.text_input("Username", key="login_user", placeholder="your username")
        login_pass = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")

        if st.button("Login →", key="btn_login", use_container_width=True):
            if not login_user or not login_pass:
                st.warning("⚠️ Please fill in all fields.")
            else:
                import hashlib
                from core.storage import get_user, save_user
                
                user = get_user(login_user)
                if not user:
                    st.error("⚠️ Username not found.")
                else:
                    hashed_input = hashlib.sha256(login_pass.encode()).hexdigest()
                    if user.get("password") != hashed_input:
                        st.error("⚠️ Incorrect password.")
                    else:
                        st.session_state.logged_in     = True
                        st.session_state.auth_user_id  = login_user
                        st.session_state.auth_username = login_user
                        st.session_state.auth_bio      = user.get("bio", "")
                        st.session_state.auth_pic      = None
                        st.success("Login successful! Loading your workspace…")
                        st.rerun()

    with tab_reg:
        st.markdown("#### Create your account")
        reg_user    = st.text_input("Choose Username", key="reg_user",    placeholder="e.g. storyteller42")
        reg_pass    = st.text_input("Choose Password", type="password", key="reg_pass",    placeholder="min 8 chars")
        reg_confirm = st.text_input("Confirm Password",type="password", key="reg_confirm", placeholder="repeat password")
        st.caption("Password: 8+ chars · uppercase · lowercase · number · special char")

        if st.button("Create Account →", key="btn_register", use_container_width=True):
            if not reg_user or not reg_pass:
                st.warning("⚠️ Fields cannot be empty.")
            elif reg_pass != reg_confirm:
                st.error("⚠️ Passwords do not match.")
            else:
                err = validate_password(reg_pass)
                if err:
                    st.error(err)
                else:
                    import hashlib
                    from core.storage import get_user, save_user
                    
                    if get_user(reg_user):
                        st.error("⚠️ Username already taken.")
                    else:
                        hashed_pass = hashlib.sha256(reg_pass.encode()).hexdigest()
                        save_user(reg_user, {"username": reg_user, "password": hashed_pass, "bio": "I love creating amazing stories."})
                        st.success("Account created! You can now login.")
