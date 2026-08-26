# Reverse Learning App

### AI-Powered Learning Intelligence & Interview Preparation Platform

> **"An adaptive AI learning platform that evaluates whether students truly understand concepts by asking them to explain in their own words, detecting knowledge gaps, dynamically adapting study roadmaps, and conducting resume-targeted mock interviews."**

---

### 🌟 Key Platform Highlights

- **✓ Reverse Learning Engine:** Evaluate true comprehension using the Feynman Technique (learning by teaching).
- **✓ Multi-Dimensional AI Evaluation:** 4D evaluation scoring across Technical Accuracy, Concept Understanding, Communication, and Grammar.
- **✓ Automated Knowledge Gap Detection:** Identify micro-level concept failures rather than simple percentage scores.
- **✓ Dynamic Adaptive Roadmap:** Real-time learning path adjustments based on performance and user career goals.
- **✓ Smart Spaced Repetition:** Ebbinghaus memory curve scheduler for optimal topic revision.
- **✓ Resume Intelligence:** Extract skills/projects from PDF & DOCX resumes to build personalized interview questions.
- **✓ Adaptive AI Mock Interviews:** Dynamic difficulty adjustments and follow-up probes during live interview practice.
- **✓ AI Communication Coach:** Track speech pacing (WPM), filler words (*"um"*, *"like"*), clarity, and vocal confidence.
- **✓ Secure Multi-Tenant Architecture:** Strict user isolation, OWASP security headers, JWT validation, and RBAC rules.
- **✓ Master QA & Resiliency:** Comprehensive test suite handling AI rate limits (403/429), malformed JSON, and DB rollbacks.

---

## 💡 Why This Project Is Different

Most learning platforms rely on passive content consumption (videos, reading) or simple multiple-choice quizzes that foster the **illusion of competence**. 

**Reverse Learning App is NOT an AI chatbot wrapper or static quiz app.** It establishes a **continuous closed-loop learning pipeline**:

```
 Learn Concept
      │
      ▼
 Explain to AI (Reverse Learning)
      │
      ▼
 Structured AI Evaluation (4D Metrics)
      │
      ▼
 Detect Specific Knowledge Gaps
      │
      ▼
 Calculate Adaptive Priority & Update Roadmap
      │
      ▼
 Smart Spaced Revision & Retest
      │
      ▼
 Resume-Targeted Adaptive Mock Interview
      │
      ▼
 Track Longitudinal Communication & Skill Analytics
```

---

## 📌 Problem Statement vs. Solution

### The Problem
Traditional learning methods fail technical students and job seekers because:
- **Illusion of Competence:** Students passively watch tutorials without verifying if they can articulate the material.
- **Generic Quizzes:** Multiple-choice tests fail to measure technical depth, communication skills, or explanation clarity.
- **Static Roadmaps:** Fixed course outlines do not adapt when a student struggles with foundational prerequisites.
- **Irrelevant Interview Prep:** Generic practice questions ignore a candidate's actual resume experience and project background.
- **Unmeasured Soft Skills:** Students receive zero feedback on filler words, speaking pace, and structural clarity.

### The Solution
The **Reverse Learning App** turns the learning paradigm upside down:
1. **Learn a Concept:** Select a target topic from an extensive multi-disciplinary curriculum (Python, Java, Full Stack, SQL, AI/ML, Soft Skills).
2. **Teach the AI:** Explain the concept in your own words via text or voice.
3. **Receive 4D Feedback:** The Gemini AI engine grades technical accuracy, concept mastery, completeness, examples, relevance, communication, and grammar out of 100.
4. **Identify Knowledge Gaps:** Failed sub-concepts are isolated into actionable weak spots.
5. **Adaptive Recommendations:** The system dynamically computes the next priority topic to study.
6. **Smart Revision:** Spaced repetition schedules review sessions before memory decay occurs.
7. **Dynamic Roadmap:** Career goals automatically update estimated completion time and topic sequence.
8. **Resume Intelligence:** Upload `.pdf` or `.docx` resumes to extract projects and generate ATS targeted questions.
9. **Adaptive Mock Interviews:** Questions increase or decrease in difficulty dynamically based on answer quality.
10. **Communication Coaching:** Analyze filler words, speaking pace (WPM), and clarity metrics.
11. **Master Analytics:** Track longitudinal progress via interactive Radar charts and trend graphs.

---

## ✨ Features Breakdown

