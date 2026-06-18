from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean

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

from sqlalchemy import Column, Integer, String, Boolean
# models.py

from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)

    is_blocked = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    verification_status = Column(
        String(20),
        default="Pending"
    )