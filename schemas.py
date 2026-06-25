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