### 🎯 1. Learning Intelligence Dashboard
- Aggregated Overall Mastery Score.
- Technical Mastery vs. Communication Progress.
- Connected 6-Step Student Learning Pipeline Banner.
- Strongest & Weakest Topic breakdown.
- Recommended Next Focus Action & AI Insights.

### 🔍 2. Knowledge Gap Engine
- Automated tracking of failed concepts vs. mastered topics.
- Attempt history tracking and accuracy ratio.
- Micro-level concept diagnostics (e.g. *"Understands binary search time complexity, but fails edge-case boundary conditions"*).

### 🤖 3. Multi-Dimensional AI Evaluation Engine
- **Technical Accuracy (0-100):** Correctness of code logic and domain theory.
- **Concept Understanding (0-100):** Depth of explanation and intuitive grasp.
- **Completeness & Examples (0-100):** Presence of code snippets, analogies, and edge cases.
- **Communication & Grammar (0-100):** Vocabulary quality, sentence structure, and clarity.
- **Advanced Version Suggestions:** Generates a polished, professional version of the student's explanation to learn from.

### 🗺️ 4. Dynamic Learning Roadmap
- Customized career targets (e.g., *Backend Security Engineer*, *Full Stack Developer*, *AI/ML Engineer*).
- Dynamic time estimation based on user weekly availability (hours/day, days/week).
- Automated topic re-ordering when prerequisites are failed.

### 🔄 5. Smart Spaced Revision Scheduler
- Ebbinghaus memory curve implementation.
- Categorization into *Due Today*, *Overdue*, and *Upcoming*.
- Performance-driven review interval scaling.

### 📄 6. Resume Intelligence Engine
- Multi-format document parser (`PyMuPDF` for `.pdf` and `python-docx` for `.docx`).
- Automated extraction of technical skills, projects, work experience, and education.
- ATS keyword gap analysis against target job roles.
- Personalized, project-specific interview question generation.

### 🎙️ 7. Adaptive AI Mock Interviewer
- Real-time difficulty scaling (EASY $\rightarrow$ MEDIUM $\rightarrow$ HARD).
- Dynamic follow-up probe questions based on previous answer weaknesses.
- Comprehensive post-interview feedback report with overall scores and problem-solving breakdowns.

### 🗣️ 8. AI Communication Coach
- Voice & text transcript analysis.
- Detection of filler words (*"um"*, *"like"*, *"basically"*, *"you know"*).
- Estimated speaking pace calculation (Words Per Minute - WPM).
- Structural advice and actionable confidence recommendations.

### 🏆 9. Gamification & Achievement Engine
- Study streak counter with active flame indicators.
- Unlockable achievement badges (e.g., *First Step*, *Streak Master*, *Interview Ace*).
- Real-time achievement unlock notifications.

### 🔒 10. Security & Multi-Tenant Architecture
- User isolation: Strict tenant scoping preventing User A from querying User B's interviews, resumes, or evaluations.
- JWT stateless authentication with hashed passwords (`bcrypt`).
- OWASP recommended security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`).
- Executable (`.exe`, `.js`) and path-traversal upload protection.

---

## 🏗️ System Architecture

```
                  +-----------------------------------+
                  |         Student User (Client)     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   React + Vite Frontend Application|
                  +-----------------------------------+
                                    | REST APIs (Axios + JWT)
                                    v
                  +-----------------------------------+
                  |       FastAPI Backend Server      |
                  |     (Security, Auth & Routing)    |
                  +-----------------------------------+
                                    |
     +------------------------------+------------------------------+
     |                              |                              |
     v                              v                              v
+---------------------+       +-------------------+       +-----------------------+
| PostgreSQL Database |       |  Google Gemini AI |       | Resume Document Parser|
|  (SQLAlchemy ORM)   |       |  Evaluation Engine|       | (PyMuPDF & docx)      |
+---------------------+       +-------------------+       +-----------------------+
     |                              |                              |
     +------------------------------+------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Knowledge Gap & Adaptive Engines  |
                  +-----------------------------------+
```

---

## 🔄 Core AI & System Workflows

### 1. Reverse Learning & Evaluation Workflow
```
Student Explanation  --->  FastAPI Endpoint  --->  Gemini 1.5/2.0 API  --->  JSON Structured Parse
                                                                                   |
Dashboard Analytics  <---  Database Update   <---  Knowledge Gap Engine <----------+
```

### 2. Adaptive Learning & Roadmap Workflow
```
Student Evaluation Result  --->  Mastery Score Calculated  --->  Knowledge Gap Identified
                                                                       |
