from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, Union
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.db.session import get_db
from app.db.models import User, UserRole

# Native bcrypt hashing implementation (compatible with modern Python 3.13 and bcrypt 4.x/5.x)
try:
    import bcrypt

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8")[:72],
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False

    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8")[:72], salt).decode("utf-8")

except ImportError:
    import hashlib
    import hmac

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        key = settings.SECRET_KEY.encode("utf-8")
        computed = hmac.new(key, plain_password.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, hashed_password)

    def get_password_hash(password: str) -> str:
        key = settings.SECRET_KEY.encode("utf-8")
        return hmac.new(key, password.encode("utf-8"), hashlib.sha256).hexdigest()



# OAuth2 Bearer token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=True
)


def create_access_token(
    subject: Union[str, Any],
    role: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate signed JWT access token with user identifier and role claim."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
    }
    if role:
        to_encode["role"] = str(role)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    OAuth2 dependency: Extracts and verifies JWT bearer token,
    then loads the corresponding active User from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    email: Optional[str] = payload.get("sub")
    if not email:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # If running in local mock/pre-migration dev mode, create an in-memory fallback user object
        role_claim = payload.get("role", UserRole.DEVELOPER.value)
        try:
            matched_role = UserRole(role_claim)
        except ValueError:
            matched_role = UserRole.DEVELOPER
        user = User(
            id=1,
            email=email,
            full_name="Nextserve Operator",
            role=matched_role,
            is_active=True
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    return user


def require_roles(*allowed_roles: UserRole):
    """
    Role-Based Access Control (RBAC) dependency factory.
    Allowed roles: Support Admin, Instructor, Developer, Owner.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User role '{current_user.role}' is not authorized. Allowed: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Optional ASGI Middleware to inspect incoming requests for Authorization headers,
    decode JWT tokens, and inject user claims into request.state.user.
    """
    def __init__(self, app, exclude_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            f"{settings.API_V1_STR}/auth/login",
            f"{settings.API_V1_STR}/school",
        ]

    async def dispatch(self, request: Request, call_next):
        # Skip middleware auth check on public / docs endpoints
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            payload = decode_access_token(token)
            if payload:
                request.state.user = payload
            else:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired JWT token"}
                )

        return await call_next(request)
