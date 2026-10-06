import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from app.config import settings

# Szablon HTML wiadomości e-mail
EMAIL_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
        .card { background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
        .header { color: #e53e3e; font-size: 20px; font-weight: bold; }
        .info { margin: 15px 0; font-size: 16px; line-height: 1.5; }
        .footer { font-size: 12px; color: #888888; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">Price Alert: {{ coin_name }} ({{ symbol }})</div>
        <div class="info">
            <strong>Hello! Your alert for {{ coin_name }} has been triggered!</strong><br><br>
            <strong>Current price:</strong> {{ current_price }} USD<br>
            <strong>24h change:</strong> {{ change_24h }}% <br>
            <strong>Your condition:</strong> {{ condition_text }} {{ target_value }}<br>
        </div>
        <div class="footer">
            Message generated automatically by CryptoAlert API.
        </div>
    </div>
</body>
</html>
"""

def send_alert_email(to_email: str, coin_name: str, symbol: str, current_price: float, condition: str, target_value: float, change_24h: float):
    """
    Wysyła e-mail z alertem.
    """
    condition_text_map = {
        "price_above": ("went above", "Price above"),
        "price_below": ("went below", "Price below"),
        "change_24h_above": ("in last 24h gained above", "24h gain above"),
        "change_24h_below": ("in last 24h dropped below", "24h drop below")
    }
    subject_text, body_text = condition_text_map.get(condition, (condition, condition))

    # Renderujemy treść e-maila za pomocą Jinja2
    template = Template(EMAIL_HTML_TEMPLATE)
    html_content = template.render(
        coin_name=coin_name,
        symbol=symbol,
        current_price=f"{current_price:,.2f}",
        condition_text=body_text,
        target_value=f"{target_value:,.2f}",
        change_24h=f"{change_24h:+.2f}" if change_24h is not None else "0.00"
    )

    subject = f"🚨 CryptoAlert: {symbol} {subject_text} {target_value}"


    # wysyłka SMTP przez serwer pocztowy
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"CryptoAlert <{settings.SMTP_USER}>"
        msg["To"] = to_email

        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)

        # Bezpieczne połączenie z serwerem SMTP
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        server.quit()
        
        print(f"Sukces: Wysłano e-mail do {to_email}")
        return True
    except Exception as e:
        print(f"Błąd wysyłania e-maila do {to_email}: {e}")
        return False
