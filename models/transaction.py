from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum
from datetime import datetime
from .base import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    
    # 4 TIPOS: renda, despesa_fixa, despesa_variavel, economia
    type = Column(Enum('renda', 'despesa_fixa', 'despesa_variavel', 'economia', name='transaction_type'), nullable=False)
    
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(200))
    date = Column(Date, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    detected_by = Column(String(50), default='manual')
    original_message = Column(String(500))
    
    def __repr__(self):
        return f"<Transaction(type={self.type}, amount={self.amount}, category={self.category})>"
    
    @property
    def is_income(self):
        return self.type == 'renda'
    
    @property 
    def is_expense(self):
        return self.type in ['despesa_fixa', 'despesa_variavel']
    
    @property
    def is_savings(self):
        return self.type == 'economia'
    
    @property
    def signed_amount(self):
        if self.is_income:
            return self.amount
        else:
            return -self.amount