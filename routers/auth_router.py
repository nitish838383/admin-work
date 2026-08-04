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
            "total_revenue": total_revenue
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
# IMPROVED AI CHAT ASSISTANT (replace old /chat-ai)
# =====================================================================
import re
from typing import Any, Dict, List, Optional

@router.get("/chat-ai")
def chat_ai(message: str):
    """
    Natural language AI assistant for Bookings / Workers / Customers / Revenue etc.
    Supports:
    - Booking 15 / Booking ID 15 / Show booking 15
    - Worker 20 / Worker ID 20
    - Customer 8 / Customer ID 8
    - Pending / Completed / Cancelled bookings
    - Today's bookings / Today's revenue / Monthly revenue
    - Top workers / Top customers / Top categories
    - Pending payments / Pending KYC etc.
    """
    if not message or not message.strip():
        return {"reply": "Please type a question, e.g. Booking 15, Pending bookings, Today's revenue"}

    msg = message.lower().strip()

    # ---------- Helper: safe API call ----------
    def safe_get(url: str, key: Optional[str] = None) -> List[Dict]:
        try:
            r = requests.get(url, timeout=12)
            r.raise_for_status()
            data = r.json()
            if key and isinstance(data, dict):
                return data.get(key, []) if isinstance(data.get(key), list) else []
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                # try common keys
                for k in ("data", "booking", "bookings", "customers", "workers"):
                    if k in data and isinstance(data[k], list):
                        return data[k]
            return []
        except Exception as e:
            print(f"API Error [{url}]: {e}")
            return []

    # ---------- Correct APIs (same as your dashboard) ----------
    workers   = safe_get("https://mistripoint-1.onrender.com/worker-profiles", "data")
    bookings  = safe_get("https://mistripoint-backend-1.onrender.com/auth/admin/bookings")  # FIXED URL
    customers = safe_get("https://mistripoint-backend-1.onrender.com/auth/all-customers", "customers")
    kycs      = safe_get("https://mistripoint-1.onrender.com/worker-kyc", "data")
    categories= safe_get("https://mistripoint-backend-1.onrender.com/auth/categories")
    notifications = safe_get("https://mistripoint-1.onrender.com/notifications", "data")

    # ---------- Regex ID extraction ----------
    def extract_id(patterns: List[str]) -> Optional[int]:
        for p in patterns:
            m = re.search(p, msg, re.IGNORECASE)
            if m:
                try:
                    return int(m.group(1))
                except:
                    pass
        return None

    booking_id  = extract_id([r"booking\s*(?:id)?\s*[#:]?\s*(\d+)", r"show\s+booking\s+(\d+)", r"booking\s+(\d+)"])
    worker_id   = extract_id([r"worker\s*(?:id)?\s*[#:]?\s*(\d+)", r"show\s+worker\s+(\d+)", r"worker\s+(\d+)"])
    customer_id = extract_id([r"customer\s*(?:id)?\s*[#:]?\s*(\d+)", r"show\s+customer\s+(\d+)", r"customer\s+(\d+)"])

    # ---------- Format helpers ----------
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

    # ===================== LOGIC =====================

    # 1. Single Booking by ID
    if booking_id is not None:
        b = next((x for x in bookings if x.get("id") == booking_id), None)
        if b:
            return {"reply": fmt_booking(b)}
        return {"reply": f"❌ Booking #{booking_id} not found."}

    # 2. Single Worker by ID
    if worker_id is not None:
        w = next((x for x in workers if x.get("id") == worker_id), None)
        if w:
            return {"reply": fmt_worker(w)}
        return {"reply": f"❌ Worker #{worker_id} not found."}

    # 3. Single Customer by ID
    if customer_id is not None:
        c = next((x for x in customers if x.get("id") == customer_id), None)
        if c:
            return {"reply": fmt_customer(c)}
        return {"reply": f"❌ Customer #{customer_id} not found."}

    # 4. Status-based bookings
    if any(k in msg for k in ["pending booking", "pending bookings"]):
        items = [b for b in bookings if str(b.get("status", "")).lower() == "pending"]
        if not items:
            return {"reply": "No pending bookings found."}
        lines = [fmt_booking(b) for b in items[:8]]
        return {"reply": f"🟡 **Pending Bookings ({len(items)})**\n\n" + "\n\n────────────────\n\n".join(lines)}

    if any(k in msg for k in ["completed booking", "completed bookings"]):
        items = [b for b in bookings if str(b.get("status", "")).lower() == "completed"]
        if not items:
            return {"reply": "No completed bookings found."}
        lines = [fmt_booking(b) for b in items[:8]]
        return {"reply": f"✅ **Completed Bookings ({len(items)})**\n\n" + "\n\n────────────────\n\n".join(lines)}

    if any(k in msg for k in ["cancelled booking", "cancelled bookings", "cancel booking"]):
        items = [b for b in bookings if str(b.get("status", "")).lower() in ("cancelled", "canceled")]
        if not items:
            return {"reply": "No cancelled bookings found."}
        lines = [fmt_booking(b) for b in items[:8]]
        return {"reply": f"❌ **Cancelled Bookings ({len(items)})**\n\n" + "\n\n────────────────\n\n".join(lines)}

    # 5. Today's bookings / revenue
    if "today" in msg and "booking" in msg:
        from datetime import date
        today = date.today().isoformat()
        items = [b for b in bookings if str(b.get("booking_date", b.get("date", "")))[:10] == today]
        if not items:
            return {"reply": "No bookings for today."}
        lines = [fmt_booking(b) for b in items[:10]]
        return {"reply": f"📅 **Today's Bookings ({len(items)})**\n\n" + "\n\n────────────────\n\n".join(lines)}

    if "today" in msg and "revenue" in msg:
        from datetime import date
        today = date.today().isoformat()
        total = sum(float(b.get("amount", 0)) for b in bookings
                    if str(b.get("booking_date", b.get("date", "")))[:10] == today)
        return {"reply": f"💰 **Today's Revenue : ₹{total:,.2f}**"}

    # 6. Monthly / Total revenue
    if any(k in msg for k in ["monthly revenue", "this month revenue", "month revenue"]):
        from datetime import date
        today = date.today()
        total = sum(float(b.get("amount", 0)) for b in bookings
                    if str(b.get("booking_date", b.get("date", "")))[:7] == today.strftime("%Y-%m"))
        return {"reply": f"💰 **This Month's Revenue : ₹{total:,.2f}**"}

    if "total revenue" in msg or "revenue" in msg:
        total = sum(float(b.get("amount", 0)) for b in bookings)
        return {"reply": f"💰 **Total Revenue : ₹{total:,.2f}**"}

    # 7. Pending payments
    if "pending payment" in msg or "pending payments" in msg:
        items = [b for b in bookings if str(b.get("payment_status", "")).lower() in ("pending", "unpaid")]
        if not items:
            return {"reply": "No pending payments."}
        lines = [fmt_booking(b) for b in items[:8]]
        return {"reply": f"💳 **Pending Payments ({len(items)})**\n\n" + "\n\n────────────────\n\n".join(lines)}

    # 8. Totals
    if any(k in msg for k in ["total worker", "total workers", "how many worker"]):
        return {"reply": f"👷 **Total Workers : {len(workers)}**"}

    if any(k in msg for k in ["total booking", "total bookings", "how many booking"]):
        return {"reply": f"📦 **Total Bookings : {len(bookings)}**"}

    if any(k in msg for k in ["total customer", "total customers", "how many customer"]):
        return {"reply": f"👤 **Total Customers : {len(customers)}**"}

    if any(k in msg for k in ["total category", "total categories"]):
        return {"reply": f"🛠 **Total Categories : {len(categories)}**"}

    # 9. Worker status counts
    if "approved worker" in msg:
        total = len([w for w in workers if str(w.get("profile_status", "")).lower() == "approved"])
        return {"reply": f"✅ **Approved Workers : {total}**"}

    if "pending worker" in msg:
        total = len([w for w in workers if str(w.get("profile_status", "")).lower() == "pending"])
        return {"reply": f"🟡 **Pending Workers : {total}**"}

    # 10. KYC
    if "pending kyc" in msg:
        total = len([k for k in kycs if str(k.get("kyc_status", "")).lower() == "pending"])
        return {"reply": f"📄 **Pending KYC : {total}**"}

    if "approved kyc" in msg:
        total = len([k for k in kycs if str(k.get("kyc_status", "")).lower() == "approved"])
        return {"reply": f"✅ **Approved KYC : {total}**"}

    if "rejected kyc" in msg:
        total = len([k for k in kycs if str(k.get("kyc_status", "")).lower() == "rejected"])
        return {"reply": f"❌ **Rejected KYC : {total}**"}

    # 11. Top lists (simple)
    if "top worker" in msg or "top workers" in msg:
        # count bookings per worker if possible, else just first 5
        top = workers[:5]
        lines = [f"• {w.get('name')} (ID: {w.get('id')}) – {w.get('city', '')}" for w in top]
        return {"reply": "🏆 **Top Workers**\n" + "\n".join(lines)}

    if "top customer" in msg or "top customers" in msg:
        top = customers[:5]
        lines = []
        for c in top:
            name = f"{c.get('first_name','')} {c.get('last_name','')}".strip() or c.get('name') or 'N/A'
            lines.append(f"• {name} (ID: {c.get('id')})")
        return {"reply": "🏆 **Top Customers**\n" + "\n".join(lines)}

    if "top categor" in msg:
        top = categories[:5]
        lines = [f"• {c.get('name') or c.get('category_name')}" for c in top]
        return {"reply": "🏆 **Top Categories**\n" + "\n".join(lines)}

    # 12. Notifications
    if "notification" in msg:
        return {"reply": f"🔔 **Total Notifications : {len(notifications)}**"}

    # ---------- Default help ----------
    return {
        "reply": (
            "🤖 Main aapki madad kar sakta hoon:\n\n"
            "• Booking 15 / Booking ID 15 / Show booking 15\n"
            "• Worker 20 / Worker ID 20\n"
            "• Customer 8 / Customer ID 8\n"
            "• Pending bookings / Completed bookings / Cancelled bookings\n"
            "• Today's bookings / Today's revenue\n"
            "• Monthly revenue / Total revenue\n"
            "• Pending payments\n"
            "• Top workers / Top customers / Top categories\n"
            "• Pending KYC / Approved workers\n\n"
            "Bas natural language mein type kijiye!"
        )
    }