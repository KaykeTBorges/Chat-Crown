from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .base import Base

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    category = Column(String(100), nullable=False)
    monthly_amount = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Budget(category={self.category}, amount={self.monthly_amount})>"