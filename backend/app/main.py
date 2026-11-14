from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.routes import study_routes, curriculum_routes, topics_routes, insights_routes, achievements_routes, sessions_routes, evaluations_routes, auth_routes, interview_routes, adaptive_routes, roadmap_routes, analytics_routes, knowledge_gap_routes, dashboard_routes, revision_routes, resume_routes, communication_routes
from contextlib import asynccontextmanager
from app.database import engine, get_db, SessionLocal
from app import models
from app.core.logging_config import logger

def seed_topics(db_session: Session = None):
    db = db_session if db_session is not None else SessionLocal()
    close_db = db_session is None
    try:
        curriculums_data = [
            # Programming & CS
            {"name": "Python Mastery", "desc": "Learn Python from scratch to pro", "diff": "beginner", "topics": [
                "Introduction to Python & Setup", "Variables, Data Types & Operators", "Control Flow (If, For, While)", 
                "Functions & Scope", "Lists, Tuples & Sets", "Dictionaries & Data Modeling", "File Handling & I/O", 
                "Error Handling & Exceptions", "Object-Oriented Programming (OOP)", "Inheritance & Polymorphism", 
                "Modules & Packages", "Decorators & Generators", "Context Managers", "Multithreading & Multiprocessing", 
                "Pro Level: Asynchronous Programming (Asyncio)", "Pro Level: C-Extensions & Memory Management"
            ]},
            {"name": "Java Fundamentals", "desc": "Object-oriented programming in Java", "diff": "intermediate", "topics": [
                "Introduction to Java & JVM", "Variables, Types & Operators", "Control Structures", "Arrays & Strings", 
                "Classes, Objects & Constructors", "Inheritance & Interfaces", "Polymorphism & Abstraction", 
                "Exception Handling", "Java Collections Framework", "Generics", "File I/O & Serialization", 
                "Multithreading & Concurrency", "Java 8 Streams & Lambdas", "JDBC & Database Connectivity", 
                "Pro Level: Spring Boot Framework Basics", "Pro Level: Advanced JVM Tuning"
            ]},
            {"name": "SQL Mastery", "desc": "From basic queries to advanced database tuning", "diff": "beginner", "topics": [
                "Introduction to Relational Databases", "Basic SELECT Queries", "Filtering Data (WHERE, LIKE, IN)", 
                "Sorting & Paging (ORDER BY, LIMIT)", "Aggregate Functions (COUNT, SUM, AVG)", "GROUP BY & HAVING", 
                "INNER JOIN & LEFT JOIN", "RIGHT & FULL OUTER JOINS", "Subqueries & Nested Selects", 
                "Common Table Expressions (CTEs)", "Data Modification (INSERT, UPDATE, DELETE)", 
                "DDL (CREATE, ALTER, DROP Tables)", "Views & Stored Procedures", "Database Normalization", 
                "Pro Level: Window Functions (OVER, PARTITION)", "Pro Level: Query Optimization & Indexing"
            ]},
            {"name": "Full Stack Web Development", "desc": "End-to-end web app creation", "diff": "intermediate", "topics": [
                "Introduction to the Web (HTTP, DNS)", "HTML5 Semantic Structure", "CSS3 Basics & Flexbox/Grid", 
                "Responsive Design & Media Queries", "JavaScript Fundamentals", "DOM Manipulation & Events", 
                "Async JS (Promises & Fetch API)", "React.js: Components & State", "React.js: Hooks & Context", 
                "Node.js & Express.js Basics", "RESTful API Design", "MongoDB & Mongoose (NoSQL)", 
                "Authentication (JWT & Cookies)", "WebSockets for Real-time Apps", 
                "Pro Level: System Design & Microservices", "Pro Level: CI/CD & Docker Deployment"
            ]},
            {"name": "Artificial Intelligence", "desc": "Core concepts of AI", "diff": "advanced", "topics": [
                "Introduction to AI & History", "Problem Solving as Search", "Uninformed Search (BFS, DFS)", 
                "Informed Search (A* Algorithm)", "Adversarial Search (Minimax)", "Knowledge Representation & Logic", 
                "Probabilistic Reasoning & Bayes Nets", "Markov Decision Processes (MDP)", "Reinforcement Learning Basics", 
                "Intro to Artificial Neural Networks", "Natural Language Processing Basics", "Computer Vision Basics", 
                "Pro Level: Advanced Deep Learning Architectures", "Pro Level: AI Safety & Alignment"
            ]},
            {"name": "Machine Learning Fundamentals", "desc": "Theory and practice of ML models", "diff": "intermediate", "topics": [
                "Introduction to Machine Learning", "Data Preprocessing & Feature Engineering", "Linear Regression", 
                "Logistic Regression", "Decision Trees & Random Forests", "Support Vector Machines (SVM)", 
                "K-Nearest Neighbors (KNN)", "Model Evaluation (Precision, Recall, ROC)", "Cross-Validation & Grid Search", 
                "Unsupervised Learning: K-Means Clustering", "Unsupervised Learning: PCA (Dimensionality Reduction)", 
                "Gradient Boosting (XGBoost, LightGBM)", "Pro Level: Building MLOps Pipelines", "Pro Level: Advanced Ensemble Methods"
            ]},
            
            # Languages & Soft Skills
            {"name": "English Vocabulary & Expression", "desc": "Enhance your professional communication", "diff": "intermediate", "topics": [
                "Introduction to Professional English", "Common Business Idioms & Phrases", "Descriptive Adjectives for Impact", 
                "Action Verbs for Resumes & Interviews", "Nuanced Phrasal Verbs", "Industry-Specific Jargon (Tech/Business)", 
                "Polite Disagreement & Diplomacy", "Structuring Presentations", "Writing Professional Emails", 
                "Pro Level: Persuasive & Academic Writing", "Pro Level: Advanced Public Speaking Tropes"
            ]},
            {"name": "English Grammar & Syntax", "desc": "Master sentence structures", "diff": "beginner", "topics": [
                "Introduction to Parts of Speech", "Simple Tenses (Past, Present, Future)", "Continuous & Perfect Tenses", 
                "Subject-Verb Agreement", "Articles & Prepositions", "Active vs. Passive Voice", "Direct vs. Indirect Speech", 
                "Conditional Sentences (If clauses)", "Relative Clauses", "Compound & Complex Sentences", 
                "Pro Level: Advanced Syntactical Structures", "Pro Level: Editing & Proofreading Techniques"
            ]},
            {"name": "Interview Preparation", "desc": "Mock interview strategies", "diff": "beginner", "topics": [
                "Introduction to the Interview Process", "Crafting Your Elevator Pitch", "The STAR Method for Behavioral Questions", 
                "Answering 'Tell Me About Yourself'", "Handling Questions About Weaknesses", "Discussing Past Failures & Conflict", 
                "Technical Communication for Engineers", "Whiteboard Interview Strategies", "Questions to Ask the Interviewer", 
                "Following Up Post-Interview", "Pro Level: Salary Negotiation Tactics", "Pro Level: Handling Executive/Panel Interviews"
            ]}
        ]

        for cur_data in curriculums_data:
            cur = db.query(models.Curriculum).filter(models.Curriculum.name == cur_data["name"]).first()
            if not cur:
                cur = models.Curriculum(name=cur_data["name"], description=cur_data["desc"], difficulty=cur_data["diff"])
                db.add(cur)
                db.flush()
                
            existing_topics = db.query(models.Topic).filter(models.Topic.curriculum_id == cur.id).all()
            existing_topic_names = {t.name.strip().casefold() for t in existing_topics if t.name}

            topics_to_add = []
            for idx, topic_name in enumerate(cur_data["topics"]):
                clean_name = topic_name.strip()
                if clean_name.casefold() not in existing_topic_names:
                    topics_to_add.append(
                        models.Topic(
                            name=clean_name,
                            category="Engineering",
                            curriculum_id=cur.id,
                            order_in_curriculum=idx + 1
                        )
                    )
                    existing_topic_names.add(clean_name.casefold())

            if topics_to_add:
                db.add_all(topics_to_add)
                db.flush()

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error in seed_topics: {e}")
        raise
    finally:
        if close_db:
            db.close()

