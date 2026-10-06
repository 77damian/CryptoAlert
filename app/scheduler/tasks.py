from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import SessionLocal
from app.services.price_service import fetch_and_save_prices
from app.services.alert_service import check_and_trigger_alerts

# odpowiada za pobieranie cen co okreslony czas 

# Inicjalizacja asynchronicznego schedulera
scheduler = AsyncIOScheduler()

async def scheduled_crypto_job():
    """
    Zadanie wykonywane cyklicznie przez scheduler w tle:
    1. Otwiera sesję bazy danych.
    2. Pobiera i zapisuje najnowsze ceny z CoinGecko API.
    3. Sprawdza alerty i wyzwala powiadomienia e-mail.
    4. Zamyka sesję bazy.
    """
    print("\n[SCHEDULER] Uruchamiam cykliczne sprawdzanie rynku kryptowalut...")
    db = SessionLocal()
    try:
        # 1. Pobranie i zapis cen
        saved_prices = await fetch_and_save_prices(db)
        print(f"[SCHEDULER] Zaktualizowano ceny dla {len(saved_prices)} monet.")

        # 2. Sprawdzenie alertów
        triggered_count = check_and_trigger_alerts(db)
        print(f"[SCHEDULER] Sprawdzono alerty. Wyzwolono {triggered_count} powiadomień.\n")
    except Exception as e:
        print(f"[SCHEDULER ERROR] Błąd podczas wykonywania zadania cyklicznego: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Uruchamia scheduler w tle. Zadanie będzie się wykonywać np. co 1 minutę.
    """
    refresh_minutes = 1
    scheduler.add_job(scheduled_crypto_job, "interval", minutes=refresh_minutes, id="crypto_job", replace_existing=True)
    scheduler.start()
    print(f"[SCHEDULER] APScheduler został pomyślnie uruchomiony (odświeżenie co {refresh_minutes} minut).")


def stop_scheduler():
    """
    Zatrzymuje scheduler przy wyłączaniu aplikacji.
    """
    scheduler.shutdown()
    print("[SCHEDULER] APScheduler został zatrzymany.")
