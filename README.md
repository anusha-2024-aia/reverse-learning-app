# Reverse Learning Studio

### AI-Powered Learning Intelligence, Feynman Technique & Mock Interview Platform

> **"An adaptive AI learning platform that evaluates whether students truly understand concepts by asking them to explain in their own words, detecting knowledge gaps, dynamically adapting study roadmaps, and conducting resume-targeted mock interviews."**

---

## 🚀 Live Demo & Production Deployment

| Service | Live Link | Description |
| :--- | :--- | :--- |
| 🌐 **Live Web Application** | [reverse-learning-frontend-anusha.onrender.com](https://reverse-learning-frontend-anusha.onrender.com/) | Deployed Production Single-Page React Application |
| ⚙️ **Backend REST API** | [reverse-learning-app.onrender.com](https://reverse-learning-app.onrender.com/) | Live FastAPI Async Web Server |
| 📚 **Interactive API Docs** | [Swagger API Documentation](https://reverse-learning-app.onrender.com/docs) | Live Swagger UI for API Endpoint Testing |
| 📄 **OpenAPI Specification** | [OpenAPI JSON Spec](https://reverse-learning-app.onrender.com/openapi.json) | Machine-Readable API Endpoint Schema |

---

## 🌟 Key Platform Highlights

- **✓ Reverse Learning Studio:** Evaluate true comprehension using the Feynman Technique (*learning by teaching*).
- **✓ Multi-Dimensional AI Evaluation:** 4D evaluation scoring across Technical Accuracy, Concept Understanding, Communication, and Grammar.
- **✓ Automated Knowledge Gap Detection:** Identify micro-level concept failures rather than vague percentage scores.
- **✓ Dynamic Adaptive Roadmap:** Real-time learning path adjustments based on performance and user career goals.
- **✓ Smart Spaced Repetition:** Ebbinghaus memory curve scheduler for optimal topic revision.
- **✓ Resume Intelligence:** Extract skills and projects from PDF & DOCX resumes to generate personalized interview questions.
- **✓ Adaptive AI Mock Interviews:** Dynamic difficulty adjustments (Easy $\rightarrow$ Medium $\rightarrow$ Hard) and follow-up probes during live interview practice.
- **✓ AI Communication Coach:** Track speech pacing (Words Per Minute - WPM), filler words (*"um"*, *"like"*, *"basically"*), clarity, and vocal confidence.
- **✓ Secure Multi-Tenant Architecture:** Strict user isolation, OWASP security headers, JWT validation, and RBAC rules.
- **✓ Master QA & Resiliency:** Comprehensive test suite handling AI rate limits (403/429), malformed JSON, and DB rollbacks.

---

## 📌 Problem Statement vs. Solution

### ❌ The Problem
Traditional learning methods (reading tutorials, watching videos, or taking simple multiple-choice quizzes) fail technical students and job seekers because:
- **Illusion of Competence:** Students passively recognize material but cannot articulate concepts clearly in their own words.
- **Multiple-Choice Limitations:** Quizzes fail to measure technical depth, communication clarity, or explanation structure.
- **Static Roadmaps:** Fixed course outlines do not adapt when a student struggles with foundational prerequisites.
- **Irrelevant Interview Prep:** Generic practice questions ignore a candidate's actual resume experience and project background.
- **Unmeasured Soft Skills:** Students receive zero feedback on filler words, speaking pace, and structural explanation quality.

### 💡 The Solution
The **Reverse Learning Studio** turns the traditional learning paradigm upside down. Instead of being spoon-fed information, users must **teach the AI**:

1. **Learn a Concept:** Select a target topic from an extensive multi-disciplinary curriculum (Python, Java, Full Stack, SQL, AI/ML, Interview Prep).
2. **Teach the AI:** Explain the concept in your own words via text or voice.
3. **Receive 4D Feedback:** The Gemini AI engine grades technical accuracy, concept mastery, completeness, examples, relevance, communication, and grammar out of 100.
4. **Identify Knowledge Gaps:** Failed sub-concepts are isolated into actionable weak spots.
5. **Adaptive Recommendations:** The system dynamically computes the next priority topic to study.
6. **Smart Revision:** Spaced repetition schedules review sessions before memory decay occurs.
7. **Dynamic Roadmap:** Career goals automatically update estimated completion time and topic sequence.
8. **Resume Intelligence:** Upload `.pdf` or `.docx` resumes to extract projects and generate ATS targeted questions.
9. **Adaptive Mock Interviews:** Questions shift in difficulty dynamically based on live answer quality.
10. **Communication Coaching:** Analyze filler words, speaking pace (WPM), and structural clarity metrics.
11. **Master Analytics:** Track longitudinal progress via interactive Radar charts and trend graphs.

---

## 💡 Closed-Loop Learning Pipeline

```
 Learn Concept
      │
      ▼
 Explain to AI (Reverse Learning Studio)
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

## ✨ Feature Breakdown

### 🎙️ 1. Reverse Learning Studio
- Interactive studio for submitting explanations via **Text-to-Text**, **Voice-to-Text**, or **Voice-to-Voice**.
- Prompts students to explain algorithms, data structures, and system design concepts using the Feynman Technique.

### 📊 2. Multi-Dimensional AI Evaluation Engine
- **Technical Logic & Accuracy (0-100):** Deep evaluation of core technical mechanics.
- **Concept Mastery (0-100):** Depth of theoretical understanding.
- **Completeness & Examples (0-100):** Presence of code snippets, analogies, and edge cases.
- **Communication & Grammar (0-100):** Vocabulary quality, sentence structure, and clarity.
- **Advanced Version Generation:** Provides a polished, professional version of the student's explanation to learn from.

### 🔍 3. Automated Knowledge Gap Engine
- Tracks attempt history and accuracy ratios across micro-concepts.
- Categorizes weakness severity into **Mild**, **Moderate**, or **Severe**.
- Provides targeted learning recommendations and action items.

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
+------------------+       +-------------------+       +-----------------------+
|  SQLite Database |       |  Google Gemini AI |       | Resume Document Parser|
| (SQLAlchemy ORM) |       |  Evaluation Engine|       | (PyMuPDF & docx)      |
+------------------+       +-------------------+       +-----------------------+
     |                              |                              |
     +------------------------------+------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Knowledge Gap & Adaptive Engines  |
                  +-----------------------------------+
```

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
- **Database Engine:** SQLite (SQLAlchemy ORM) / PostgreSQL compatible
- **Authentication:** JWT (`python-jose`) & Password Hashing (`passlib[bcrypt]`)

### AI & Document Parsing
- **AI LLM Engine:** Google Gemini API (`google-genai` / `google-generativeai`)
- **Document Text Extraction:** PyMuPDF (`fitz`) for PDF & `python-docx` for Word Documents

### Testing & QA
- **Unit & E2E Testing:** Python `unittest` & `fastapi.testclient`
- **Master Test Runner:** Custom master test runner ([`run_all_tests.py`](file:///c:/Users/anush/Desktop/reverse-learning-app/backend/run_all_tests.py))

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

## 🚀 How to Run (Getting Started Locally)

### Prerequisites
- **Node.js** (v18+)
- **Python** (3.9+)

### 1. Backend Setup

Navigate to the `backend` directory and set up the Python environment:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file inside `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./study.db
JWT_SECRET=your_secret_jwt_key_here
FRONTEND_URL=http://localhost:5173
```

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

The backend server will run on `http://localhost:8000`.

---

### 2. Frontend Setup

Open a new terminal window and navigate to the `frontend` directory:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend application will run on `http://localhost:5173`. Open this URL in your browser to start your Reverse Learning journey!

---

## 🔐 Environment Variables Configuration

| Variable Name | Environment | Example / Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Backend | Google Gemini API Key |
| `DATABASE_URL` | Backend | `sqlite:///./study.db` or PostgreSQL connection string |
| `JWT_SECRET` | Backend | Secret key for signing JWT tokens |
| `JWT_ALGORITHM` | Backend | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | `1440` (24 hours) |
| `FRONTEND_URL` | Backend | `http://localhost:5173` or deployed frontend URL |
| `VITE_API_BASE_URL` | Frontend | `http://localhost:8000/api` or deployed backend API URL |

---

## 🧪 Automated Master Test Matrix

Run the automated master test suite:

```bash
python backend/run_all_tests.py
```

### Test Results Summary

```text
==================================================
           PHASE 13 TEST SUMMARY REPORT          
==================================================
Total Tests Executed : 19
Passed               : 19
Failed               : 0
==================================================
ALL PRODUCTION & QA TESTS PASSED SUCCESSFULLY!
```

---

## 📄 License & Attribution

Developed with ❤️ as part of the **Reverse Learning Studio** project. Empowering learners worldwide to master technical topics through the Feynman Technique.
