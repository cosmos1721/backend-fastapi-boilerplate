import os
from datetime import datetime, timedelta, timezone
from fastapi import Response
from jose import jwt
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7  days
ACCESS_TOKEN_EXPIRE_TEMP_MINUTES = 60 * 2 # 2 hours

def create_jwt_token(user_id: str, expires_delta: timedelta = None, temp: bool = False) -> str:
    """
    Generate a JWT token for the specified user ID with an optional expiration delta.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    elif temp:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #temp CHANGE ALTER
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    sub = {"user_id": user_id, "time": datetime.now().isoformat()}
    to_encode = {"exp": expire, "sub": user_id}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_jwt_cookie(response: Response, user_id: str) -> Response:
    """
    Create a JWT token and set it as a cookie in the response with a 7-day expiration.
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(user_id, access_token_expires)
    response.set_cookie(key="access_token", value=access_token, samesite='lax', max_age=access_token_expires.total_seconds(), expires=expire)
    return response

def delete_jwt_cookie(response: Response) -> Response:
    """
    Delete the JWT token cookie from the response.
    """
    response.delete_cookie(key="access_token")
    return response

def create_refresh_token(user_id: str, expires_delta: timedelta = None) -> str:
    """
    Generate a refresh token for sensitive operations, with an optional expiration delta.
    """
    refresh_encoded_jwt = create_jwt_token(user_id, expires_delta)
    return refresh_encoded_jwt

#for hashing password in login/signup
def get_hashed_password(password: str) -> str:
    """
    Hash the provided password using bcrypt and return the hashed password.
    """
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    """
    Verify the provided password against the hashed password.
    """
    return password_context.verify(password, hashed_pass)
