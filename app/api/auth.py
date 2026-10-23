from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.security import create_access_token, get_current_user
from app.db.models import User, UserRole

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.DEVELOPER


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str


class UserResponse(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    if not payload.email or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    assigned_role = payload.role.value if payload.role else UserRole.DEVELOPER.value
    token = create_access_token(subject=payload.email, role=assigned_role)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=assigned_role,
        email=payload.email
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role if isinstance(current_user.role, str) else current_user.role.value,
        is_active=current_user.is_active
    )
