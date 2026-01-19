from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tier = Column(String, default="free", nullable=False)
    credits_remaining = Column(Integer, default=10, nullable=False)
    credits_reset_date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def reset_credits_if_needed(self):
        if self.credits_reset_date and datetime.utcnow() >= self.credits_reset_date:
            credits_map = {"free": 10, "academic": 100, "pro": 1000, "enterprise": 10000}
            self.credits_remaining = credits_map.get(self.tier, 10)
            self.credits_reset_date = datetime.utcnow() + timedelta(days=30)
    
    def __repr__(self):
        return f"<User(email={self.email}, tier={self.tier}, credits={self.credits_remaining})>"
