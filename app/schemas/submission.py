from pydantic import BaseModel
from typing import Optional, Dict, Any, Union, List
from datetime import datetime

class ClassificationSubmission(BaseModel):
    label: str  # Example: "Cat" or "Dog"

class BoundingBox(BaseModel):
    label: str  # Example: "Car" or "Person"
    x: int
    y: int
    width: int
    height: int

class ObjectDetectionSubmission(BaseModel):
    bounding_boxes: List[BoundingBox]

class TaskSubmissionSchema(BaseModel):
    data: Union[ClassificationSubmission, ObjectDetectionSubmission]

class TaskInfo(BaseModel):
    id: int
    title: str
    type: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: str

class TaskSubmissionResponse(BaseModel):
    task: TaskInfo
    user: UserInfo
    status: str
    labeled_data: Optional[Dict[str, Any]]
    submitted_at: Optional[datetime]
    review_status: str
    feedback: Optional[str]

    class Config:
        from_attributes = True

class AdminReviewAction(BaseModel):
    action: str  # "approve" or "reject"
    feedback: Optional[str] = None  # Optional feedback message for rejections
