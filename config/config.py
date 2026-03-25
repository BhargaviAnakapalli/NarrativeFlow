# config/config.py — App-wide settings and themes (merged from settings.py + themes.py)

# ── Ollama ──
OLLAMA_URL  = "http://localhost:11434/api/generate"
OLLAMA_TAGS = "http://localhost:11434/api/tags"

# ── Models & Length ──
MODELS = ["llama3:latest", "mistral", "gemma", "codellama", "phi3", "llama2"]

LENGTH_MAP = {
    "Short":        150,
    "Medium":       300,
    "Long":         500,
    "Chapter Mode": 700,
}

# ── Pages ──
PAGES = ["💬 Story Chat", "🗺 World Builder", "🔧 Writer Tools", "✏️ Split Editor"]

# ── Story Options ──
GENRES = ["Fantasy","Sci-Fi","Thriller","Romance","Mystery","Horror","Adventure","Historical"]
TONES  = ["Dramatic","Dark","Funny","Emotional","Inspirational","Mysterious","Suspenseful"]
STYLES = ["Descriptive","Simple English","Advanced","Poetic","Dialogue-heavy"]

PERSONALITIES = [
    "Brave","Intelligent","Shy","Aggressive","Mysterious",
    "Cunning","Empathetic","Reckless","Wise","Broken",
]

QUICK_STARTERS = [
    "Begin with a mysterious letter at midnight",
    "A forgotten kingdom stirs from slumber",
    "The last human wakes to silence",
    "Two rivals meet for the final time",
    "A secret buried for centuries resurfaces",
]

# ── Themes ──
THEMES = {
    "Dark": {
        "--bg": "#0c1222",
        "--bg2": "#111827",
        "--bg3": "#1f2937",
        "--text": "#e5e7eb",
        "--muted": "#9ca3af",
        "--accent": "#c9a96e",
        "--accent-dim": "rgba(201,169,110,0.12)",
        "--border": "rgba(255,255,255,0.08)",
        "--surface": "rgba(255,255,255,0.03)",
        "--ai-bg": "rgba(201,169,110,0.05)",
        "--user-bg": "rgba(78,138,195,0.1)",
        "--user-bdr": "rgba(78,138,195,0.3)"
    },
    "Light": {
        "--bg": "#f9fafb",
        "--bg2": "#f3f4f6",
        "--bg3": "#ffffff",
        "--text": "#111827",
        "--muted": "#6b7280",
        "--accent": "#b8860b",
        "--accent-dim": "rgba(184,134,11,0.1)",
        "--border": "rgba(0,0,0,0.08)",
        "--surface": "rgba(0,0,0,0.02)",
        "--ai-bg": "rgba(184,134,11,0.04)",
        "--user-bg": "rgba(59,130,246,0.08)",
        "--user-bdr": "rgba(59,130,246,0.2)"
    },
    "Custom": {
        "--bg": "#0f1522",
        "--bg2": "#161d2d",
        "--bg3": "#1e2638",
        "--text": "#e2e8f0",
        "--muted": "#94a3b8",
        "--accent": "#d4af37",
        "--accent-dim": "rgba(212,175,55,0.12)",
        "--border": "rgba(255,255,255,0.06)",
        "--surface": "rgba(255,255,255,0.02)",
        "--ai-bg": "rgba(212,175,55,0.05)",
        "--user-bg": "rgba(99,102,241,0.08)",
        "--user-bdr": "rgba(99,102,241,0.25)"
    }
}
