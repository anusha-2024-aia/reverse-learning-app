from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models
from app.services import dashboard_service

router = APIRouter()

@router.get("")
@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns the aggregated payload for the Learning Intelligence Dashboard for authenticated user.
    """
    try:
        data = dashboard_service.generate_dashboard_data(db, current_user.id)
        return data
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unable to load your learning data.")
