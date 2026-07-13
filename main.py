from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from database import engine
from fastapi import Request
from models import Base
from fastapi.staticfiles import StaticFiles

from routers.auth_router import router as auth_router
from routers.auth_router import router as worker_router


# Create Tables
Base.metadata.create_all(bind=engine)

# Create App
app = FastAPI(
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(
    directory="templates"
)

# Include Router
app.include_router(auth_router)
app.include_router(worker_router)

@app.get("/")
def home(request: Request):
    return  templates.TemplateResponse(
        request = request,
        name="index.html"



    )

from starlette.middleware.sessions import SessionMiddleware



app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-this"
)


        
    

