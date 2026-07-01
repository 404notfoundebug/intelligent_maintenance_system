from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_password_hash, verify_password
from app.models.role import Role
from app.models.user import User
from app.schemas.user_management import (
    UserChangePassword,
    UserCreate,
    UserResetPassword,
    UserRoleUpdate,
    UserStatusUpdate,
    UserUpdate,
)


class UserManagementService:
    @staticmethod
    def _role_name(user: User) -> str | None:
        return user.role.name if user.role else None

    @staticmethod
    def user_to_dict(user: User) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "phone": user.phone,
            "email": user.email,
            "role": user.role.name if user.role else None,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    @staticmethod
    def role_to_dict(role: Role) -> dict:
        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "created_at": role.created_at,
            "updated_at": role.updated_at,
        }

    @staticmethod
    def get_role_by_name(db: Session, role_name: str) -> Role | None:
        return db.scalar(select(Role).where(Role.name == role_name))

    @staticmethod
    def get_user(db: Session, user_id: int) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.id == user_id)
        return db.scalar(stmt)

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.username == username)
        return db.scalar(stmt)

    @staticmethod
    def create_user(db: Session, payload: UserCreate) -> User:
        if UserManagementService.get_user_by_username(db, payload.username):
            raise ValueError("用户名已存在")

        role = UserManagementService.get_role_by_name(db, payload.role)
        if role is None:
            raise LookupError("角色不存在")

        user = User(
            username=payload.username,
            password_hash=get_password_hash(payload.password),
            real_name=payload.real_name,
            phone=payload.phone,
            email=payload.email,
            role_id=role.id,
            is_active=payload.is_active,
        )
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return UserManagementService.get_user(db, user.id) or user
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("用户名已存在") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def list_users(
        db: Session,
        page: int,
        page_size: int,
        keyword: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[int, list[User]]:
        conditions = []
        if keyword:
            pattern = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    User.username.like(pattern),
                    User.real_name.like(pattern),
                    User.phone.like(pattern),
                    User.email.like(pattern),
                )
            )
        if role:
            conditions.append(Role.name == role)
        if is_active is not None:
            conditions.append(User.is_active == is_active)

        count_stmt = select(func.count()).select_from(User).join(Role)
        query_stmt = select(User).options(joinedload(User.role)).join(Role).order_by(User.created_at.desc(), User.id.desc())
        if conditions:
            count_stmt = count_stmt.where(*conditions)
            query_stmt = query_stmt.where(*conditions)

        total = db.scalar(count_stmt) or 0
        items = db.scalars(query_stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return total, list(items)

    @staticmethod
    def update_user(db: Session, user_id: int, payload: UserUpdate, current_user: User) -> User:
        user = UserManagementService.get_user(db, user_id)
        if user is None:
            raise LookupError("用户不存在")

        is_admin = UserManagementService._role_name(current_user) == "admin"
        if not is_admin and user.id != current_user.id:
            raise PermissionError("没有权限修改该用户")

        update_data = payload.model_dump(exclude_unset=True)
        if not is_admin:
            update_data.pop("username", None)

        new_username = update_data.get("username")
        if new_username and new_username != user.username:
            existing = UserManagementService.get_user_by_username(db, new_username)
            if existing and existing.id != user.id:
                raise ValueError("用户名已存在")

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            db.commit()
            db.refresh(user)
            return UserManagementService.get_user(db, user.id) or user
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("用户名已存在") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def update_user_role(db: Session, user_id: int, payload: UserRoleUpdate, current_user: User) -> User:
        user = UserManagementService.get_user(db, user_id)
        if user is None:
            raise LookupError("用户不存在")
        if user.id == current_user.id and payload.role != "admin":
            raise ValueError("禁止将自己的角色修改为非admin")

        role = UserManagementService.get_role_by_name(db, payload.role)
        if role is None:
            raise LookupError("角色不存在")

        user.role_id = role.id
        try:
            db.commit()
            db.refresh(user)
            return UserManagementService.get_user(db, user.id) or user
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def update_user_status(db: Session, user_id: int, payload: UserStatusUpdate, current_user: User) -> User:
        user = UserManagementService.get_user(db, user_id)
        if user is None:
            raise LookupError("用户不存在")
        if user.id == current_user.id and not payload.is_active:
            raise ValueError("禁止禁用当前登录用户")

        user.is_active = payload.is_active
        try:
            db.commit()
            db.refresh(user)
            return UserManagementService.get_user(db, user.id) or user
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def reset_password(db: Session, user_id: int, payload: UserResetPassword) -> User:
        user = UserManagementService.get_user(db, user_id)
        if user is None:
            raise LookupError("用户不存在")

        user.password_hash = get_password_hash(payload.new_password)
        try:
            db.commit()
            db.refresh(user)
            return UserManagementService.get_user(db, user.id) or user
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def change_my_password(db: Session, current_user: User, payload: UserChangePassword) -> None:
        user = UserManagementService.get_user(db, current_user.id)
        if user is None:
            raise LookupError("用户不存在")
        if not verify_password(payload.old_password, user.password_hash):
            raise ValueError("旧密码错误")

        user.password_hash = get_password_hash(payload.new_password)
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def get_roles(db: Session) -> list[Role]:
        return list(db.scalars(select(Role).order_by(Role.id.asc())).all())

    @staticmethod
    def list_workers(db: Session) -> list[User]:
        """获取所有激活的维修工人"""
        stmt = (
            select(User)
            .options(joinedload(User.role))
            .join(Role)
            .where(Role.name == "worker", User.is_active == True)
            .order_by(User.real_name.asc(), User.id.asc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        user = UserManagementService.get_user(db, user_id)
        if user is None:
            raise LookupError("用户不存在")
        try:
            db.delete(user)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def update_my_profile(db: Session, current_user: User, payload: UserUpdate) -> User:
        """更新当前用户的个人信息（不允许修改用户名和角色）"""
        user = UserManagementService.get_user(db, current_user.id)
        if user is None:
            raise LookupError("用户不存在")

        update_data = payload.model_dump(exclude_unset=True)
        # 普通用户不允许修改用户名
        update_data.pop("username", None)

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            db.commit()
            db.refresh(user)
            return UserManagementService.get_user(db, user.id) or user
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("数据冲突") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def create_role(db: Session, name: str, description: str | None = None) -> Role:
        existing = UserManagementService.get_role_by_name(db, name)
        if existing:
            raise ValueError("角色已存在")
        role = Role(name=name, description=description)
        try:
            db.add(role)
            db.commit()
            db.refresh(role)
            return role
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("角色已存在") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def update_role(db: Session, role_id: int, name: str | None = None, description: str | None = None) -> Role:
        role = db.get(Role, role_id)
        if role is None:
            raise LookupError("角色不存在")
        if name is not None and name != role.name:
            existing = UserManagementService.get_role_by_name(db, name)
            if existing and existing.id != role_id:
                raise ValueError("角色名已存在")
            role.name = name
        if description is not None:
            role.description = description
        try:
            db.commit()
            db.refresh(role)
            return role
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("角色名已存在") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def delete_role(db: Session, role_id: int) -> None:
        role = db.get(Role, role_id)
        if role is None:
            raise LookupError("角色不存在")
        # 检查是否有用户使用该角色
        user_count = db.scalar(select(func.count()).select_from(User).where(User.role_id == role_id))
        if user_count and user_count > 0:
            raise ValueError(f"该角色下还有 {user_count} 个用户，无法删除")
        try:
            db.delete(role)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
