from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os

# We explicitly use 'bcrypt' and handle the library conflict
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # Truncate to 72 chars to satisfy bcrypt's hard limit and prevent crashes
    return pwd_context.hash(password[:71])

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv("SECRET_KEY", "CONDUCTOR_KEY"), algorithm="HS256")
