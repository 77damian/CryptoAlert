from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Coin, Price
from app.schemas.schemas import CoinResponse, CoinCreate, CoinWithPriceResponse

router = APIRouter(prefix="/coins", tags=["Coins"])

@router.get("/", response_model=List[CoinWithPriceResponse])
def list_coins(db: Session = Depends(get_db)):
    """
    Get the list of all monitored cryptocurrencies along with the current price
    """
    coins = db.query(Coin).filter(Coin.is_active == True).all()
    result = []
    for coin in coins:
        latest_price = db.query(Price).filter(Price.coin_id == coin.id).order_by(Price.recorded_at.desc()).first()
        
        # Create a dictionary with coin data and append the price
        coin_data = {
            "id": coin.id,
            "symbol": coin.symbol,
            "name": coin.name,
            "coingecko_id": coin.coingecko_id,
            "is_active": coin.is_active,
            "latest_price": latest_price.price_usd if latest_price else None
        }
        result.append(coin_data)
        
    return result

@router.get("/{coin_id}/prices")
def get_coin_price_history(coin_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """
    Get price history for a selected cryptocurrency
    """
    coin = db.query(Coin).filter(Coin.id == coin_id).first()
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with ID {coin_id} does not exist."
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

@router.post("/", response_model=CoinResponse, status_code=status.HTTP_201_CREATED)
def create_coin(coin_in: CoinCreate, db: Session = Depends(get_db)):
    """
    Add a new cryptocurrency for monitoring
    """
    existing_coin = db.query(Coin).filter(Coin.coingecko_id == coin_in.coingecko_id).first()
    if existing_coin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This cryptocurrency is already being monitored."
        )
    
    new_coin = Coin(
        symbol=coin_in.symbol,
        name=coin_in.name,
        coingecko_id=coin_in.coingecko_id
    )
    db.add(new_coin)
    db.commit()
    db.refresh(new_coin)
    return new_coin

@router.delete("/{coin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coin(coin_id: int, db: Session = Depends(get_db)):
    """
    Delete a cryptocurrency by ID
    """
    coin = db.query(Coin).filter(Coin.id == coin_id).first()
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cryptocurrency not found."
        )
    
    db.delete(coin)
    db.commit()
    return None
