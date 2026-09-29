from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "rifadb"
    JWT_SECRET: str = "change-this-in-production-rifa-secret-key-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 8

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "rifa2024"

    # Twilio SMS (opcional)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # Email SMTP
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_FROM_NAME: str = "Movimiento Faro"
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587

    # Información de la Rifa y Pago
    RAFFLE_NAME: str = "Integración de Amistad - Día del Movimiento Faro"
    EVENT_DATE: str = "Sábado 3 de Octubre de 2026"
    EVENT_TIME: str = "7:30PM"
    EVENT_PLACE: str = "Salón de eventos Parque del Amor"
    PAYMENT_BANK: str = "Bancolombia"
    PAYMENT_ACCOUNT_NUMBER: str = "123-456789-00"
    PAYMENT_ACCOUNT_TYPE: str = "Cuenta de Ahorros"
    PAYMENT_OWNER: str = "Organización Rifa"
    PAYMENT_DOCUMENT: str = "900.123.456-7"

    class Config:
        env_file = ".env"


settings = Settings()
