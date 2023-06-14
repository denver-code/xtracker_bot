from typing import List, Union
from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    PROJECT_NAME: str
    # DATABASE_URL: str
    WHITELIST: List[int] = []
    TOKEN: str

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
