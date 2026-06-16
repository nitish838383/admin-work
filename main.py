from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from database import engine
from models import Base

from routers.auth_router import router as auth_router

# Create Tables
Base.metadata.create_all(bind=engine)

# Create App
app = FastAPI(
    title="Admin Panel API"
)

# Templates
templates = Jinja2Templates(
    directory="templates"
)

# Include Router
app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "message": "Admin Panel Running"
    }