import time
import uuid
import os
from fastapi import Request, Response
from app.core.error_handlers import register_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    try:
        from app.migrate_v5 import migrate_db
        migrate_db()
    except Exception as err:
        logger.error(f"Migration error in lifespan: {err}")
    seed_topics()
    yield

app = FastAPI(title="Reverse Learning API", lifespan=lifespan)

# Register Centralized Exception Handlers
register_exception_handlers(app)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:5174",  # Vite alternative
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    for url in frontend_url.split(","):
        cleaned_url = url.strip()
        if cleaned_url and cleaned_url not in origins:
            origins.append(cleaned_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    request.state.request_id = request_id
    start_time = time.time()

    response: Response = await call_next(request)

    duration = round(time.time() - start_time, 4)
    user_str = ""
    if hasattr(request.state, "user") and getattr(request.state.user, "id", None):
        user_str = f" user_id={request.state.user.id}"

    logger.info(
        f"request_id={request_id}{user_str} method={request.method} path={request.url.path} "
        f"status={response.status_code} duration={duration:.2f}s"
    )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Include Routers
app.include_router(auth_routes.router, prefix="/api")
app.include_router(study_routes.router, prefix="/api", tags=["Study"])
app.include_router(curriculum_routes.router, prefix="/api", tags=["Curriculum"])
app.include_router(topics_routes.router, prefix="/api", tags=["Topics"])
app.include_router(insights_routes.router, prefix="/api/insights", tags=["Insights"])
app.include_router(achievements_routes.router, prefix="/api/achievements", tags=["Achievements"])
app.include_router(sessions_routes.router, prefix="/api", tags=["Sessions"])
app.include_router(evaluations_routes.router, prefix="/api", tags=["Evaluations"])
app.include_router(interview_routes.router, prefix="/api", tags=["Interviews"])
app.include_router(adaptive_routes.router, prefix="/api", tags=["Adaptive Engine"])
app.include_router(roadmap_routes.router, prefix="/api", tags=["Roadmap"])
app.include_router(analytics_routes.router, prefix="/api", tags=["Analytics"])
app.include_router(knowledge_gap_routes.router, prefix="/api", tags=["knowledge-gaps"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard-data", tags=["Dashboard"])
app.include_router(revision_routes.router, prefix="/api", tags=["Smart Revision"])
app.include_router(resume_routes.router, prefix="/api", tags=["Resume Intelligence"])
app.include_router(communication_routes.router, prefix="/api", tags=["Communication Coach"])



@app.get("/")
async def root():
    return {"message": "Welcome to the Reverse Learning API"}

@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
