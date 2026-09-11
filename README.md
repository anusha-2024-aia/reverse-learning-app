# Reverse Learning App

[![CI](https://github.com/anusha-2024-aia/reverse-learning-app/actions/workflows/ci.yml/badge.svg)](https://github.com/anusha-2024-aia/reverse-learning-app/actions/workflows/ci.yml)

AI-Powered Learning Intelligence, Feynman Technique & Mock Interview Platform.

An adaptive AI learning platform that evaluates whether students truly understand concepts by asking them to explain in their own words, detecting knowledge gaps, dynamically adapting study roadmaps, and conducting resume-targeted mock interviews.

---

## 1. Project Overview

The **Reverse Learning App** turns traditional passive learning upside down. Instead of passively reading or taking multiple-choice quizzes, students **teach the AI** using the Feynman Technique:
- **Learn a Concept:** Pick a topic from Python, Java, SQL, Full Stack, AI/ML, or Interview Prep.
- **Explain to AI:** Articulate the concept via text or voice.
- **Multi-Dimensional AI Evaluation:** Receive instant 4D feedback on technical accuracy, concept understanding, completeness, examples, relevance, communication, and grammar.
- **Knowledge Gap Detection:** Automatically isolate micro-level concept weaknesses.
- **Adaptive Roadmap & Revision:** Dynamic career path adjustment and Ebbinghaus spaced repetition.
- **Resume Intelligence & Mock Interviews:** Upload resumes (`.pdf` / `.docx`) to generate project-targeted adaptive mock interview questions.

---

## 2. Key Features

- **Reverse Learning Studio:** Interactive explanation studio supporting text and voice inputs.
- **Multi-Dimensional AI Assessment:** 4D scoring engine evaluating technical depth, clarity, and structural explanation quality out of 100.
- **Automated Knowledge Gap Engine:** Isolates micro-concept failures and assigns severity levels (Mild, Moderate, Severe).
- **Dynamic Learning Roadmap:** Automatically adjusts study milestones and estimated time based on performance.
- **Smart Spaced Repetition:** Ebbinghaus memory curve scheduler categorizing topics into *Due Today*, *Overdue*, and *Upcoming*.
- **Resume Intelligence:** Extract technical skills, projects, and work experience from PDF and DOCX documents.
- **Adaptive AI Mock Interviewer:** Dynamic difficulty scaling (Easy $\rightarrow$ Medium $\rightarrow$ Hard) with follow-up probe questions.
- **AI Communication Coach:** Tracks speech pace (WPM), filler word frequency (*"um"*, *"like"*, *"basically"*), and vocal clarity.
- **Security & Multi-Tenant Isolation:** User data isolation, bcrypt password hashing, stateless JWT authentication, and OWASP security headers.

---

## 3. Tech Stack

### Frontend
- **Framework:** React 19 (Vite)
- **Styling:** Tailwind CSS 4, Vanilla CSS Design System
- **Icons:** Lucide React
- **Charts & Visualization:** Recharts
- **Routing:** React Router v7
- **HTTP Client:** Axios

### Backend
- **Framework:** Python 3.9+ & FastAPI (Async ASGI Engine)
- **Server:** Uvicorn
- **Database ORM:** SQLAlchemy
- **Database:** SQLite (Local Development)
- **Authentication:** JWT (`python-jose`) & Password Hashing (`bcrypt`)
- **Document Parsing:** PyMuPDF (`fitz`) for PDF & `python-docx` for Word Documents

### AI Engine
- **LLM Engine:** Google Gemini API (`openai` SDK with Google Generative Language endpoint)

---

## 4. Project Structure

```text
reverse-learning-app/
├── backend/
│   ├── app/
│   │   ├── ai_service/      # Gemini AI evaluation & interview engines
│   │   ├── routes/          # FastAPI API route handlers
│   │   ├── services/        # Business logic & adaptive engines
│   │   ├── auth.py          # JWT & bcrypt authentication
│   │   ├── database.py      # SQLAlchemy engine & session setup
│   │   ├── main.py          # FastAPI app initialization & CORS
│   │   ├── models.py        # SQLAlchemy database models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   └── seeds.py         # Initial topic curriculum seed data
│   ├── tests/               # Backend unit, security & E2E tests
│   ├── .env.example         # Backend environment template
│   ├── create_tables.py     # Standalone DB initialization script
│   ├── requirements.txt     # Python runtime dependencies
│   └── run_all_tests.py     # Master test suite runner
├── frontend/
│   ├── public/              # Static public assets
│   ├── src/
│   │   ├── api/             # Axios instance configuration
│   │   ├── components/      # Reusable UI components
│   │   ├── context/         # Auth & state management contexts
│   │   ├── pages/           # Application views & dashboards
│   │   └── services/        # Frontend API call wrappers
│   ├── .env.example         # Frontend environment template
│   ├── package.json         # Node.js dependencies & scripts
│   └── vite.config.js       # Vite build configuration
├── .env.example             # Root environment variable template
├── .gitignore               # Git untracked files pattern
└── README.md                # Project documentation
```

---

## 5. Prerequisites

Before installing the project, ensure you have the following installed on your machine:

- **Python:** Version 3.9, 3.10, 3.11, or 3.12 (`python --version`)
- **Node.js:** Version 18.0.0 or higher (`node -v`)
- **npm:** Version 9.0.0 or higher (`npm -v`)
- **Google Gemini API Key:** Required for AI features ([Get Gemini API Key](https://aistudio.google.com/))

---

## 6. Clone Repository

Open your terminal or PowerShell and run:

```bash
git clone https://github.com/anusha-2024-aia/reverse-learning-app.git
cd reverse-learning-app
```

---

## 7. Backend Setup

### Step 7.1: Navigate to Backend Directory

```bash
cd backend
```

### Step 7.2: Create Virtual Environment

On Windows (PowerShell / Command Prompt):

```powershell
python -m venv venv
```

On Linux / macOS:

```bash
python3 -m venv venv
```

### Step 7.3: Activate Virtual Environment

On Windows (PowerShell):

```powershell
.\venv\Scripts\activate
```

On Windows (Command Prompt):

```cmd
venv\Scripts\activate.bat
```

On Linux / macOS:

```bash
source venv/bin/activate
```

### Step 7.4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 7.5: Configure Environment Variables

Copy `.env.example` to `.env`:

On Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

On Command Prompt / Linux / macOS:

```bash
cp .env.example .env
```

Generate a strong random secret key for local development:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Edit `backend/.env` with your settings:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./study.db
JWT_SECRET=your_generated_random_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_URL=http://localhost:5173
```

> **IMPORTANT SECURITY REQUIREMENTS:**
> 1. `JWT_SECRET` is **mandatory**. If missing or empty, application startup will fail immediately with a clear configuration error.
> 2. Never commit `.env` or hardcode secrets into source code or repository configuration.
> 3. Generate a unique, cryptographically strong secret for each environment.

### Step 7.6: Database Initialization

The database automatically initializes SQLite tables and seeds the curriculum topics when the FastAPI server starts.

Alternatively, you can manually trigger database initialization anytime by running:

```bash
python create_tables.py
```

### Step 7.7: Start Backend Server

```bash
python -m uvicorn app.main:app --reload
```

The backend server will run on `http://localhost:8000`.

---

## 8. Frontend Setup

Open a **new terminal window**, enter the project root directory, and navigate to `frontend`:

```bash
cd frontend
```

### Step 8.1: Install Node Dependencies

```bash
npm install
```

### Step 8.2: Configure Environment Variables

Copy `.env.example` to `.env`:

On Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

On Command Prompt / Linux / macOS:

```bash
cp .env.example .env
```

Ensure `frontend/.env` contains:

```env
VITE_API_URL=http://localhost:8000
```

> **Note:** If `.env` is omitted, the frontend defaults to `http://localhost:8000`.

### Step 8.3: Start Frontend Development Server

```bash
npm run dev
```

The frontend application will start on `http://localhost:5173`.

---

## 9. Database Configuration & Environment Variables

### Database Configuration

#### Local Development

The project uses lightweight **SQLite** locally (`sqlite:///./study.db`). No PostgreSQL server or Docker installation is required on your local machine.

Example local configuration in `backend/.env`:

```env
DATABASE_URL=sqlite:///./study.db
```

#### Production

Production uses a managed **Cloud PostgreSQL** database (such as Supabase, AWS RDS, Neon, or Render PostgreSQL).

The production hosting platform provides `DATABASE_URL` as a server-side environment variable:

```env
DATABASE_URL=postgresql://username:password@host:5432/database
```

- Database selection is automatically controlled by `DATABASE_URL`.
- Standard legacy `postgres://` URLs are automatically normalized to `postgresql://` centrally in `app/database.py`.
- Unencoded special characters in passwords are safely handled by the database layer.
- Never commit production database credentials to version control.

### Environment Variables Matrix

| Variable Name | Scope | Purpose | Safe Example |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Backend | Google Gemini API key for AI evaluation & mock interviews | `AIzaSy...` (from Google AI Studio) |
| `DATABASE_URL` | Backend | SQLAlchemy connection URL (SQLite local / PostgreSQL prod) | `sqlite:///./study.db` |
| `JWT_SECRET` | Backend | Secret key used to sign JWT authentication tokens | `replace_with_a_secure_random_secret` |
| `JWT_ALGORITHM` | Backend | Algorithm for JWT signature validation | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | Expiration window for access tokens (in minutes) | `1440` (24 hours) |
| `FRONTEND_URL` | Backend | Frontend URL allowed by CORS policy | `http://localhost:5173` |
| `VITE_API_URL` | Frontend | Base URL of the FastAPI backend server | `http://localhost:8000` |

---

## 10. Running the Application

To run the complete application locally:

### Terminal 1: Backend Server

```bash
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

### Terminal 2: Frontend Server

```bash
cd frontend
npm run dev
```

### Application User Flow

1. Open your browser to `http://localhost:5173`.
2. Click **Register** to create a new local user account.
3. **Log in** with your credentials.
4. Go to **Curriculum / Topics**, pick a concept (e.g., *Variables, Data Types & Operators* in Python Mastery).
5. Open **Reverse Learning Studio**, type or speak your explanation of the concept, and click **Submit Evaluation**.
6. View your **4D AI Score breakdown**, detected **Knowledge Gaps**, and **Smart Spaced Revision** schedule on the **Dashboard**.

---

## 11. API Health Check

Verify that the FastAPI backend server is running correctly by sending a request to the health check endpoint:

```bash
curl http://localhost:8000/health
```

**Expected JSON Response:**

```json
{
  "status": "ok"
}
```

You can also check `http://localhost:8000/health` directly in your browser.

---

## 12. API Documentation

FastAPI automatically generates interactive OpenAPI documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc UI:** `http://localhost:8000/redoc`
- **OpenAPI Schema (JSON):** `http://localhost:8000/openapi.json`

Use Swagger UI to test endpoints like `/api/auth/register`, `/api/auth/login`, and `/api/health` directly from your browser.

---

## 13. Running Tests

### Backend Automated Test Suite

Ensure your backend virtual environment is activated, then run the master test suite:

```bash
cd backend
python run_all_tests.py
```

Or run tests via `pytest`:

```bash
cd backend
python -m pytest
```

### Verified Test Suite Coverage

- **Health Check Endpoint:** `GET /health` verification (`status 200 OK`)
- **Authentication & Security:** User registration, password hashing (`bcrypt`), JWT token validation, unauthorized endpoint rejection
- **User Data Isolation:** Verification that User A cannot access User B's resumes or interview reports
- **Security Protections:** Rejection of non-PDF/DOCX executable file uploads and path traversal sanitization
- **AI & DB Resiliency:** Handling AI rate limit responses gracefully and rolling back failed DB transactions
- **Mocked Evaluation API:** Verification of `/api/evaluate` without making external Gemini API network calls

### Continuous Integration (GitHub Actions)

GitHub Actions automatically validates backend and frontend changes on every `push` or `pull_request` to the `main` branch:

- **Backend CI Job (`Python 3.11`)**:
  - Automatically installs dependencies from `backend/requirements.txt`.
  - Configures safe, isolated test environment variables (`DATABASE_URL=sqlite:///./ci_test.db`, test JWT secret).
  - Executes the master test suite (`python run_all_tests.py`) verifying all 47 backend unit, security, rate limiting, and resiliency tests without requiring external Gemini API credentials.
- **Frontend CI Job (`Node.js 20`)**:
  - Installs dependencies using `npm ci` in `frontend/`.
  - Executes ESLint static checks (`npm run lint`).
  - Executes the production Vite build (`npm run build`) to ensure client bundle compilation succeeds cleanly.


Workflow configuration file: [`.github/workflows/ci.yml`](file:///c:/Users/anush/Desktop/reverse-learning-app/.github/workflows/ci.yml)

---

## 14. Troubleshooting

### Problem: Port 8000 or 5173 is already in use
- **Cause:** Another process is listening on port 8000 or 5173.
- **Solution (Windows):** Find and kill the process using port 8000:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
  ```
  Or start FastAPI on a different port:
  ```bash
  python -m uvicorn app.main:app --reload --port 8001
  ```
  If changing backend port, update `frontend/.env` to `VITE_API_URL=http://localhost:8001`.

---

### Problem: Missing .env or GEMINI_API_KEY error
- **Cause:** `backend/.env` file is missing or `GEMINI_API_KEY` is not set.
- **Solution:** Create `backend/.env` from `backend/.env.example` and set `GEMINI_API_KEY=your_gemini_api_key_here`. Non-AI routes and health check will still work without key.

---

### Problem: Frontend displays "API Error" or cannot connect to backend
- **Cause:** Backend server is not running or `VITE_API_URL` is misconfigured.
- **Solution:**
  1. Confirm backend is running at `http://localhost:8000`.
  2. Verify `curl http://localhost:8000/health` returns `{"status": "ok"}`.
  3. Ensure `frontend/.env` has `VITE_API_URL=http://localhost:8000`.
  4. Restart frontend dev server (`npm run dev`).

---

### Problem: CORS Policy Error in Browser Console
- **Cause:** Frontend is running on a port not listed in backend CORS origins.
- **Solution:** Backend automatically allows `http://localhost:5173` and `http://localhost:5174`. If your frontend runs on a custom port (e.g. `5175`), update `FRONTEND_URL=http://localhost:5175` in `backend/.env` and restart backend.

---

### Problem: Database locked or initialization error
- **Cause:** A previous Python process did not close `study.db`.
- **Solution:** Stop running Python processes, delete local `backend/study.db` if corrupted, and run `python create_tables.py` to recreate a fresh database.

---

### Problem: npm install fails with dependency conflicts
- **Cause:** Node.js version mismatch.
- **Solution:** Use Node v18+ and run:
  ```bash
  npm install --legacy-peer-deps
  ```

---

## 15. Architecture

### System Architecture Diagram

```text
LOCAL DEVELOPMENT:

React (Vite)
    │
    ▼
FastAPI Backend
    │
    ▼
SQLAlchemy ORM
    │
    ▼
SQLite Database (study.db)


PRODUCTION DEPLOYMENT:

React (Vite / CDN)
    │
    ▼
FastAPI Backend
    │
    ▼
SQLAlchemy ORM
    │
    ▼
Cloud Managed PostgreSQL (DATABASE_URL)
```

### System Component Flow

```mermaid
graph TD
    A[Student / Recruiter Browser] -->|HTTP / REST| B[React + Vite Frontend]
    B -->|Axios + JWT Auth| C[FastAPI Backend Server]
    C -->|ORM / Dynamic DB| D[(SQLite / Cloud PostgreSQL)]
    C -->|OpenAI SDK Client| E[Google Gemini AI Engine]
    C -->|PyMuPDF & python-docx| F[Resume Document Parser]
```

### Data & Evaluation Pipeline

```text
User Explanation (Text / Voice)
             │
             ▼
FastAPI Security & Auth Middleware
             │
             ▼
Gemini AI 4D Assessment Engine
             │
             ▼
Knowledge Gap Diagnostic Engine
             │
             ▼
SQLAlchemy DB Persistence (SQLite / PostgreSQL)
             │
             ▼
React Frontend Dashboard & Radar Analytics
```

---

## 16. Development Flow

```text
Git Clone Repository
         │
         ▼
Configure .env Files (Backend & Frontend)
         │
         ▼
Install Dependencies (pip install & npm install)
         │
         ▼
Initialize Database (Automatic / create_tables.py)
         │
         ▼
Run Local Servers (FastAPI :8000 & Vite :5173)
         │
         ▼
Run Test Suite (python run_all_tests.py)
```

---

## 🛡️ API Rate Limiting (Security & Cost Protection)

The backend features a lightweight, zero-dependency, in-memory sliding window API rate limiter ([`app/rate_limiter.py`](file:///c:/Users/anush/Desktop/reverse-learning-app/backend/app/rate_limiter.py)) designed to protect expensive Gemini AI evaluation, document parsing, and authentication endpoints from excessive requests.

### Key Rate Limits & Defaults

| Endpoint Category | Default Limit | Identification Key | Purpose | Config Environment Variable |
|---|---|---|---|---|
| **AI Evaluation** | `5 requests / min` | `user.id` | Prevents Gemini API quota exhaustion | `AI_EVALUATION_RATE_LIMIT` |
| **Mock Interview** | `5 requests / min` | `user.id` | Controls interview AI generation | `INTERVIEW_RATE_LIMIT` |
| **Document Processing** | `3 requests / min` | `user.id` | Limits resume upload & parsing | `DOCUMENT_RATE_LIMIT` |
| **Communication Coach** | `5 requests / min` | `user.id` | Limits audio transcript analysis | `COMMUNICATION_RATE_LIMIT` |
| **AI Roadmap** | `3 requests / min` | `user.id` | Limits onboarding AI roadmap creation | `ROADMAP_RATE_LIMIT` |
| **Authentication** | `10 requests / min` | Client IP Address | Prevents credential brute-forcing | `AUTH_RATE_LIMIT` |
| **Health Checks** | `Unrestricted` | N/A | Uptime monitoring (`/health`) | N/A |

### Rate Limit Exceeded Response (`HTTP 429`)

When a client or authenticated user exceeds their allowed rate limit, the API immediately returns `HTTP 429 Too Many Requests` BEFORE invoking any downstream AI models or database queries:

```json
{
  "detail": "Too many requests. Please try again later."
}
```

Response Headers returned:
- `Retry-After`: Number of seconds remaining until requests are accepted again.
- `X-RateLimit-Limit`: Maximum requests permitted per window.
- `X-RateLimit-Remaining`: Remaining request quota in current window (`0`).

> [!NOTE]  
> **Multi-Worker Deployment Note**: In multi-worker backend deployments (e.g. Uvicorn with multiple `--workers`), rate limits apply per backend process unless sticky sessions or a centralized redis cache are configured. For single-instance deployments, this in-memory implementation provides zero-overhead, instant protection.

---

## 🔒 Centralized Error Handling & Structured Logging

The FastAPI backend incorporates standardized centralized error handling, machine-readable error codes, safe logging, and request timing middleware.

### Response JSON Schema

All error responses return a standardized, secure JSON payload:

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable safe message",
  "request_id": "req_a1b2c3d4e5f6"
}
```

### Error Code Matrix

| Error Code | HTTP Status | Trigger Condition |
|---|---|---|
| `BAD_REQUEST` | `400` | Malformed request parameters or invalid file upload |
| `AUTHENTICATION_FAILED` | `401` | Missing, expired, or tampered JWT token |
| `AUTHORIZATION_FAILED` | `403` | Access forbidden to requested user resource |
| `RESOURCE_NOT_FOUND` | `404` | Topic, evaluation, resume, or session missing |
| `VALIDATION_ERROR` | `422` | Request body or query field validation failure |
| `RATE_LIMIT_EXCEEDED` | `429` | Sliding window rate limit threshold breached |
| `DATABASE_ERROR` | `500` | Internal database query or transaction exception |
| `AI_SERVICE_ERROR` | `503` / `500` | Gemini API service unavailable or quota error |
| `INTERNAL_SERVER_ERROR` | `500` | Unhandled unexpected backend exception |

### Structured Request Logging & Privacy Protection

- Every HTTP request receives a unique `X-Request-ID` header (e.g. `req_a1b2c3d4e5f6`).
- Request timing middleware logs execution duration in seconds (`duration=0.12s`).
- Sensitive data filtering guarantees `GEMINI_API_KEY`, `JWT_SECRET`, `DATABASE_URL`, user passwords, authorization tokens, and request/response payloads are **never logged**.

---

## 📄 License

Developed as part of the **Reverse Learning App** project. Empowering learners to achieve true technical mastery through the Feynman Technique.
