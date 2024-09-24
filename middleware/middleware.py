import os
import uuid
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from utils.helpers import current_datetime
from utils.invalid_response_class import AuthenticationError, AuthenticationMissing
from utils.logData import LogDataClass
from utils.exception import CustomException

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)

async def create_request_id(request: Request):
    """
    Generate or retrieve a unique request ID and log the request data.
    
    Uses 'X-Request-ID' header if available; otherwise generates a UUID. 
    Captures the start time and logs the request details.

    Args:
        request (Request): The incoming HTTP request.

    Raises:
        CustomException: If logging or processing fails.
    """
    try:
        request_id = request._headers.get('X-Request-ID')
        if request_id:
            request.state.request_token = str(request_id)
        else:
            request_id = str(uuid.uuid4())
            request.state.request_token = request_id
        
        # Capture the start time
        request.state.start_time = str(current_datetime())
        
        log = await LogDataClass(request_id=request_id).request_log(request)
    except:
        raise CustomException().raise_exception(request_id=request.state.request_token)

async def authorisation(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate JWT from Authorization header and extract user ID.
    
    Checks for a valid JWT token in the Authorization header. If valid, 
    stores the user ID in request state; raises exceptions if invalid.

    Args:
        request (Request): The incoming HTTP request.
        credentials (HTTPAuthorizationCredentials): JWT token from the header.

    Raises:
        AuthenticationMissing: If the Authorization header is missing.
        AuthenticationError: If the token is invalid or expired.
        CustomException: For general exceptions during processing.
    """
    if credentials is None:
        raise AuthenticationMissing("Authorization header is missing")
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        request.state.user_data = user_id
        
    except JWTError:
        raise AuthenticationError("Invalid or expired token")
    except Exception as e:
        raise CustomException().raise_exception(request_id=request.state.request_token)
