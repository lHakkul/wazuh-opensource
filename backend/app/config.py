from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    WAZUH_API_URL: str = "https://localhost:55000"
    WAZUH_API_USER: str = "wazuh"
    WAZUH_API_PASSWORD: str = "wazuh"
    WAZUH_VERIFY_SSL: bool = False

    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None

    ALERT_CHECK_INTERVAL: int = 60
    HISTORY_MAX_EVENTS: int = 200

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    WAZUH_MOCK: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
