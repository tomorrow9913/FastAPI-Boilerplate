from pydantic_settings import BaseSettings


class CryptConfig(BaseSettings):
    SECRET_KEY: str = "default_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
