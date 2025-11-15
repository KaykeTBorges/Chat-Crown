# models/transaction.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False, index=True)
    user = relationship("User", back_populates="transactions")

    # Tipos: renda, despesa_fixa, despesa_variavel, economia
    type = Column(
        Enum("renda", "despesa_fixa", "despesa_variavel", "economia", name="transaction_type"),
        nullable=False
    )
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(200))
    date = Column(Date, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Campos extras
    detected_by = Column(String(50), default="manual")  # manual ou IA
    original_message = Column(String(500))  # mensagem original do bot

    def __repr__(self):
        return (
            f"<Transaction(telegram_id={self.telegram_id}, type={self.type}, "
            f"amount={self.amount}, category={self.category})>"
        )

    # Propriedades auxiliares (sem mudanças)
    @property
    def is_income(self):
        return self.type == "renda"

    @property
    def is_expense(self):
        return self.type in ["despesa_fixa", "despesa_variavel"]

    @property
    def is_savings(self):
        return self.type == "economia"

    @property
    def signed_amount(self):
        """Retorna positivo para renda e negativo para despesas/economia"""
        return self.amount if self.is_income else -self.amount