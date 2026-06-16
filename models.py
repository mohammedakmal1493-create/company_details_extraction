from sqlalchemy import Column, String, Numeric
from database import Base

class Company(Base):
    """
    SQLAlchemy ORM Model representing the central target corporate registry.
    Maps explicitly to your Supabase PostgreSQL 'companies' table layout.
    """
    # Force alignment with the exact table naming structure inside your schema
    __tablename__ = "companies"

    # Primary Key identifier column sequence matches
    CIN = Column(String, primary_key=True, index=True, nullable=False)
    
    # Core Corporate Profile Specification Elements
    Company_Name = Column(String, nullable=True)
    Company_Registration_Date = Column(String, nullable=True)
    Company_Status = Column(String, nullable=True)
    Company_Class = Column(String, nullable=True)
    Company_Category = Column(String, nullable=True)
    Company_ROC = Column(String, nullable=True)
    
    # Financial Assets Matrix (Numeric maps perfectly to postgres decimal arrays)
    Authorized_Capital = Column(Numeric, nullable=True)
    Paidup_Capital = Column(Numeric, nullable=True)
    
    # Regional Location Identification Targets
    Company_Address = Column(String, nullable=True)
    Company_State = Column(String, nullable=True)
    Pin_Code = Column(String, nullable=True)
    
    # Industry Class Metrics
    Company_Industrial_Classification = Column(String, nullable=True)
    
    # Operational Process State Tracking Metric
    enrichment_status = Column(String, default="PENDING")
