from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import (
    TaskCreate,
    TaskResponse,
    TaskResponseWithUser,
    UserResponse,
    TaskSubmissionResponse,
    AdminReviewAction
)

from app.db.session import get_db
from app.services.admin_service import (
    get_all_users,
    create_task,
    edit_task,
    delete_task,
    view_all_tasks,
    view_all_completed_submissions,
    review_submission_action
)
from app.auth.dependencies import get_current_admin_user
from app.models.user import User


router = APIRouter()

@router.get("/users/", response_model=List[UserResponse])
def admin_get_all_users(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    return get_all_users(db)

@router.post("/tasks/create", response_model=TaskResponse)
def admin_create_task(task_data: TaskCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    return create_task(db, task_data)

@router.put("/tasks/{task_id}/edit", response_model=TaskResponse)
def admin_edit_task(task_id: int, task_data: TaskCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    return edit_task(db, task_id, task_data)


@router.delete("/tasks/{task_id}/delete", response_model=dict)
def admin_delete_task(task_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    return delete_task(db, task_id)

@router.get("/tasks/", response_model=List[TaskResponseWithUser])
def admin_view_all_tasks(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    return view_all_tasks(db)

@router.get("/submissions/", response_model=List[TaskSubmissionResponse])
def admin_view_all_completed_submissions(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    return view_all_completed_submissions(db)

@router.post("/submissions/{submission_id}/review", response_model=TaskSubmissionResponse)
def admin_review_submission(submission_id: int, review_action: AdminReviewAction, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    return review_submission_action(db, submission_id, review_action)
