from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.rate_limiter import rate_limiter, RateLimitExceededError

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        raise UnauthorizedError("Authentication token required.")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload.get("sub"))
    except Exception:
        raise UnauthorizedError("Invalid or expired authentication token.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise UnauthorizedError("User account is inactive or not found.")
    return user

def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(f"Operation requires one of roles: {[r.value for r in allowed_roles]}")
        return current_user
    return role_checker

async def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    is_limited = await rate_limiter.is_rate_limited(client_ip)
    if is_limited:
        raise RateLimitExceededError()
