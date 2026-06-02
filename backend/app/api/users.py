from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.user_management import (
    UserApiResponse,
    UserChangePassword,
    UserCreate,
    UserResetPassword,
    UserRoleUpdate,
    UserStatusUpdate,
    UserUpdate,
)
from app.services.user_management_service import UserManagementService

router = APIRouter(prefix="/api/users", tags=["users"])


def success(data: dict | list | None = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data or {}}


def raise_service_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if isinstance(exc, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库操作失败：{exc}",
        ) from exc
    raise exc


@router.get("/roles", response_model=UserApiResponse)
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        roles = UserManagementService.get_roles(db)
        return success(data=[UserManagementService.role_to_dict(role) for role in roles])
    except Exception as exc:
        raise_service_error(exc)


@router.get("/me/profile", response_model=UserApiResponse)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    return success(data=UserManagementService.user_to_dict(current_user))


@router.put("/me/password", response_model=UserApiResponse)
def change_my_password(
    payload: UserChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        UserManagementService.change_my_password(db, current_user, payload)
        return success(data={"user_id": current_user.id}, message="密码修改成功")
    except Exception as exc:
        raise_service_error(exc)


@router.post("", response_model=UserApiResponse)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        user = UserManagementService.create_user(db, payload)
        return success(data=UserManagementService.user_to_dict(user))
    except Exception as exc:
        raise_service_error(exc)


@router.get("", response_model=UserApiResponse)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        total, items = UserManagementService.list_users(
            db=db,
            page=page,
            page_size=page_size,
            keyword=keyword,
            role=role,
            is_active=is_active,
        )
        return success(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [UserManagementService.user_to_dict(item) for item in items],
            }
        )
    except Exception as exc:
        raise_service_error(exc)


@router.get("/{user_id}", response_model=UserApiResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        if UserManagementService._role_name(current_user) != "admin" and user_id != current_user.id:
            raise PermissionError("没有权限查看该用户")
        user = UserManagementService.get_user(db, user_id)
        if user is None:
            raise LookupError("用户不存在")
        return success(data=UserManagementService.user_to_dict(user))
    except Exception as exc:
        raise_service_error(exc)


@router.put("/{user_id}", response_model=UserApiResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        user = UserManagementService.update_user(db, user_id, payload, current_user)
        return success(data=UserManagementService.user_to_dict(user))
    except Exception as exc:
        raise_service_error(exc)


@router.put("/{user_id}/role", response_model=UserApiResponse)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        user = UserManagementService.update_user_role(db, user_id, payload, current_user)
        return success(data=UserManagementService.user_to_dict(user))
    except Exception as exc:
        raise_service_error(exc)


@router.put("/{user_id}/status", response_model=UserApiResponse)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        user = UserManagementService.update_user_status(db, user_id, payload, current_user)
        return success(data=UserManagementService.user_to_dict(user))
    except Exception as exc:
        raise_service_error(exc)


@router.put("/{user_id}/reset-password", response_model=UserApiResponse)
def reset_password(
    user_id: int,
    payload: UserResetPassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        user = UserManagementService.reset_password(db, user_id, payload)
        return success(data={"user_id": user.id}, message="密码重置成功")
    except Exception as exc:
        raise_service_error(exc)
