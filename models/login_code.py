from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base

class LoginCode(Base):
    __tablename__ = "login_codes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    code = Column(String(12), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=datetime.utcnow)
