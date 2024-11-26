from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import User, Task, UserTask,Token
from app.services.token_service import issue_tokens_to_user
from typing import List
from app.models import Task, UserTask, User
from app.schemas import TaskResponseWithUser,AdminReviewAction,TaskSubmissionResponse, TaskInfo, UserInfo



def get_all_users(db: Session):
    users = db.query(User).all()
    return users

def create_task(db: Session, task_data):
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
    return new_task

def edit_task(db: Session, task_id: int, task_data):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    existing_assignment = db.query(UserTask).filter(UserTask.task_id == task_id).first()
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Cannot edit a task that has already been assigned")

    task.title = task_data.title
    task.description = task_data.description
    task.image_url = task_data.image_url
    task.type = task_data.type
    
    db.commit()
    db.refresh(task)
    return task

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
    return [
        {
            "task": task,
            "assigned_user": db.query(User).filter(User.id == user_task.user_id).first() if (user_task := db.query(UserTask).filter(UserTask.task_id == task.id).first()) else None
        }
        for task in tasks
    ]



def view_all_completed_submissions(db: Session):
    submissions = db.query(UserTask).filter(
        UserTask.review_status.in_(["sys-passed", "admin-rejected"])
    ).all()

    return [
        TaskSubmissionResponse(
            task=TaskInfo(id=submission.task.id, title=submission.task.title, type=submission.task.type),
            user=UserInfo(id=submission.user.id, username=submission.user.username, email=submission.user.email),
            status=submission.status,
            labeled_data=submission.labeled_data,
            submitted_at=submission.submitted_at,
            review_status=submission.review_status,
            feedback=submission.feedback
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