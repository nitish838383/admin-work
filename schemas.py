from pydantic import BaseModel
from pydantic import EmailStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
# -------------------------------------------------------------------------------------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

from pydantic import BaseModel
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class BookingCreate(BaseModel):
    service_id: int
    
    booking_date: date
    time_slot: str
    latitude: float
    longitude: float
    amount: Decimal
    payment_method: str

from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str


from pydantic import BaseModel

class SkillCreate(BaseModel):
    skill_name: str

from pydantic import BaseModel
from datetime import datetime


class KycCreate(BaseModel):
    worker_id: int

    aadhaar_number: str
    pan_number: str

    account_holder_name: str
    account_number: str
    bank_name: str
    ifsc_code: str

    aadhaar_front: str
    aadhaar_back: str
    pan_card_image: str
    passbook_image: str
    selfie_image: str


class KycResponse(BaseModel):
    id: int

   

    aadhaar_number: str
    pan_number: str

    account_holder_name: str
    account_number: str
    bank_name: str
    ifsc_code: str

    aadhaar_front: str
    aadhaar_back: str
    pan_card_image: str
    passbook_image: str
    selfie_image: str

    kyc_status: str

    created_at: datetime
    updated_at: datetime

from pydantic import BaseModel

class NotificationCreate(BaseModel):
    worker_id: int
    title: str
    message: str




class ReviewCreate(BaseModel):
    booking_id: int
    rating: int
    review: str