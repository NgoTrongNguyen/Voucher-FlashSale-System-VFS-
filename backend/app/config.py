from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Quản lý cấu hình application, đọc file .env

    # Database configuration
    DATABASE_URL: str = "postgresql://voucher_user:voucher_pass123@localhost:5432/voucher_db"
    DB_ECHO: bool = False

    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    REDIS_SOCKET_TIMEOUT: int = 5

    # Kafka configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_VOUCHER: str = "voucher_events"
    KAFKA_GROUP_ID: str = "voucher_consumer_group"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"
    KAFFKA_MAX_POOL_RECORDS: int = 100

    # Server configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False

    # Logging configuration
    LOG_LEVEL: str = "INFO"

    # CORS configuration
    CORS_ORIGINS: List[str] = ["https://localhost:3000", "https://localhost:5173"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # Bussiness configuration
    CLAIM_COOLDOWN_SECONDS: int = 1
    KAFKA_PROCESS_TIMEOUT_SECONDS: int = 15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()