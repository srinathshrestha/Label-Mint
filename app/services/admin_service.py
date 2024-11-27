from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import User, Task, UserTask,Token
from app.services.token_service import issue_tokens_to_user
from typing import List
from app.models import Task, UserTask, User
from app.schemas import (
    TaskCreate,
    TaskResponse,
    TaskResponseWithUser,
    AdminReviewAction,
    TaskSubmissionResponse,
    TaskInfo,
    UserInfo,
    UserResponse
)



def get_all_users(db: Session):
    users = db.query(User).all()
    return users

def create_task(db: Session, task_data: TaskCreate) -> TaskResponse:
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        image_url=task_data.image_url,
        type=task_data.type,
        token_reward=task_data.token_reward,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Convert to TaskResponse schema
    return TaskResponse(
        id=new_task.id,
        task_id=new_task.id,  # Assuming task_id is the same as the task's primary key
        user_id=None,         # No user assigned yet
        status="unassigned",  # Default status for a new task
        title=new_task.title,
        description=new_task.description,
        image_url=new_task.image_url,
        type=new_task.type,
        created_at=new_task.created_at
    )

def edit_task(db: Session, task_id: int, task_data: TaskCreate) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    existing_assignment = db.query(UserTask).filter(UserTask.task_id == task_id).first()
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Cannot edit a task that has already been assigned")

    # Update the task fields
    task.title = task_data.title
    task.description = task_data.description
    task.image_url = task_data.image_url
    task.type = task_data.type
    
    db.commit()
    db.refresh(task)

    # Convert to TaskResponse schema
    return TaskResponse(
        id=task.id,
        task_id=task.id,
        user_id=None,  # Assuming the task is unassigned after editing
        status="unassigned",  # Default status for edited tasks
        title=task.title,
        description=task.description,
        image_url=task.image_url,
        type=task.type,
        created_at=task.created_at
    )


# Continue similarly for other functions, importing schemas only inside the function as needed


def delete_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete related assignments
    db.query(UserTask).filter(UserTask.task_id == task_id).delete()

    # Delete the task
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}





def view_all_tasks(db: Session) -> List[TaskResponseWithUser]:
    tasks = db.query(Task).all()
    response_list = []

    for task in tasks:
        # Fetch the UserTask entry if it exists
        user_task = db.query(UserTask).filter(UserTask.task_id == task.id).first()

        if user_task:
            status = user_task.status
            user_id = user_task.user_id
            # Fetch the assigned user
            assigned_user = db.query(User).filter(User.id == user_task.user_id).first()
            assigned_user_response = UserResponse(
                id=assigned_user.id,
                username=assigned_user.username,
                email=assigned_user.email,
                profile_picture=assigned_user.profile_picture,
                role=assigned_user.role,
                created_at=assigned_user.created_at
            )
        else:
            status = "unassigned"
            user_id = None
            assigned_user_response = None

        # Create TaskResponse object with all required fields
        task_response = TaskResponse(
            id=task.id,
            user_id=user_id,
            status=status,
            title=task.title,
            description=task.description,
            image_url=task.image_url,
            type=task.type,
            created_at=task.created_at
        )

        # Append to the response list
        response_list.append(TaskResponseWithUser(
            task=task_response,
            assigned_user=assigned_user_response
        ))

    return response_list




def view_all_completed_submissions(db: Session):
    submissions = db.query(UserTask).filter(
        UserTask.review_status.in_(["sys-passed", "admin-rejected"])
    ).all()

    return [
        TaskSubmissionResponse(
            id=submission.id,
            task_id=submission.task_id,
            user_id=submission.user_id,
            status=submission.status,
            labeled_data=submission.labeled_data,
            submitted_at=submission.submitted_at,
            review_status=submission.review_status,
            feedback=submission.feedback,
            task=TaskInfo(
                id=submission.task.id,
                title=submission.task.title,
                type=submission.task.type
            ),
            user=UserInfo(
                id=submission.user.id,
                username=submission.user.username,
                email=submission.user.email
            )
        )
        for submission in submissions
    ]


def review_submission_action(db: Session, submission_id: int, review_action: AdminReviewAction):
    submission = db.query(UserTask).filter(
        UserTask.id == submission_id,
        UserTask.review_status.in_(["sys-passed", "admin-rejected"])
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found or not eligible for review")
    
    if review_action.action == "approve":
        submission.review_status = "admin-passed"
        submission.status = "reviewed"
        submission.feedback = review_action.feedback or "Submission approved"
        
        # Issue tokens based on the task's reward amount
        task_reward = submission.task.token_reward
        issue_tokens_to_user(db, submission.user_id, token_amount=task_reward)
        
    elif review_action.action == "reject":
        submission.review_status = "admin-rejected"
        submission.feedback = review_action.feedback or "Submission rejected due to quality issues"
        submission.status = "reviewed"
    
    db.commit()
    db.refresh(submission)
    return submission


def view_unassigned_tasks(db: Session):
    """Fetch all tasks that have not been assigned to any user."""
    unassigned_tasks = db.query(Task).filter(
        ~db.query(UserTask.task_id).filter(UserTask.task_id == Task.id).exists()
    ).all()
    return unassigned_tasks