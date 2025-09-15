import os
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
    APP_NAME: str | None = os.getenv("APP_NAME")
    APP_DESCRIPTION: str | None = os.getenv("APP_DESCRIPTION")
    APP_VERSION: str | None = os.getenv("APP_VERSION")

    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"

    POD_CONTROLLER_SERVICE: str = os.getenv(
        "POD_CONTROLLER", "pod-manager-service.pod-manager.svc.cluster.local"
    )

    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = (pathlib.Path(__file__).resolve().parents[3] / "logs").as_posix()
    LOG_FILE: str = "app.log"
    LOG_MAX_BYTES: int = 10485760  # 10 MB
    LOG_BACKUP_COUNT: int = 5
    LOG_NOTIFIER_URL: str | None = os.getenv("LOG_NOTIFIER_URL")

    YAPPI_PROFILE_ENABLE: bool = os.getenv("YAPPI_PROFILE_ENABLE", "False") == "True"

    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_SENDER_EMAIL: str | None = os.getenv("SMTP_SENDER_EMAIL")
    SMTP_SENDER_PASSWORD: str | None = os.getenv("SMTP_SENDER_PASSWORD")

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
