from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# ----------------------------------------
# SCHEMATY UŻYTKOWNIKA (USER)
# ----------------------------------------

class UserCreate(BaseModel):
    """Dane wymagane przy rejestracji użytkownika"""
    email: EmailStr

class UserResponse(BaseModel):
    """Dane użytkownika odsyłane w odpowiedzi API"""
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------------------
# SCHEMATY MONET (COIN)
# ----------------------------------------

class CoinCreate(BaseModel):
    """Dane wymagane przy dodawaniu nowej monety"""
    symbol: str
    name: str
    coingecko_id: str

class CoinResponse(BaseModel):
    """Dane monety odsyłane w odpowiedzi API"""
    id: int
    symbol: str
    name: str
    coingecko_id: str
    is_active: bool

    class Config:
        from_attributes = True

class CoinWithPriceResponse(CoinResponse):
    """Dane monety wzbogacone o ostatnią znaną cenę"""
    latest_price: Optional[float] = None


# ----------------------------------------
# SCHEMATY ALERTÓW (ALERT)
# ----------------------------------------

class AlertCreate(BaseModel):
    """Dane wymagane przy tworzeniu nowego alertu"""
    user_id: int
    coin_id: int
    condition: str = Field(
        ..., 
        description="Typ warunku: 'price_above', 'price_below', 'change_24h_above', 'change_24h_below'"
    )
    target_value: float = Field(..., description="Wartość progowa (np. 60000.0 dla USD lub 5.0 dla %)")

class AlertResponse(BaseModel):
    """Dane alertu odsyłane w odpowiedzi API"""
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
