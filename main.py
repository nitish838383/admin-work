from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from database import engine
from fastapi import Request
from models import Base

from routers.auth_router import router as auth_router
from routers.auth_router import router as worker_router


# Create Tables
Base.metadata.create_all(bind=engine)

# Create App
app = FastAPI(docs_url=None
)

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


        
    

