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
        print("跳过 knowledge_chunks.file_id 可空迁移：当前不是 MySQL 数据库")
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE knowledge_chunks MODIFY COLUMN file_id INT NULL"))
    print("已将 knowledge_chunks.file_id 调整为可空，用于检修案例入库")


def ensure_maintenance_audit_columns() -> None:
    """为已有本地数据库补齐维保审核字段、索引和外键。"""
    if engine.dialect.name != "mysql":
        raise RuntimeError("本项目仅支持本地 MySQL 数据库")

    table_name = "maintenance_records"
    inspector = inspect(engine)
    existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
    column_statements = {
        "audit_status": (
            "ALTER TABLE maintenance_records "
            "ADD COLUMN audit_status VARCHAR(20) NOT NULL DEFAULT 'pending'"
        ),
        "auditor_id": "ALTER TABLE maintenance_records ADD COLUMN auditor_id INT NULL",
        "audit_time": "ALTER TABLE maintenance_records ADD COLUMN audit_time DATETIME NULL",
        "reject_reason": "ALTER TABLE maintenance_records ADD COLUMN reject_reason TEXT NULL",
    }

    for column_name, statement in column_statements.items():
        if column_name in existing_columns:
            continue
        with engine.begin() as connection:
            connection.execute(text(statement))
        print(f"已新增 maintenance_records.{column_name}")

    inspector = inspect(engine)
    existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    if "ix_maintenance_records_audit_status" not in existing_indexes:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE INDEX ix_maintenance_records_audit_status "
                    "ON maintenance_records (audit_status)"
                )
            )
        print("已创建 maintenance_records.audit_status 索引")

    inspector = inspect(engine)
    has_auditor_foreign_key = any(
        foreign_key.get("constrained_columns") == ["auditor_id"]
        and foreign_key.get("referred_table") == "users"
        for foreign_key in inspector.get_foreign_keys(table_name)
    )
    if not has_auditor_foreign_key:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE maintenance_records "
                    "ADD CONSTRAINT fk_maintenance_records_auditor_id_users "
                    "FOREIGN KEY (auditor_id) REFERENCES users(id)"
                )
            )
        print("已创建 maintenance_records.auditor_id 外键")


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
        ensure_maintenance_audit_columns()
        with Session(engine) as db:
            roles = init_roles(db)
            init_default_admin(db, roles["admin"])
            db.commit()
        print("数据库初始化完成")
    except (SQLAlchemyError, RuntimeError) as exc:
        print(f"数据库初始化失败：{exc}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
