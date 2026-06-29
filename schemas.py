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

class BookingCreate(BaseModel):
    customer_name:str
    worker_name:str
    service_name:str
    service_selection_name:str
    
    booking_date: str
    slot: str

    quantity: int
    state: str
    address: str
    city: str
    pincode: str

    amount: int

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