Updated Roadmap Timeline   <---  Priority Score Recalculated <---------+
```

### 3. Resume-Targeted Interview Workflow
```
Resume Upload (.pdf/.docx) ---> Document Text Extraction ---> Gemini ATS & Project Parser
                                                                      |
Final Interview Report     <--- Dynamic Difficulty Probe    <--- Generated Custom Qs
```

---

## 🗄️ Database Schema & Entities

The application uses SQLAlchemy ORM backed by SQLite (with production support for PostgreSQL):

```
       +------------------+
       |      User        |
       +------------------+
         |      |       |
         |      |       +------------------------------------+
         |      v                                            v
         |    +-------------------+                +-------------------+
         |    |   Evaluations     |                |     Roadmaps      |
         |    +-------------------+                +-------------------+
         |              |                                    |
         |              v                                    v
         |    +-------------------+                +-------------------+
         |    |  Knowledge Gaps   |                |   Roadmap Items   |
         |    +-------------------+                +-------------------+
         |
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
+------------------+ +---------------+ +-----------------------+
|    Interviews    | |    Resumes    | | Communication Analyses|
+------------------+ +---------------+ +-----------------------+
         |                  |
         v                  v
+------------------+ +---------------+
|Interview Questions| |Resume Questions|
+------------------+ +---------------+
```

### Core Database Entities:
- `users`: User credentials, target role preferences, hours per day, days per week.
- `curricula` & `topics`: Multi-disciplinary topic hierarchy and pre-seeded subjects.
- `evaluations`: 4D multi-dimensional scores, explanations, and AI insights.
- `user_mastery`: Aggregated topic mastery scores, attempt counts, and failure tracking.
- `roadmaps` & `roadmap_items`: Career roadmap milestones, target hours, and priority status.
- `resumes` & `resume_questions`: Uploaded document metadata, parsed JSON skills/projects, and generated questions.
- `interviews`, `interview_questions`, `interview_answers`: Interview session state, difficulty levels, and responses.
- `communication_analyses`: Speaking pace (WPM), filler word metrics, grammar corrections, and advice.
- `streaks` & `user_achievements`: Gamification tracking and unlock timestamps.

---

## 💻 Tech Stack

### Frontend
- **Framework:** React 19 (Vite)
- **Styling:** Tailwind CSS 4, Vanilla CSS Design System
- **Icons:** Lucide React
- **Charts & Data Viz:** Recharts (Radar charts, line trends, progress bars)
- **Routing:** React Router v7

### Backend
- **Framework:** Python 3.9+ & FastAPI (Async API Engine)
- **Server:** Uvicorn (ASGI)
- **Database Engine:** PostgreSQL (SQLAlchemy ORM + Psycopg driver)
- **Authentication:** JWT (`python-jose`) & Password Hashing (`passlib[bcrypt]`)

### AI & Document Parsing
- **AI LLM Engine:** Google Gemini API (`google-genai` / `google-generativeai`)
- **Document Text Extraction:** PyMuPDF (`fitz`) for PDF & `python-docx` for Word Documents

### Testing & QA
- **Unit & E2E Testing:** Python `unittest` & `fastapi.testclient`
- **Master Test Runner:** Custom master test runner ([`run_all_tests.py`](file:///c:/Users/anush/Desktop/reverse-learning-app/backend/run_all_tests.py))

---

## ⚡ Key Engineering Challenges & Solutions

| Challenge | Approach / Architecture | Result |
| :--- | :--- | :--- |
| **Structured AI Outputs** | Configured Pydantic JSON schemas and strict parsing prompts with fallback regex repair. | Zero application crashes from raw LLM text formatting discrepancies. |
| **Micro Knowledge-Gap Isolation** | Mapped evaluation sub-score failures against pre-seeded sub-concepts in `UserMastery`. | Precise weakness diagnostic instead of vague percentage scores. |
| **Multi-Tenant User Isolation** | Scoped database queries by authenticated `user_id` from JWT context across all routes. | Total isolation verified by security tests (User A cannot view User B resources). |
| **Resume Extraction & Parsing** | Built dual parser supporting PyMuPDF stream buffers and python-docx structure parsing. | Seamless parsing of complex PDF/DOCX resumes into structured JSON skills and project entities. |
| **Adaptive Interview Probing** | Created difficulty adjustment logic evaluating current answer scores against a sliding window. | Questions dynamically shift from Easy $\rightarrow$ Medium $\rightarrow$ Hard based on live performance. |
| **AI Failure Resiliency** | Implemented graceful fallback handlers for HTTP 403/429 Gemini API quota limits. | System degrades gracefully without breaking DB transactions or dropping client requests. |

---

## 🔌 Core API Endpoints

### 🔑 Authentication
| Method | Endpoint | Auth | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register new user account |
| `POST` | `/api/auth/login` | Public | Authenticate user & return JWT token |
| `GET` | `/api/auth/me` | Bearer JWT | Fetch active user profile |

### 📊 Dashboard & Analytics
| Method | Endpoint | Auth | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/dashboard-data` | Bearer JWT | Fetch aggregated dashboard metrics & student pipeline |
| `GET` | `/api/analytics` | Bearer JWT | Fetch skill radar data, score trends, and topic progress |

