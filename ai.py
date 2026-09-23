import os
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

# Initialize OpenAI client if key exists
openai_client = None
if Config.OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    except Exception as e:
        logger.warning(f"Could not initialize OpenAI client: {e}")

SYSTEM_MENTOR_PROMPT = """You are SkillMap AI — Personal Career Mentor, an expert career mentor for students and beginners.

You help users with:
- career planning
- skill-gap analysis
- learning roadmaps
- programming
- projects
- internships
- interview preparation
- resume improvement
- study schedules
- portfolio development

Always:
- Explain simply and warmly
- Give practical, step-by-step instructions
- Avoid unnecessary complexity or jargon without explanation
- Recommend realistic learning paths
- Break large goals into smaller, achievable milestones
- Mention prerequisites when needed
- Give concrete project ideas
- Give estimated learning time where appropriate
- Format responses cleanly with bold headings, bullet points, and code snippets when relevant
"""

def call_openai_chat(messages, system_prompt=SYSTEM_MENTOR_PROMPT, response_json=False):
    """
    Attempt calling OpenAI API using Responses or Chat Completions API.
    Falls back gracefully to alternative models and local engine if key is missing or invalid.
    """
    if not openai_client:
        return None

    preferred_model = Config.OPENAI_MODEL or "gpt-5.6-luna"
    # Try preferred model first, then standard production models if fictional/unavailable
    models_to_try = [preferred_model]
    for fallback in ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    formatted_messages = [{"role": "system", "content": system_prompt}]
    for m in messages:
        formatted_messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})

    for model in models_to_try:
        try:
            # Try responses API first if supported
            if hasattr(openai_client, "responses") and callable(getattr(openai_client.responses, "create", None)):
                try:
                    kwargs = {
                        "model": model,
                        "input": formatted_messages,
                    }
                    res = openai_client.responses.create(**kwargs)
                    if hasattr(res, "output_text"):
                        return res.output_text
                except Exception:
                    pass

            # Standard Chat Completions
            kwargs = {
                "model": model,
                "messages": formatted_messages,
                "temperature": 0.7,
            }
            if response_json:
                kwargs["response_format"] = {"type": "json_object"}

            response = openai_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            err_str = str(e).lower()
            logger.warning(f"OpenAI attempt with model '{model}' failed: {e}")
            if "invalid api key" in err_str or "incorrect api key" in err_str:
                break
            continue

    return None


# =====================================================================
# 1. AI CHAT MENTOR ENGINE
# =====================================================================
def get_chat_response(messages, user_context=None):
    """
    Get chat response from OpenAI or smart multi-topic career mentor fallback.
    """
    sys_prompt = SYSTEM_MENTOR_PROMPT
    if user_context:
        sys_prompt += f"\nUser Context: Target Career: {user_context.get('target_career')}, Level: {user_context.get('current_level')}"

    # Try live OpenAI
    ai_text = call_openai_chat(messages, system_prompt=sys_prompt)
    if ai_text:
        return ai_text

    # Intelligent fallback career mentor simulation with full conversational awareness
    return generate_fallback_chat_reply(messages, user_context)


