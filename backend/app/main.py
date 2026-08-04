from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import study_routes, curriculum_routes, topics_routes, insights_routes, achievements_routes
from app.seeds import seed_data
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed data on startup
    seed_data()
    yield

app = FastAPI(title="Reverse Learning API", lifespan=lifespan)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:5174",  # Vite alternative
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(study_routes.router, prefix="/api", tags=["Study"])
app.include_router(curriculum_routes.router, prefix="/api", tags=["Curriculum"])
app.include_router(topics_routes.router, prefix="/api", tags=["Topics"])
app.include_router(insights_routes.router, prefix="/api/insights", tags=["Insights"])
app.include_router(achievements_routes.router, prefix="/api/achievements", tags=["Achievements"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Reverse Learning API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
