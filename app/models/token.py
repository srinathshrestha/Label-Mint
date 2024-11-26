# Token model

from sqlalchemy import Column, Integer, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token_balance = Column(Numeric, default=0)
    last_updated = Column(DateTime, server_default=func.now())


class Redemption(Base):
    __tablename__ = "redemptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    amount = Column(Numeric, nullable=False)
    transaction_hash = Column(Text)
    redeemed_at = Column(DateTime, server_default=func.now())
