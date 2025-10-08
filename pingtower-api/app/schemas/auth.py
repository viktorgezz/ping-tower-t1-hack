from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class TokenRefresh(BaseModel):
    refreshToken: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str

class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str
    user: UserResponse

class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
