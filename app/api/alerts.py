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
    Tworzenie nowego alertu cenowego dla użytkownika
    """
    # 1. Sprawdzamy czy warunek jest poprawny
    if alert_in.condition not in ALLOWED_CONDITIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Niedozwolony warunek. Dozwolone warunki to: {', '.join(ALLOWED_CONDITIONS)}"
        )

    # 2. Sprawdzamy czy użytkownik istnieje
    user = db.query(User).filter(User.id == alert_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Użytkownik o ID {alert_in.user_id} nie istnieje."
        )

    # 3. Sprawdzamy czy moneta istnieje
    coin = db.query(Coin).filter(Coin.id == alert_in.coin_id).first()
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kryptowaluta o ID {alert_in.coin_id} nie istnieje."
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
    Pobranie listy alertów (opcjonalnie przefiltrowanych po user_id)
    """
    query = db.query(Alert)
    if user_id:
        query = query.filter(Alert.user_id == user_id)
    return query.all()

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Usuwanie wybranego alertu
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert o ID {alert_id} nie istnieje."
        )
    db.delete(alert)
    db.commit()
    return None
