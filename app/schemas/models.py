# app/schemas/models.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, Union, List
from datetime import datetime
from decimal import Decimal

# User Schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "user"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    profile_picture: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class UpdateUser(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class UserInfo(BaseModel):
    id: int
    username: str
    email: str

# Task Schemas
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    type: str  # "classification" or "object_detection"
    token_reward: int

class TaskResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    status: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    type: str
    created_at: datetime

    class Config:
        from_attributes = True

class MinimalTaskResponse(BaseModel):
    id: int
    title: str
    type: str  # Only the basic info

    class Config:
        from_attributes = True

class TaskDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    type: str
    created_at: datetime

    class Config:
        from_attributes = True

class TaskInfo(BaseModel):
    id: int
    title: str
    type: str

# UserTask Schemas
class UserTaskResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    status: str
    labeled_data: Optional[Union[str, Dict[str, Any]]] = None  # Allow None
    submitted_at: Optional[datetime] = None
    review_status: Optional[str] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,  # Serialize datetime to ISO 8601 string
        }

# Submission Schemas
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

class TaskSubmissionResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    status: str
    labeled_data: Optional[Dict[str, Any]]
    submitted_at: Optional[datetime]
    review_status: str
    feedback: Optional[str]

    class Config:
        from_attributes = True

# Admin Schemas
class AdminReviewAction(BaseModel):
    action: str  # "approve" or "reject"
    feedback: Optional[str] = None  # Optional feedback message for rejections

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

# Task with Assigned User Schema
class TaskResponseWithUser(BaseModel):
    task: TaskResponse
    assigned_user: Optional[UserResponse] = None  # Show user details if assigned

    class Config:
        from_attributes = True

# Rebuild models if necessary
# TaskResponseWithUser.model_rebuild()
