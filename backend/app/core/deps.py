"""
FastAPI dependencies for authentication and role-based authorization.
Use `get_current_user` on any protected route, and `require_roles(...)` to
restrict a route to specific roles (e.g. only HR can upload).
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.security import JWTError, decode_access_token
from app.models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode the JWT, then load the live user row from PostgreSQL (so a
    deactivated/deleted user is rejected even with a still-valid token)."""
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise ValueError("Token missing subject")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


def require_roles(*allowed_roles: str):
    """Dependency factory: restrict a route to specific roles, e.g.
    Depends(require_roles("HR"))."""

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return _check
