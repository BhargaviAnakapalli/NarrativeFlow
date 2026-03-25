# ui/styles.py — Theme injection into Streamlit app (renamed from ui/css.py)
import streamlit as st
from config.config import THEMES


def inject_theme():
    """Inject CSS variables and all custom styles based on current session state."""
    t  = THEMES.get(st.session_state.ui_theme, THEMES["Dark"])
    fs = st.session_state.font_size
    bs = st.session_state.bubble_style

    radius_map = {"Rounded": "18px", "Minimal": "4px", "Glass style": "14px"}
    bubble_radius = radius_map.get(bs, "14px")

    glass_ai   = "backdrop-filter: blur(10px);" if bs == "Glass style" else ""
    glass_user = "backdrop-filter: blur(10px);" if bs == "Glass style" else ""

    css_vars = "\n".join(f"    {k}: {v};" for k, v in t.items())

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap');

:root {{
{css_vars}
    --radius: {bubble_radius};
    --font-size: {fs}px;
}}

html, body, [data-testid="stAppViewContainer"] {{
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: var(--font-size) !important;
}}
[data-testid="stHeader"] {{ background: transparent !important; height: 0 !important; }}

[data-testid="stAppViewBlockContainer"] {{ padding-top: 0.5rem !important; }}
.block-container {{ padding-top: 0.5rem !important; max-width: 100% !important; }}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stTextInput > div > div {{
    background: var(--bg3) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    font-size: 0.85rem !important;
}}

/* MAIN AREA STARFIELD */
[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(1px 1px at 15% 25%, rgba(255,255,255,0.12) 0%, transparent 100%),
        radial-gradient(1px 1px at 75% 15%, rgba(255,255,255,0.08) 0%, transparent 100%),
        radial-gradient(600px 400px at 80% 10%, rgba(201,169,110,0.03) 0%, transparent 100%),
        radial-gradient(700px 500px at 10% 90%, rgba(78,138,195,0.03) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
}}

.hero-compact {{
    text-align: center;
    padding: 0.4rem 0 0.8rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
    position: relative;
}}
.hero-compact::after {{
    content: '';
    position: absolute;
    bottom: -1px; left: 30%; width: 40%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}}
.hero-compact h1 {{
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 2rem !important;
    font-weight: 300 !important;
    letter-spacing: 0.04em;
    color: var(--text) !important;
    margin: 0 0 0.2rem !important;
}}
.hero-compact h1 span {{ color: var(--accent); }}
.hero-compact p {{
    color: var(--text) !important;
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 !important;
}}

.model-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0 auto;
    color: var(--accent);
}}

[data-testid="stButton"] > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button {{
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stButton"] > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover {{
    background: var(--accent-dim) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(201, 169, 110, 0.15) !important;
}}

hr {{
    border-bottom: 1px solid var(--accent) !important;
    margin: 1.5rem 0 !important;
    opacity: 0.6 !important;
}}

[data-testid="stExpander"] summary svg,
[data-baseweb="select"] div svg,
.stSelectbox svg {{
    fill: var(--accent) !important;
    color: var(--accent) !important;
}}
[data-testid="stWidgetLabel"] p {{
    color: var(--accent) !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
}}

*:focus {{ outline: none !important; }}
div[role="combobox"]:focus-within {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}}

.chapter-nav {{
    display: flex;
    gap: 6px;
    align-items: center;
    padding: 0.4rem 0;
    margin-bottom: 0.3rem;
    border-bottom: 1px solid var(--border);
}}
.chapter-label {{
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    padding: 0.25rem 0;
    margin-bottom: 0.5rem;
}}

[data-testid="stTextArea"] textarea {{
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.4rem !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: calc(var(--font-size) + 2px) !important;
    line-height: 1.85 !important;
    color: var(--text) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    resize: vertical !important;
}}
[data-testid="stTextArea"] textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 12px rgba(201,169,110,0.12) !important;
}}
[data-testid="stTextArea"] textarea::placeholder {{
    color: var(--muted) !important;
    opacity: 0.6 !important;
    font-style: italic !important;
}}

