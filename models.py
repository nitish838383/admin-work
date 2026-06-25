from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from datetime import datetime
from database import Base

# -----------------------------------------------------------------------------------------------------------------------------------------------

# admin
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

# -----------------------------------------------------------------------------------------------------------------------------------------------

# 
class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    mobile = Column(String(20), unique=True, nullable=False)

    gender = Column(String(20))
    date_of_birth = Column(Date)

    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))

    category_id = Column(Integer)

    experience_years = Column(Integer, default=0)

    skills = Column(Text)
    about = Column(Text)

    aadhaar_number = Column(String(20), unique=True)
    status = Column(String(20), default="Pending")
    profile_image = Column(String(255))
    aadhaar_front = Column(String(255))
    aadhaar_back = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    mobile = Column(String(20), unique=True)




from sqlalchemy import Column, Integer, String
from database import Base

class AllCustomer(Base):
    __tablename__ = "all_customers"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(100))
    last_name = Column(String(100))

    phone = Column(String(20), unique=True)

    city = Column(String(100))
    address = Column(String(255))
    pincode = Column(String(20))  
    status = Column(String(20), default="Pending") 

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(225))
    worker_name = Column(String(255))
    service_name = Column(String(225))
    booking_date = Column(String(20))
    slot = Column(String(50))

    quantity = Column(Integer)
    state= Column(String(225))

    address = Column(String(255))
    city = Column(String(100))
    pincode = Column(String(20))

    amount = Column(Integer)

    payment_method = Column(String(50))
    payment_status = Column(String(20), default="Pending")

    status = Column(String(20), default="Pending")

    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(Integer)

    amount = Column(Integer)

    payment_method = Column(String(50))

    payment_status = Column(String(20), default="Pending")

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
