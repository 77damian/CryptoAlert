#  CryptoAlert

An automated cryptocurrency tracking system that monitors market changes and sends personalized email alerts when prices reach a set target.

##  Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the example file and fill in your own values:

```bash
cp .env.example .env
```

Open `.env` and set your SMTP credentials:

```ini
APP_NAME="CryptoAlert"
DATABASE_URL="sqlite:///./cryptoalert.db"

SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your_email@gmail.com"
SMTP_PASSWORD="your_app_password"
```

> **Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular account password.

### 3. Run the application

```bash
python -m uvicorn app.main:app --reload
```

The app will be available at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

