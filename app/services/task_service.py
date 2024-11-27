from sqlalchemy.orm import Session
from app.models import Task, UserTask
from fastapi import HTTPException, status
from app.models.user import User
from datetime import datetime
from app.models import Task, UserTask,Token
from app.schemas import (
    TaskDetailResponse,
    TaskResponse,
    MinimalTaskResponse,
    TaskSubmissionSchema,
    TaskSubmissionResponse,
    UserTaskResponse,
    TaskInfo,
    UserInfo
)



# Add any additional task-related functions here, with local imports as needed
TASK_TIMEOUT_MINUTES = 30
MAX_RETRIES = 10




def fetch_user_assigned_tasks(db: Session, user_id: int):
    user_tasks = db.query(UserTask).filter(UserTask.user_id == user_id).all()

    if not user_tasks:
        raise HTTPException(status_code=404, detail="No tasks assigned to the user")

    return [
        UserTaskResponse(
            id=user_task.id,
            task_id=user_task.task_id,
            user_id=user_task.user_id,
            status=user_task.status,
            labeled_data=user_task.labeled_data,  # Handles string or nested dict
            submitted_at=user_task.submitted_at,
            review_status=user_task.review_status,
            feedback=user_task.feedback
        )
        for user_task in user_tasks
    ]


def view_unassigned_tasks(db: Session):
    """Fetch all tasks that have not been assigned to any user."""
    unassigned_tasks = db.query(Task).filter(
        db.query(UserTask.task_id).filter(UserTask.task_id == Task.id).exists()
    ).all()
    return unassigned_tasks


def view_task_detail(db: Session, task_id: int) -> TaskDetailResponse:
    """
    Retrieve the details of a specific task by ID.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Convert to TaskDetailResponse schema
    return TaskDetailResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        image_url=task.image_url,
        type=task.type,
        created_at=task.created_at
    )


def drop_task(db: Session, task_id: int, user_id: int):
    user_task = db.query(UserTask).filter(UserTask.task_id == task_id, UserTask.user_id == user_id, UserTask.status == "pending").first()
    if not user_task:
        raise HTTPException(status_code=404, detail="No pending task found to drop")

    db.delete(user_task)
    db.commit()
    return {"message": "Task dropped"}
def confirm_task(db: Session, task_id: int, user_id: int) -> UserTaskResponse:
    """
    Mark a task as confirmed by a specific user.
    """
    # Check if the task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Check if this task is already confirmed or assigned to the user
    user_task = db.query(UserTask).filter(UserTask.task_id == task_id, UserTask.user_id == user_id).first()
    if user_task:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task already confirmed by the user")

    # Create a new UserTask association to mark it as confirmed by the user
    new_user_task = UserTask(
        task_id=task_id,
        user_id=user_id,
        status="pending",
        assigned_at=datetime.now()
    )
    db.add(new_user_task)
    db.commit()
    db.refresh(new_user_task)  # Refresh to ensure we have an ID for the new_user_task

    # Return TaskResponse with all required fields
    return UserTaskResponse(
        id=new_user_task.id,
        task_id=new_user_task.task_id,
        user_id=new_user_task.user_id,
        status=new_user_task.status,
        labeled_data=new_user_task.labeled_data,
        submitted_at=new_user_task.submitted_at,
        review_status=new_user_task.review_status,
        feedback=new_user_task.feedback
    )





def submit_task(db: Session, task_id: int, user_id: int, submission_data: TaskSubmissionSchema) -> UserTaskResponse:
    """
    Submit labeled data for a specific task by a user.
    """
    # Check if the task exists and assined to the user
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Check if the task is already submitted by the user
    user_task = db.query(UserTask).filter(UserTask.task_id == task_id, UserTask.user_id == user_id).first()
    if user_task and user_task.status == "submitted":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task already submitted by the user")

    # If the task hasn't been submitted yet, create or update the UserTask with submission details
    if not user_task:
        user_task = UserTask(
            task_id=task_id,
            user_id=user_id,
            status="submitted",
            labeled_data=submission_data.model_dump(),
            submitted_at=datetime.now(),
            review_status="pending"  # Assuming review is needed for the submission
        )
        db.add(user_task)
    else:
        # Update existing entry if it exists but wasn’t submitted yet
        user_task.status = "submitted"
        user_task.labeled_data = submission_data.model_dump()
        user_task.submitted_at = datetime.now()
        user_task.review_status = "pending"

    db.commit()
    db.refresh(user_task)
    # Construct the TaskInfo and UserInfo fields
    task_info = TaskInfo(id=task.id, title=task.title, type=task.type)
    user_info = UserInfo(
        id=user_task.user.id,
        username=user_task.user.username,
        email=user_task.user.email
    )

    return UserTaskResponse(
        id=user_task.id,
        task_id=user_task.task_id,
        user_id=user_task.user_id,
        status=user_task.status,
        labeled_data=user_task.labeled_data,
        submitted_at=user_task.submitted_at,
        review_status=user_task.review_status,
        feedback=user_task.feedback
    )


def view_unassigned_tasks(db: Session):
    """
    Retrieve all tasks that are unassigned.
    """
    # Get tasks that do not have any entries in UserTask (i.e., unassigned)
    unassigned_tasks = db.query(Task).filter(~Task.id.in_(
        db.query(UserTask.task_id).distinct()
    )).all()

    # Return minimal information about each unassigned task
    return [
        MinimalTaskResponse(
            id=task.id,
            title=task.title,
            type=task.type
        ) for task in unassigned_tasks
    ]


def get_token_balance(db: Session, user_id: int) -> dict:
    """
    Retrieve the token balance for the user.
    """
    token_entry = db.query(Token).filter(Token.user_id == user_id).first()
    if not token_entry:
        return {"token_balance": 0}  # Assuming new users start with 0 tokens

    return {"token_balance": token_entry.token_balance}



def get_rejected_submissions(db: Session, user_id: int):
    """
    Get all rejected submissions for the current user.
    """
    rejected_submissions = db.query(UserTask).filter(
    UserTask.user_id == user_id,
    UserTask.review_status.in_(["sys-rejected", "admin-rejected"])
    ).all()

    if not rejected_submissions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rejected submissions found for the user"
        )

    return [
        TaskSubmissionResponse(
            task={
                "id": task.task.id,
                "title": task.task.title,
                "type": task.task.type
            },
            user={
                "id": user_id,
                "username": task.user.username,
                "email": task.user.email
            },
            status=task.status,
            labeled_data=task.labeled_data,
            submitted_at=task.submitted_at,
            review_status=task.review_status,
            feedback=task.feedback
        ) for task in rejected_submissions
    ]