def generate_fallback_chat_reply(messages, user_context=None):
    """
    Comprehensive, non-repetitive conversational career mentor engine.
    Understands programming languages, architectures, study plans, and career questions.
    """
    user_context = user_context or {}
    career = user_context.get('target_career', 'Technology')
    level = user_context.get('current_level', 'Beginner')
    hours = user_context.get('study_hours', 2.5)

    user_msgs = [m.get("content", "").strip() for m in messages if m.get("role") == "user"]
    query = user_msgs[-1].lower() if user_msgs else ""
    conv_depth = len(user_msgs)

    # 1. PYTHON
    if "python" in query:
        return f"""### 🐍 Mastering Python for {career}

Python is one of the highest-ROI languages you can learn today. Here is the structured path to master it effectively:

1. **Core Language Fundamentals (Days 1–10)**
   - Data types: Lists, Tuples, Dictionaries, Sets, and list comprehensions.
   - Functions, `*args`, `**kwargs`, lambda functions, and scope.
   - Clean Object-Oriented Programming (Classes, Inheritance, Dunder methods).
2. **Standard Library & Tooling (Days 11–18)**
   - Virtual environments (`venv`), `pip`, and package management.
   - File I/O, `json`, `datetime`, and exception handling (`try-except-finally`).
3. **Domain-Specific Libraries (Days 19–35)**
   - **For Data/AI:** `pandas`, `numpy`, `matplotlib`, and `scikit-learn`.
   - **For Web/Backend:** `Flask`, `FastAPI`, and `SQLAlchemy` ORM.
4. **Hands-On Practice Exercise**
   - Write a script that fetches data from a public REST API (e.g. GitHub API), parses the JSON response, and generates a formatted CSV report.

💡 *Next Step:* Would you like a daily study schedule for Python, or project ideas using Python for {career}?"""

    # 2. JAVASCRIPT / TYPESCRIPT / FRONTEND
    elif any(k in query for k in ["javascript", "js", "typescript", "react", "vue", "frontend", "html", "css"]):
        return f"""### ⚡ Modern Frontend & JavaScript Strategy

To excel in frontend engineering for **{career}**, focus on practical architecture rather than endless tutorial syntax:

1. **Deep Vanilla JavaScript (First Principles)**
   - Master Execution Context, Event Loop, Closures, and Promises (`async/await`).
   - DOM manipulation, custom events, and debouncing/throttling.
2. **Modern Component Frameworks (React / Next.js)**
   - Functional components, core hooks (`useState`, `useEffect`, `useMemo`, `useCallback`).
   - State management patterns (Context API, Zustand, or Redux Toolkit).
   - Component composition and reusable custom hooks.
3. **TypeScript Integration**
   - Type definitions, Interfaces, Generics, and strict null checks to eliminate runtime bugs.
4. **Key Project Milestone**
   - Build an interactive, responsive dashboard with dark/light theming, client-side routing, and real-time filtering.

👉 *Next Action:* Check out the **Projects** tab to generate a complete frontend capstone specification with folder trees!"""

    # 3. SQL / DATABASES
    elif any(k in query for k in ["sql", "database", "postgres", "mysql", "mongodb", "nosql", "query"]):
        return f"""### 🗄️ SQL & Database Mastery Guide

Databases are the bedrock of {career}. Here is what separates junior developers from hireable engineers:

- **Core Querying:** Master `SELECT`, `WHERE`, `GROUP BY`, and `HAVING` (remember: `WHERE` filters rows *before* aggregation; `HAVING` filters aggregated groups).
- **Joins & Relationships:** Understand `INNER JOIN`, `LEFT JOIN`, `CROSS JOIN`, and foreign key constraint cascades.
- **Advanced Aggregations & Window Functions:** Learn `ROW_NUMBER()`, `RANK()`, `LEAD()`, and `LAG()` — these are heavily tested in technical interviews!
- **Indexing & Performance:** Understand how B-Tree indexes speed up lookups and when indexes introduce write overhead.
- **SQL vs NoSQL:** Use PostgreSQL/MySQL for structured data with ACID transactions; use MongoDB/Redis for flexible schemas or high-speed caching.

Would you like to practice a mock SQL interview question right now?"""

    # 4. BACKEND / APIS / REST
    elif any(k in query for k in ["backend", "api", "rest", "endpoint", "graphql", "server", "microservice", "jwt"]):
        return f"""### ⚙️ Production Backend & API Architecture

Building resilient backends requires more than just connecting endpoints. Here is the blueprint for **{career}**:

1. **RESTful API Standards**
   - Use proper HTTP verbs: `GET` (fetch), `POST` (create), `PUT`/`PATCH` (update), `DELETE` (remove).
   - Return semantic HTTP status codes: `200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `500 Server Error`.
2. **Security & Authentication**
   - JWT (JSON Web Tokens) or session cookies with `HttpOnly` and `Secure` flags.
   - Password hashing with `bcrypt` / Argon2 (never store plain text passwords).
   - Input validation and sanitization to prevent SQL injection and XSS.
3. **Database Integration & ORMs**
   - Use SQLAlchemy or Prisma to structure relational data with clean migrations.
4. **Testing & Documentation**
   - Write integration tests for every critical endpoint and document schemas with OpenAPI/Swagger.

💡 *Pro Tip:* Use our **Project Generator** in the sidebar to view a complete backend folder tree and database schema design!"""

    # 5. AI / MACHINE LEARNING / DATA SCIENCE
    elif any(k in query for k in ["machine learning", "ai engineer", "data science", "llm", "deep learning", "pytorch", "neural", "rag"]):
        return f"""### 🧠 AI & Machine Learning Engineering Roadmap

Transitioning into Artificial Intelligence requires a pragmatic blend of theory and systems engineering:

1. **Mathematical Foundations (Don't skip, but be practical):**
   - Linear Algebra (Matrix multiplications, eigenvalues).
   - Calculus (Partial derivatives, gradients, chain rule for backpropagation).
   - Probability & Statistics (Distributions, hypothesis testing, Bayes' theorem).
2. **Classical Machine Learning (Scikit-Learn):**
   - Regression, Decision Trees, Random Forests, XGBoost, and k-Means.
   - Evaluation metrics: Precision, Recall, F1-score, ROC-AUC, and Cross-Validation.
3. **Deep Learning & Neural Networks (PyTorch):**
   - Multi-Layer Perceptrons, CNNs for computer vision, RNNs/Transformers for sequences.
4. **Modern Generative AI & Systems:**
   - Vector Databases (Chroma, Pinecone) + Embeddings.
   - RAG (Retrieval-Augmented Generation) pipelines and LLM evaluation frameworks.

👉 *Next Step:* Head over to **Career Roadmap** and enter "AI Engineer" to generate a detailed 4-phase timeline!"""

    # 6. CYBERSECURITY
    elif any(k in query for k in ["cyber", "security", "hacking", "penetration", "wireshark", "nmap", "soc", "siem"]):
        return f"""### 🛡️ Cybersecurity & Defensive Engineering Blueprint

To break into cybersecurity, hands-on lab experience is infinitely more valuable than textbook memorization:

- **1. Networking & Protocols (The Foundation):**
  - Thoroughly understand the TCP/IP model, DNS resolution, ARP, DHCP, and Subnetting.
  - Practice packet capture and analysis with Wireshark.
- **2. Linux Administration:**
  - Learn command-line navigation, file permissions (`chmod`, `chown`), process management, and bash automation.
- **3. Security Operations & Blue Team Tools:**
  - SIEM platforms (Splunk, Elastic SIEM), log auditing, and anomaly detection.
  - OWASP Top 10 web vulnerabilities (SQLi, XSS, CSRF, Broken Auth).
- **4. Recognized Industry Credentials:**
  - CompTIA Security+ (industry standard entry gate).
  - BTL1 (Blue Team Level 1) or Certified Ethical Hacker (CEH).

Would you like advice on setting up a free home lab with VirtualBox and Kali Linux?"""

    # 7. STUDY SCHEDULE / DAILY ROUTINE
    elif any(k in query for k in ["schedule", "routine", "how many hours", "hours", "study plan", "time management", "daily plan"]):
        hrs = hours or 2.5
        concept_min = int(hrs * 20)
        coding_min = int(hrs * 30)
        review_min = int(hrs * 10)
        return f"""### ⏱️ Optimized Daily Study Schedule ({hrs} Hours/Day)

Consistency beats intensity. Here is an evidence-based daily schedule designed to prevent burnout and maximize retention:

- **Block 1: Deep Theory & Concept Acquisition ({concept_min} minutes)**
  - Read documentation, watch 1 focused tutorial, or read an architectural chapter.
  - Take active notes in Markdown (explain the concept in your own words).
- **Block 2: Active Coding & Hands-on Implementation ({coding_min} minutes)**
  - Close the tutorial. Open your IDE.
  - Write code from scratch. Intentionally break things to observe error messages and debug.
- **Block 3: Consolidation, Git Commit & Review ({review_min} minutes)**
  - Review what worked and what blocked you.
  - Commit your code to GitHub with descriptive commit messages.
  - Log your hours in our **Progress** dashboard to maintain your study streak!

💡 *Golden Rule:* If you get stuck for more than 20 minutes, search official documentation or error logs before checking a solution!"""

    # 8. PROJECTS & PORTFOLIO
    elif any(k in query for k in ["project", "portfolio", "what to build", "build", "capstone", "github"]):
        return f"""### 🛠️ High-Impact Portfolio Strategy for {career}

To stand out in hiring pipelines, avoid basic tutorial clones (to-do lists, weather apps, clones of popular sites). Instead, build projects with **real-world business utility**:

1. **Architect for Production:**
   - Implement real user authentication, persistent databases, error handling, and automated tests.
2. **Quantify the Impact:**
   - Instead of *"built a backend"*, document *"architected REST API handling 2,000 requests/min with sub-100ms response time"*.
3. **Deploy Live:**
   - Host on Render, Vercel, or AWS with a clean GitHub repository containing architecture diagrams and demo GIFs.

👉 *Next Action:* Go to the **Projects** tab in the sidebar right now to generate a complete architecture blueprint tailored to your skill level!"""

    # 9. RESUME & ATS
    elif any(k in query for k in ["resume", "cv", "ats", "keywords", "experience"]):
        return """### 📄 Resume & ATS Optimization Blueprint

Recruiters spend an average of 6 seconds reviewing a resume. Here is how to pass both the ATS filter and human reviewers:

1. **The Google X-Y-Z Formula for Bullet Points:**
   - *"Accomplished [X], as measured by [Y], by doing [Z]"*.
   - *Example:* "Decreased database query latency by 45% (Y) across 50,000 records (X) by redesigning relational indexes and foreign key constraints (Z)."
2. **ATS Formatting Cleanliness:**
   - Use single-column layouts. Avoid tables, icons, graphics, or text boxes that confuse ATS parsers.
   - Include direct, clickable links to your live projects and GitHub profile.
3. **Keyword Density:**
   - Match skills directly from target job postings (e.g. Docker, REST API, React, PostgreSQL).

👉 *Next Action:* Upload your resume in the **Resume Analyzer** tab to get an instant ATS score and keyword gap analysis!"""

    # 10. INTERVIEW PREPARATION
    elif any(k in query for k in ["interview", "prepare", "mock", "questions", "behavioral", "star method"]):
        return f"""### 🎯 Technical & Behavioral Interview Masterclass

Technical interviews for **{career}** evaluate three core dimensions:

1. **Problem Solving & Fundamentals (40%):**
   - Explain your thought process out loud before writing a single line of code.
   - Identify edge cases early: empty inputs, negative numbers, null pointers, large datasets.
2. **System & Architectural Trade-offs (30%):**
   - Never say "this is the best tool". Say *"I chose X over Y because X gives us ACID guarantees, whereas Y would require custom transaction handling."*
3. **Behavioral STAR Stories (30%):**
   - Prepare 4 concrete stories: A project you led, a severe technical bug you debugged, a conflict with a teammate, and a time you learned a new technology under deadline.

👉 *Try It Now:* Click **Interview Practice** in the sidebar to simulate live turn-by-turn interview questions with instant AI feedback!"""

    # 11. ROADMAP & WHERE TO START
    elif any(k in query for k in ["roadmap", "where to start", "how to begin", "step by step", "guide me", "start"]):
        return f"""### 🚀 Strategic Career Roadmap for {career}

Here is the 4-phase master progression designed for **{level}** level:

- **Phase 1: Foundations (Month 1):** Solidify language fundamentals, data structures, terminal CLI, and Git version control.
- **Phase 2: Core Engineering (Months 2–3):** Deep dive into frameworks, database modeling (SQL), API communication, and automated testing.
- **Phase 3: Production Capstones (Months 4–5):** Build 2 end-to-end full-stack applications with authentication, cloud deployment, and CI/CD pipelines.
- **Phase 4: Job Readiness (Month 6):** ATS resume polish, portfolio deployment, LeetCode/interview practice, and targeted networking.

💡 *Recommendation:* Use our **Career Roadmap** generator in the sidebar to view your custom visual milestone timeline!"""

    # 12. SKILL GAP & MISSING COMPETENCIES
    elif any(k in query for k in ["missing", "skill gap", "skills", "what do i need", "what am i missing"]):
        return f"""### 🔍 Market Competencies for {career}

In today's hiring market for **{career}**, recruiters look for three distinct layers:

1. **Non-Negotiable Core:** Programming language proficiency, Git collaboration, relational databases, and REST APIs.
2. **Differentiating Edge:** Containerization (Docker), cloud deployment (AWS/Render), and basic AI integration.
3. **Professional Communication:** Clean technical documentation, explaining architectural decisions, and code reviews.

👉 *Next Step:* Run the **Skill Gap** analyzer in the sidebar to compare your exact skills against industry standards!"""

    # 13. CAREER TRANSITION / NON-CS BACKGROUND / DEGREE
    elif any(k in query for k in ["career switch", "no degree", "non-cs", "college", "job", "hire", "fresher", "internship", "salary"]):
        return f"""### 💼 Breaking into {career} (Non-CS or Self-Taught)

A computer science degree is no longer mandatory if you have **indisputable proof of work**. Here is how to succeed:

1. **Build a Living Portfolio:** 2 production apps with real users or live demos beat a diploma every single time.
2. **Contribute to Open Source:** Making small PRs to existing open-source projects proves you can read someone else's codebase.
3. **Network Through Value:** Share what you learn publicly on LinkedIn or Twitter/X. Write technical walkthroughs of problems you solved.
4. **Target High-Signal Roles:** Look for startups and small-to-medium companies where engineers review applications directly rather than HR keyword filters.

What is your current background, and what is the biggest obstacle you feel you are facing?"""

    # 14. LEETCODE / DSA / ALGORITHMS
    elif any(k in query for k in ["leetcode", "dsa", "data structures", "algorithm", "problem solving"]):
        return """### 🧩 Algorithmic Problem Solving & LeetCode Strategy

Do not blindly grind hundreds of random LeetCode questions. Instead, master the **core patterns**:

1. **Two Pointers & Sliding Window:** Perfect for arrays, strings, and subarray problems.
2. **Fast & Slow Pointers:** Cycle detection in linked lists.
3. **Binary Search:** Any sorted search space (logarithmic time $O(\\log n)$).
4. **BFS & DFS:** Tree and graph traversals.
5. **Hash Maps & Sets:** $O(1)$ lookups for frequency counting and pairing problems.

*Study Rule:* Spend 20 minutes attempting the problem alone. If stuck, review the pattern solution, understand the recurrence relation, and re-implement it from scratch without looking!"""

    # 15. FOLLOW-UP / CONFIRMATION / CONTINUATION ("YES", "TELL ME MORE", "THANKS", "OK")
    elif any(k in query for k in ["yes", "ok", "okay", "sure", "thanks", "thank you", "tell me more", "what next", "continue", "example", "how"]):
        if "thank" in query:
            return f"You're very welcome! Keep up the momentum on your journey towards **{career}**. What specific topic or challenge would you like to tackle next?"
        return f"""### 💡 Recommended Next Steps for {career}

Based on our discussion, here are three high-impact actions you can take right now:

1. **Solidify Your Target Timeline:** Check the **Career Roadmap** tab to review your phases.
2. **Audit Your Current Toolset:** Open **Skill Gap** and mark which technologies you already know.
3. **Practice a Coding Challenge or Concept:** Ask me any technical question (e.g., *"How do React Hooks work under the hood?"* or *"Explain SQL Indexing"*).

What would you like to dive into next?"""

    # 16. GREETINGS
    elif any(k in query for k in ["hi", "hello", "hey", "greetings", "good morning", "good evening"]):
        if conv_depth > 1:
            return f"Hey again! Ready to make more progress toward **{career}**? Feel free to ask me to explain a concept, review a study plan, or suggest project architectures."
        return f"""Hello! I'm your **SkillMap AI Career Mentor**.

I am here to help you accelerate your journey into **{career}**. Here are a few ways we can work together:

- 🗺️ **Career Roadmaps:** Customized to your study hours and target timeframe
- 📊 **Skill Gap Audits:** Identify and prioritize what to learn next
- 💡 **Portfolio Projects:** Blueprints with database schemas and folder layouts
- 🎙️ **Interview Coaching:** Role-specific technical and behavioral preparation
- 📄 **Resume Review:** Actionable feedback to pass ATS screening

What would you like to explore first?"""

    # 17. CONTEXTUAL INTELLIGENT FALLBACK (NEVER REPEATS GENERIC WELCOME)
    else:
        return f"""### 💡 Career Guidance on "{user_msgs[-1]}"

When preparing for **{career}**, every question connects back to building real competence and proof of work:

- **Core Concept:** Break this down into foundational principles first. Understand *why* the technology or process exists before learning the syntax.
- **Practical Application:** Connect it immediately to a portfolio project or real business use case.
- **Interview Relevance:** Be prepared to discuss the pros, cons, and alternatives when interviewers ask about this area.

Would you like me to:
1. Provide a step-by-step tutorial or code example?
2. Show you how this skill applies directly to your roadmap?
3. Give you a practice interview question on this topic?"""



