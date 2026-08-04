# Reverse Learning App

A full-stack application featuring a React frontend built with Vite and a Python backend.

## Project Structure

```
reverse-learning-app/
├── backend/            # Python backend application
│   ├── app/            # Application source code
│   ├── requirements.txt # Python dependencies
│   └── .env            # Environment variables Configuration
├── frontend/           # React + Vite frontend application
│   ├── src/            # Frontend source code (React components like StudyRoom)
│   ├── package.json    # Node dependencies and scripts
│   └── vite.config.js  # Vite configuration
└── README.md           # This file
```

## Working Flow

The application is an AI-powered learning co-pilot that leverages the **Feynman Technique** (learning by explaining) to help engineers master concepts. 

1. **Welcome Screen:** The user starts their learning journey.
2. **Topic Selection (Syllabus Roadmap):** The user selects a specific target concept/node from an interactive, isometric syllabus map (e.g., Core Foundations, System Architecture).
3. **Explanation Input:** The user provides an explanation of the topic as if they were teaching it. They can choose from different "Learning Contexts" (General Knowledge, Technical & DSA, or English Fluency) to tailor the AI's grading criteria.
4. **AI Evaluation & Feedback:** The explanation is sent to the backend, where it is analyzed by an AI (Gemini). The UI displays the AI's "Cognition Phase" real-time thinking, followed by a detailed, structured feedback card with scores and constructive critiques.
5. **Mastery & Progression:** Once the user successfully demonstrates understanding, they achieve "Mastery" of the topic, which formally unlocks the next advanced phases in their curriculum.

## Getting Started

### Prerequisites

* Node.js (for the frontend)
* Python 3.x (for the backend)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (if you haven't already):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server (typically using uvicorn or flask run, depending on your framework):
   ```bash
   # Make sure to check backend/app for the specific start script
   # e.g., uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Development

* The frontend is running on Vite, which usually defaults to `http://localhost:5173`.
* Ensure that the backend server is running and accessible to the frontend application (check `.env` files for configuration).
