from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from app.ai_service.gemini_agent import evaluate_explanation, stream_evaluate_explanation
from app.database import get_db
from app.models import Evaluation, Topic
from app.services import achievement_service

router = APIRouter()

# Replaced by evaluations_routes.py
