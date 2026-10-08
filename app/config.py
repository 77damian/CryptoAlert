from pydantic_settings import BaseSettings, SettingsConfigDict

# This class provides access to variables from the .env file.
# Values can be used throughout the app via e.g. settings.DATABASE_URL

class Settings(BaseSettings):
    APP_NAME: str = "CryptoAlert"
    DEBUG: bool = True

    # Database connection URL (defaults to local SQLite file)
    DATABASE_URL: str = "sqlite:///./cryptoalert.db"

    # Email (SMTP) settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Configuration for loading the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Global settings instance available across the entire application
settings = Settings()
