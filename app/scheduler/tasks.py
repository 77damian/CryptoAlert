from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import SessionLocal
from app.services.price_service import fetch_and_save_prices
from app.services.alert_service import check_and_trigger_alerts

# Responsible for fetching prices at a defined interval

# Initialize the async scheduler
scheduler = AsyncIOScheduler()

async def scheduled_crypto_job():
    """
    Recurring background job executed by the scheduler:
    1. Opens a database session.
    2. Fetches and saves the latest prices from the CoinGecko API.
    3. Checks alerts and triggers email notifications.
    4. Closes the database session.
    """
    print("\n[SCHEDULER] Running scheduled cryptocurrency market check...")
    db = SessionLocal()
    try:
        # 1. Fetch and save prices
        saved_prices = await fetch_and_save_prices(db)
        print(f"[SCHEDULER] Updated prices for {len(saved_prices)} coins.")

        # 2. Check alerts
        triggered_count = check_and_trigger_alerts(db)
        print(f"[SCHEDULER] Alerts checked. {triggered_count} notification(s) triggered.\n")
    except Exception as e:
        print(f"[SCHEDULER ERROR] Error during scheduled job execution: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Starts the background scheduler. The job runs at the specified interval (e.g. every 1 minute).
    """
    refresh_minutes = 1
    scheduler.add_job(scheduled_crypto_job, "interval", minutes=refresh_minutes, id="crypto_job", replace_existing=True)
    scheduler.start()
    print(f"[SCHEDULER] APScheduler started successfully (refresh every {refresh_minutes} minute(s)).")


def stop_scheduler():
    """
    Stops the scheduler when the application shuts down.
    """
    scheduler.shutdown()
    print("[SCHEDULER] APScheduler stopped.")
