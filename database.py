from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Settings 

# 1. Initialize the Settings template structure to read your cloud credentials
settings_instance = Settings()

# 2. Build the database engine connection pooler framework.
# The connect_args dictionary forces SSL encryption, which is strictly required 
# by Supabase to allow queries coming from external servers like Render.
engine = create_engine(
    settings_instance.DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# 3. Create session factories for request-scoped database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Define the declarative base wrapper context template for ORM models mapping
Base = declarative_base()

def get_db():
    """
    Database Session Dependency Lifecycle Provider.
    Yields an active database transactional context loop per request,
    and cleanly tears down the state connection thread when the endpoint terminates.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
