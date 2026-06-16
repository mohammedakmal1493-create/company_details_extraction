from sqlalchemy import Column, Integer, String, Text, Enum, BigInteger
from database import Base
import enum

class EnrichmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    enrichment_status = Column(Enum(EnrichmentStatus), default=EnrichmentStatus.PENDING)
    website = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    
    # Exact field names matching your MySQL Workbench layout
    CIN = Column(String(50), unique=True, nullable=False)
    Company_Name = Column(String(255), nullable=False)
    Company_Registration_Date = Column(String(50))
    Company_Category = Column(String(100))
    Company_Class = Column(String(100))
    Listing_Status = Column(String(50))
    Authorized_Capital = Column(BigInteger)
    Paidup_Capital = Column(BigInteger)
    Company_ROC = Column(String(100))
    Company_Address = Column(Text)
    Pin_Code = Column(String(20))
    Company_State = Column(String(100))
    Company_Status = Column(String(100))
    Company_Sub_Category = Column(String(100))
    Company_Industrial_Classification = Column(String(100))