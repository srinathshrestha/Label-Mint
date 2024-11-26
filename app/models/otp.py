from sqlalchemy import Column, Integer, String, DateTime
from app.db.session import Base

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    otp = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
