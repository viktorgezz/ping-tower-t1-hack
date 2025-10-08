from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List

class Settings(BaseSettings):
    # Основные настройки
    app_name: str = "PingTower API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Настройки сервера
    host: str = "0.0.0.0"
    port: int = 8000
    
    # JWT настройки
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # База данных PostgreSQL
    database_url: str = Field(
        default="postgresql://postgres:Passw0rd@203.81.208.57:5432/hack",
        env="DATABASE_URL"
    )
    
    # CORS настройки
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    # Настройки логирования
    log_level: str = "INFO"
    
    # Настройки мониторинга
    default_timeout: int = 5000  # мс
    check_interval: int = 60  # секунды
    
    class Config:
        env_file = ".env"

settings = Settings()
