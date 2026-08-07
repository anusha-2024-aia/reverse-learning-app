# Reverse Learning Studio: AI-Powered "Feynman Technique" Application

## 📌 Problem Statement
Traditional passive learning (reading, watching lectures) often leads to the illusion of competence, where students recognize material but cannot actively apply or explain it. When preparing for technical interviews, exams, or complex real-world engineering tasks, the inability to articulate concepts clearly becomes a massive bottleneck. Learners lack immediate, objective, and personalized feedback on their true comprehension.

## 🎯 End User
- **Software Engineering Students & Bootcamp Grads**: Preparing for rigorous technical interviews and needing to practice explaining algorithms and system designs.
- **Self-Taught Developers**: Looking to solidify foundational knowledge across various stacks (Python, Full-Stack, AI/ML, SQL).
- **Professionals & Lifelong Learners**: Anyone wanting to test their true grasp of a subject using the Feynman Technique, improving both technical depth and communication skills.

## 💡 Solution
The **Reverse Learning Studio** turns the traditional learning paradigm upside down. Instead of being spoon-fed information, users must *teach* the AI. Leveraging the **Feynman Technique** (learning by teaching), the platform challenges users to explain concepts in their own words—via text or voice. The system's AI evaluates these explanations in real-time for technical accuracy, grammar, and fluency, acting as a personal mentor that instantly highlights knowledge gaps and guides users to mastery.

## ✨ Features
*   **Dynamic Syllabus Engine:** An extensive, automatically generated curriculum ranging from "Basic to Pro" levels across multiple disciplines (Python, Java, AI, SQL, Full Stack, Interview Prep). 
*   **The "Reverse Learning" Room:** An interactive studio where users submit explanations via Text-to-Text, Voice-to-Text, or Voice-to-Voice.
*   **Multi-Dimensional AI Evaluation:** Advanced LLM integration that grades submissions based on Technical Logic, General Knowledge analogies, or English Fluency. It provides a score out of 10, grammar corrections, vocabulary suggestions, and an "Advanced Version" to learn from.
*   **Gamification & Engagement:** A persistent local database tracks user progress, study streaks, and perfect scores, rewarding users with achievements to keep them motivated.
*   **AI Mock Interview Simulator:** A dedicated interview module that evaluates not just technical accuracy, but also "Soft Skills" and "Confidence", visualized using interactive Radar charts.
*   **Document Parsing:** Users can upload `.pdf` or `.docx` study notes, which are parsed and fed into the AI as context to generate personalized study plans and challenge questions.

## 🛠 Tech Stack
**Frontend:**
*   **React (Vite):** Blazing fast modern frontend framework.
*   **Tailwind CSS:** For premium, responsive, modern UI components.
*   **Lucide React:** Beautiful, consistent iconography.
*   **Recharts:** Interactive charting for visualizing interview performance metrics.
*   **React Router:** For seamless single-page application navigation.

**Backend:**
*   **Python & FastAPI:** High-performance async web framework for handling API routes and AI orchestration.
*   **SQLite (SQLAlchemy):** Relational database with ORM for robust state, user, and curriculum management.
*   **Google Gemini AI API:** The core LLM engine powering evaluations, JSON-structured feedback, and dynamic syllabus generation.
*   **PyMuPDF (`fitz`) & `python-docx`:** For robust document text extraction.
*   **JWT & OAuth2 (Architecture Built-in):** Configured for secure, stateless authentication and session management.

## 🚀 How to Run (Getting Started)

### Prerequisites
*   **Node.js** (v16+)
*   **Python** (3.9+)

### 1. Backend Setup
Navigate to the backend directory and set up the Python environment:
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload
```
*The backend will run on `http://localhost:8000`.*

### 2. Frontend Setup
Open a new terminal window, navigate to the frontend directory:
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
*The frontend will be accessible at `http://localhost:5173`. Open this in your browser to start your Reverse Learning journey!*
