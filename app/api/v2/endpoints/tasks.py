from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import MinimalTaskResponse, TaskDetailResponse, UserTaskResponse, TaskSubmissionSchema, TaskSubmissionResponse
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.services.task_service import (
    view_unassigned_tasks,
    view_task_detail,
    confirm_task,
    submit_task,
    get_rejected_submissions,
    get_token_balance
)

router = APIRouter()

@router.get("/", response_model=List[MinimalTaskResponse])
def view_tasks(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return view_unassigned_tasks(db)

@router.get("/{task_id}/", response_model=TaskDetailResponse)
def view_task(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return view_task_detail(db, task_id)

@router.post("/{task_id}/confirm", response_model=UserTaskResponse)
def confirm_user_task(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return confirm_task(db, task_id, current_user.id)

@router.post("/{task_id}/submit", response_model=UserTaskResponse)
def submit_user_task(task_id: int, submission: TaskSubmissionSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return submit_task(db, task_id, submission, current_user)

@router.get("/user/rejected-submissions", response_model=List[TaskSubmissionResponse])
def get_user_rejected_submissions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_rejected_submissions(db, current_user)

@router.get("/user/tokens", response_model=dict)
def get_user_token_balance(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_token_balance(db, current_user)

@router.get("/tasks/unassigned/")
def get_unassigned_tasks(db: Session = Depends(get_db)):
    from app.services.task_service import view_unassigned_tasks  # Import here to avoid circular issues
    unassigned_tasks = view_unassigned_tasks(db)
    if not unassigned_tasks:
        raise HTTPException(status_code=404, detail="No unassigned tasks found")
    return unassigned_tasks