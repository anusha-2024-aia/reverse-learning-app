from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, UserMastery, Interview, Evaluation, LearningActivity
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Analytics"])

@router.get("/analytics")
@router.get("/analytics/")
def get_analytics(
    range: Optional[str] = Query("30d", alias="range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns comprehensive, user-isolated Learning Analytics for authenticated user.
    """
    return AnalyticsService.get_comprehensive_analytics(db, current_user.id, range or "30d")

@router.get("/analytics/dashboard")
def get_dashboard_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Returns aggregated analytics for the user's dashboard.
    """
    return AnalyticsService.get_comprehensive_analytics(db, current_user.id, "30d")
