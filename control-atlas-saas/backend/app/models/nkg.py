from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
class NKGRegistry(Base):
    __tablename__ = "nkg_registry"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True)
    primary_law = Column(String, index=True) 
    secondary_laws = Column(JSON)
    generator_model = Column(String, default="Chai-1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