# =====================================================================
# 2. CAREER ROADMAP GENERATION
# =====================================================================
def generate_roadmap_ai(career_goal, current_level, current_skills, hours_per_day, target_duration):
    """Generate comprehensive structured career roadmap."""
    prompt = f"""Generate a detailed career roadmap for someone wanting to become a '{career_goal}'.
Current Skill Level: {current_level}
Current Skills: {current_skills or 'None / Beginner'}
Available Study Hours: {hours_per_day} hours/day
Target Duration: {target_duration}

Return a valid JSON object with the following exact keys:
{{
  "title": "Comprehensive {career_goal} Roadmap",
  "overview": "Clear 2-3 sentence overview of this career and market potential.",
  "prerequisites": "Prerequisites needed before starting.",
  "phases": [
    {{
      "phase_number": 1,
      "name": "Phase 1: Foundation & Basics",
      "duration": "Weeks 1-4",
      "milestone_tag": "FOUNDATION",
      "description": "Core concepts and setup",
      "topics": ["Topic 1", "Topic 2", "Topic 3"],
      "action_items": ["Action 1", "Action 2"],
      "estimated_hours": 40
    }},
    {{
      "phase_number": 2,
      "name": "Phase 2: Programming & Core Skills",
      "duration": "Weeks 5-10",
      "milestone_tag": "CORE SKILLS",
      "description": "Deep dive into language and tools",
      "topics": ["Topic 1", "Topic 2"],
      "action_items": ["Action 1", "Action 2"],
      "estimated_hours": 60
    }},
    {{
      "phase_number": 3,
      "name": "Phase 3: Advanced Concepts & Frameworks",
      "duration": "Weeks 11-16",
      "milestone_tag": "PROJECTS",
      "description": "Frameworks, databases, and architectural patterns",
      "topics": ["Topic 1", "Topic 2"],
      "action_items": ["Action 1", "Action 2"],
      "estimated_hours": 70
    }},
    {{
      "phase_number": 4,
      "name": "Phase 4: Portfolio, Interview & Job Readiness",
      "duration": "Weeks 17-24",
      "milestone_tag": "JOB READY",
      "description": "Real-world projects, resume, and interview prep",
      "topics": ["Portfolio Deployment", "Mock Interviews", "ATS Resume"],
      "action_items": ["Action 1", "Action 2"],
      "estimated_hours": 50
    }}
  ],
  "milestones_timeline": [
    "FOUNDATION", "PROGRAMMING", "CORE SKILLS", "PROJECTS", "PORTFOLIO", "INTERVIEW", "JOB READY"
  ],
  "important_technologies": ["Tech 1", "Tech 2", "Tech 3", "Tech 4", "Tech 5"],
  "projects": [
    {{"title": "Beginner Project", "description": "Short description", "tech": "Tech list"}},
    {{"title": "Capstone Project", "description": "Production grade full-stack app", "tech": "Tech list"}}
  ],
  "certifications": ["Cert 1", "Cert 2"],
  "interview_prep": "Key interview topics and preparation advice.",
  "portfolio_requirements": "Essential requirements for a standout portfolio.",
  "job_prep": "Tips for internships, cold outreach, and job applications."
}}
"""
    raw = call_openai_chat([{"role": "user", "content": prompt}], response_json=True)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass

    # Built-in structured generator fallback
    return build_fallback_roadmap(career_goal, current_level, current_skills, hours_per_day, target_duration)


