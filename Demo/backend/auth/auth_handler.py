from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
from pydantic import BaseModel

SECRET_KEY = "tcs_hackathon_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

def hash_password(password: str) -> str:
    """Simple SHA256 hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password

#user database
USERS_DB = {
    "sravani@tcs.com": {
        "username": "sravani@tcs.com",
        "full_name": "Sravani",
        "email": "sravani@tcs.com",
        "hashed_password": hash_password("password123"),
        "department": "Sales",
        "role": "Manager",
        "disabled": False
    },
    "adithi@tcs.com": {
        "username": "adithi.com",
        "full_name": "Adithi",
        "email": "adithi@tcs.com",
        "hashed_password": hash_password("password123"),
        "department": "Finance",
        "role": "Director",
        "disabled": False
    },
    "admin@tcs.com": {
        "username": "admin@tcs.com",
        "full_name": "Admin User",
        "email": "admin@tcs.com",
        "hashed_password": hash_password("admin123"),
        "department": "Executive",
        "role": "C-Level",
        "disabled": False
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: str
    full_name: str
    department: str
    role: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

def get_user(username: str):
    if username in USERS_DB:
        user_dict = USERS_DB[username]
        return UserInDB(**user_dict)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None