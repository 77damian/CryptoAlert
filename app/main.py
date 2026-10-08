from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database import engine, Base, get_db
import app.models  # Import ORM models
from app.services.price_service import fetch_and_save_prices
from app.services.alert_service import check_and_trigger_alerts
from app.scheduler.tasks import start_scheduler, stop_scheduler

from app.api.users import router as users_router
from app.api.alerts import router as alerts_router
from app.api.coins import router as coins_router

# Create tables in the database
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage FastAPI application lifecycle:
    Starts the scheduler on startup and stops it on shutdown.
    """
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(
    title=settings.APP_NAME,
    description="CryptoAlert API - cryptocurrency price monitoring and email alert system",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers with endpoints
app.include_router(users_router)
app.include_router(alerts_router)
app.include_router(coins_router)

# Mount the static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", tags=["UI"])
def read_root():
    """Serves the main application interface (Frontend)"""
    return FileResponse("app/static/index.html")

@app.post("/fetch-prices", tags=["Prices"])
async def trigger_price_fetch(db: Session = Depends(get_db)):
    """
    Manual trigger to fetch the latest prices from CoinGecko API and save them to the database.
    """
    saved_prices = await fetch_and_save_prices(db)
    return {
        "message": f"Successfully fetched and saved prices for {len(saved_prices)} coins.",
        "count": len(saved_prices)
    }

@app.post("/check-alerts", tags=["Alerts"])
def trigger_alert_check(db: Session = Depends(get_db)):
    """
    Manual trigger to check alerts and send emails.
    """
    triggered_count = check_and_trigger_alerts(db)
    return {
        "message": f"Checked alerts. Triggered and sent {triggered_count} notifications.",
        "triggered_count": triggered_count
    }