def build_fallback_roadmap(career_goal, current_level, current_skills, hours, duration):
    """High-quality predefined roadmap blueprints."""
    goal_lower = career_goal.lower()

    if "data" in goal_lower:
        techs = ["Python", "SQL", "Pandas", "Power BI / Tableau", "Statistics", "Machine Learning Basics", "Git"]
        p1 = {"phase_number": 1, "name": "Phase 1: Foundations & Analytical Thinking", "duration": "Weeks 1-4", "milestone_tag": "FOUNDATION", "description": "Master Excel/Sheets, Statistics fundamentals, and relational databases.", "topics": ["Descriptive Statistics", "Advanced Excel (XLOOKUP, Pivot Tables)", "SQL Basics & Joins"], "action_items": ["Solve 30 SQL query challenges on LeetCode/StrataScratch", "Analyze a sales dataset in Excel"], "estimated_hours": int(hours * 25)}
        p2 = {"phase_number": 2, "name": "Phase 2: Programming with Python & SQL", "duration": "Weeks 5-10", "milestone_tag": "CORE SKILLS", "description": "Deepen SQL window functions and Python data manipulation.", "topics": ["Python Data Types & Functions", "Pandas & NumPy", "Complex SQL Aggregations"], "action_items": ["Clean and process messy CSV data with Pandas", "Connect Python to SQLite/PostgreSQL"], "estimated_hours": int(hours * 35)}
        p3 = {"phase_number": 3, "name": "Phase 3: Visualization & Business Intelligence", "duration": "Weeks 11-16", "milestone_tag": "PROJECTS", "description": "Transform data into interactive dashboards and executive stories.", "topics": ["Power BI / Tableau Dashboard Design", "Data Storytelling & KPI Metrics", "Seaborn / Plotly Charts"], "action_items": ["Build an Executive Sales KPI Dashboard", "Publish dashboard portfolio online"], "estimated_hours": int(hours * 35)}
        p4 = {"phase_number": 4, "name": "Phase 4: Capstone, Portfolio & Interview Prep", "duration": "Weeks 17-24", "milestone_tag": "JOB READY", "description": "Real-world end-to-end data analysis and technical interview mastery.", "topics": ["A/B Testing Fundamentals", "SQL Live Coding Interviews", "Resume ATS Alignment"], "action_items": ["Publish comprehensive Kaggle analysis case study", "Prepare 5 STAR format case study presentations"], "estimated_hours": int(hours * 30)}
        certs = ["Google Data Analytics Professional Certificate", "Microsoft Certified: Power BI Data Analyst (PL-300)"]
    elif "ai" in goal_lower or "machine" in goal_lower:
        techs = ["Python", "PyTorch / TensorFlow", "Scikit-Learn", "FastAPI", "Vector DBs (Chroma/Pinecone)", "LangChain / LLM APIs", "Docker"]
        p1 = {"phase_number": 1, "name": "Phase 1: Mathematical Foundations & Python Mastery", "duration": "Weeks 1-4", "milestone_tag": "FOUNDATION", "description": "Linear algebra, calculus, and advanced Python OOP.", "topics": ["Vector/Matrix Operations", "NumPy & Calculus Basics", "Object-Oriented Python"], "action_items": ["Implement gradient descent from scratch", "Set up Dockerized ML development environment"], "estimated_hours": int(hours * 25)}
        p2 = {"phase_number": 2, "name": "Phase 2: Machine Learning & Feature Engineering", "duration": "Weeks 5-10", "milestone_tag": "CORE SKILLS", "description": "Supervised, unsupervised learning, model evaluation, and cross-validation.", "topics": ["Regression & Classification", "Random Forests & XGBoost", "Hyperparameter Tuning"], "action_items": ["Build customer churn predictor on real data", "Achieve top 25% on a Kaggle competition"], "estimated_hours": int(hours * 35)}
        p3 = {"phase_number": 3, "name": "Phase 3: Deep Learning, LLMs & Generative AI", "duration": "Weeks 11-16", "milestone_tag": "PROJECTS", "description": "Neural networks, PyTorch, Embeddings, RAG systems, and OpenAI API.", "topics": ["Transformers Architecture", "RAG (Retrieval-Augmented Generation)", "FastAPI Model Serving"], "action_items": ["Build an AI Document Q&A Assistant with Vector DB", "Deploy model endpoint on cloud container"], "estimated_hours": int(hours * 40)}
        p4 = {"phase_number": 4, "name": "Phase 4: MLOps, System Design & Interview Mastery", "duration": "Weeks 17-24", "milestone_tag": "JOB READY", "description": "Monitoring, CI/CD for models, AI system design, and interview readiness.", "topics": ["MLOps Pipelines (MLflow/DVC)", "AI System Design Interviews", "Research Paper Walkthroughs"], "action_items": ["Deploy production ML pipeline on AWS/GCP", "Record demo walkthrough for GitHub portfolio"], "estimated_hours": int(hours * 30)}
        certs = ["DeepLearning.AI TensorFlow Developer", "AWS Certified Machine Learning - Specialty"]
    elif "cyber" in goal_lower or "security" in goal_lower:
        techs = ["Linux CLI", "Networking (TCP/IP, DNS)", "Wireshark", "Python Scripting", "Nmap", "Metasploit", "SIEM (Splunk)"]
        p1 = {"phase_number": 1, "name": "Phase 1: Networking & Operating Systems Foundations", "duration": "Weeks 1-4", "milestone_tag": "FOUNDATION", "description": "Deep understanding of TCP/IP, OSI model, Linux administration, and security basics.", "topics": ["Linux Command Line & Bash", "Network Protocols & Subnetting", "Port Scanning & Firewall Config"], "action_items": ["Set up VirtualBox security lab with Kali Linux", "Analyze packet captures using Wireshark"], "estimated_hours": int(hours * 25)}
        p2 = {"phase_number": 2, "name": "Phase 2: Vulnerability Analysis & Scripting", "duration": "Weeks 5-10", "milestone_tag": "CORE SKILLS", "description": "Security testing, Python automation scripts, and vulnerability scanning.", "topics": ["Python for Security Automation", "OWASP Top 10 Web Vulnerabilities", "Nmap & Vulnerability Scanning"], "action_items": ["Build a network port and banner scanner in Python", "Complete 10 TryHackMe beginner rooms"], "estimated_hours": int(hours * 35)}
        p3 = {"phase_number": 3, "name": "Phase 3: Defensive & Offensive Operations", "duration": "Weeks 11-16", "milestone_tag": "PROJECTS", "description": "SOC analyst operations, log analysis, SIEM tools, and penetration testing.", "topics": ["SIEM & Log Analysis with Splunk", "Incident Response Protocols", "Privilege Escalation Fundamentals"], "action_items": ["Set up personal SOC home lab with Splunk", "Write detailed incident response report for a simulated breach"], "estimated_hours": int(hours * 35)}
        p4 = {"phase_number": 4, "name": "Phase 4: Certifications, Portfolio & Job Readiness", "duration": "Weeks 17-24", "milestone_tag": "JOB READY", "description": "Hands-on CTF demonstrations, CompTIA Security+ prep, and technical interviews.", "topics": ["CompTIA Security+ Exam Domain Review", "Threat Intelligence Analysis", "Technical Security Interviews"], "action_items": ["Publish 3 CTF writeups on Medium / Personal Blog", "Prepare defense case study for hiring managers"], "estimated_hours": int(hours * 30)}
        certs = ["CompTIA Security+", "Certified Ethical Hacker (CEH) or BTL1"]
    else:  # Full Stack / Software Developer
        techs = ["HTML5/CSS3", "JavaScript (ES6+)", "React / Vue", "Node.js / Python", "SQL & NoSQL", "Git & GitHub", "Docker & CI/CD"]
        p1 = {"phase_number": 1, "name": "Phase 1: Web Foundations & Modern JavaScript", "duration": "Weeks 1-4", "milestone_tag": "FOUNDATION", "description": "Responsive layout, semantic HTML, modern CSS, and core JavaScript logic.", "topics": ["HTML5 Semantic Tags & CSS Flex/Grid", "JavaScript DOM Manipulation & Events", "Async JS, Fetch API, and Promises"], "action_items": ["Build 3 responsive interactive landing pages", "Publish code to GitHub with clean READMEs"], "estimated_hours": int(hours * 25)}
        p2 = {"phase_number": 2, "name": "Phase 2: Frontend Frameworks & State Management", "duration": "Weeks 5-10", "milestone_tag": "CORE SKILLS", "description": "Modern frontend framework (React/Vue), reusable components, and client-side routing.", "topics": ["Component Lifecycle & Hooks", "State Management & Context", "RESTful API Consumption & Authentication"], "action_items": ["Build a full-featured eCommerce / Kanban dashboard in React", "Integrate third-party API with error boundaries"], "estimated_hours": int(hours * 35)}
        p3 = {"phase_number": 3, "name": "Phase 3: Backend Architecture & Databases", "duration": "Weeks 11-16", "milestone_tag": "PROJECTS", "description": "Server-side REST API development, database modeling, JWT authentication, and security.", "topics": ["Express.js or Python Flask/FastAPI", "SQL Relational Modeling & Migrations", "JWT Auth, Rate Limiting & Middleware"], "action_items": ["Design and deploy secure multi-tenant REST API", "Optimize database indexing and query latency"], "estimated_hours": int(hours * 35)}
        p4 = {"phase_number": 4, "name": "Phase 4: DevOps, Portfolio & Technical Interviews", "duration": "Weeks 17-24", "milestone_tag": "JOB READY", "description": "Docker containerization, CI/CD deployment, system design, and algorithmic interview prep.", "topics": ["Docker & Cloud Deployment (Vercel/Render)", "Data Structures & LeetCode Top 75", "System Design Fundamentals"], "action_items": ["Launch live full-stack capstone project with custom domain", "Polish ATS-friendly software engineer resume"], "estimated_hours": int(hours * 30)}
        certs = ["Meta Front-End / Back-End Developer Certificate", "AWS Certified Cloud Practitioner"]

    return {
        "title": f"Tailored {career_goal} Career Roadmap",
        "overview": f"A comprehensive step-by-step master plan designed for {current_level} level, dedicating {hours} hours daily over {duration} to achieve job readiness as a competitive {career_goal}.",
        "prerequisites": "Basic computer literacy, familiarity with command line terminal, and a growth mindset.",
        "phases": [p1, p2, p3, p4],
        "milestones_timeline": [
            "FOUNDATION", "PROGRAMMING", "CORE SKILLS", "PROJECTS", "PORTFOLIO", "INTERVIEW", "JOB READY"
        ],
        "important_technologies": techs,
        "projects": [
            {
                "title": f"Production {career_goal} Platform",
                "description": "Full-stack application featuring authentication, real-time analytics, and persistent storage.",
                "tech": ", ".join(techs[:4])
            },
            {
                "title": "Interactive Data & Workflow Automation Engine",
                "description": "High performance tool connecting external APIs, background processing, and custom dashboards.",
                "tech": ", ".join(techs[3:7])
            }
        ],
        "certifications": certs,
        "interview_prep": "Focus on data structures, algorithmic problem solving (LeetCode), behavioral STAR stories, and system architecture tradeoffs.",
        "portfolio_requirements": "3 deployed web applications with live URLs, GitHub repositories with clear documentation, unit tests, and demo videos.",
        "job_prep": "Build an active GitHub contribution graph, optimize your LinkedIn profile for recruiter search, and connect with 5 industry professionals weekly."
    }


