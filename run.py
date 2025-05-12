import uvicorn
import os
from app.utils.db_utils import init_db

if __name__ == "__main__":
    # Create required directories if they don't exist
    os.makedirs("app/static/uploads", exist_ok=True)
    os.makedirs("app/static/audio", exist_ok=True)
    os.makedirs("app/templates", exist_ok=True)
    os.makedirs("app/data", exist_ok=True)
    
    # Initialize the database
    if init_db():
        print("Database initialized successfully")
    else:
        print("Failed to initialize database")
    
    # Run the FastAPI application
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)