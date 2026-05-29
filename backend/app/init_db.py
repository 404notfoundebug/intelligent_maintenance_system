import sys

from sqlalchemy import inspect, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import Base, engine
from app.core.security import get_password_hash
from app.models import (
    CaseAuditRecord,
    Device,
    FaultImage,
    FaultReport,
    InspectionOrder,
    InspectionOrderStep,
    InspectionTemplate,
    InspectionTemplateStep,
    MaintenanceRecord,
    Role,
    RepairCase,
    User,
)


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


def ensure_knowledge_chunk_file_id_nullable() -> None:
    inspector = inspect(engine)
    columns = inspector.get_columns("knowledge_chunks")
    file_id_column = next((column for column in columns if column["name"] == "file_id"), None)
    if file_id_column is None or file_id_column.get("nullable"):
        return

    if engine.dialect.name != "mysql":
        print("璺宠繃 knowledge_chunks.file_id 鍙┖杩佺Щ锛氬綋鍓嶉潪 MySQL 鏁版嵁搴?")
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE knowledge_chunks MODIFY COLUMN file_id INT NULL"))
    print("宸插皢 knowledge_chunks.file_id 璋冩暣涓哄彲绌猴紝鐢ㄤ簬妫€淇渚嬪叆搴?")


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
        ensure_knowledge_chunk_file_id_nullable()
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