# =====================================================================
# 3. SKILL GAP ANALYZER
# =====================================================================
def analyze_skill_gap_ai(target_career, current_skills_input):
    """Analyze missing skills, status, priority, and learning order."""
    prompt = f"""Target Career: {target_career}
Current Skills: {current_skills_input}

Analyze the skill gap for this career.
Return a valid JSON object with the following format:
{{
  "target_career": "{target_career}",
  "match_percentage": 65,
  "summary": "Short 2 sentence evaluation of the candidate's current readiness.",
  "skills": [
    {{
      "name": "Python",
      "status": "✓",
      "priority": "High",
      "category": "Languages",
      "learning_order": 1,
      "proficiency": 80,
      "why_needed": "Fundamental language for data handling and backend."
    }},
    {{
      "name": "SQL",
      "status": "✓",
      "priority": "High",
      "category": "Databases",
      "learning_order": 2,
      "proficiency": 75,
      "why_needed": "Essential for querying and managing structured data."
    }},
    {{
      "name": "Statistics",
      "status": "Missing",
      "priority": "High",
      "category": "Concepts",
      "learning_order": 3,
      "proficiency": 15,
      "why_needed": "Required for hypothesis testing and metric validation."
    }},
    {{
      "name": "Power BI / Tableau",
      "status": "Missing",
      "priority": "High",
      "category": "BI Tools",
      "learning_order": 4,
      "proficiency": 10,
      "why_needed": "Primary visualization tool used by business stakeholders."
    }},
    {{
      "name": "Pandas & NumPy",
      "status": "Missing",
      "priority": "High",
      "category": "Libraries",
      "learning_order": 5,
      "proficiency": 20,
      "why_needed": "Standard libraries for high performance data manipulation."
    }},
    {{
      "name": "Machine Learning",
      "status": "Missing",
      "priority": "Medium",
      "category": "Advanced",
      "learning_order": 6,
      "proficiency": 5,
      "why_needed": "Predictive modeling and advanced analytics capabilities."
    }}
  ],
  "learning_order_summary": ["First master foundational skills", "Then build intermediate pipelines", "Finally tackle advanced models"],
  "recommended_next_step": "Dedicate the next 2 weeks to mastering high-priority missing skills."
}}
"""
    raw = call_openai_chat([{"role": "user", "content": prompt}], response_json=True)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass

    return build_fallback_skill_gap(target_career, current_skills_input)


