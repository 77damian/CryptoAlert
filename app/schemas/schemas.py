from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# ----------------------------------------
# USER SCHEMAS
# ----------------------------------------

class UserCreate(BaseModel):
    """Data required for user registration"""
    email: EmailStr

class UserResponse(BaseModel):
    """User data sent in API response"""
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------------------
# COIN SCHEMAS
# ----------------------------------------

class CoinCreate(BaseModel):
    """Data required when adding a new coin"""
    symbol: str
    name: str
    coingecko_id: str

class CoinResponse(BaseModel):
    """Coin data sent in API response"""
    id: int
    symbol: str
    name: str
    coingecko_id: str
    is_active: bool

    class Config:
        from_attributes = True

class CoinWithPriceResponse(CoinResponse):
    """Coin data enriched with the last known price"""
    latest_price: Optional[float] = None


# ----------------------------------------
# ALERT SCHEMAS
# ----------------------------------------

class AlertCreate(BaseModel):
    """Data required when creating a new alert"""
    user_id: int
    coin_id: int
    condition: str = Field(
        ..., 
        description="Condition type: 'price_above', 'price_below', 'change_24h_above', 'change_24h_below'"
    )
    target_value: float = Field(..., description="Threshold value (e.g. 60000.0 for USD or 5.0 for %)")

class AlertResponse(BaseModel):
    """Alert data sent in API response"""
    id: int
    user_id: int
    coin_id: int
    condition: str
    target_value: float
    is_active: bool
    created_at: datetime
    coin: Optional[CoinResponse] = None

    class Config:
        from_attributes = True
