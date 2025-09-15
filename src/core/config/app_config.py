import pathlib

import toml
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application configuration settings.
    This class holds the configuration settings for the FastAPI application,
    including environment variables, application metadata, logging settings,
    """

    # https://fastapi.tiangolo.com/tutorial/metadata/
    # https://fastapi.tiangolo.com/reference/fastapi/
    APP_NAME: str | None = None
    APP_DESCRIPTION: str | None = None
    APP_VERSION: str | None = None

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = (pathlib.Path(__file__).resolve().parents[3] / "logs").as_posix()
    LOG_FILE: str = "app.log"
    LOG_MAX_BYTES: int = 10485760  # 10 MB
    LOG_BACKUP_COUNT: int = 5
    LOG_NOTIFIER_URL: str | None

    YAPPI_PROFILE_ENABLE: bool = False

    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_SENDER_EMAIL: str | None
    SMTP_SENDER_PASSWORD: str | None

    def __init__(self, **data):
        super().__init__(**data)

        pyproject_path = pathlib.Path(__file__).resolve().parents[3] / "pyproject.toml"
        pyproject_data = toml.load(pyproject_path)
        project_info = pyproject_data.get("project", {})

        self.APP_NAME = (
            self.APP_NAME or project_info.get("name", "FastAPI Template").capitalize()
        )
        self.APP_DESCRIPTION = self.APP_DESCRIPTION or project_info.get(
            "description", "This Is FastAPI Template"
        )
        self.APP_VERSION = self.APP_VERSION or project_info.get("version", "v0.0.1")
