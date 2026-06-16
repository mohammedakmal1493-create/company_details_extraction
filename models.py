from sqlalchemy import Column, String, Numeric
from database import Base

class Company(Base):
    __tablename__ = "companies"

    CIN = Column(String, primary_key=True, index=True, nullable=False)
    Company_Name = Column(String, nullable=True)
    Company_Registration_Date = Column(String, nullable=True)
    Company_Status = Column(String, nullable=True)
    Company_Class = Column(String, nullable=True)
    Company_Category = Column(String, nullable=True)
    Company_ROC = Column(String, nullable=True)
    Authorized_Capital = Column(Numeric, nullable=True)
    Paidup_Capital = Column(Numeric, nullable=True)
    Company_Address = Column(String, nullable=True)
    Company_State = Column(String, nullable=True)
    Pin_Code = Column(String, nullable=True)
    
    # Matching hidden fields called out inside your details layout template block
    Listing_Status = Column(String, nullable=True, default="Unlisted")
    Company_Sub_Category = Column(String, nullable=True, default="Non-govt company")
    Company_Industrial_Classification = Column(String, nullable=True)
    
    # Enrichment fields called out inside your dashboard layout panel
    website = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    enrichment_status = Column(String, default="PENDING")

    @property
    def id(self):
        """Allows c.id from JavaScript fetches to correctly resolve into the row primary key (CIN)."""
        return self.CIN