### 🎙️ Evaluation & Study Room
| Method | Endpoint | Auth | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/evaluate` | Bearer JWT | Submit concept explanation for 4D AI evaluation |
| `GET` | `/api/evaluations/history` | Bearer JWT | Fetch user evaluation submission history |
| `GET` | `/api/dashboard/knowledge-gap` | Bearer JWT | Retrieve user knowledge gap diagnostic matrix |

### 🗺️ Roadmap & Revision
| Method | Endpoint | Auth | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/roadmap` | Bearer JWT | Fetch user career roadmap and milestone items |
| `POST` | `/api/roadmap/generate` | Bearer JWT | Generate dynamic AI career roadmap |
| `GET` | `/api/revision/summary` | Bearer JWT | Get Ebbinghaus spaced revision schedule |

### 📄 Resume & Mock Interview
| Method | Endpoint | Auth | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/resume/upload` | Bearer JWT | Upload PDF/DOCX resume for ATS parsing |
| `POST` | `/api/interview/start` | Bearer JWT | Initialize adaptive mock interview session |
| `POST` | `/api/interview/answer` | Bearer JWT | Submit interview answer & trigger adaptive probe |
| `POST` | `/api/communication/analyze` | Bearer JWT | Analyze speech pacing, filler words, and clarity |

---

## 🔐 Environment Variables Configuration

Create a `.env` file inside the `backend/` directory based on `.env.example`:

```env
# Google Gemini AI API Key (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Database Connection (PostgreSQL default)
DATABASE_URL=postgresql+psycopg://username:password@host:5432/database_name

# JWT Security Settings
JWT_SECRET=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Frontend CORS Configuration
FRONTEND_URL=http://localhost:5173
```

> **Note:** Never commit actual API keys or `.env` files to source control.

---

## 🛠️ Installation & Setup Guide

### Prerequisites
- **Node.js** (v18+)
- **Python** (3.9+)

### 1. Clone Repository
```bash
git clone https://github.com/your-username/reverse-learning-app.git
cd reverse-learning-app
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Activate Virtual Environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Create Environment File
cp .env.example .env
# Edit backend/.env and insert your GEMINI_API_KEY
```

Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload
```
*Backend API will run at `http://localhost:8000` (Docs available at `http://localhost:8000/docs`).*

### 3. Frontend Setup
Open a new terminal window:
```bash
cd frontend

# Install Dependencies
npm install

# Start Development Server
npm run dev
```
*Frontend will run at `http://localhost:5173`.*

---

## 🧪 Production Testing Suite (Phase 13)

