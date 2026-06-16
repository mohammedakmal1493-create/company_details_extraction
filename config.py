import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str = "postgres.huaunrcimslfefjnwzvz"
    DB_PASSWORD: str = "RnBS01iSLCnzyU7y"
    DB_HOST: str = "aws-1-ap-northeast-1.pooler.supabase.com"  # <- If this is the direct host, ensure port is 5432
    DB_PORT: str = "5432"  # <- Direct connection port
    DB_NAME: str = "postgres"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