def build_fallback_skill_gap(target_career, current_skills_input):
    """Fallback skill gap matrix calculation."""
    current_tokens = [s.strip().lower() for s in (current_skills_input or "").replace(',', '\n').split('\n') if s.strip()]

    # Skill catalogues for common careers
    career_catalogue = {
        "data analyst": [
            ("Python", "High", "Languages", 85, "Core scripting language for automation and ETL"),
            ("SQL", "High", "Databases", 90, "Essential for querying transactional and warehouse databases"),
            ("Excel", "Medium", "Spreadsheets", 80, "Universal business tool for rapid data modeling and pivot tables"),
            ("Statistics", "High", "Concepts", 75, "Underpins variance, hypothesis testing, and AB test interpretation"),
            ("Power BI", "High", "BI Tools", 70, "Industry standard interactive dashboard and KPI development"),
            ("Pandas", "High", "Libraries", 80, "Data frame wrangling, cleansing, and manipulation"),
            ("Data Visualization", "Medium", "Concepts", 65, "Visual communication principles and executive charts"),
            ("Machine Learning", "Medium", "Advanced", 50, "Predictive analytics and clustering algorithms")
        ],
        "full stack developer": [
            ("HTML/CSS", "High", "Frontend", 90, "Semantic structure and modern responsive CSS layout"),
            ("JavaScript", "High", "Languages", 95, "Client and server scripting standard for modern web"),
            ("React", "High", "Frontend", 85, "Component-driven user interface architecture"),
            ("Node.js / Python", "High", "Backend", 85, "Server-side REST API development and business logic"),
            ("SQL / Databases", "High", "Databases", 80, "Relational data persistence, schema design, and queries"),
            ("Git / GitHub", "High", "DevOps", 85, "Version control, branching strategies, and collaboration"),
            ("REST APIs", "High", "Architecture", 80, "Stateless API contract design and HTTP error handling"),
            ("Docker", "Medium", "DevOps", 65, "Containerization for consistent deployment across environments")
        ],
        "ai engineer": [
            ("Python", "High", "Languages", 95, "Primary ecosystem for artificial intelligence and machine learning"),
            ("Linear Algebra & Calculus", "High", "Math", 75, "Foundational math for neural activations and backprop"),
            ("PyTorch / TensorFlow", "High", "Frameworks", 85, "Deep learning model construction and training"),
            ("Scikit-Learn", "High", "ML Libraries", 80, "Classical machine learning algorithms and pipelines"),
            ("FastAPI", "High", "Backend", 75, "High-performance asynchronous model inference APIs"),
            ("Vector Databases", "High", "AI Tools", 80, "Similarity search and embeddings for RAG systems"),
            ("Docker & Cloud", "Medium", "DevOps", 70, "Packaging and scaling AI workloads in production"),
            ("MLOps", "Medium", "DevOps", 60, "Model registry, experiment tracking, and drift monitoring")
        ],
        "cybersecurity": [
            ("Linux CLI", "High", "Operating Systems", 90, "Command line administration and bash shell scripting"),
            ("Networking (TCP/IP)", "High", "Infrastructure", 90, "Packet analysis, routing, DNS, and OSI layer architecture"),
            ("Wireshark", "High", "Tools", 80, "Deep packet inspection and protocol anomaly detection"),
            ("Python Scripting", "High", "Languages", 75, "Security automation, log parsing, and exploit prototyping"),
            ("Nmap & Recon", "High", "Security Tools", 80, "Host discovery, port scanning, and vulnerability detection"),
            ("SIEM (Splunk)", "High", "Defensive", 75, "Centralized event logging, alerting, and incident response"),
            ("OWASP Top 10", "High", "Concepts", 85, "Web application attack vectors and mitigation strategies"),
            ("Cryptography", "Medium", "Concepts", 65, "Encryption protocols, TLS, hashing, and key management")
        ]
    }

    # Match closest career
    key_found = "full stack developer"
    for k in career_catalogue:
        if k in target_career.lower():
            key_found = k
            break

    catalogue = career_catalogue[key_found]
    analyzed_skills = []
    matched_count = 0

    for idx, (name, priority, category, base_prof, why) in enumerate(catalogue, start=1):
        is_matched = any(token in name.lower() or name.lower() in token for token in current_tokens)
        if is_matched:
            matched_count += 1
            status = "✓"
            proficiency = base_prof
        else:
            status = "Missing"
            proficiency = 15

        analyzed_skills.append({
            "name": name,
            "status": status,
            "priority": priority,
            "category": category,
            "learning_order": idx,
            "proficiency": proficiency,
            "why_needed": why
        })

    match_pct = int((matched_count / len(catalogue)) * 100) if catalogue else 40

    return {
        "target_career": target_career,
        "match_percentage": match_pct,
        "summary": f"You possess {matched_count} of {len(catalogue)} fundamental skills for {target_career}. Addressing the {len(catalogue) - matched_count} identified missing skills will significantly increase your hiring potential.",
        "skills": analyzed_skills,
        "learning_order_summary": [
            "1. Close foundational high-priority gaps first",
            "2. Integrate databases and API connectivity",
            "3. Build full-stack portfolio demonstrations"
        ],
        "recommended_next_step": f"Focus immediately on learning the highest priority missing skills: {[s['name'] for s in analyzed_skills if s['status'] == 'Missing'][:3]}."
    }


# =====================================================================
# 4. PROJECT GENERATOR
# =====================================================================
def generate_project_ai(career, level, tech, difficulty):
    """Generate comprehensive, industry-grade portfolio project blueprint."""
    prompt = f"""Generate a standout portfolio project for:
Career: {career}
Skill Level: {level}
Primary Technologies: {tech or 'Modern industry stack'}
Difficulty: {difficulty}

Return a valid JSON object matching this exact format:
{{
  "title": "Inspiring Project Title",
  "career_target": "{career}",
  "difficulty": "{difficulty}",
  "technology": "{tech}",
  "problem_statement": "Comprehensive problem statement explaining why this project is valuable.",
  "features": [
    "Feature 1: Interactive user authentication & role management",
    "Feature 2: Real-time data processing and analytics dashboard",
    "Feature 3: Export reports and automated email alerts",
    "Feature 4: Responsive mobile-friendly UI with dark mode"
  ],
  "technologies": ["Tech 1", "Tech 2", "Tech 3", "Tech 4", "Tech 5"],
  "database_design": "Detailed SQL or document database schema describing tables/collections, columns, types, and foreign key relationships.",
  "folder_structure": "ASCII directory tree demonstrating professional repository architecture.",
  "development_steps": [
    "Step 1: Environment setup and database schema initialization",
    "Step 2: Backend REST API route implementation and testing",
    "Step 3: Frontend state management and UI component assembly",
    "Step 4: End-to-end integration and automated test suite",
    "Step 5: Production containerization and cloud deployment"
  ],
  "expected_output": "Description of the live working application and user experience.",
  "resume_description": "• Built and deployed a production-grade full-stack platform using [Tech] serving [X users] with sub-100ms latency.\\n• Implemented automated CI/CD pipeline reducing deployment overhead by 40%."
}}
"""
    raw = call_openai_chat([{"role": "user", "content": prompt}], response_json=True)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass

    return build_fallback_project(career, level, tech, difficulty)


