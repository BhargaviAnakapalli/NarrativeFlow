# NarrativeFlow: Interactive Story Co-Writer

**Your personal, offline, AI-powered writing companion.**

---

## 📖 What is NarrativeFlow?
NarrativeFlow is an offline AI storytelling application powered by Llama 3 via Ollama. It provides a seamless, private, and distraction-free environment for writers to brainstorm, generate, expand, and organize stories locally without relying on cloud services.

## 💡 Core Idea
* **Local First:** Completely offline execution ensures absolute privacy and ownership of your creative work.
* **AI-Assisted Writing:** Collaborate with an AI that understands narrative context, pacing, and tone.
* **Streamlined Workflow:** A unified environment designed specifically for authors, taking you from initial concept to a final exported document.

## ✨ Key Features

* **Main Writing Area:** 
  * Real-time story generation
  * Expand or rewrite existing text
  * Dynamically adjust genres, tones, and moods
* **Export Options:** 
  * Easily export your finished stories to DOCX or PDF format.
* **Tools & Workspace:** 
  * Dedicated Chat Area for brainstorming and world-building queries
  * Main Story Area for continuous writing
  * World Builder for tracking lore, characters, and settings
  * Split Editor view for parallel creativity and referencing
* **Story Management:** 
  * User login and personalized workspace
  * Reliable autosave functionality
  * Edit, search, and organize past stories seamlessly

## 🛠️ Tech Stack


| Layer      | Technology           | Purpose                |
|------------|----------------------|------------------------|
| Frontend   | **Streamlit**        | UI & interaction       |
| Backend    | **Python**           | Core logic             |
| AI Engine  | **Ollama (Llama 3)** | Story generation       |
| Storage    | **JSON**             | Memory persistence     |
| Export     | **FPDF2 / python-docx**| Document generation    |

## ⚙️ How It Works

```text
[User Prompt] ➔ [Streamlit UI] ➔ [Python Backend] ➔ [Ollama (Llama 3)]
                                                           │
[Saved to JSON] ◄── [Displayed in UI] ◄── [Generated Story] ◄─┘
```

## 🛡️ Guardrails
NarrativeFlow includes specialized system prompts and guardrails that keep the AI strictly focused on **storytelling only**. If a user asks for coding help, general facts, or off-topic information, the system respectfully redirects the conversation back to creative writing and world-building.

## 📁 Project Structure

```text
NarrativeFlow/
├── app.py, login.py          # App entry point & authentication
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
│
├── data/                     # JSON storage (users, stories, chats, history)
│
├── config/
│   └── config.py             # App settings, models, themes
│
├── core/
│   ├── engine.py             # AI logic (Ollama + prompts)
│   ├── state.py              # Session management
│   ├── storage.py            # Data handling (JSON DB)
│   └── export.py             # PDF/DOC export
│
└── ui/
    ├── layout.py             # Sidebar & navigation
    ├── editor.py             # Story workspace
    ├── chat.py               # AI interaction
    ├── tools.py              # World builder & tools
    └── styles.py             # UI styling
```

## 🚀 Setup & Installation

### Prerequisites
* Python 3.8+
* [Ollama](https://ollama.com/) installed on your machine

### 1. Install Ollama + Llama 3
Once Ollama is installed, open your terminal and pull the Llama 3 model:
```bash
ollama run llama3
```

### 2. Install Dependencies
Clone this repository, navigate to the project folder, and install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Run the App
Launch the Streamlit web application:
```bash
streamlit run app.py
```
Open in browser:
👉 http://localhost:8501

## 🎯 Final Summary
**Empower your imagination with a secure, intelligent, and boundless local storytelling companion.**

## 🔮 Future Improvements
* Advanced story analytics
* Multi-user collaboration
* Cloud sync (optional mode)
* Enhanced UI/UX

## 👤 Author
**Bhargavi Anakapalli**  
*Passionate about AI & creative coding*


