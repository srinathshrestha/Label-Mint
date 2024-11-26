# Task model

from sqlalchemy import Column, Integer, Numeric, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    image_url = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)  # "classification" or "object_detection"
    token_reward = Column(Numeric, nullable=False, default=10)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship to access all user assignments related to this task
    user_tasks = relationship("UserTask", back_populates="task")


class UserTask(Base):
    __tablename__ = "user_tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    status = Column(String(20), nullable=False, default="pending")  # "pending", "completed", "reviewed"
    labeled_data = Column(JSON)
    submitted_at = Column(DateTime)
    review_status = Column(String(20), nullable=False, default="pending")  # "pending", "approved", "rejected"
    feedback = Column(Text)

    # Relationships to User and Task
    user = relationship("User", back_populates="user_tasks")
    task = relationship("Task", back_populates="user_tasks")
