from fastapi import APIRouter, Depends, HTTPException, Request,Form,UploadFile, File, HTTPException
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
from fastapi.responses import RedirectResponse
from datetime import datetime
import os
from uuid import uuid4







templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
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
from models import User, Worker, Booking
import requests

@router.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(
            url="/auth/login",
            status_code=302
        )

    # External API se customers data
    response = requests.get(
        "https://mistripoint-backend-1.onrender.com/auth/all-customers"
    )

    data = response.json()

    total_customers = data["total_customers"]

    # Apni DB ka data
    total_users = db.query(User).count()
    total_workers = db.query(Worker).count()
    total_bookings = db.query(Booking).count()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_users": total_users,
            "total_workers": total_workers,
            "total_bookings": total_bookings,
            "total_customers": total_customers
        }
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





# ---------------- FILE SAVE FUNCTION ----------------
def save_file(file: UploadFile, folder="uploads"):
    if not file:
        return None

    os.makedirs(folder, exist_ok=True)

    ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    path = os.path.join(folder, filename)

    with open(path, "wb") as buffer:
        buffer.write(file.file.read())

    return filename


# ---------------- REGISTER ROUTE ----------------
@router.post("/register")
def worker_register(
    name: str = Form(...),
    email: str = Form(None),
    mobile: str = Form(...),
    gender: str = Form(None),
    date_of_birth: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    pincode: str = Form(None),
    category_id: int = Form(None),
    experience_years: int = Form(0),
    skills: str = Form(None),
    about: str = Form(None),
    aadhaar_number: str = Form(None),

    profile_image: UploadFile = File(None),
    aadhaar_front: UploadFile = File(None),
    aadhaar_back: UploadFile = File(None),

    db: Session = Depends(get_db)
):

    # ---------------- DOB FIX ----------------
    dob = None
    if date_of_birth:
        try:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            dob = datetime.strptime(date_of_birth, "%d-%m-%Y").date()

    # ---------------- CREATE WORKER ----------------
    worker = Worker(
        name=name,
        email=email,
        mobile=mobile,
        gender=gender,
        date_of_birth=dob,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        category_id=category_id,
        experience_years=experience_years,
        skills=skills,
        about=about,
        aadhaar_number=aadhaar_number,
        status="Pending",
        profile_image=save_file(profile_image),
        aadhaar_front=save_file(aadhaar_front),
        aadhaar_back=save_file(aadhaar_back)
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    return RedirectResponse(
        url="/auth/worker-admin",
        status_code=303
    )

    # ------------------------------------------------------------------------------------------------------------

# get worker-admin
from models import Worker

@router.get("/worker-admin")
def worker_admin_page(
    request: Request,
    db: Session = Depends(get_db)
):
    workers = db.query(Worker).order_by(Worker.id.asc()).all()
    return templates.TemplateResponse(
        request=request,
        name="worker_admin.html",
        context={
            "workers": workers
        }
    )


@router.get("/worker/{worker_id}/approve")
def approve_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if worker:
        worker.status = "Approved"
        db.commit()

    return RedirectResponse(
        url="/auth/worker-admin",
        status_code=303
    )


@router.get("/worker/{worker_id}/reject")
def reject_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if worker:
        worker.status = "Rejected"
        db.commit()

    return RedirectResponse(
        url="/auth/worker-admin",
        status_code=303
    )

@router.get("/worker/{worker_id}/delete")
def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if worker:
        db.delete(worker)
        db.commit()

    return RedirectResponse(
        url="/auth/worker-admin",
        status_code=303
    )

@router.post("/worker/{worker_id}/edit")
def edit_worker(
    worker_id: int,
    name: str = Form(...),
    mobile: str = Form(...),
    email: str = Form(...),
    skills: str = Form(...),
    experience_years: int = Form(...),
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    worker.name = name
    worker.mobile = mobile
    worker.email = email
    worker.skills = skills
    worker.experience_years = experience_years

    db.commit()

    return RedirectResponse(
        url="/auth/worker-admin",
        status_code=303
    )

@router.get("/users")
def users_page(
    request: Request,
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={
            "users": users
        }
    )


from models import AllCustomer
import requests

@router.get("/all-customers")
def all_customers(
    request: Request,
    db: Session = Depends(get_db)
):
    response = requests.get(
        "https://mistripoint-backend-1.onrender.com/auth/all-customers"
    )

    data = response.json()

    total_customers = data["total_customers"]
    customers = data["customers"]

    return templates.TemplateResponse(
        request=request,
        name="All_customers.html",
        context={
            "customers": customers,
            "total_customers": total_customers
        }
    )


@router.get("/customer_approved/{customer_id}/approve")
def approve_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(AllCustomer).filter(
        AllCustomer.id == customer_id
    ).first()

    if customer:
        customer.status = "Approved"
        db.commit()

    return RedirectResponse(
        url="/auth/all-customers",
        status_code=303
    )


from models import AllCustomer

@router.get("/customer_rejected/{customer_id}/reject")
def reject_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(AllCustomer).filter(
        AllCustomer.id == customer_id
    ).first()

    if customer:
        customer.status = "Rejected"
        db.commit()

    return RedirectResponse(
        url="/auth/all-customers",
        status_code=303
    )