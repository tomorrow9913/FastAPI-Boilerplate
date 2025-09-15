from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    WRITER_DB_URL: str
    READER_DB_URL: str

    REDIS_URL: str
