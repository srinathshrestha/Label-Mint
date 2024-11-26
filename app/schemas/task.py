from pydantic import BaseModel, ConfigDict
from typing import Any, Optional, Dict, Union
from datetime import datetime
from .user import UserResponse  # Import the UserResponse schema from the same package


class UserTaskResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    status: str
    labeled_data: Optional[Union[str, Dict[str, Dict[str, str]]]] = None  # Allow None
    submitted_at: Optional[datetime] = None
    review_status: Optional[str] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,  # Serialize datetime to ISO 8601 string
        }

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    type: str  # "classification" or "object_detection"
    token_reward: int

    
class TaskResponse(BaseModel):
    id: int
    task_id: int
    user_id: Optional [int] = None
    status: str
    title: str
    description: str
    image_url: str
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

class TaskResponseWithUser(BaseModel):
    task: TaskResponse
    assigned_user: Optional[UserResponse] = None  # Show user details if assigned

    model_config = ConfigDict(from_attributes=True)

TaskResponseWithUser.model_rebuild()

class TaskInfo(BaseModel):
    id: int
    title: str
    type: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: str

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