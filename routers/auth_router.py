from fastapi import APIRouter, Depends, HTTPException, Request,Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Form, HTTPException
from auth import verify_password
from database import get_db
from models import Admin
from schemas import LoginSchema
from auth import create_access_token
from fastapi import Request
from fastapi import APIRouter, Request, Form, Depends
from auth import hash_password





templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
# -----------------------------------------------------------------------------------------------------------------------------------------------
#
# -------------------------------------------------------------------------------------------------------------------------------

# get login page
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )
# ---------------------------------------------------------------------------------------------------------------------------------

@router.post("/login-page")
def login_form(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if not verify_password(password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid Password")

    token = create_access_token({
        "admin_id": admin.id,
        "email": admin.email
    })

    response = RedirectResponse(
        url="/auth/dashboard",
        status_code=302
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax"
    )

    return response

# ------------------------------------------------------------------------------------------------------------------------------------------------

# get dashboard
@router.get("/dashboard")
def dashboard(
    request: Request
):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    
    return templates.TemplateResponse(
        request=request,
        name= "dashboard.html"

        )

# -------------------------------------------------------------------------------------------------------------------------------------------

# get Logout
@router.get("/logout")
def logout():
    response = RedirectResponse(
        url="/auth/login",
        status_code=302,
        
        
        
    )

    response.delete_cookie("access_token")

    return response
# ----------------------------------------------------------------------------------------------------------------------------------------

# Forgot Password Page
@router.get("/forgot-password")
def forgot_password(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name= "forgot_password.html"

       
       
    )

# ----------------------------------------------------------------------------------------------------------------------------------

# post reset-password
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




templates = Jinja2Templates(directory="templates")


# -----------------------------------------------------------------------------------------------------------------------------------------------



# get register
@router.get("/register")
def worker_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="worker_registration.html",
    )

# ----------------------------------------------------------------------------------------------------------------------------------------------

# post register
@router.post("/register")
def worker_register(
    name: str = Form(...),
    email: str = Form(...),
    category_id: int = Form(...),
    mobile: str = Form(...),
    gender: str = Form(...),
    date_of_birth: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    pincode: str = Form(...),
    experience_years: int = Form(...),
    skills: str = Form(...),
    about: str = Form(...),
    aadhaar_number: str = Form(...),
    db: Session = Depends(get_db)
):

    worker = worker(
        name=name,
        email=email,
        mobile=mobile,
        gender=gender,
        date_of_birth=date_of_birth,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        category_id=category_id,
        experience_years=experience_years,
        skills=skills,
        about=about,
        aadhaar_number=aadhaar_number
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    return RedirectResponse(
        url="/auth/register",
        status_code=303
    )
# ------------------------------------------------------------------------------------------------------------------

# get worker-admin
@router.get("/worker-admin")
def worker_admin_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="worker_admin.html",
    )