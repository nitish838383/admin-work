import os

SECRET_KEY = os.getenv("SECRET_KEY", "my-super-secret-key-123456789")
ALGORITHM = "HS256"