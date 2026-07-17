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
from schemas import BookingCreate
from fastapi.responses import JSONResponse
import random
from datetime import datetime, timedelta









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
async def google_callback(request: Request):

    token = await oauth.google.authorize_access_token(request)

    user = token["userinfo"]

    email = user["email"]
    name = user["name"]

    # Database check yahan kar sakte ho

    return RedirectResponse("/auth/dashboard")
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

# ------------------------------------------------------------------------------------------------------------------------------------------------
# get dashboard
# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------

from models import User, Booking
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

    # ---------------- Customers ----------------
    try:
        customers_response = requests.get(
            "https://mistripoint-backend-1.onrender.com/auth/all-customers",
            timeout=10
        )
        customers_response.raise_for_status()

        data_customers = customers_response.json()

        if isinstance(data_customers, dict):
            customers = data_customers.get("customers", [])
        else:
            customers = data_customers

        total_customers = len(customers)

    except Exception as e:
        print("Customers API Error:", e)
        customers = []
        total_customers = 0

    # ---------------- Workers ----------------
    try:
        workers_response = requests.get(
            "https://mistripoint-1.onrender.com/worker-profiles",
            timeout=10
        )
        workers_response.raise_for_status()

        data_workers = workers_response.json()

        if isinstance(data_workers, dict):
            workers = data_workers.get("data", [])
        else:
            workers = data_workers

        total_workers = len(workers)

    except Exception as e:
        print("Workers API Error:", e)
        workers = []
        total_workers = 0

    # ---------------- Skills ----------------
    try:
        skills_response = requests.get(
            "https://mistripoint-1.onrender.com/skills",
            timeout=10
        )
        skills_response.raise_for_status()

        data_skills = skills_response.json()

        if isinstance(data_skills, dict):
            skills = data_skills.get("data", [])
        else:
            skills = data_skills

        total_skills = len(skills)

    except Exception as e:
        print("Skills API Error:", e)
        skills = []
        total_skills = 0

    # ---------------- Worker KYC ----------------
    try:
        kycs_response = requests.get(
            "https://mistripoint-1.onrender.com/worker-kyc",
            timeout=10
        )
        kycs_response.raise_for_status()

        data_kycs = kycs_response.json()

        if isinstance(data_kycs, dict):
            kycs = data_kycs.get("data", [])
        else:
            kycs = data_kycs

        total_kyc_workers = len(kycs)

    except Exception as e:
        print("KYC API Error:", e)
        kycs = []
        total_kyc_workers = 0

    # ---------------- Notifications ----------------
    try:
        notification_response = requests.get(
            "https://mistripoint-1.onrender.com/notifications",
            timeout=10
        )
        notification_response.raise_for_status()

        data_notifications = notification_response.json()

        if isinstance(data_notifications, dict):
            notifications = data_notifications.get("data", [])
        else:
            notifications = data_notifications

        total_notifications = len(notifications)

    except Exception as e:
        print("Notification API Error:", e)
        notifications = []
        total_notifications = 0

    # ---------------- Reviews ----------------
    try:
        reviews_response = requests.get(
            "https://mistripoint-1.onrender.com/reviews",
            timeout=10
        )
        reviews_response.raise_for_status()

        data_reviews = reviews_response.json()

        if isinstance(data_reviews, dict):
            reviews = data_reviews.get("data", [])
        else:
            reviews = data_reviews

        total_reviews = len(reviews)

    except Exception as e:
        print("Reviews API Error:", e)
        reviews = []
        total_reviews = 0

    # ---------------- Customers ----------------
    try:
        booking_response = requests.get(
            "https://mistripoint-backend-1.onrender.com/auth/admin/bookings",
            timeout=10
        )
        booking_response.raise_for_status()

        data_booking = booking_response.json()

        if isinstance(data_booking, dict):
            booking = data_booking.get("booking", [])
        else:
            booking = data_booking

        total_bookings = len(booking)

    except Exception as e:
        print("booking API Error:", e)
        booking = []
        total_bookings = 0


    # ---------------- Local Database ----------------
    total_users = db.query(User).count()
    total_bookings = db.query(Booking).count()

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
import os
import requests

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
            "email": "admin.ustadji@gmail.com"
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": "OTP Verification",
        "htmlContent": f"""
        <h2>Password Reset OTP</h2>

        <h1>{otp}</h1>

        <p>This OTP is valid for 10 minutes.</p>
        """
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(response.status_code)
    print(response.text)
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

# ===================================================================================================================================
# all- skills
@router.get("/all-skills")
def all_skills(
    request: Request,
    db: Session = Depends(get_db)
):
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
            "total_skills":total_skills,
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
    
    try:
        customers_response = requests.get(
            "https://mistripoint-backend-1.onrender.com/auth/all-customers",
            timeout=10
        )
        customers_response.raise_for_status()

        data_customers = customers_response.json()

        if isinstance(data_customers, dict):
            customers = data_customers.get("customers", [])
        else:
            customers = data_customers

        total_customers = len(customers)

    except Exception as e:
        print("Customers API Error:", e)
        customers = []
        total_customers = 0

    try:
        workers_response = requests.get(
            "https://mistripoint-1.onrender.com/worker-profiles",
            timeout=10
        )
        workers_response.raise_for_status()

        data_workers = workers_response.json()

        if isinstance(data_workers, dict):
            workers = data_workers.get("data", [])
        else:
            workers = data_workers

        total_workers = len(workers)

    except Exception as e:
        print("Workers API Error:", e)
        workers = []
        total_workers = 0
    return templates.TemplateResponse(
        name = "report.html",
        request=request,
        context={
            "request":request,
            
            "total_customers": total_customers,
            "total_workers": total_workers,
            
            "customers": customers,
           
            
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