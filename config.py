import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str = os.getenv("DB_USER", "root")
    # REPLACE THIS WITH YOUR ACTUAL MYSQL WORKBENCH PASSWORD
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "company_enrichment")

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()