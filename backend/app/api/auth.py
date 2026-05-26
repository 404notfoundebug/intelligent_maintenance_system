from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token
from app.models.user import User
from app.schemas.auth import (
    CurrentUserApiResponse,
    LoginRequest,
    LoginResponse,
    LoginResponseData,
    OAuthTokenResponse,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def build_oauth_token_response(user: User) -> OAuthTokenResponse:
    return OAuthTokenResponse(
        access_token=create_access_token(subject=str(user.id)),
        token_type="bearer",
    )


def build_login_response(user: User) -> dict:
    token = build_oauth_token_response(user)
    user_data = UserService.to_current_user_response(user)
    return {
        "code": 200,
        "message": "success",
        "data": LoginResponseData(
            access_token=token.access_token,
            token_type=token.token_type,
            user=user_data,
        ),
    }


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token 无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id_int = int(user_id)
    except (JWTError, ValueError) as exc:
        raise credentials_exception from exc

    user = UserService.get_user_by_id(db, user_id_int)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    return current_user


def require_roles(roles: list[str]) -> Callable[[User], User]:
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        role_name = current_user.role.name if current_user.role else None
        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="当前用户无权访问该资源",
            )
        return current_user

    return role_checker


@router.post("/login", response_model=OAuthTokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = UserService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return build_oauth_token_response(user)


@router.post("/login-json", response_model=LoginResponse)
def login_json(payload: LoginRequest, db: Session = Depends(get_db)):
    user = UserService.authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return build_login_response(user)


@router.get("/me", response_model=CurrentUserApiResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return {
        "code": 200,
        "message": "success",
        "data": UserService.to_current_user_response(current_user),
    }
