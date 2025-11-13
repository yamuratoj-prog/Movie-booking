from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = os.getenv("JWT_SECRET", "secret")
ALG = os.getenv("JWT_ALG", "HS256")
EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def hash_password(pwd: str):
    return pwd_context.hash(pwd)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(sub: str):
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    to_encode = {"sub": sub, "exp": expire}
    return jwt.encode(to_encode, SECRET, algorithm=ALG)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALG])
        return payload.get("sub")
    except JWTError:
        return None