.editor-stats {{
    display: flex;
    gap: 1.5rem;
    padding: 0.4rem 0.2rem;
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.03em;
}}
.editor-stats span {{ display: flex; align-items: center; gap: 4px; }}

.tags-container {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 0.5rem;
}}
.story-tag {{
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    color: var(--accent);
    letter-spacing: 0.04em;
}}

.ai-panel-header {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 0 0.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.5rem;
}}
.ai-panel-icon {{ font-size: 1.3rem; }}
.ai-panel-title {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.3rem;
    font-weight: 400;
    color: var(--accent);
    letter-spacing: 0.04em;
}}
.ai-status {{
    font-size: 0.72rem;
    color: var(--muted);
    margin-bottom: 0.75rem;
    letter-spacing: 0.04em;
}}
.ai-empty-state {{
    text-align: center;
    color: var(--muted);
    font-size: 0.83rem;
    padding: 3rem 1rem;
    line-height: 1.6;
}}

.ai-msg-user {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    margin-bottom: 0.75rem;
    animation: fadeIn 0.3s ease both;
}}
.ai-msg-ai {{
    display: flex;
    gap: 8px;
    align-items: flex-start;
    margin-bottom: 0.75rem;
    animation: fadeIn 0.3s ease both;
}}
.ai-avatar {{
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; flex-shrink: 0;
    background: var(--bg3);
    border: 1px solid var(--accent);
}}
.ai-msg-bubble {{
    max-width: 88%;
    padding: 0.6rem 0.9rem;
    border-radius: var(--radius);
    font-size: var(--font-size);
    line-height: 1.65;
}}
.ai-msg-bubble.user {{
    background: var(--user-bg);
    border: 1px solid var(--user-bdr);
    text-align: right;
    {glass_user}
}}

