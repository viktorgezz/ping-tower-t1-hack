import os
from typing import Optional

class Settings:
    """Конфигурация приложения"""
    
    # ClickHouse настройки
    CLICKHOUSE_HOST: str = os.getenv("CLICKHOUSE_HOST", "203.81.208.57")
    CLICKHOUSE_PORT: int = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    CLICKHOUSE_DATABASE: str = os.getenv("CLICKHOUSE_DATABASE", "default")
    CLICKHOUSE_USER: Optional[str] = os.getenv("CLICKHOUSE_USER", "admin")
    CLICKHOUSE_PASSWORD: Optional[str] = os.getenv("CLICKHOUSE_PASSWORD", "Passw0rd")
    
    # API настройки
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Настройки анализа
    DEFAULT_CHECK_COUNT: int = int(os.getenv("DEFAULT_CHECK_COUNT", "100"))
    MAX_CHECK_COUNT: int = int(os.getenv("MAX_CHECK_COUNT", "1000"))

settings = Settings()
