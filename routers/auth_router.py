from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from database import get_db
from models import Admin

from schemas import LoginSchema

from auth import verify_password
from auth import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login")
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

    # ✅ THIS MUST BE OUTSIDE
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