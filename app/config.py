from pydantic_settings import BaseSettings, SettingsConfigDict

# mamy dostep do danych z .env dzieki tej klasie, mozemy uzywac w kodzie np. settings.DATABASE_URL

class Settings(BaseSettings):
    APP_NAME: str = "CryptoAlert"
    DEBUG: bool = True
    
    # URL do bazy danych (domyślnie plik sqlite)
    DATABASE_URL: str = "sqlite:///./cryptoalert.db"
    
    # Ustawienia e-mail
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Konfiguracja wczytywania pliku .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instancja ustawień dostępna w całej aplikacji
settings = Settings()
