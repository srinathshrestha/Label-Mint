from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserResponse
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.services.user_service import upload_profile_picture, update_username

router = APIRouter()

@router.get("/user/profile/", response_model=UserResponse)
def get_user_profile(current_user=Depends(get_current_user)):
    return current_user

@router.post("/user/upload-profile-picture", response_model=dict)
async def user_upload_profile_picture(file: UploadFile = File(...), current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return upload_profile_picture(db, file, current_user)

@router.post("/user/update-username", response_model=UserResponse)
async def user_update_username(new_username: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return update_username(db, new_username, current_user)
