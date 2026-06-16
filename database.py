from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Settings 

settings_instance = Settings()

# Update your engine to force SSL mode requirement parameters
engine = create_engine(
    settings_instance.DATABASE_URL,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
