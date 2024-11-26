from sqlalchemy import Column, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class QualityCheck(Base):
    __tablename__ = "quality_checks"
    id = Column(Integer, primary_key=True, index=True)
    user_task_id = Column(Integer, ForeignKey("user_tasks.id", ondelete="CASCADE"))
    issues = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
