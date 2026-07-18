"""本地 MySQL 连通性和结构检查脚本。"""
import sys

from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError

import app.models  # noqa: F401 - 导入全部模型以注册 SQLAlchemy metadata
from app.core.config import settings
from app.core.database import Base, check_database_connection, engine


def main() -> int:
    print("=" * 50)
    print("  本地 MySQL 数据库检查")
    print("=" * 50)

    ok, message = check_database_connection()
    print("\n[1] 基础连接 (SELECT 1)")
    print(f"    状态: {'成功' if ok else '失败'}")
    print(f"    详情: {message}")
    if not ok or engine is None or not settings.database_url:
        return 1

    url = make_url(settings.database_url)
    is_local = (url.host or "").lower() in {"localhost", "127.0.0.1", "::1"}
    print("\n[2] 连接目标")
    print(f"    驱动: {url.drivername}")
    print(f"    主机: {url.host}:{url.port or 3306}")
    print(f"    数据库: {url.database}")
    print(f"    本地连接: {'是' if is_local else '否'}")
    if not is_local:
        return 1

    try:
        with engine.connect() as connection:
            version = connection.execute(text("SELECT VERSION()")).scalar()
            charset = connection.execute(text("SELECT @@character_set_database")).scalar()
        print("\n[3] 数据库信息")
        print(f"    版本: {version}")
        print(f"    字符集: {charset}")

        inspector = inspect(engine)
        database_tables = set(inspector.get_table_names())
        model_tables = set(Base.metadata.tables)
        missing_tables = sorted(model_tables - database_tables)
        extra_tables = sorted(database_tables - model_tables)
        column_issues: list[str] = []

        for table_name in sorted(model_tables & database_tables):
            model_columns = set(Base.metadata.tables[table_name].columns.keys())
            database_columns = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            missing_columns = sorted(model_columns - database_columns)
            if missing_columns:
                column_issues.append(f"{table_name}: 缺少 {', '.join(missing_columns)}")

        print("\n[4] 表结构")
        print(f"    模型表数量: {len(model_tables)}")
        print(f"    数据库表数量: {len(database_tables)}")
        print(f"    缺少表: {', '.join(missing_tables) if missing_tables else '无'}")
        print(f"    额外表: {', '.join(extra_tables) if extra_tables else '无'}")
        print(f"    字段问题: {'; '.join(column_issues) if column_issues else '无'}")

        if missing_tables or column_issues:
            print("\n检查失败：请先执行 python -m app.init_db 完成本地数据库迁移")
            return 1

        with engine.connect() as connection:
            roles = connection.execute(text("SELECT COUNT(*) FROM roles")).scalar()
            users = connection.execute(text("SELECT COUNT(*) FROM users")).scalar()
        print("\n[5] 基础数据")
        print(f"    角色: {roles} 条")
        print(f"    用户: {users} 条")
    except SQLAlchemyError as exc:
        print(f"\n检查失败: {exc}")
        return 1

    print("\n本地 MySQL 连接和表结构检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
