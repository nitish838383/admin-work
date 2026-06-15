from fastapi import FastAPI

from database import engine
from models import Base

from routers.auth_router import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Admin Panel API"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Admin Panel Running"
    }