.ai-suggestion-card {{
    background: var(--ai-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: calc(var(--font-size) + 1px);
    line-height: 1.7;
    color: var(--text);
    {glass_ai}
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    margin-bottom: 0.3rem;
    word-break: break-word;
}}
.ai-msg-meta {{
    font-size: 0.65rem;
    color: var(--muted);
    margin-top: 0.2rem;
    padding: 0 0.2rem;
}}

@keyframes fadeIn {{
    from {{ opacity:0; transform:translateY(8px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}

.top-icon-nav {{
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.5rem;
}}
.top-icon-nav [data-testid="stButton"] > button {{
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    width: 40px !important;
    height: 40px !important;
    min-height: 40px !important;
    max-width: 40px !important;
    padding: 0 !important;
    font-size: 1.15rem !important;
    color: var(--muted) !important;
    box-shadow: none !important;
}}
.top-icon-nav [data-testid="stButton"] > button:hover {{
    background: rgba(201,169,110,0.08) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}}
.top-icon-nav [data-testid="stBaseButton-primary"] {{
    background: rgba(201,169,110,0.15) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 10px rgba(201,169,110,0.2) !important;
}}

[data-testid="stColumn"]:nth-child(2) {{
    border-left: 1px solid var(--border) !important;
    padding-left: 1rem !important;
}}

.msg-wrap {{
    display: flex; gap: 10px;
    margin-bottom: 1rem;
    animation: fadeIn 0.35s ease both;
}}
.msg-wrap.user {{ flex-direction: row-reverse; }}
.msg-avatar {{
    width: 34px; height: 34px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem; flex-shrink: 0;
    border: 1px solid var(--border);
}}
.msg-avatar.ai   {{ background: var(--bg3); border-color: var(--accent); }}
.msg-avatar.user {{ background: var(--user-bg); border-color: var(--user-bdr); }}
.msg-bubble {{
    max-width: 80%;
    padding: 0.85rem 1.1rem;
    border-radius: var(--radius);
    font-size: var(--font-size);
    line-height: 1.7;
    position: relative;
}}
.msg-bubble.ai {{
    background: var(--ai-bg);
    border: 1px solid var(--border);
    font-family: 'Cormorant Garamond', serif;
    font-size: calc(var(--font-size) + 1px);
    color: var(--text);
    {glass_ai}
    box-shadow: 0 0 30px rgba(0,0,0,0.2);
}}
.msg-bubble.user {{
    background: var(--user-bg);
    border: 1px solid var(--user-bdr);
    text-align: right;
    {glass_user}
}}
.msg-meta {{ font-size: 0.68rem; color: var(--muted); margin-top: 0.3rem; padding: 0 0.25rem; }}

.stButton > button {{
    background: var(--surface) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.83rem !important;
    transition: all 0.2s !important;
}}
.new-story-btn [data-testid="stButton"] > button {{
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(201,169,110,0.05) !important;
}}
.new-story-btn [data-testid="stButton"] > button:hover {{
    background: rgba(201,169,110,0.15) !important;
    box-shadow: 0 0 8px rgba(201,169,110,0.2) !important;
}}
.stDownloadButton > button,
button[data-testid="stBaseButton-primary"] {{
    background: var(--accent-dim) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    border-radius: 8px !important;
}}
.stSelectbox > div > div,
.stTextInput > div > div,
.stTextArea > div > div {{
    background: var(--bg3) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}}
.stTabs [data-baseweb="tab-list"] {{
    background: var(--bg2) !important;
    border-bottom: 1px solid var(--border) !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.86rem !important;
}}
.stTabs [aria-selected="true"] {{
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: var(--surface) !important;
}}
.stExpander {{
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}}
.stChatInput > div {{
    background: var(--bg3) !important;
    border: 1.5px solid var(--accent) !important;
    border-radius: 14px !important;
    box-shadow: 0 0 8px rgba(201,169,110,0.1) !important;
}}
.stChatInput > div:focus-within {{
    border-color: #c9a96e !important;
    box-shadow: 0 0 14px rgba(201,169,110,0.25) !important;
}}
.stChatInput textarea {{
    background: transparent !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    caret-color: var(--accent) !important;
}}
.stChatInput textarea::placeholder {{
    color: var(--muted) !important;
    opacity: 0.6 !important;
}}
.stChatInput [data-testid="stChatInputSubmitButton"] {{
    background: transparent !important;
    color: var(--accent) !important;
}}

.profile-actions div[data-testid="stButton"] > button {{
    min-height: 38px !important;
    height: 38px !important;
    padding: 0 !important;
    font-size: 0.88rem !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    background: transparent !important;
    border-radius: 8px !important;
    width: 100% !important;
}}
.stAlert {{ border-radius: 10px !important; }}
.section-lbl {{
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent);
    margin: 1.1rem 0 0.4rem;
}}
.editor-panel {{
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    min-height: 380px;
    font-family: 'Cormorant Garamond', serif;
    font-size: calc(var(--font-size) + 1px);
    line-height: 1.75;
    color: var(--text);
}}

[data-testid="stPopover"] > button {{
    background: transparent !important;
    border: none !important;
    color: var(--muted) !important;
    font-size: 1.2rem !important;
    border-radius: 5px !important;
    padding: 0 !important;
    height: 36px !important;
    box-shadow: none !important;
}}
[data-testid="stPopover"] > button:hover {{
    color: var(--accent) !important;
    background: rgba(201,169,110,0.1) !important;
}}
[data-testid="stPopoverBody"] {{
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}}
[data-testid="stPopoverBody"] [data-testid="stButton"] > button {{
    border: none !important;
    background: transparent !important;
    color: var(--text) !important;
    text-align: left !important;
    padding: 0.4rem 0.5rem !important;
    font-size: 0.85rem !important;
}}
[data-testid="stPopoverBody"] [data-testid="stButton"] > button:hover {{
    color: var(--accent) !important;
    background: rgba(201,169,110,0.1) !important;
}}

.status-dot {{ width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:5px; }}
.status-dot.online  {{ background:#4ade80; }}
.status-dot.offline {{ background:#f87171; }}
::-webkit-scrollbar {{ width:3px; }}
::-webkit-scrollbar-track {{ background:var(--bg); }}
::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:2px; }}
</style>
""", unsafe_allow_html=True)
