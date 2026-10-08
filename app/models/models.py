from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Coin(Base):
    """Dictionary of cryptocurrencies monitored in the application"""
    __tablename__ = "coins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)      # e.g. BTC
    name: Mapped[str] = mapped_column(String(100))                                 # e.g. Bitcoin
    coingecko_id: Mapped[str] = mapped_column(String(100), unique=True)           # e.g. bitcoin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    prices: Mapped[List["Price"]] = relationship("Price", back_populates="coin", cascade="all, delete-orphan")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="coin", cascade="all, delete-orphan")


class Price(Base):
    """History of cryptocurrency price measurements"""
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    coin_id: Mapped[int] = mapped_column(Integer, ForeignKey("coins.id"), index=True)
    price_usd: Mapped[float] = mapped_column(Float)
    change_24h: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    market_cap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume_24h: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    coin: Mapped["Coin"] = relationship("Coin", back_populates="prices")


class User(Base):
    """Users/subscribers of alerts"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Alert(Base):
    """Alert conditions set by users"""
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    coin_id: Mapped[int] = mapped_column(Integer, ForeignKey("coins.id"), index=True)
    
    # price_above, price_below, change_24h_above, change_24h_below
    condition: Mapped[str] = mapped_column(String(50))
    target_value: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="alerts")
    coin: Mapped["Coin"] = relationship("Coin", back_populates="alerts")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="alert", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "condition IN ('price_above', 'price_below', 'change_24h_above', 'change_24h_below')",
            name="check_valid_condition"
        ),
    )


class Notification(Base):
    """History of sent email notifications (prevents spamming)"""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[int] = mapped_column(Integer, ForeignKey("alerts.id"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    price_at_trigger: Mapped[float] = mapped_column(Float)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    alert: Mapped["Alert"] = relationship("Alert", back_populates="notifications")
    user: Mapped["User"] = relationship("User", back_populates="notifications")
