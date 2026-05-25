from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from slowapi import Limiter
from backend.app.models.database import get_db
from backend.app.models.user import User
from backend.app.core.security import decode_access_token
from backend.app.core.logging import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_user_rate_limit_key(request: Request) -> str:
    """
    Computes a unique key for rate-limiting. Uses authenticated user ID if present,
    otherwise falls back to client IP address.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            return f"user_{payload['sub']}"
            
    # Fallback to remote IP address
    return request.client.host if request.client else "127.0.0.1"


# Initialize the slowapi Limiter using our custom user key function
limiter = Limiter(key_func=get_user_rate_limit_key)


def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Retrieves the current authenticated user from the JWT token.
    Raises 401 Unauthorized if token is missing or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user
