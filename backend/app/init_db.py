import sys

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import Base, engine
from app.core.security import get_password_hash
from app.models import Device, InspectionOrder, InspectionOrderStep, InspectionTemplate, InspectionTemplateStep, Role, User


DEFAULT_ROLES = [
    {"name": "admin", "description": "管理员"},
    {"name": "worker", "description": "维保人员"},
    {"name": "auditor", "description": "审核员"},
]

DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin123456",
    "real_name": "系统管理员",
}


def init_roles(db: Session) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for role_data in DEFAULT_ROLES:
        role = db.scalar(select(Role).where(Role.name == role_data["name"]))
        if role is None:
            role = Role(**role_data)
            db.add(role)
            db.flush()
            print(f"已创建角色：{role.name}")
        else:
            print(f"角色已存在：{role.name}")
        roles[role.name] = role
    return roles


def init_default_admin(db: Session, admin_role: Role) -> None:
    admin = db.scalar(select(User).where(User.username == DEFAULT_ADMIN["username"]))
    if admin is not None:
        print("默认管理员已存在：admin")
        return

    admin = User(
        username=DEFAULT_ADMIN["username"],
        password_hash=get_password_hash(DEFAULT_ADMIN["password"]),
        real_name=DEFAULT_ADMIN["real_name"],
        role_id=admin_role.id,
        is_active=True,
    )
    db.add(admin)
    print("已创建默认管理员：admin / admin123456")


def init_database() -> None:
    if engine is None:
        print("数据库未配置，请先在 .env 中设置 DATABASE_URL")
        sys.exit(1)

    try:
        Base.metadata.create_all(bind=engine)
        with Session(engine) as db:
            roles = init_roles(db)
            init_default_admin(db, roles["admin"])
            db.commit()
        print("数据库初始化完成")
    except SQLAlchemyError as exc:
        print(f"数据库初始化失败：{exc}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
