import os

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eventlog.db")
    API_KEY: str = os.getenv("API_KEY", "dev-key")


settings = Settings()
