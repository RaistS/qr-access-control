from typing import List, Optional, Union
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "QR Access Control API"
    DATABASE_URL: str = "sqlite:///./qrac.db"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    QR_BASE_URL: Optional[Union[AnyHttpUrl, str]] = None

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = "QR Access Control"

settings = Settings()








