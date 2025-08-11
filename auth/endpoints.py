from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.auth import UserLogin, Token, TokenRefresh, TokenResponse, User
from auth.database import authenticate_user, get_user_by_id
from auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from typing import Optional

# Router para endpoints de autenticação
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Dependency para obter o usuário atual baseado no token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token, "access")
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency para obter o usuário atual ativo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency para obter o usuário atual que seja admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Endpoint para fazer login e obter tokens JWT"""
    # Autentica o usuário
    user = authenticate_user(user_credentials.username, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )
    
    # Cria os tokens
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.username, "user_id": user.id})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh):
    """Endpoint para renovar o token de acesso usando o refresh token"""
    # Verifica o refresh token
    token_info = verify_token(token_data.refresh_token, "refresh")
    
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Verifica se o usuário ainda existe e está ativo
    user = get_user_by_id(token_info.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists or is inactive",
        )
    
    # Cria um novo access token
    new_access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    
    return TokenResponse(access_token=new_access_token)

@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Endpoint para obter informações do usuário atual"""
    return current_user

@router.get("/admin-only")
async def admin_only_endpoint(current_user: User = Depends(get_current_admin_user)):
    """Endpoint de exemplo que só admins podem acessar"""
    return {
        "message": "Hello admin!",
        "user": current_user.username,
        "admin_level": True
    }