The project includes a comprehensive master QA test runner in [`backend/run_all_tests.py`](file:///c:/Users/anush/Desktop/reverse-learning-app/backend/run_all_tests.py):

To run all automated tests:
```bash
cd backend
python run_all_tests.py
```

### Test Suite Matrix:
- **Unit Engines Suite (`TestUnitEngines`):** Tests calculation of mastery, spaced revision decay, and achievement triggers.
- **Auth & Security Matrix (`TestAuthAndSecurity`):** Verifies bcrypt hashing, JWT validation, malicious file upload rejection (`.exe`, `.js`), and strict User A $\rightarrow$ User B isolation.
- **AI & DB Resiliency Matrix (`TestAIAndDBResiliency`):** Verifies graceful fallbacks when Gemini API returns 403/429 quota errors or malformed JSON, ensuring zero DB corruptions.
- **E2E User Journey (`TestE2EUserJourney`):** Validates the entire user pipeline from signup to roadmap, study evaluation, revision, interview, and analytics.

---

## 🛡️ Security & Privacy Features

- **Strict Tenant Data Isolation:** All database read/write queries enforce `user_id` filtering from JWT token claims.
- **File Upload Protection:** Strict MIME-type checking and file extension validation rejecting `.exe`, `.bat`, `.js`, and oversized files (>10MB).
- **Path Traversal Sanitization:** Filenames are cleaned of directory traversal tokens (`../`, `..\\`).
- **OWASP Header Compliance:** Configured default headers preventing MIME-sniffing and frame embedding attacks.
- **Zero API Key Leakage:** Backend secrets and AI credentials are strictly confined to server-side execution.

---

## 🖼️ Application Screenshots

![alt text](image.png)


## 🎥 Project Demo

- **Demo Status:** Local demonstration ready.
- **Live Deployment:** *Skipped intentionally for Phase 15 documentation.*

---

## 📁 Repository Structure

```
reverse-learning-app/
├── backend/
│   ├── app/
│   │   ├── ai_service/          # Gemini AI Agent & Prompt Orchestration
│   │   ├── routes/              # FastAPI Router Modules (17 Routers)
│   │   ├── services/            # Business Logic & Adaptive Engines
│   │   ├── auth.py              # JWT Authentication & Password Hashing
│   │   ├── database.py          # SQLAlchemy Session Management
│   │   ├── main.py              # Application Entrypoint & CORS Middleware
│   │   ├── models.py            # Database Models & ORM Entities
│   │   └── schemas.py           # Pydantic Request/Response Models
│   ├── tests/                   # Automated Unit, Security & E2E Test Suite
│   ├── .env.example             # Safe Environment Variable Template
│   ├── requirements.txt         # Backend Python Dependencies
│   └── run_all_tests.py         # Phase 13 Master Test Runner
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios HTTP Client Configuration
│   │   ├── components/          # Reusable UI & Dashboard Components
│   │   ├── context/             # React AuthContext State Management
│   │   ├── pages/               # Application Page Views (16 Pages)
│   │   ├── services/            # API Helper Functions
│   │   ├── App.jsx              # Router Setup & Application Container
│   │   └── main.jsx             # React DOM Mounting Script
│   ├── package.json             # Frontend Node Dependencies
│   └── vite.config.js           # Vite Configuration
├── .gitignore                   # Version Control Ignore Rules
├── .env.example                 # Root Environment Template
└── README.md                    # Professional Repository Documentation
```

---

## 🗺️ Development Roadmap Progression

- [x] **Phase 1:** Foundation Architecture, Auth & Evaluation Engine
- [x] **Phase 2:** Curriculum & Topic Hierarchy Engine
- [x] **Phase 3:** Dynamic Learning Path & Roadmap Generator
- [x] **Phase 4:** Multi-Dimensional Feynman AI Evaluation Engine
- [x] **Phase 5:** AI Custom Learning Path & Dynamic Roadmap
- [x] **Phase 6:** AI Smart Revision & Spaced Repetition Scheduler
- [x] **Phase 7:** Gamification, Badges & Achievement Engine
- [x] **Phase 8:** Resume Intelligence & Document Parsing
- [x] **Phase 9:** AI Adaptive Interview & Knowledge Gap Analysis
- [x] **Phase 10:** AI Communication Coach & Soft Skills Analyzer
- [x] **Phase 11:** Security, Auth, RBAC & Multi-Tenant User Isolation
- [x] **Phase 12:** Comprehensive Analytics, Insights & Skill Radar Engine
- [x] **Phase 13:** Master QA, AI Resiliency & System Integration Testing
- [ ] **Phase 14:** Production Deployment — *Skipped intentionally*
- [x] **Phase 15:** Professional Project Documentation & Repository Polish

---

## 🔮 Future Improvements

- **Real-Time Video Interviewer Avatar:** Integrate WebRTC video avatars for interactive mock interviews.
- **Audio Voice Synthesis:** Native Text-to-Speech (TTS) voice playback for interviewer prompts.
- **Offline Learning Support:** Local caching of study topics for offline review sessions.
- **Enterprise Team Dashboards:** Manager/Instructor views for tracking student cohort progress.

---

## 📄 License & Contribution

- **Contributing:** Contributions, issues, and feature requests are welcome! Feel free to fork the repository and submit a pull request.
- **License:** License not yet specified.
