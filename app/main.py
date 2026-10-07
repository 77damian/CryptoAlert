from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database import engine, Base, get_db
import app.models  # Import modeli ORM
from app.services.price_service import fetch_and_save_prices
from app.services.alert_service import check_and_trigger_alerts
from app.scheduler.tasks import start_scheduler, stop_scheduler

from app.api.users import router as users_router
from app.api.alerts import router as alerts_router
from app.api.coins import router as coins_router

# Tworzymy tabele w bazie danych
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Zarządzanie cyklem życia aplikacji FastAPI:
    Startuje scheduler przy uruchomieniu i wyłącza go przy zamknięciu.
    """
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(
    title=settings.APP_NAME,
    description="CryptoAlert API - system monitorowania cen kryptowalut i wysyłania alertów e-mail",
    version="1.0.0",
    lifespan=lifespan
)

# Podłączamy routery z endpointami
app.include_router(users_router)
app.include_router(alerts_router)
app.include_router(coins_router)

# Podłączamy folder statyczny
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", tags=["UI"])
def read_root():
    """Serwuje główny interfejs aplikacji (Frontend)"""
    return FileResponse("app/static/index.html")

@app.post("/fetch-prices", tags=["Prices"])
async def trigger_price_fetch(db: Session = Depends(get_db)):
    """
    Ręczne wyzwolenie pobrania najnowszych cen z CoinGecko API i zapisania ich do bazy.
    """
    saved_prices = await fetch_and_save_prices(db)
    return {
        "message": f"Pomyślnie pobrano i zapisano ceny dla {len(saved_prices)} monet.",
        "count": len(saved_prices)
    }

@app.post("/check-alerts", tags=["Alerts"])
def trigger_alert_check(db: Session = Depends(get_db)):
    """
    Ręczne wyzwolenie sprawdzania alertów i wysyłki e-maili.
    """
    triggered_count = check_and_trigger_alerts(db)
    return {
        "message": f"Sprawdzono alerty. Wyzwolono i wysłano {triggered_count} powiadomień.",
        "triggered_count": triggered_count
    }
