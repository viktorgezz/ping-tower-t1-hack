from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from app.models.user import User, RefreshToken
from app.schemas.auth import UserLogin, UserRegister, AuthResponse, TokenResponse
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.post("/login", response_model=AuthResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Аутентификация пользователя"""
    # Поиск пользователя по email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    # Создание токенов
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Сохранение refresh токена в БД
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(db_refresh_token)
    db.commit()
    
    return AuthResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    )

@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверка существования пользователя
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создание нового пользователя
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Создание токенов
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Сохранение refresh токена в БД
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(db_refresh_token)
    db.commit()
    
    return AuthResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: dict, db: Session = Depends(get_db)):
    """Обновление access токена"""
    refresh_token = token_data.get("refreshToken")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token не предоставлен"
        )
    
    # Проверка refresh токена в БД
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh token"
        )
    
    # Создание новых токенов
    new_access_token = create_access_token(data={"sub": str(db_token.user_id)})
    new_refresh_token = create_refresh_token(data={"sub": str(db_token.user_id)})
    
    # Обновление refresh токена в БД
    db_token.token = new_refresh_token
    db_token.expires_at = datetime.utcnow() + timedelta(days=7)
    db.commit()
    
    return TokenResponse(
        accessToken=new_access_token,
        refreshToken=new_refresh_token
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(authorization: str = None, db: Session = Depends(get_db)):
    """Выход из системы"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация"
        )
    
    token = authorization.split(" ")[1]
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        # Удаление всех refresh токенов пользователя
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        db.commit()
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )
