from functools import lru_cache
import os
from pydantic import Field

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DJANGO_KEY:str
    DB_URL: str
    DB_NAME: str
    DB_PASS: str
    DB_PORT: int
    DB_USER: str

    class Config:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(current_dir, '.env')
        env_file_encoding = "utf-8"



settings = Settings()
