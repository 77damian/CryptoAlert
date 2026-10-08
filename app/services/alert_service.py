from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import Alert, Price, Notification
from app.services.email_service import send_alert_email

def check_and_trigger_alerts(db: Session):
    """
    Checks all active alerts and triggers the email service when conditions are met.
    """
    active_alerts = db.query(Alert).filter(Alert.is_active == True).all()
    triggered_count = 0

    for alert in active_alerts:
        # Fetch the latest price for this coin
        latest_price = db.query(Price)\
                         .filter(Price.coin_id == alert.coin_id)\
                         .order_by(Price.recorded_at.desc())\
                         .first()

        if not latest_price:
            continue

        # Check whether the alert condition is met
        is_triggered = False
        current_price = latest_price.price_usd
        change_24h = latest_price.change_24h or 0.0

        if alert.condition == "price_above" and current_price >= alert.target_value:
            is_triggered = True
        elif alert.condition == "price_below" and current_price <= alert.target_value:
            is_triggered = True
        elif alert.condition == "change_24h_above" and change_24h >= alert.target_value:
            is_triggered = True
        elif alert.condition == "change_24h_below" and change_24h <= alert.target_value:
            is_triggered = True

        if is_triggered:
            # Check whether a notification was already sent in the last 24 hours (anti-spam)
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            recent_notification = db.query(Notification)\
                                    .filter(Notification.alert_id == alert.id)\
                                    .filter(Notification.sent_at >= twenty_four_hours_ago)\
                                    .first()

            if not recent_notification:
                # Send the alert email
                email_sent = send_alert_email(
                    to_email=alert.user.email,
                    coin_name=alert.coin.name,
                    symbol=alert.coin.symbol,
                    current_price=current_price,
                    condition=alert.condition,
                    target_value=alert.target_value,
                    change_24h=change_24h
                )

                if email_sent:
                    # Save the notification record to prevent spam
                    new_notif = Notification(
                        alert_id=alert.id,
                        user_id=alert.user_id,
                        price_at_trigger=current_price
                    )
                    db.add(new_notif)
                    db.commit()
                    triggered_count += 1

    return triggered_count
