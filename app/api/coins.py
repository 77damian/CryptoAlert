from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Coin, Price
from app.schemas.schemas import CoinResponse

router = APIRouter(prefix="/coins", tags=["Coins"])

@router.get("/", response_model=List[CoinResponse])
def list_coins(db: Session = Depends(get_db)):
    """
    Pobranie listy wszystkich monitorowanych kryptowalut
    """
    return db.query(Coin).filter(Coin.is_active == True).all()

@router.get("/{coin_id}/prices")
def get_coin_price_history(coin_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """
    Pobranie historii cen dla wybranej kryptowaluty
    """
    coin = db.query(Coin).filter(Coin.id == coin_id).first()
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kryptowaluta o ID {coin_id} nie istnieje."
        )

    prices = db.query(Price)\
               .filter(Price.coin_id == coin_id)\
               .order_by(Price.recorded_at.desc())\
               .limit(limit)\
               .all()
    
    return {
        "coin": coin.name,
        "symbol": coin.symbol,
        "history_count": len(prices),
        "prices": prices
    }
