from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import dashboard_service

router = APIRouter()

USER_ID = 1 # Authenticated user identity mockup

@router.get("")
@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    """
    Returns the aggregated payload for the Learning Intelligence Dashboard.
    """
    try:
        data = dashboard_service.generate_dashboard_data(db, USER_ID)
        return data
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unable to load your learning data.")
