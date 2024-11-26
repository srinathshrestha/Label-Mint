from fastapi import FastAPI
from app.api.v2.router import api_router
from app.db.session import init_db

app = FastAPI()

# Initialize the database tables
init_db()

# Include routers
app.include_router(api_router, prefix="/api/v2")
