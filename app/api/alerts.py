from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Alert, User, Coin
from app.schemas.schemas import AlertCreate, AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])

ALLOWED_CONDITIONS = {"price_above", "price_below", "change_24h_above", "change_24h_below"}

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)):
    """
    Create a new price alert for a user
    """
    # 1. Check if the condition is valid
    if alert_in.condition not in ALLOWED_CONDITIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid condition. Allowed conditions are: {', '.join(ALLOWED_CONDITIONS)}"
        )

    # 2. Check if the user exists
    user = db.query(User).filter(User.id == alert_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {alert_in.user_id} does not exist."
        )

    # 3. Check if the coin exists
    coin = db.query(Coin).filter(Coin.id == alert_in.coin_id).first()
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with ID {alert_in.coin_id} does not exist."
        )

    new_alert = Alert(
        user_id=alert_in.user_id,
        coin_id=alert_in.coin_id,
        condition=alert_in.condition,
        target_value=alert_in.target_value
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert

@router.get("/", response_model=List[AlertResponse])
def list_alerts(user_id: int = None, db: Session = Depends(get_db)):
    """
    Get the list of alerts (optionally filtered by user_id)
    """
    query = db.query(Alert)
    if user_id:
        query = query.filter(Alert.user_id == user_id)
    return query.all()

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Delete a selected alert
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} does not exist."
        )
    db.delete(alert)
    db.commit()
    return None
