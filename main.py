import os
import uvicorn
from fastapi import FastAPI
from app.api.v2.router import api_router
from app.db.session import init_db

app = FastAPI()

# Initialize the database tables
init_db()

# Include routers
app.include_router(api_router, prefix="/api/v2")


# Run the application
if __name__ == "__main__":
    
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)