from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.security import verify_password
from app.models.user import User
from app.schemas.user import CurrentUserResponse


class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.id == user_id)
        return db.scalar(stmt)

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.username == username)
        return db.scalar(stmt)

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User | None:
        user = UserService.get_user_by_username(db, username)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def to_current_user_response(user: User) -> CurrentUserResponse:
        return CurrentUserResponse(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            role=user.role.name,
        )
