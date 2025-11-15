# models/financial_goal.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from datetime import datetime
from .base import Base

class FinancialGoal(Base):
    __tablename__ = "financial_goals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    telegram_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(Date, nullable=False)
    category = Column(String(100))  # 'viagem', 'reserva', 'investimento', 'casa', 'carro'
    priority = Column(Integer, default=1)  # 1-5, onde 5 é mais importante
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'progress_percentage': self.progress_percentage,
            'remaining_amount': self.target_amount - self.current_amount,
            'deadline': self.deadline,
            'days_remaining': self.days_remaining,
            'category': self.category,
            'priority': self.priority,
            'created_at': self.created_at
        }
    
    @property
    def progress_percentage(self):
        """Calcula o progresso em porcentagem"""
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100
    
    @property
    def days_remaining(self):
        """Calcula dias restantes"""
        remaining = (self.deadline - datetime.now().date()).days
        return max(0, remaining)