def build_fallback_project(career, level, tech, difficulty):
    """High-quality predefined project blueprint fallback."""
    tech_str = tech if tech else "Python, Flask, SQLite, Chart.js, HTML5/CSS3"
    
    return {
        "title": f"AI-Powered {career} Intelligent Workflow & Analytics Engine",
        "career_target": career,
        "difficulty": difficulty,
        "technology": tech_str,
        "problem_statement": f"Junior candidates in {career} often lack real-world full-stack projects showcasing end-to-end data pipelines, asynchronous processing, and measurable user utility. This application solves a concrete business operations problem by collecting structured inputs, running predictive intelligence algorithms, and presenting executive-ready visualization dashboards.",
        "features": [
            "Dynamic telemetry data ingestion & multi-format export (JSON, CSV, PDF)",
            "Automated KPI anomaly detection and threshold-based alerting",
            "Interactive analytics dashboard built with modern glassmorphic Chart.js views",
            "Role-based access control (Admin, Analyst, Viewer) with secure session handling",
            "Full RESTful API interface documented with Swagger/Postman specifications"
        ],
        "technologies": [t.strip() for t in tech_str.split(',') if t.strip()] + ["Git", "Docker", "REST API"],
        "database_design": """-- Database Schema Design (SQLite / PostgreSQL)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role VARCHAR(20) DEFAULT 'Analyst',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analytics_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    metrics_data JSON NOT NULL,
    status VARCHAR(50) DEFAULT 'Processed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "folder_structure": """project-root/
├── app.py                 # Application server & endpoint routing
├── config.py              # Environment configuration & DB constants
├── models.py              # SQLAlchemy database models & schemas
├── services/
│   ├── analytics.py       # Core algorithmic calculations & aggregation
│   └── notifier.py        # Asynchronous notification dispatcher
├── static/
│   ├── css/style.css      # Custom responsive dark-mode styling
│   └── js/main.js         # Chart rendering & client-side API requests
├── templates/
│   ├── index.html         # Landing page and telemetry input forms
│   └── dashboard.html     # Real-time analytics & visual graphs
├── tests/
│   └── test_api.py        # Automated endpoint integration tests
├── Dockerfile             # Container configuration
└── requirements.txt       # Frozen application dependencies""",
        "development_steps": [
            "Milestone 1: Scaffold repository, configure virtual environment, and initialize database schemas.",
            "Milestone 2: Develop backend REST API endpoints with comprehensive input validation and error handling.",
            "Milestone 3: Construct responsive web user interface using CSS variables, semantic tags, and Chart.js.",
            "Milestone 4: Connect frontend asynchronous fetch calls with backend routes and test edge cases.",
            "Milestone 5: Write automated unit tests, create Dockerfile, and deploy to cloud staging environment."
        ],
        "expected_output": "A fully deployed, interactive web application featuring real-time graphical data dashboards, responsive navigation, zero console errors, and comprehensive GitHub documentation with architecture diagrams.",
        "resume_description": f"• Engineered an end-to-end {career} platform utilizing {tech_str}, automating workflow analytics and decreasing data processing cycle times by 35%.\n• Designed scalable relational database schemas with foreign-key cascades and optimized SQL query indexing for sub-80ms response times.\n• Packaged and deployed application with Docker containers, maintaining 99.8% uptime."
    }


# =====================================================================
# 5. RESUME ANALYZER
# =====================================================================
def analyze_resume_ai(resume_text, target_career="Software Engineer"):
    """Perform comprehensive ATS, keyword, and section audit."""
    prompt = f"""Target Career: {target_career}
Resume Content:
\"\"\"{resume_text[:4000]}\"\"\"

Analyze this resume for alignment with the target career.
Calculate an ATS Score (0-100) based on this transparent rubric:
- Keyword Relevance & Density (30% weight)
- Quantifiable Metrics & Action Verbs (25% weight)
- Section Completeness & Clear Structure (25% weight)
- Formatting Cleanliness & Readability (20% weight)

Return a valid JSON object matching this exact schema:
{{
  "ats_score": 78,
  "career_match_pct": 82,
  "summary": "Clear 2-sentence executive summary of the resume's strengths and weaknesses.",
  "extracted_skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
  "missing_keywords": ["Keyword 1", "Keyword 2", "Keyword 3", "Keyword 4"],
  "projects_critique": "Critique of how projects are described, with tips for adding metrics and tech stack tags.",
  "education_critique": "Assessment of education section clarity, relevant coursework, and credentials.",
  "experience_critique": "Review of work experience bullet points and recommendations for stronger action verbs.",
  "formatting_suggestions": [
    "Formatting tip 1",
    "Formatting tip 2",
    "Formatting tip 3"
  ],
  "ats_improvements": [
    "ATS improvement 1",
    "ATS improvement 2",
    "ATS improvement 3"
  ]
}}
"""
    raw = call_openai_chat([{"role": "user", "content": prompt}], response_json=True)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass

    return build_fallback_resume_analysis(resume_text, target_career)


def build_fallback_resume_analysis(resume_text, target_career):
    """Fallback transparent ATS evaluation rubric."""
    text_lower = resume_text.lower() if resume_text else ""
    
    # Check key sections
    has_skills = any(w in text_lower for w in ["skills", "technologies", "tech stack", "competencies"])
    has_experience = any(w in text_lower for w in ["experience", "work history", "employment", "internship"])
    has_projects = any(w in text_lower for w in ["projects", "personal projects", "portfolio", "capstone"])
    has_education = any(w in text_lower for w in ["education", "degree", "university", "bachelor", "b.tech", "college"])
    has_numbers = any(char.isdigit() for char in resume_text)

    # Keywords catalogue
    common_skills = [
        "python", "javascript", "react", "sql", "git", "docker", "aws", "rest api",
        "html", "css", "linux", "pandas", "machine learning", "mongodb", "postgresql",
        "fastapi", "flask", "node.js", "agile", "ci/cd"
    ]
    extracted = [s.title() for s in common_skills if s in text_lower]
    if not extracted:
        extracted = ["Python", "Problem Solving", "Git", "SQL", "Team Collaboration"]

    career_keywords = {
        "data analyst": ["sql", "excel", "power bi", "tableau", "statistics", "pandas", "data cleansing", "kpi"],
        "full stack developer": ["react", "node.js", "rest api", "sql", "git", "docker", "javascript", "ci/cd"],
        "ai engineer": ["pytorch", "tensorflow", "python", "embeddings", "vector db", "scikit-learn", "fastapi"],
        "cybersecurity": ["wireshark", "linux", "siem", "nmap", "owasp", "tcp/ip", "incident response"]
    }
    
    key_role = "full stack developer"
    for r in career_keywords:
        if r in target_career.lower():
            key_role = r
            break
            
    expected = career_keywords[key_role]
    missing = [w.title() for w in expected if w not in text_lower][:5]
    if not missing:
        missing = ["Cloud Deployment (AWS/GCP)", "Automated Unit Testing", "CI/CD Pipelines"]

    # Calculate rubric-based score
    score = 45
    if has_skills: score += 12
    if has_experience: score += 12
    if has_projects: score += 12
    if has_education: score += 10
    if has_numbers: score += 9
    score = min(score, 92)

    return {
        "ats_score": score,
        "career_match_pct": min(score + 4, 95),
        "summary": f"Your resume demonstrates clear technical foundations for {target_career}, but lacks critical industry keywords and quantified bullet points required to bypass strict Applicant Tracking Systems (ATS).",
        "extracted_skills": extracted,
        "missing_keywords": missing,
        "projects_critique": "Your projects show functional understanding, but lack quantifiable impact metrics (e.g., latency reduction, user throughput, test coverage) and direct links to live deployments and GitHub repositories.",
        "education_critique": "The education section is appropriately positioned. Ensure your graduation year, relevant coursework, and honors/awards are clearly demarcated without excessive whitespace.",
        "experience_critique": "Transform passive duty descriptions into active accomplishment statements starting with strong action verbs (e.g., 'Engineered', 'Architected', 'Streamlined', 'Deployed').",
        "formatting_suggestions": [
            "Use standard, machine-readable headings (Work Experience, Education, Technical Skills).",
            "Avoid multi-column tables, text boxes, and complex graphics that confuse ATS parsers.",
            "Maintain consistent date formatting throughout (e.g., Month Year - Month Year)."
        ],
        "ats_improvements": [
            f"Infuse {', '.join(missing[:3])} directly into relevant project descriptions.",
            "Quantify bullet points using the Google X-Y-Z formula: 'Accomplished [X] as measured by [Y] by doing [Z]'.",
            "Include your clean GitHub and LinkedIn profile URLs in the header contact section."
        ]
    }


