from fastapi import APIRouter, Depends, HTTPException, Request,Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Form, HTTPException

from database import get_db
from models import Admin
from schemas import LoginSchema
from auth import create_access_token

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# API Login
@router.post("/login_page")
def login(
    request: LoginSchema,
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(
        Admin.email == request.email
    ).first()

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Admin not found"
        )

    if request.password != admin.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    token = create_access_token(
        {
            "admin_id": admin.id,
            "email": admin.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

# Login Form Submit
@router.post("/login-page")
def login_page_submit(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(
        Admin.email == email
    ).first()

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Admin not found"
        )

    if password != admin.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    token = create_access_token(
        {
            "admin_id": admin.id,
            "email": admin.email
        }
    )

    response = RedirectResponse(
        url="/auth/dashboard",
        status_code=302
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True
    )

    return response

@router.get("/dashboard")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={}
    )

# Logout
@router.get("/logout")
def logout():
    response = RedirectResponse(
        url="/auth/login",
        status_code=302
    )

    response.delete_cookie("access_token")

    return response


# Forgot Password Page
@router.get("/forgot-password")
def forgot_password(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name= "forgot_password.html"

       
       
    )
from fastapi import Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Admin
from auth import hash_password

@router.post("/reset-password")
def reset_password(
    email: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):

    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin.password = hash_password(new_password)

    db.commit()

    return RedirectResponse(url="/auth/login", status_code=303)