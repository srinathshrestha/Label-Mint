from fastapi import APIRouter
from app.api.v2.endpoints import auth,admin,tasks

api_router = APIRouter()

# Include each router with its prefix
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])      # Routes like /auth/register, /auth/login
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])   # Routes like /admin/users, /admin/tasks
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"]) # Uncomment when needed, like /tasks/unassigned
# api_router.include_router(users.router, prefix="/users", tags=["users"]) # Uncomment when needed, like /users/profile

# Now each router has a distinct prefix and tag