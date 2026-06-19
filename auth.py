from passlib.context import CryptContext
from jose import jwt
from datetime import datetime
from datetime import timedelta

SECRET_KEY = "super_secret_key"
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
# ----------------------------------------------------------------------------------------------------------------------------------------
# harsh-passworrd
def hash_password(password: str):
    return pwd_context.hash(password)

# --------------------------------------------------------------------------------------------------------------------------------------------

# verify-password
def verify_password(plain_password: str, hashed_password: str):
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)

# -----------------------------------------------------------------------------------------------------------------------------------------------

# create_access_token
def create_access_token(data):

    expire = datetime.utcnow() + timedelta(hours=8)

    payload = data.copy()

    payload.update(
        {"exp": expire}
    )

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token