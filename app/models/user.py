# User model

from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    profile_picture = Column(Text)
    auth_provider = Column(String(10), nullable=False, default="email")
    role = Column(String(10), nullable=False, default="user")  # "user" or "admin"
    created_at = Column(DateTime, server_default=func.now())
    
    # Unique constraint across users
    __table_args__ = (UniqueConstraint('email', name='_user_email_uc'),)

    # Relationship to access all tasks assigned to this user
    user_tasks = relationship("UserTask", back_populates="user")
