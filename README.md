# 🚀 SKILLMAP AI
### AI Career Roadmap & Skill Gap Platform
*Architected & Engineered by **SANJAY***

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/framework-Flask%203.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![OpenAI Responses](https://img.shields.io/badge/AI-OpenAI%20Responses%20API-emerald.svg)](https://openai.com/)
[![SQLite SQLAlchemy](https://img.shields.io/badge/database-SQLite%20%7C%20SQLAlchemy-orange.svg)](https://www.sqlalchemy.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

---

## 📖 1. Project Overview

**SkillMap AI** is an intelligent full-stack career acceleration and mentorship web application designed for students, aspiring engineers, and professionals breaking into modern technology fields.

Unlike generic career advice tools, **SkillMap AI** dynamically audits your existing skillset against real market demands, generates concrete milestone roadmaps, provides turn-by-turn interactive interview coaching, scores resumes against transparent ATS standards, and architecturally blueprints production-grade portfolio projects with schemas, folder trees, and resume descriptions.

---

## ✨ 2. Key Features

### 🤖 1. AI Career Mentor Chat
- Persistent multi-turn conversations stored in SQLite via SQLAlchemy.
- Real-time conversation management with create, delete, and switch sessions.
- Expert system prompts tuned for actionable career guidance, study schedules, and guidance.
- Markdown rendering support (code snippets, bold headings, bullet milestones).
- "SkillMap AI is thinking..." loading animations.

### 🗺️ 2. Career Roadmap Generator
- Generates 4-phase master career timelines customized to your daily study hours and target timeframe (3, 6, or 12 months).
- Visual sequential milestone pipeline:
  $$\text{FOUNDATION} \longrightarrow \text{PROGRAMMING} \longrightarrow \text{CORE SKILLS} \longrightarrow \text{PROJECTS} \longrightarrow \text{PORTFOLIO} \longrightarrow \text{INTERVIEW} \longrightarrow \text{JOB READY}$$
- In-depth breakdowns: prerequisites, weekly goals, estimated hours, core technologies, industry certifications, portfolio criteria, and internship strategies.
- Past roadmaps drawer allowing instant recall of previous plans.

### 🎯 3. Skill Gap Analyzer
- Evaluates target roles (e.g. Data Analyst, Full Stack Developer, AI Engineer, Cybersecurity) against your current skills.
- Displays match percentages, role readiness gauge, and an interactive Competency Matrix.
- Classifies skills into **✓ Mastered**, **In Progress**, or **Missing** with Priority levels (High, Medium, Low) and optimal learning sequence.
- Interactive status toggling that immediately synchronizes with your personal telemetry.

### 🛠️ 4. Portfolio Project Generator
- Generates high-impact capstone project blueprints to replace generic tutorial clones.
- Complete specifications: Problem statements, features list, relational SQL database schemas, clean repository folder structures, step-by-step development milestones, and ready-to-use resume bullet points (using the Google X-Y-Z formula).

### 📊 5. Progress Tracking & Visual Telemetry
- Real-time telemetry dashboard powered by **Chart.js**.
- Tracks overall career readiness %, total mastered competencies, active portfolio builds, study hours, and multi-day streaks.
- Interactive visual charts:
  - **Weekly Study Distribution** (Bar chart)
  - **Competency Status Breakdown** (Doughnut chart)
- Interactive skills checklist with instant 1-click mastery toggles.
- Modal to log daily study sessions and notes.

### 📄 6. Resume ATS & Keyword Analyzer
- Multi-format file ingestion supporting **PDF**, **DOCX**, and plain text.
- 4-Pillar transparent ATS scoring rubric (Keywords 30%, Quantified Metrics 25%, Section Completeness 25%, Formatting 20%).
- Keyword comparison: detected industry keywords (green badges) vs missing critical keywords (red badges).
- Actionable section-by-section critique for Projects, Experience, and Education.

### 🎙️ 7. Turn-by-Turn Interview Practice
- Realistic technical and behavioral interview simulation for multiple career tracks.
- Selectable difficulty tiers: Beginner, Intermediate, Advanced.
- One question at a time with optional hints.
- AI evaluation delivers scores (0–100), ratings, missing points/blind spots, structural improvements, and an exemplary model answer before advancing to the next challenge.

### 🎨 8. Dark & Light Theme System
- Default sleek dark mode with glassmorphic cards and vibrant accent gradients.
- Crisp light mode toggle with state persistence in `localStorage`.

### 🛡️ 9. Zero-Crash Fallback Engine
- Features an offline-safe career simulation engine that ensures all 7 core modules work smoothly without crashing even if an OpenAI API key is missing or encounters network timeouts.

---

## 🏗️ 3. Technology Stack

- **Frontend:**
  - Semantic HTML5 & Modern Vanilla CSS3 (custom design system, glassmorphism, responsive breakpoints)
  - Vanilla JavaScript (ES6+ modular controller, router, async fetch API)
  - [Lucide Icons](https://lucide.dev/) (lightweight SVG icon library)
  - [Chart.js](https://www.chartjs.org/) (responsive telemetry charts)

- **Backend:**
  - Python 3.10+
  - Flask (REST API microframework)
  - Flask-SQLAlchemy (ORM)
  - Werkzeug (secure file handling)
  - pypdf & python-docx (resume text extraction)

- **Database:**
  - SQLite (development and local deployment)

- **AI Integration:**
  - OpenAI Python SDK (Chat Completions & Responses API with JSON mode)
  - Configurable model via `.env` (Default: `gpt-5.6-luna`)

---

## 📁 4. Project Directory Structure

```
SkillMap-AI/
│
├── app.py                   # Main Flask application & all REST endpoints
├── ai.py                    # OpenAI client integration & fallback knowledge engine
├── models.py                # SQLAlchemy ORM models & relationships
├── config.py                # App configuration & environment loader
├── requirements.txt         # Python package dependencies
├── .env.example             # Template for API keys & settings
├── .env                     # Local environment configuration
├── .gitignore               # Ignored cache, DB, and virtualenv files
├── README.md                # Comprehensive documentation
│
├── database/
│   ├── .gitkeep
│   └── skillmap.db          # Auto-generated SQLite database
│
├── templates/
│   ├── index.html           # Main Single-Page App workspace & panels
│   ├── dashboard.html       # Analytics & Telemetry dashboard view
│   └── login.html           # User profile & goals manager
│
└── static/
    ├── css/
    │   └── style.css        # Design tokens, glassmorphism, responsive CSS
    ├── js/
    │   └── app.js           # Client-side router, chat, charts, and API logic
    └── assets/
        └── favicon.svg      # Vector brand logo
```

---

## ⚡ 5. Installation & Setup

### Prerequisites
- Python 3.10 or higher installed on your system.
- Git (optional, for version control).

### Step 1: Create a Virtual Environment
```bash
# Navigate to the project root directory
cd SkillMap-AI

# Create virtual environment
python -m venv venv
```

### Step 2: Activate the Virtual Environment
- **Windows (Command Prompt / PowerShell):**
  ```powershell
  venv\Scripts\activate
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the template configuration file:
- **Windows:**
  ```powershell
  copy .env.example .env
  ```
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```

Open `.env` in any text editor and optionally configure your OpenAI API Key:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5.6-luna
SECRET_KEY=your_secure_random_secret_key
DATABASE_URL=sqlite:///database/skillmap.db
PORT=5000
DEBUG=True
DEVELOPER_NAME=SANJAY
```

> [!NOTE]
> If you leave `OPENAI_API_KEY` blank, the platform automatically activates its intelligent built-in career simulation engine so all features, generation algorithms, and charts can be tested immediately with zero crashes!

---

## 🚀 6. Running the Application

Start the Flask server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🗄️ 7. Database Models & Schema

The application uses SQLAlchemy with the following database tables:

| Model | Description |
| :--- | :--- |
| `User` | Stores profile, target career, experience level, and daily study hours. |
| `Conversation` | Manages separate chat threads with title and career context. |
| `Message` | Stores individual user and assistant chat bubbles. |
| `Roadmap` | Stores generated career roadmaps with JSON phases and timelines. |
| `Skill` | Master catalogue of industry technical competencies. |
| `UserSkill` | User-specific tracking with status (`✓`, `In Progress`, `Missing`), priority, and proficiency. |
| `Project` | Generated portfolio project blueprints, database schemas, and folder trees. |
| `Progress` | Logs study hours, notes, streaks, and overall career readiness. |
| `ResumeAnalysis` | Persists ATS scores, extracted keywords, missing gaps, and critique. |

Database tables are initialized automatically when you first launch `python app.py`.

---

## 🔌 8. API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Main interactive application interface |
| `GET` | `/dashboard` | Standalone telemetry & analytics page |
| `GET` | `/login` | User profile & settings view |
| `POST` | `/api/chat` | Send a message to AI Career Mentor |
| `GET` | `/api/chats` | Retrieve user conversation history list |
| `POST` | `/api/chats` | Start a new conversation thread |
| `GET` | `/api/chats/<id>` | Retrieve messages for a specific conversation |
| `DELETE`| `/api/chats/<id>` | Delete a conversation thread |
| `POST` | `/api/roadmap` | Generate a tailored career roadmap |
| `GET` | `/api/roadmaps` | List previously saved roadmaps |
| `POST` | `/api/skill-gap` | Run a skill gap analysis |
| `GET` | `/api/skills` | Retrieve active user skills |
| `POST` | `/api/skills/toggle`| Toggle status (`✓`, `In Progress`, `Missing`) |
| `POST` | `/api/project` | Generate a portfolio project blueprint |
| `GET` | `/api/projects` | List saved project blueprints |
| `GET` | `/api/progress` | Get telemetry, stats, and Chart.js data |
| `POST` | `/api/progress` | Log daily study hours and notes |
| `POST` | `/api/interview` | Generate turn-by-turn interview question |
| `POST` | `/api/interview/answer`| Evaluate user answer with feedback & model answer |
| `POST` | `/api/resume/analyze` | Parse PDF/DOCX/text and perform ATS audit |

---

## 🛠️ 9. Troubleshooting & Common Questions

1. **Missing OpenAI API Key:**
   - *Behavior:* If no API key is specified in `.env`, SkillMap AI does not crash. It leverages its intelligent fallback engine to deliver realistic responses, roadmaps, and interview simulations.
   - *Fix:* When ready for live OpenAI generation, set `OPENAI_API_KEY=sk-...` in `.env` and restart `python app.py`.

2. **File Upload Limit:**
   - The application enforces a safe 16MB maximum upload limit for PDF and DOCX files. Ensure resumes are under this threshold.

3. **Port 5000 in Use:**
   - In `.env`, change `PORT=5000` to `PORT=5050` or any available port.

---

## 🌟 10. Future Improvements

- OAuth2 social login (GitHub and Google authentication).
- Webhook notifications for daily study streak reminders.
- GitHub API integration to auto-detect verified repositories and project commits.
- Voice-enabled interview simulation using Web Speech API or Whisper.

---

## 👨‍💻 Credits & Author

**SKILLMAP AI** — Designed, architected, and built with ❤️ by **SANJAY**.
