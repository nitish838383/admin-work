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
from config import SECRET_KEY, ALGORITHM
from schemas import BookingCreate
from fastapi.responses import JSONResponse
import random
from datetime import datetime, timedelta
from sqlalchemy import func









templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
#
# -------------------------------------------------------------------------------------------------------------------------------
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
import os

load_dotenv()

oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
)

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)
# get login page
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

@router.get("/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    token = await oauth.google.authorize_access_token(request)
    user = token["userinfo"]

    email = user["email"]

    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Email not found. Please contact administrator."
            },
            status_code=400
        )

    access_token = create_access_token({
        "admin_id": admin.id,
        "email": admin.email
    })

    response = RedirectResponse(
        url="/auth/loading",
        status_code=302
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return response
# ---------------------------------------------------------------------------------------------------------------------------------

@router.post("/login-view")
def login_view(
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
@router.post("/api/login")
def api_login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Email not found")

    print("Entered Password:", password)
    print("DB Password:", admin.password)

    print("Verify Result:", verify_password(password, admin.password))

    if not verify_password(password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid Password")

    token = create_access_token({
        "admin_id": admin.id,
        "email": admin.email
    })

    return {
        "success": True,
        "message": "Login Successful",
        "token": token,
        "admin_id": admin.id,
        "email": admin.email
    }

@router.post("/login")
def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        return templates.TemplateResponse(
    request=request,
    name="login.html",
    context={
        "error": "Email not found!"
    },
    status_code=400
)

    if not verify_password(password, admin.password):
        return templates.TemplateResponse(
    request=request,
    name="login.html",
    context={
        "error": "Invalid Password"
    },
    status_code=400
)

    token = create_access_token({
        "admin_id": admin.id,
        "email": admin.email
    })

    response = RedirectResponse(
        url="/auth/loading",
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


# dashboard hai app ka
from fastapi import Depends
from sqlalchemy.orm import Session
import requests

@router.get("/api/dashboard")
def dashboard_api(db: Session = Depends(get_db)):

    # ---------------- Customers ----------------
    try:
        response = requests.get(
            "https://mistripoint-backend-1.onrender.com/auth/all-customers",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        customers = data.get("customers", []) if isinstance(data, dict) else data
        total_customers = len(customers)

    except Exception:
        total_customers = 0

    # ---------------- Bookings ----------------
    try:
        response = requests.get(
            "https://mistripoint-backend-1.onrender.com/auth/admin/bookings",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        bookings = data.get("booking", []) if isinstance(data, dict) else data

        total_bookings = len(bookings)

        total_revenue = sum(
            float(item.get("amount", 0))
            for item in bookings
        )

    except Exception:
        total_bookings = 0
        total_revenue = 0

    # ---------------- Workers ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/worker-profiles",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        workers = data.get("data", []) if isinstance(data, dict) else data
        total_workers = len(workers)

    except Exception:
        total_workers = 0

    # ---------------- Skills ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/skills",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        skills = data.get("data", []) if isinstance(data, dict) else data
        total_skills = len(skills)

    except Exception:
        total_skills = 0

    # ---------------- KYC ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/worker-kyc",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        kycs = data.get("data", []) if isinstance(data, dict) else data
        total_kyc_workers = len(kycs)

    except Exception:
        total_kyc_workers = 0

    # ---------------- Notifications ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/notifications",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        notifications = data.get("data", []) if isinstance(data, dict) else data
        total_notifications = len(notifications)

    except Exception:
        total_notifications = 0

    # ---------------- Reviews ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/reviews",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        reviews = data.get("data", []) if isinstance(data, dict) else data
        total_reviews = len(reviews)

    except Exception:
        total_reviews = 0

    # ---------------- Local Users ----------------
    total_users = db.query(User).count()

    # ---------------- JSON Response ----------------
    return {
        "success": True,
        "dashboard": {
            "total_users": total_users,
            "total_customers": total_customers,
            "total_bookings": total_bookings,
            "total_workers": total_workers,
            "total_skills": total_skills,
            "total_kyc_workers": total_kyc_workers,
            "total_notifications": total_notifications,
            "total_reviews": total_reviews,
            "total_revenue": total_revenue,
            "bookings": bookings,
        }
    }

# ------------------------------------------------------------------------------------------------------------------------------------------------
# get dashboard
# --------------------------------------------------------------------------
# Dashboard website ka hai
# --------------------------------------------------------------------------
from sqlalchemy import func
from models import User
import requests

from jose import jwt, JWTError
@router.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    

    token = request.cookies.get("access_token")
    print("Token:", token)
    if not token:
        print("No token found")
        return RedirectResponse("/auth/login", status_code=302)

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        

    except JWTError as e:
        print("JWT Error:", e)

        response = RedirectResponse(
            url="/auth/login",
            status_code=302
        )
        response.delete_cookie("access_token")
        return response
    # ↓ Iske baad tumhara existing dashboard code rahega

    # ---------------- Customers ----------------
    try:
        response = requests.get(
            "https://mistripoint-backend-1.onrender.com/auth/all-customers",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            customers = data.get("customers", [])
        else:
            customers = data

        total_customers = len(customers)

    except Exception as e:
        print("Customers API Error:", e)
        customers = []
        total_customers = 0

    # ---------------- Bookings & Revenue ----------------
    try:
        response = requests.get(
            "https://mistripoint-backend-1.onrender.com/auth/admin/bookings",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            bookings = data.get("booking", [])
        else:
            bookings = data

        total_bookings = len(bookings)

        total_revenue = sum(
            float(b.get("amount", 0))
            for b in bookings
        )
       
        

    except Exception as e:
        print("Booking API Error:", e)
        bookings = []
        total_bookings = 0
        total_revenue = 0

    # ---------------- Workers ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/worker-profiles",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            workers = data.get("data", [])
        else:
            workers = data

        total_workers = len(workers)

    except Exception as e:
        print("Workers API Error:", e)
        workers = []
        total_workers = 0

    # ---------------- Skills ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/skills",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            skills = data.get("data", [])
        else:
            skills = data

        total_skills = len(skills)

    except Exception as e:
        print("Skills API Error:", e)
        skills = []
        total_skills = 0

    # ---------------- Worker KYC ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/worker-kyc",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            kycs = data.get("data", [])
        else:
            kycs = data

        total_kyc_workers = len(kycs)

    except Exception as e:
        print("KYC API Error:", e)
        kycs = []
        total_kyc_workers = 0

    # ---------------- Notifications ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/notifications",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            notifications = data.get("data", [])
        else:
            notifications = data

        total_notifications = len(notifications)

    except Exception as e:
        print("Notification API Error:", e)
        notifications = []
        total_notifications = 0

    # ---------------- Reviews ----------------
    try:
        response = requests.get(
            "https://mistripoint-1.onrender.com/reviews",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            reviews = data.get("data", [])
        else:
            reviews = data

        total_reviews = len(reviews)

    except Exception as e:
        print("Reviews API Error:", e)
        reviews = []
        total_reviews = 0

    # ---------------- Local Database ----------------
    total_users = db.query(User).count()

    # ---------------- Render ----------------
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "total_users": total_users,
            "total_bookings": total_bookings,
            "total_customers": total_customers,
            "total_workers": total_workers,
            "total_skills": total_skills,
            "total_kyc_workers": total_kyc_workers,
            "total_notifications": total_notifications,
            "total_reviews": total_reviews,
            "customers": customers,
            "reviews": reviews,
            "total_revenue": total_revenue,
            "bookings": bookings,
            "notifications": notifications,  
            "workers": workers,
            "reviews": reviews,
        }
    )
# ----------------------------------------------------------
# ------------------------------------------------------------

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
import os
import os
import requests

MCP_API_KEY = os.getenv("MCP_API_KEY")

async def send_otp_email(email: str, otp: str):
    headers = {
        "api-key": MCP_API_KEY,
        "content-type": "application/json"
    }

    # ...
import requests
import os


BREVO_API_KEY = os.getenv("BREVO_API_KEY")

async def send_otp_email(email: str, otp: str):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": "UstadJi",
            "email": "nitishkumar971727@gmail.com"
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": "OTP Verification",
        "htmlContent": f"""
        <h2>Password Reset OTP</h2>
        <p>Your OTP is:</p>
        <h1>{otp}</h1>
        <p>This OTP is valid for 10 minutes.</p>
        """
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("Status Code:", response.status_code)
        print("Response:", response.text)

        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        print("Brevo Error:", str(e))
        return False

   
# ----------------------------------------------------------------------------------------------------------------------------------
# opt send
@router.post("/send-otp")
async def send_otp(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    otp = str(random.randint(100000, 999999))
   
 

    # Save in database
    admin.otp = otp
    admin.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    db.refresh(admin)
   

    # Save in session
    request.session["reset_email"] = email
    
    await send_otp_email(email, otp)


    # TODO: Send OTP to email
   

    return JSONResponse({
        "success": True,
        "message": "OTP sent successfully"
    })

# ------------------------------------------------------------------------------------------------
# varify opt
from datetime import datetime

@router.post("/verify-otp")
def verify_otp(
    request: Request,
    otp: str = Form(...),
    db: Session = Depends(get_db)
):
    email = request.session.get("reset_email")
    

    if not email:
        raise HTTPException(status_code=400, detail="Session expired")

    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if admin.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if admin.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP Expired")

    request.session["otp_verified"] = True

    return JSONResponse({
        "success": True,
        "message": "OTP verified successfully"
    })

# post reset-password
@router.post("/reset-password")
def reset_password(
    email: str = Form(...),
    otp: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):

    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if admin.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if admin.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP Expired")

    admin.password = hash_password(new_password)
    admin.otp = None
    admin.otp_expiry = None

    db.commit()

    return RedirectResponse("/auth/login", status_code=303)


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

# ==========================================
# Worker Admin Page
# ==========================================
from models import Worker
@router.get("/worker-admin")
def worker_admin_page(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(
            url="/auth/login",
            status_code=302
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        admin_id = payload.get("admin_id")

        if admin_id is None:
            raise JWTError()

        admin = db.query(Admin).filter(Admin.id == admin_id).first()

        if not admin:
            raise JWTError()

    except JWTError:
        response = RedirectResponse(
            url="/auth/login",
            status_code=302
        )
        response.delete_cookie("access_token")
        return response
    response = requests.get(
        "https://mistripoint-1.onrender.com/worker-profiles"
    )

    workers = response.json()

    return templates.TemplateResponse(
        request=request,
        name="worker_admin.html",
        context={
        
            "request": request,
            "workers": workers,
            "total_workers": len(workers)
        }
    )


# ==========================================
# Approve Worker
# ==========================================

@router.get("/worker/{worker_id}/approve")
def approve_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):

    response = requests.put(
        f"https://mistripoint-1.onrender.com/admin/worker-profile/approve/{worker_id}",
        
    )
    print(response.status_code, response.text)


  

    

    return RedirectResponse(
        url="/auth/worker-admin",
        status_code=303
    )


# ==========================================
# Reject Worker
# ==========================================

@router.get("/worker/{worker_id}/reject")
def reject_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):

    response = requests.put(
        f"https://mistripoint-1.onrender.com/admin/worker-profile/reject/{worker_id}",
        
    )
    print(response.status_code, response.text)


    

    return RedirectResponse(
        url="/auth/worker-admin",
        status_code=303
    )


# __________________________________________________________________________________________________________________________________________

@router.get("/worker/{worker_id}/active")
def active_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if worker:
        worker.status = "Active"
        db.commit()

    return RedirectResponse(
        url="/auth/worker-admin",
        status_code=303
    )

# __________________________________________________________________________________________________________________________________

# worker edit

@router.get("/worker/{worker_id}/inactive")
def inactive_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if worker:
        worker.status = "Inactive"
        db.commit()

    return RedirectResponse(
        url="/auth/worker-admin",
        status_code=303
    )
# __________________________________________________________________________________________________________________________________________

@router.put("/api/worker/{worker_id}/approve")
def approve_worker_api(worker_id: int):

    response = requests.put(
        f"https://mistripoint-1.onrender.com/admin/worker-profile/approve/{worker_id}"
    )

    return response.json()
@router.put("/api/worker/{worker_id}/reject")
def reject_worker_api(worker_id: int):

    response = requests.put(
        f"https://mistripoint-1.onrender.com/admin/worker-profile/reject/{worker_id}"
    )

    return response.json()
@router.put("/api/worker/{worker_id}/active")
def active_worker_api(
    worker_id: int,
    db: Session = Depends(get_db)
):

    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if worker:
        worker.status = "Active"
        db.commit()

    return {
        "success": True,
        "message": "Worker Activated"
    }
@router.put("/api/worker/{worker_id}/inactive")
def inactive_worker_api(
    worker_id: int,
    db: Session = Depends(get_db)
):

    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if worker:
        worker.status = "Inactive"
        db.commit()

    return {
        "success": True,
        "message": "Worker Inactivated"
    }

# users detail


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

# _____________________________________________________________________________________________________________________________________
# all_customers detail
from models import AllCustomer
import requests

@router.get("/all-customers")
def all_customers(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(
            url="/auth/login",
            status_code=302
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        admin_id = payload.get("admin_id")

        if admin_id is None:
            raise JWTError()

        admin = db.query(Admin).filter(Admin.id == admin_id).first()

        if not admin:
            raise JWTError()

    except JWTError:
        response = RedirectResponse(
            url="/auth/login",
            status_code=302
        )
        response.delete_cookie("access_token")
        return response
    response = requests.get(
        "https://mistripoint-backend-1.onrender.com/auth/all-customers"
    )

    data = response.json()
    print(data)

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

# app customer api

@router.get("/api/all-customers")
def get_all_customers():

    response = requests.get(
        "https://mistripoint-backend-1.onrender.com/auth/all-customers"
    )

    return response.json()

@router.get("/customer_approved/{customer_id}/approve")
def approve_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    response = requests.put(
        f"https://mistripoint-backend-1.onrender.com/auth/admin/approve/{customer_id}"
    )

    if response.status_code == 200:
        return RedirectResponse(
            url="/auth/all-customers",
            status_code=303
        )

    return {
        "success": False,
        "status_code": response.status_code,
        "response": response.text
    }
# __________________________________________________________________________________________________________________________________________
# customer reject
from models import AllCustomer

@router.get("/customer_rejected/{customer_id}/reject")
def reject_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    response = requests.put(
        f"https://mistripoint-backend-1.onrender.com/auth/admin/reject/{customer_id}"
    )

    if response.status_code == 200:
        return RedirectResponse(
            url="/auth/all-customers",
            status_code=303
        )

    return {
        "success": False,
        "status_code": response.status_code,
        "response": response.text
    }

@router.get("/customer_delete/{customer_id}/delete")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    response = requests.delete(
        f"https://mistripoint-backend-1.onrender.com/auth/admin/delete-customer/{customer_id}"
    )

    if response.status_code == 200:
        return RedirectResponse(
            url="/auth/all-customers",
            status_code=303
        )

    return {
        "success": False,
        "status_code": response.status_code,
        "response": response.text
    }

    
    


# _________________________________________________________________________________________________________________________________________
# services
@router.get("/services")
def service(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="services.html"

    )

# _____________________________________________________________________________________________________________________________________________________
# contact
@router.get("/contact")
def Contact(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="contact.html"
    )








# ---------------------------------------------------------------------------------------------------------------------------------------------
from models import Booking


# ------------------------------------------------------------------------------------------------------------------------------------------

# booking items page
@router.get("/worker_list")
def worker_item_view(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="worker_list.html"
    )

# ====================================================================================================================================
# all booking 
@router.get("/all-bookings")
def all_bookings(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(
            url="/auth/login",
            status_code=302
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        admin_id = payload.get("admin_id")

        if admin_id is None:
            raise JWTError()

        admin = db.query(Admin).filter(Admin.id == admin_id).first()

        if not admin:
            raise JWTError()

    except JWTError:
        response = RedirectResponse(
            url="/auth/login",
            status_code=302
        )
        response.delete_cookie("access_token")
        return response

    response=requests.get(
        "https://mistripoint-backend-1.onrender.com/auth/admin/bookings"
    )

    bookings = response.json()
    
    total_bookings=len(bookings)

    return templates.TemplateResponse(
        request=request,
        name="booking_admin.html",
        context={
            "request": request,
            "bookings": bookings,
            "total_bookings":total_bookings,
        }
        
    )


@router.get("/api/all-bookings")
def get_all_bookings_api():

    response = requests.get(
        "https://mistripoint-backend-1.onrender.com/auth/admin/bookings"
    )

    return response.json()
# ______________________________________________________________________________________________________________________________________
# service-selections
@router.get("/service-selection")
def service_selection_name(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="service-selection.html"
    )

# -----------------------------------------------------------------------------------------------------------------------
# payment
@router.get("/payment")
def payment_view_page(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="payment.html"

    )

# # ===================================================================================================================================
# all-skills
from jose import jwt, JWTError

@router.get("/all-skills")
def all_skills(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(
            url="/auth/login",
            status_code=302
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        admin_id = payload.get("admin_id")

        if admin_id is None:
            raise JWTError()

        admin = db.query(Admin).filter(
            Admin.id == admin_id
        ).first()

        if not admin:
            raise JWTError()

    except JWTError:
        response = RedirectResponse(
            url="/auth/login",
            status_code=302
        )
        response.delete_cookie("access_token")
        return response

    # ---------------- Skills API ----------------
    response = requests.get(
        "https://mistripoint-1.onrender.com/skills"
    )

    data = response.json()

    total_skills = len(data)
    skills = data

    return templates.TemplateResponse(
        request=request,
        name="skills.html",
        context={
            "request": request,
            "skills": skills,
            "total_skills": total_skills,
        }
    )
# -----------------------------------------------------------------------------------------------------------------------------------
# kyc-admin

@router.get("/kyc-admin")
def kyc_admin(
    request: Request
):
    
    response = requests.get(
        "https://mistripoint-1.onrender.com/worker-kyc"

    )

    data = response.json()
    kycs=data["data"]

    total_kyc_workers = len(data)
   

    return templates.TemplateResponse(
        request=request,
        name="kyc_admin.html",
        context={
            "request": request,
            "kycs": kycs,
            "total_kyc_workers": total_kyc_workers,
        }
    )
# ---------------------------------------------------------------------------------------------------------------------------------------

# kyc/{worker_id}/approve

@router.get("/kyc/{worker_id}/approve")
def approve_kyc(worker_id: int):

    response = requests.put(
        f"https://mistripoint-1.onrender.com/admin/worker-kyc/approve/{worker_id}"
    )

    print(response.status_code, response.text)

    return RedirectResponse("/auth/kyc-admin", status_code=302)


@router.get("/kyc/{worker_id}/reject")
def reject_kyc(worker_id: int):

    response = requests.put(
        f"https://mistripoint-1.onrender.com/admin/worker-kyc/reject/{worker_id}"
    )

    print(response.status_code, response.text)

    return RedirectResponse("/auth/kyc-admin", status_code=302)


# -------------------------------------------------------------------------------------------------------------------------------------
from models import Notification
from schemas import NotificationCreate


# notification
@router.post("/notifications")
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    new_notification = Notification(
        worker_id=notification.worker_id,
        title=notification.title,
        message=notification.message
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return {
        "message": "Notification Created Successfully",
        "notification": new_notification
    }

# -----------------------------------------------------------------------------------------------------------------------------------------

# notification_admin
@router.get("/notification-admin")
def notification_admin(request: Request):

    response = requests.get(
        "https://mistripoint-1.onrender.com/notifications"
    )

    data = response.json()

    notifications = data["data"]      
    total_notifications = len(notifications)

    return templates.TemplateResponse(
        request=request,
        name="notification_admin.html",
        context={
            "request": request,
            "notifications": notifications,
            "total_notifications": total_notifications
        }
    )

# --------------------------------------------------------------------------------------------------------------------------------------------
@router.get("/admin-profile")
def show_admin_profile(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_profile.html"
    )

@router.get("/profile/{admin_id}")
def get_admin_profile(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.id == admin_id).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return {
        "message": "Admin Profile",
        "data": admin
    }


@router.get("/loading")
def loading(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="splash_screen.html",
        context={
            "request": request,
            
        }
    )



@router.get("/reviews")
def reviews(request: Request):

    response = requests.get(
        "https://mistripoint-1.onrender.com/reviews"
    )

    data = response.json()

    reviews = data["data"]

    return templates.TemplateResponse(
        "reviews.html",
        {
            "request": request,
            "review": reviews,
            "total_reviews": len(reviews),
            "average_rating": 4.8,
            "five_star_reviews": 24
        }
    )
# ------------------------------------------------------------------------------------------------------

@router.get("/report")
def report(
    request: Request,
    db: Session = Depends(get_db)
    ):
    
     # ---------------- Customers ----------------
        try:
            response = requests.get(
                "https://mistripoint-backend-1.onrender.com/auth/all-customers",
                timeout=10
            )
            response.raise_for_status()
    
            data = response.json()
    
            if isinstance(data, dict):
                customers = data.get("customers", [])
            else:
                customers = data
    
            total_customers = len(customers)
    
        except Exception as e:
            print("Customers API Error:", e)
            customers = []
            total_customers = 0
    
        # ---------------- Bookings & Revenue ----------------
        try:
            response = requests.get(
                "https://mistripoint-backend-1.onrender.com/auth/admin/bookings",
                timeout=10
            )
            response.raise_for_status()
    
            data = response.json()
    
            if isinstance(data, dict):
                bookings = data.get("booking", [])
            else:
                bookings = data
    
            total_bookings = len(bookings)
    
            total_revenue = sum(
                float(b.get("amount", 0))
                for b in bookings
            )
            print("Total Revenue:", total_revenue)
            
    
        except Exception as e:
            print("Booking API Error:", e)
            bookings = []
            total_bookings = 0
            total_revenue = 0
    
        # ---------------- Workers ----------------
        try:
            response = requests.get(
                "https://mistripoint-1.onrender.com/worker-profiles",
                timeout=10
            )
            response.raise_for_status()
    
            data = response.json()
    
            if isinstance(data, dict):
                workers = data.get("data", [])
            else:
                workers = data
    
            total_workers = len(workers)
    
        except Exception as e:
            print("Workers API Error:", e)
            workers = []
            total_workers = 0
    
        # ---------------- Skills ----------------
        try:
            response = requests.get(
                "https://mistripoint-1.onrender.com/skills",
                timeout=10
            )
            response.raise_for_status()
    
            data = response.json()
    
            if isinstance(data, dict):
                skills = data.get("data", [])
            else:
                skills = data
    
            total_skills = len(skills)
    
        except Exception as e:
            print("Skills API Error:", e)
            skills = []
            total_skills = 0
    
        # ---------------- Worker KYC ----------------
        try:
            response = requests.get(
                "https://mistripoint-1.onrender.com/worker-kyc",
                timeout=10
            )
            response.raise_for_status()
    
            data = response.json()
    
            if isinstance(data, dict):
                kycs = data.get("data", [])
            else:
                kycs = data
    
            total_kyc_workers = len(kycs)
    
        except Exception as e:
            print("KYC API Error:", e)
            kycs = []
            total_kyc_workers = 0
    
        # ---------------- Notifications ----------------
        try:
            response = requests.get(
                "https://mistripoint-1.onrender.com/notifications",
                timeout=10
            )
            response.raise_for_status()
    
            data = response.json()
    
            if isinstance(data, dict):
                notifications = data.get("data", [])
            else:
                notifications = data
    
            total_notifications = len(notifications)
    
        except Exception as e:
            print("Notification API Error:", e)
            notifications = []
            total_notifications = 0
    
        # ---------------- Reviews ----------------
        try:
            response = requests.get(
                "https://mistripoint-1.onrender.com/reviews",
                timeout=10
            )
            response.raise_for_status()
    
            data = response.json()
    
            if isinstance(data, dict):
                reviews = data.get("data", [])
            else:
                reviews = data
    
            total_reviews = len(reviews)
    
        except Exception as e:
            print("Reviews API Error:", e)
            reviews = []
            total_reviews = 0
    
        # ---------------- Local Database ----------------
        total_users = db.query(User).count()
    
        # ---------------- Render ----------------
        return templates.TemplateResponse(
            request=request,
            name="report.html",
            context={
                "request": request,
                "total_users": total_users,
                "total_bookings": total_bookings,
                "total_customers": total_customers,
                "total_workers": total_workers,
                "total_skills": total_skills,
                "total_kyc_workers": total_kyc_workers,
                "total_notifications": total_notifications,
                "total_reviews": total_reviews,
                "customers": customers,
                "reviews": reviews,
                "total_revenue": total_revenue,
            }
        )


# --------------------------------------------------------------------------------------------------------------------------------------------
@router.get("/setting")
def setting(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="setting.html",
        context={
            "request":request,

        }
    )


# ______________________________________________________________________________________________________________________________-
import requests

@router.get("/categories")
def category(
    request: Request,
    db: Session = Depends(get_db),
):
    response = requests.get(
        "https://mistripoint-backend-1.onrender.com/auth/categories"
    )

    data = response.json()
    print(data)
    categories=data
    total_categories=len(categories)

    return templates.TemplateResponse(
        request=request,
        name="category.html",
        context={
            "request": request,
            "categories": categories,
            "total_categories": total_categories,
            "total_active": len(
                [c for c in data if c.get("status", "").lower() == "active"]
            ),
        }
    )
@router.get("/download-pdf")
def download_pdf(
    request: Request,
    type: str,
    worker_id: int = None
):

    if type == "notifications":

        response = requests.get(
            "https://mistripoint-1.onrender.com/notifications",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        return templates.TemplateResponse(
            request=request,
            name="reports/notifications_report.html",
            context={
                "request": request,
                "data": data["data"],
                "total": data["total_notifications"],
                "total_notifications": data["total_notifications"],
            }
        )

    elif type == "kyc":

        response = requests.get(
            "https://mistripoint-1.onrender.com/worker-kyc"
        )

        data = response.json()

        kyc = None

        for item in data["data"]:
            if item["worker_id"] == worker_id:
                kyc = item
                break

        if not kyc:
            return {"message":"Worker Not Found"}

        return templates.TemplateResponse(
            request=request,
            name="reports/worker_kyc_report.html",
            context=
            {
                "request":request,
                "kyc":kyc
            }
        )
    elif type == "kyc":
    
            response = requests.get(
                "https://mistripoint-1.onrender.com/worker-kyc"
            )
    
            data = response.json()
    
            kyc = None
    
            for item in data["data"]:
                if item["worker_id"] == worker_id:
                    kyc = item
                    break
    
            if not kyc:
                return {"message":"Worker Not Found"}
    
            return templates.TemplateResponse(
                request=request,
                name="reports/worker_kyc_report.html",
                context=
                {
                    "request":request,
                    "kyc":kyc
                }
            )
    

 
    
@router.get("/worker-kyc-search")
def worker_kyc_search(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="worker_kyc_search.html",
        context=
        {
            "request": request
        }
    )




@router.get("/worker-kyc-search")
def worker_kyc_search(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="worker_kyc_search.html",
        context=
        {
            "request": request
        }
    )


# =====================================================================
# ENTERPRISE AI CHAT ASSISTANT  –  Drop-in replacement for /chat-ai
# Fully compatible with existing endpoint + response shape
# =====================================================================

import re
import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from functools import lru_cache

import requests
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from rapidfuzz import fuzz, process
from cachetools import TTLCache
from loguru import logger
from dateutil import parser as date_parser



# ------------------------------------------------------------------
# 1. CONFIG – Real endpoints (exactly as your dashboard)
# ------------------------------------------------------------------
API = {
    "workers":       "https://mistripoint-1.onrender.com/worker-profiles",
    "bookings":      "https://mistripoint-backend-1.onrender.com/auth/admin/bookings",
    "customers":     "https://mistripoint-backend-1.onrender.com/auth/all-customers",
    "kycs":          "https://mistripoint-1.onrender.com/worker-kyc",
    "categories":    "https://mistripoint-backend-1.onrender.com/auth/categories",
    "notifications": "https://mistripoint-1.onrender.com/notifications",
}

# ------------------------------------------------------------------
# 2. MODELS
# ------------------------------------------------------------------
class Intent(str, Enum):
    BOOKING = "booking"
    WORKER = "worker"
    CUSTOMER = "customer"
    REVENUE = "revenue"
    STATISTICS = "statistics"
    PAYMENT = "payment"
    CATEGORY = "category"
    NOTIFICATION = "notification"
    KYC = "kyc"
    SEARCH = "search"
    HELP = "help"
    UNKNOWN = "unknown"

class EntityType(str, Enum):
    BOOKING_ID = "booking_id"
    WORKER_ID = "worker_id"
    CUSTOMER_ID = "customer_id"
    NAME = "name"
    PHONE = "phone"
    EMAIL = "email"
    CITY = "city"
    SKILL = "skill"
    STATUS = "status"
    DATE = "date"
    DATE_RANGE = "date_range"
    SORT = "sort"

class ExtractedEntity(BaseModel):
    type: EntityType
    value: Any
    confidence: float = 1.0
    raw: Optional[str] = None

class IntentResult(BaseModel):
    intent: Intent
    confidence: float
    entities: List[ExtractedEntity] = Field(default_factory=list)
    raw_query: str
    normalized_query: str

class HandlerResult(BaseModel):
    success: bool
    title: str
    data: Any = None
    message: Optional[str] = None

# ------------------------------------------------------------------
# 3. CACHE (in-memory, 45 s TTL)
# ------------------------------------------------------------------
_query_cache = TTLCache(maxsize=256, ttl=45)
_data_cache  = TTLCache(maxsize=32,  ttl=30)   # raw API responses

def _cache_key(intent: str, entities: dict) -> str:
    payload = json.dumps({"i": intent, "e": entities}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()

# ------------------------------------------------------------------
# 4. LAZY DATA PROVIDER (loads ONLY what the intent needs)
# ------------------------------------------------------------------
def _safe_get(url: str, key: Optional[str] = None) -> List[Dict]:
    cache_k = f"{url}|{key}"
    if cache_k in _data_cache:
        return _data_cache[cache_k]
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        result = []
        if key and isinstance(data, dict):
            result = data.get(key, []) if isinstance(data.get(key), list) else []
        elif isinstance(data, list):
            result = data
        elif isinstance(data, dict):
            for k in ("data", "booking", "bookings", "customers", "workers"):
                if k in data and isinstance(data[k], list):
                    result = data[k]
                    break
        _data_cache[cache_k] = result
        return result
    except Exception as e:
        logger.error(f"API Error [{url}]: {e}")
        return []

class DataHub:
    """Lazy-load façade – never loads everything."""
    @staticmethod
    def workers() -> List[Dict]:
        return _safe_get(API["workers"], "data")

    @staticmethod
    def bookings() -> List[Dict]:
        return _safe_get(API["bookings"])

    @staticmethod
    def customers() -> List[Dict]:
        return _safe_get(API["customers"], "customers")

    @staticmethod
    def kycs() -> List[Dict]:
        return _safe_get(API["kycs"], "data")

    @staticmethod
    def categories() -> List[Dict]:
        return _safe_get(API["categories"])

    @staticmethod
    def notifications() -> List[Dict]:
        return _safe_get(API["notifications"], "data")

# ------------------------------------------------------------------
# 5. ENTITY EXTRACTOR (fuzzy + regex)
# ------------------------------------------------------------------
PHONE_RE   = re.compile(r"(?:\+91[-\s]?)?[6-9]\d{9}")
EMAIL_RE   = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
ID_RE      = re.compile(r"\b(?:id|booking|worker|customer)?\s*[#:]?\s*(\d+)\b", re.I)

STATUS_MAP = {
    "pending": "pending", "completed": "completed",
    "cancelled": "cancelled", "canceled": "cancelled",
    "approved": "approved", "rejected": "rejected",
    "paid": "paid", "unpaid": "unpaid",
}

SKILL_KW = [
    "electrician", "plumber", "carpenter", "painter", "cleaner",
    "ac technician", "mechanic", "mason", "welder", "gardener",
]
CITY_KW = [
    "delhi", "noida", "gurgaon", "gurugram", "mumbai", "bangalore",
    "bengaluru", "hyderabad", "pune", "chennai", "kolkata", "jaipur",
    "lucknow", "ahmedabad", "chandigarh", "faridabad", "ghaziabad",
]
SORT_KW = {
    "latest": "desc", "newest": "desc", "recent": "desc",
    "oldest": "asc", "highest": "desc", "lowest": "asc",
    "top": "desc", "maximum": "desc", "minimum": "asc",
}

class EntityExtractor:
    def extract(self, query: str, known_names: Optional[List[str]] = None) -> List[ExtractedEntity]:
        q = query.strip()
        ents: List[ExtractedEntity] = []
        ents += self._ids(q)
        ents += self._phone(q)
        ents += self._email(q)
        ents += self._status(q)
        ents += self._skill(q)
        ents += self._city(q)
        ents += self._dates(q)
        ents += self._sort(q)
        ents += self._name(q, known_names or [])
        return self._dedup(ents)

    def _ids(self, q: str) -> List[ExtractedEntity]:
        out = []
        for m in ID_RE.finditer(q):
            val = int(m.group(1))
            low = m.group(0).lower()
            if "worker" in low:
                et = EntityType.WORKER_ID
            elif "customer" in low:
                et = EntityType.CUSTOMER_ID
            else:
                et = EntityType.BOOKING_ID
            out.append(ExtractedEntity(type=et, value=val, raw=m.group(0)))
        return out

    def _phone(self, q: str) -> List[ExtractedEntity]:
        return [
            ExtractedEntity(type=EntityType.PHONE, value=re.sub(r"[^\d]", "", m.group(0))[-10:], raw=m.group(0))
            for m in PHONE_RE.finditer(q)
        ]

    def _email(self, q: str) -> List[ExtractedEntity]:
        return [
            ExtractedEntity(type=EntityType.EMAIL, value=m.group(0).lower(), raw=m.group(0))
            for m in EMAIL_RE.finditer(q)
        ]

    def _status(self, q: str) -> List[ExtractedEntity]:
        low = q.lower()
        return [
            ExtractedEntity(type=EntityType.STATUS, value=v, raw=k)
            for k, v in STATUS_MAP.items() if re.search(rf"\b{k}\b", low)
        ]

    def _skill(self, q: str) -> List[ExtractedEntity]:
        low = q.lower()
        return [
            ExtractedEntity(type=EntityType.SKILL, value=s, raw=s)
            for s in SKILL_KW if s in low
        ]

    def _city(self, q: str) -> List[ExtractedEntity]:
        low = q.lower()
        return [
            ExtractedEntity(type=EntityType.CITY, value=c.title(), raw=c)
            for c in CITY_KW if c in low
        ]

    def _dates(self, q: str) -> List[ExtractedEntity]:
        low = q.lower()
        today = date.today()
        out = []
        if "today" in low:
            out.append(ExtractedEntity(type=EntityType.DATE, value=today.isoformat(), raw="today"))
        if "yesterday" in low:
            out.append(ExtractedEntity(type=EntityType.DATE, value=(today - timedelta(days=1)).isoformat(), raw="yesterday"))
        if "this month" in low or "current month" in low:
            start = today.replace(day=1)
            out.append(ExtractedEntity(type=EntityType.DATE_RANGE, value=(start.isoformat(), today.isoformat()), raw="this month"))
        if "last month" in low:
            first = today.replace(day=1)
            end = first - timedelta(days=1)
            start = end.replace(day=1)
            out.append(ExtractedEntity(type=EntityType.DATE_RANGE, value=(start.isoformat(), end.isoformat()), raw="last month"))
        return out

    def _sort(self, q: str) -> List[ExtractedEntity]:
        low = q.lower()
        return [
            ExtractedEntity(type=EntityType.SORT, value=v, raw=k)
            for k, v in SORT_KW.items() if re.search(rf"\b{k}\b", low)
        ]

    def _name(self, q: str, known: List[str]) -> List[ExtractedEntity]:
        cleaned = PHONE_RE.sub(" ", q)
        cleaned = EMAIL_RE.sub(" ", cleaned)
        cleaned = ID_RE.sub(" ", cleaned)
        cleaned = re.sub(
            r"\b(?:show|open|get|find|search|worker|customer|booking|id|phone|email|address|city|of|the|a|an|details|profile|history|top|pending|approved|rejected)\b",
            " ", cleaned, flags=re.I
        )
        cleaned = re.sub(r"[^\w\s']", " ", cleaned)
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
        if not tokens:
            return []
        candidate = " ".join(tokens).strip()
        if not candidate or candidate.isdigit():
            return []

        if known:
            match = process.extractOne(candidate, known, scorer=fuzz.token_set_ratio)
            if match and match[1] >= 70:
                return [ExtractedEntity(type=EntityType.NAME, value=match[0], confidence=match[1]/100, raw=candidate)]

        if len(tokens) <= 3:
            return [ExtractedEntity(type=EntityType.NAME, value=candidate.title(), confidence=0.75, raw=candidate)]
        return []

    def _dedup(self, ents: List[ExtractedEntity]) -> List[ExtractedEntity]:
        seen, unique = set(), []
        for e in ents:
            key = (e.type, str(e.value))
            if key not in seen:
                seen.add(key)
                unique.append(e)
        return unique

# ------------------------------------------------------------------
# 6. INTENT DETECTOR (pattern registry – no long if-else)
# ------------------------------------------------------------------
INTENT_PATTERNS: List[Tuple[Intent, List[str], float]] = [
    (Intent.HELP,         [r"\bhelp\b", r"\bwhat can you do\b", r"\bcommands\b"], 0.95),
    (Intent.NOTIFICATION, [r"\bnotification", r"\bunread", r"\balert"], 0.9),
    (Intent.KYC,          [r"\bkyc\b"], 0.9),
    (Intent.REVENUE,      [r"\brevenue\b", r"\bearning", r"\bincome\b"], 0.9),
    (Intent.PAYMENT,      [r"\bpayment", r"\bpaid\b", r"\bunpaid\b", r"\bpending payment"], 0.85),
    (Intent.STATISTICS,   [r"\btotal\s+(workers?|customers?|bookings?|revenue|categories?)", r"\bstats?\b", r"\bstatistics\b"], 0.9),
    (Intent.CATEGORY,     [r"\bcategor", r"\bmost booked", r"\btop categor"], 0.85),
    (Intent.BOOKING,      [r"\bbooking", r"\border\b", r"\bjob\b"], 0.85),
    (Intent.WORKER,       [r"\bworker", r"\btechnician", r"\belectrician", r"\bplumber", r"\bcarpenter", r"\bmistri"], 0.85),
    (Intent.CUSTOMER,     [r"\bcustomer", r"\bclient\b"], 0.85),
    (Intent.SEARCH,       [r"\bsearch\b", r"\bfind\b", r"\blookup\b"], 0.7),
]

class IntentDetector:
    def __init__(self, extractor: EntityExtractor):
        self.extractor = extractor

    def detect(self, query: str) -> IntentResult:
        normalized = re.sub(r"\s+", " ", query.strip().lower())
        entities = self.extractor.extract(normalized)

        scores = {i: 0.0 for i in Intent}
        for intent, patterns, base in INTENT_PATTERNS:
            for p in patterns:
                if re.search(p, normalized, re.I):
                    scores[intent] = max(scores[intent], base)

        for e in entities:
            if e.type == EntityType.BOOKING_ID:
                scores[Intent.BOOKING] += 0.35
            elif e.type == EntityType.WORKER_ID or e.type == EntityType.SKILL:
                scores[Intent.WORKER] += 0.3
            elif e.type == EntityType.CUSTOMER_ID:
                scores[Intent.CUSTOMER] += 0.3
            elif e.type == EntityType.STATUS and e.value in ("pending", "approved", "rejected"):
                scores[Intent.WORKER] += 0.15
                scores[Intent.BOOKING] += 0.1

        # pure name → universal search
        name_only = (
            any(e.type == EntityType.NAME for e in entities)
            and not any(e.type in (EntityType.BOOKING_ID, EntityType.WORKER_ID, EntityType.CUSTOMER_ID) for e in entities)
            and scores[Intent.BOOKING] < 0.5
            and scores[Intent.WORKER] < 0.5
            and scores[Intent.CUSTOMER] < 0.5
        )
        if name_only:
            scores[Intent.SEARCH] = max(scores[Intent.SEARCH], 0.85)

        best = max(scores, key=scores.get)
        conf = scores[best]
        if conf < 0.4:
            best, conf = Intent.UNKNOWN, 0.0

        return IntentResult(
            intent=best,
            confidence=min(conf, 1.0),
            entities=entities,
            raw_query=query,
            normalized_query=normalized,
        )

# ------------------------------------------------------------------
# 7. FORMATTERS (beautiful replies – same style as your old code)
# ------------------------------------------------------------------
def fmt_booking(b: dict) -> str:
    return (
        f"📦 **Booking #{b.get('id')}**\n"
        f"• Customer : {b.get('customer_name') or b.get('customer') or 'N/A'}\n"
        f"• Worker   : {b.get('worker_name') or b.get('worker') or 'N/A'}\n"
        f"• Service  : {b.get('service') or b.get('service_name') or 'N/A'}\n"
        f"• Category : {b.get('category') or 'N/A'}\n"
        f"• Date     : {b.get('booking_date') or b.get('date') or 'N/A'}\n"
        f"• Time     : {b.get('booking_time') or b.get('time') or 'N/A'}\n"
        f"• Address  : {b.get('address') or 'N/A'}\n"
        f"• Amount   : ₹{float(b.get('amount', 0)):,.2f}\n"
        f"• Payment  : {b.get('payment_status') or 'N/A'}\n"
        f"• Status   : {b.get('status') or 'N/A'}"
    )

def fmt_worker(w: dict) -> str:
    return (
        f"👷 **Worker #{w.get('id')} – {w.get('name')}**\n"
        f"• Mobile     : {w.get('mobile') or 'N/A'}\n"
        f"• Email      : {w.get('email') or 'N/A'}\n"
        f"• Skills     : {w.get('skills') or 'N/A'}\n"
        f"• Experience : {w.get('experience_years') or w.get('experience') or 'N/A'} yrs\n"
        f"• Category   : {w.get('category') or 'N/A'}\n"
        f"• City       : {w.get('city') or 'N/A'}\n"
        f"• Status     : {w.get('profile_status') or w.get('status') or 'N/A'}\n"
        f"• KYC Status : {w.get('kyc_status') or 'N/A'}"
    )

def fmt_customer(c: dict) -> str:
    name = f"{c.get('first_name', '')} {c.get('last_name', '')}".strip() or c.get('name') or 'N/A'
    return (
        f"👤 **Customer #{c.get('id')} – {name}**\n"
        f"• Mobile  : {c.get('phone') or c.get('mobile') or 'N/A'}\n"
        f"• Email   : {c.get('email') or 'N/A'}\n"
        f"• City    : {c.get('city') or 'N/A'}\n"
        f"• Address : {c.get('address') or 'N/A'}\n"
        f"• Total Bookings : {c.get('total_bookings') or 'N/A'}"
    )

def _list_reply(title: str, items: List[str], total: int) -> str:
    if not items:
        return f"No records found for {title}."
    body = "\n\n────────────────\n\n".join(items)
    return f"{title} ({total})\n\n{body}"

# ------------------------------------------------------------------
# 8. HANDLERS (one class per intent – SOLID)
# ------------------------------------------------------------------
class BaseHandler(ABC):
    def __init__(self, hub: DataHub):
        self.hub = hub

    @abstractmethod
    def handle(self, result: IntentResult) -> str:
        ...

    def _ent(self, entities: List[ExtractedEntity], et: EntityType):
        for e in entities:
            if e.type == et:
                return e.value
        return None

class BookingHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        ents = result.entities
        bid = self._ent(ents, EntityType.BOOKING_ID)
        status = self._ent(ents, EntityType.STATUS)
        date_val = self._ent(ents, EntityType.DATE)
        date_range = self._ent(ents, EntityType.DATE_RANGE)
        sort = self._ent(ents, EntityType.SORT) or "desc"
        q = result.normalized_query

        bookings = self.hub.bookings()

        # single ID
        if bid is not None:
            b = next((x for x in bookings if x.get("id") == bid), None)
            return fmt_booking(b) if b else f"❌ Booking #{bid} not found."

        # highest / lowest amount
        if "highest" in q or "maximum" in q:
            sorted_b = sorted(bookings, key=lambda x: float(x.get("amount", 0)), reverse=True)
            return fmt_booking(sorted_b[0]) if sorted_b else "No bookings."
        if "lowest" in q or "minimum" in q:
            sorted_b = sorted(bookings, key=lambda x: float(x.get("amount", 0)))
            return fmt_booking(sorted_b[0]) if sorted_b else "No bookings."

        items = bookings
        if status:
            items = [b for b in items if str(b.get("status", "")).lower() == status]
        if date_val:
            items = [b for b in items if str(b.get("booking_date", b.get("date", "")))[:10] == date_val]
        if date_range:
            d1, d2 = date_range
            items = [
                b for b in items
                if d1 <= str(b.get("booking_date", b.get("date", "")))[:10] <= d2
            ]

        # sort
        reverse = sort == "desc"
        items = sorted(items, key=lambda x: x.get("id", 0), reverse=reverse)

        title_map = {
            "pending": "🟡 **Pending Bookings",
            "completed": "✅ **Completed Bookings",
            "cancelled": "❌ **Cancelled Bookings",
        }
        title = title_map.get(status, "📋 **Bookings")
        if date_val:
            title = f"📅 **Bookings on {date_val}"
        lines = [fmt_booking(b) for b in items[:10]]
        return _list_reply(title, lines, len(items))

class WorkerHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        ents = result.entities
        wid = self._ent(ents, EntityType.WORKER_ID)
        name = self._ent(ents, EntityType.NAME)
        phone = self._ent(ents, EntityType.PHONE)
        email = self._ent(ents, EntityType.EMAIL)
        city = self._ent(ents, EntityType.CITY)
        skill = self._ent(ents, EntityType.SKILL)
        status = self._ent(ents, EntityType.STATUS)
        q = result.normalized_query

        workers = self.hub.workers()

        if wid is not None:
            w = next((x for x in workers if x.get("id") == wid), None)
            return fmt_worker(w) if w else f"❌ Worker #{wid} not found."

        items = workers
        if name:
            # fuzzy
            names = [w.get("name", "") for w in workers]
            matches = process.extract(name, names, scorer=fuzz.token_set_ratio, limit=10)
            matched_names = {m[0] for m in matches if m[1] >= 70}
            items = [w for w in workers if w.get("name") in matched_names]
        if phone:
            items = [w for w in items if phone in str(w.get("mobile", ""))]
        if email:
            items = [w for w in items if email.lower() in str(w.get("email", "")).lower()]
        if city:
            items = [w for w in items if city.lower() in str(w.get("city", "")).lower()]
        if skill:
            items = [w for w in items if skill.lower() in str(w.get("skills", "") + str(w.get("category", ""))).lower()]
        if status:
            items = [w for w in items if str(w.get("profile_status", w.get("status", ""))).lower() == status]

        if "top" in q or "highest rated" in q:
            items = items[:5]
            lines = [f"• {w.get('name')} (ID: {w.get('id')}) – {w.get('city', '')}" for w in items]
            return "🏆 **Top Workers**\n" + "\n".join(lines)

        if not items:
            return "No workers found matching your query."

        if len(items) == 1:
            return fmt_worker(items[0])

        title = "👷 **Workers"
        if skill:
            title = f"👷 **{skill.title()} Workers"
        if city:
            title = f"👷 **Workers in {city}"
        if status:
            title = f"👷 **{status.title()} Workers"
        lines = [fmt_worker(w) for w in items[:8]]
        return _list_reply(title, lines, len(items))

class CustomerHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        ents = result.entities
        cid = self._ent(ents, EntityType.CUSTOMER_ID)
        name = self._ent(ents, EntityType.NAME)
        phone = self._ent(ents, EntityType.PHONE)
        email = self._ent(ents, EntityType.EMAIL)

        customers = self.hub.customers()

        if cid is not None:
            c = next((x for x in customers if x.get("id") == cid), None)
            return fmt_customer(c) if c else f"❌ Customer #{cid} not found."

        items = customers
        if name:
            def full_name(c):
                return f"{c.get('first_name', '')} {c.get('last_name', '')}".strip() or c.get("name", "")
            names = [full_name(c) for c in customers]
            matches = process.extract(name, names, scorer=fuzz.token_set_ratio, limit=10)
            matched = {m[0] for m in matches if m[1] >= 70}
            items = [c for c in customers if full_name(c) in matched]
        if phone:
            items = [c for c in items if phone in str(c.get("phone", c.get("mobile", "")))]
        if email:
            items = [c for c in items if email.lower() in str(c.get("email", "")).lower()]

        if not items:
            return "No customers found."
        if len(items) == 1:
            return fmt_customer(items[0])

        lines = [fmt_customer(c) for c in items[:8]]
        return _list_reply("👤 **Customers", lines, len(items))

class RevenueHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        ents = result.entities
        date_val = self._ent(ents, EntityType.DATE)
        date_range = self._ent(ents, EntityType.DATE_RANGE)
        q = result.normalized_query
        bookings = self.hub.bookings()

        items = bookings
        if date_val:
            items = [b for b in items if str(b.get("booking_date", b.get("date", "")))[:10] == date_val]
        if date_range:
            d1, d2 = date_range
            items = [b for b in items if d1 <= str(b.get("booking_date", b.get("date", "")))[:10] <= d2]

        total = sum(float(b.get("amount", 0)) for b in items)
        if date_val:
            return f"💰 **Revenue on {date_val} : ₹{total:,.2f}**"
        if date_range:
            return f"💰 **Revenue {date_range[0]} → {date_range[1]} : ₹{total:,.2f}**"
        if "month" in q:
            return f"💰 **This Month's Revenue : ₹{total:,.2f}**"
        return f"💰 **Total Revenue : ₹{total:,.2f}**"

class PaymentHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        bookings = self.hub.bookings()
        items = [b for b in bookings if str(b.get("payment_status", "")).lower() in ("pending", "unpaid")]
        if not items:
            return "No pending payments."
        lines = [fmt_booking(b) for b in items[:8]]
        return _list_reply("💳 **Pending Payments", lines, len(items))

class StatisticsHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        q = result.normalized_query
        if "worker" in q:
            return f"👷 **Total Workers : {len(self.hub.workers())}**"
        if "customer" in q:
            return f"👤 **Total Customers : {len(self.hub.customers())}**"
        if "booking" in q:
            return f"📦 **Total Bookings : {len(self.hub.bookings())}**"
        if "categor" in q:
            return f"🛠 **Total Categories : {len(self.hub.categories())}**"
        if "revenue" in q:
            total = sum(float(b.get("amount", 0)) for b in self.hub.bookings())
            return f"💰 **Total Revenue : ₹{total:,.2f}**"
        # full dashboard
        return (
            f"📊 **Dashboard Statistics**\n"
            f"• Workers    : {len(self.hub.workers())}\n"
            f"• Customers  : {len(self.hub.customers())}\n"
            f"• Bookings   : {len(self.hub.bookings())}\n"
            f"• Categories : {len(self.hub.categories())}\n"
            f"• Revenue    : ₹{sum(float(b.get('amount', 0)) for b in self.hub.bookings()):,.2f}"
        )

class CategoryHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        cats = self.hub.categories()
        q = result.normalized_query
        if "top" in q or "most" in q:
            top = cats[:5]
            lines = [f"• {c.get('name') or c.get('category_name')}" for c in top]
            return "🏆 **Top Categories**\n" + "\n".join(lines)
        return f"🛠 **Total Categories : {len(cats)}**"

class KycHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        kycs = self.hub.kycs()
        status = self._ent(result.entities, EntityType.STATUS)
        if status:
            total = len([k for k in kycs if str(k.get("kyc_status", "")).lower() == status])
            emoji = {"pending": "📄", "approved": "✅", "rejected": "❌"}.get(status, "📄")
            return f"{emoji} **{status.title()} KYC : {total}**"
        return f"📄 **Total KYC records : {len(kycs)}**"

class NotificationHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        notifs = self.hub.notifications()
        return f"🔔 **Total Notifications : {len(notifs)}**"

class SearchHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        ents = result.entities
        name = self._ent(ents, EntityType.NAME)
        phone = self._ent(ents, EntityType.PHONE)
        email = self._ent(ents, EntityType.EMAIL)

        if not any([name, phone, email]):
            return "Please provide a name, phone or email to search."

        results = []

        # workers
        workers = self.hub.workers()
        if name:
            names = [w.get("name", "") for w in workers]
            matches = process.extract(name, names, scorer=fuzz.token_set_ratio, limit=5)
            matched = {m[0] for m in matches if m[1] >= 70}
            for w in workers:
                if w.get("name") in matched:
                    results.append(("Worker", fmt_worker(w)))
        if phone:
            for w in workers:
                if phone in str(w.get("mobile", "")):
                    results.append(("Worker", fmt_worker(w)))
        if email:
            for w in workers:
                if email.lower() in str(w.get("email", "")).lower():
                    results.append(("Worker", fmt_worker(w)))

        # customers
        customers = self.hub.customers()
        def full_name(c):
            return f"{c.get('first_name', '')} {c.get('last_name', '')}".strip() or c.get("name", "")
        if name:
            names = [full_name(c) for c in customers]
            matches = process.extract(name, names, scorer=fuzz.token_set_ratio, limit=5)
            matched = {m[0] for m in matches if m[1] >= 70}
            for c in customers:
                if full_name(c) in matched:
                    results.append(("Customer", fmt_customer(c)))
        if phone:
            for c in customers:
                if phone in str(c.get("phone", c.get("mobile", ""))):
                    results.append(("Customer", fmt_customer(c)))
        if email:
            for c in customers:
                if email.lower() in str(c.get("email", "")).lower():
                    results.append(("Customer", fmt_customer(c)))

        if not results:
            return f"No results found for '{name or phone or email}'."

        # prefer single best match
        if len(results) == 1:
            return results[0][1]

        body = "\n\n────────────────\n\n".join(r[1] for r in results[:6])
        return f"🔍 **Search Results ({len(results)})**\n\n{body}"

class HelpHandler(BaseHandler):
    def handle(self, result: IntentResult) -> str:
        return (
            "🤖 Main aapki madad kar sakta hoon:\n\n"
            "• Booking 15 / Booking ID 15 / Show booking 15\n"
            "• Worker 20 / Worker ID 20 / Worker Rahul\n"
            "• Customer 8 / Customer ID 8 / Customer Rahul\n"
            "• Pending bookings / Completed bookings / Cancelled bookings\n"
            "• Today's bookings / Today's revenue\n"
            "• Monthly revenue / Total revenue\n"
            "• Pending payments\n"
            "• Top workers / Top customers / Top categories\n"
            "• Pending KYC / Approved workers\n"
            "• Just type a name – I will search everywhere\n\n"
            "Bas natural language mein type kijiye!"
        )

# ------------------------------------------------------------------
# 9. HANDLER REGISTRY (extensible – add new intent = one new class)
# ------------------------------------------------------------------
HANDLER_MAP = {
    Intent.BOOKING:       BookingHandler,
    Intent.WORKER:        WorkerHandler,
    Intent.CUSTOMER:      CustomerHandler,
    Intent.REVENUE:       RevenueHandler,
    Intent.PAYMENT:       PaymentHandler,
    Intent.STATISTICS:    StatisticsHandler,
    Intent.CATEGORY:      CategoryHandler,
    Intent.KYC:           KycHandler,
    Intent.NOTIFICATION:  NotificationHandler,
    Intent.SEARCH:        SearchHandler,
    Intent.HELP:          HelpHandler,
}

# ------------------------------------------------------------------
# 10. ORCHESTRATOR
# ------------------------------------------------------------------
_extractor = EntityExtractor()
_detector  = IntentDetector(_extractor)
_hub       = DataHub()

def process_query(message: str) -> str:
    if not message or not message.strip():
        return "Please type a question, e.g. Booking 15, Pending bookings, Today's revenue"

    try:
        intent_result = _detector.detect(message)

        if intent_result.intent == Intent.UNKNOWN:
            return (
                "❓ Samajh nahi aaya. Try:\n"
                "Booking 15 • Pending bookings • Worker Rahul • Today's revenue • help"
            )

        # cache
        entity_map = {e.type.value: e.value for e in intent_result.entities}
        ck = _cache_key(intent_result.intent.value, entity_map)
        if ck in _query_cache:
            return _query_cache[ck]

        handler_cls = HANDLER_MAP.get(intent_result.intent, HelpHandler)
        handler = handler_cls(_hub)
        reply = handler.handle(intent_result)

        _query_cache[ck] = reply
        return reply

    except Exception as e:
        logger.exception(f"AI Assistant error: {e}")
        return "⚠️ Something went wrong. Please try again."

# ------------------------------------------------------------------
# 11. FASTAPI ENDPOINT (100 % compatible with old /chat-ai)
# ------------------------------------------------------------------
@router.get("/chat-ai")
def chat_ai(message: str = Query("", description="Natural language query")):
    """
    Enterprise Natural Language Query Engine.
    Drop-in replacement – same URL, same response shape.
    """
    reply = process_query(message)
    return {"reply": reply}