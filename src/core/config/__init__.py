import os
import pathlib
from functools import lru_cache

from dotenv import load_dotenv

from src.core.config.app_config import AppConfig
from src.core.config.crypt_config import CryptConfig
from src.core.config.database_config import DatabaseConfig


class Config:
    ENV: str
    APP_CONFIG: AppConfig
    DATABASE_CONFIG: DatabaseConfig
    SECURITY_CONFIG: CryptConfig

    def __init__(self, env: str):
        self.ENV = env
        self.APP_CONFIG = AppConfig()  # Pass env to AppConfig
        self.DATABASE_CONFIG = DatabaseConfig()  # Initialize without env argument
        self.SECURITY_CONFIG = CryptConfig()  # Initialize without env argument


@lru_cache
def get_config(env: str) -> Config:
    config_type = ["test", "local", "prod"]
    if env not in config_type:
        raise ValueError(f"Invalid environment: {env}. Choose from {config_type}.")

    # Load environment variables from .env file (before initializing Pydantic settings)
    print(f"Loading environment variables from .{env}.env")
    env_file = pathlib.Path(__file__).resolve().parents[3] / f".{env}.env"
    load_dotenv(env_file)

    return Config(env)


config: Config = get_config(os.getenv("ENV", "local"))