# =====================================================================
# 6. INTERVIEW PRACTICE ENGINE
# =====================================================================
def generate_interview_question_ai(career, difficulty, question_number=1, previous_history=None):
    """Generate role and difficulty-specific interview question."""
    prompt = f"""Career Role: {career}
Difficulty Level: {difficulty}
Question Number: {question_number}
Previous Q&A Context: {previous_history or 'None, this is the first question.'}

Generate an authentic, high-quality technical or behavioral interview question for this role.
Return a valid JSON object matching:
{{
  "question_number": {question_number},
  "question": "The interview question text.",
  "category": "Technical Concept / System Architecture / Behavioral",
  "hint": "A subtle hint to guide the candidate's thoughts."
}}
"""
    raw = call_openai_chat([{"role": "user", "content": prompt}], response_json=True)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass

    return build_fallback_interview_question(career, difficulty, question_number)


def build_fallback_interview_question(career, difficulty, question_number=1):
    """Rich curated question bank for interview simulation."""
    c_lower = career.lower()
    
    questions = {
        "data analyst": [
            {"q": "Can you explain the difference between WHERE and HAVING in SQL, and provide a concrete scenario where you must use HAVING?", "cat": "SQL & Databases", "hint": "Think about aggregations like GROUP BY and aggregate functions."},
            {"q": "How would you handle a dataset with 20% missing values in a critical column before reporting to stakeholders?", "cat": "Data Cleansing", "hint": "Consider imputation, median vs mean, data loss, and business context."},
            {"q": "Describe a time you discovered an unexpected trend or anomaly in the data. How did you communicate it to non-technical leaders?", "cat": "Storytelling & Communication", "hint": "Use the STAR method and focus on actionable business recommendations."}
        ],
        "full stack developer": [
            {"q": "Explain the difference between SQL and NoSQL databases. When would you architect a system with MongoDB versus PostgreSQL?", "cat": "System Design", "hint": "Discuss ACID compliance, schema flexibility, relation depth, and horizontal scaling."},
            {"q": "What happens under the hood when a user types a URL into their browser and presses Enter?", "cat": "Networking & Web Architecture", "hint": "Cover DNS resolution, TCP handshake, TLS negotiation, HTTP request/response, and DOM rendering."},
            {"q": "How do you handle authentication securely in a single-page application? Compare JWT stored in localStorage versus httpOnly cookies.", "cat": "Security & Architecture", "hint": "Consider XSS (Cross-Site Scripting) and CSRF (Cross-Site Request Forgery) attack vectors."}
        ],
        "ai engineer": [
            {"q": "What is the vanishing/exploding gradient problem in deep neural networks, and how do modern architectures like ResNets or transformers mitigate it?", "cat": "Deep Learning Theory", "hint": "Mention activation functions (ReLU), residual skip connections, and layer normalization."},
            {"q": "How does Retrieval-Augmented Generation (RAG) work, and how do you evaluate hallucination rates in production?", "cat": "Generative AI Systems", "hint": "Explain vector embeddings, cosine distance, context injection, and ground-truth validation."},
            {"q": "Explain the bias-variance tradeoff and how you use cross-validation and regularization to find the optimal model balance.", "cat": "Machine Learning Fundamentals", "hint": "Relate underfitting to high bias and overfitting to high variance."}
        ]
    }

    key = "full stack developer"
    for k in questions:
        if k in c_lower:
            key = k
            break

    q_list = questions[key]
    selected = q_list[(question_number - 1) % len(q_list)]
    return {
        "question_number": question_number,
        "question": selected["q"],
        "category": selected["cat"],
        "hint": selected["hint"]
    }


def evaluate_interview_answer_ai(career, difficulty, question, user_answer):
    """Evaluate candidate answer and generate constructive feedback."""
    prompt = f"""Career Role: {career}
Difficulty: {difficulty}
Question: \"{question}\"
Candidate's Answer: \"{user_answer}\"

Evaluate this candidate's response.
Provide an assessment with score (0-100), detailed constructive feedback, missing points, better answer structure, and an exemplary suggested answer.
Return a valid JSON object matching:
{{
  "score": 82,
  "rating": "Strong / Good / Needs Improvement",
  "feedback": "2-3 sentences of constructive feedback highlighting strengths and weaknesses.",
  "missing_points": [
    "Crucial point 1 omitted",
    "Technical edge case not addressed"
  ],
  "better_structure": "Guidance on how to structure this answer (e.g. definition -> practical example -> trade-offs).",
  "suggested_answer": "A clear, concise, and professional model answer that would impress an interviewer."
}}
"""
    raw = call_openai_chat([{"role": "user", "content": prompt}], response_json=True)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass

    return build_fallback_interview_evaluation(career, difficulty, question, user_answer)


def build_fallback_interview_evaluation(career, difficulty, question, user_answer):
    """Heuristic interview evaluation fallback."""
    ans_len = len(user_answer.strip()) if user_answer else 0
    score = 50
    if ans_len > 60: score += 15
    if ans_len > 150: score += 15
    if any(k in user_answer.lower() for k in ["because", "for example", "tradeoff", "performance", "trade-off", "latency", "scale"]):
        score += 10
    score = min(score, 90)

    rating = "Strong" if score >= 80 else ("Good" if score >= 65 else "Needs Improvement")

    return {
        "score": score,
        "rating": rating,
        "feedback": f"Your response demonstrates a practical baseline understanding of the core concept. To reach the senior tier, provide a concrete real-world engineering example and discuss architectural trade-offs.",
        "missing_points": [
            "Mentioning specific failure modes or edge cases in high-throughput environments.",
            "Connecting the technical theory directly to business or user impact."
        ],
        "better_structure": "1. Direct 1-sentence definition → 2. Core operational mechanics → 3. Concrete production example → 4. Trade-offs / Best practices.",
        "suggested_answer": f"In a production system for {career}, I prioritize clarity and resilience. First, I establish the theoretical foundation, then validate assumptions with testable metrics. For instance, when designing this component, I balance developer velocity against performance overhead, ensuring comprehensive monitoring and logging are in place."
    }
