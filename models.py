from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from datetime import datetime

from database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100))
    email = Column(String(100), unique=True)
    mobile = Column(String(20), unique=True)

    gender = Column(String(20))
    date_of_birth = Column(Date)

    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))

    experience_years = Column(Integer)

    skills = Column(Text)
    about = Column(Text)

    aadhaar_number = Column(String(20))

    created_at = Column(DateTime, default=datetime.utcnow)
    
