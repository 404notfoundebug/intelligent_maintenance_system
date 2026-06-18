"""数据库连通性检查脚本"""
import sys
sys.path.insert(0, ".")

from sqlalchemy import text
from app.core.database import engine, check_database_connection

print("=" * 50)
print("  数据库连通性检查")
print("=" * 50)

# 1. 基础连接
ok, msg = check_database_connection()
print(f"\n[1] 基础连接 (SELECT 1)")
print(f"    状态: {'✅ 成功' if ok else '❌ 失败'}")
print(f"    详情: {msg}")

if not ok:
    sys.exit(1)

# 2. 数据库信息
with engine.connect() as conn:
    print(f"\n[2] 数据库信息")
    version = conn.execute(text("SELECT VERSION()")).scalar()
    print(f"    版本: {version}")

    db_name = conn.execute(text("SELECT DATABASE()")).scalar()
    print(f"    当前库: {db_name}")

    charset = conn.execute(text("SELECT @@character_set_database")).scalar()
    print(f"    字符集: {charset}")

# 3. 表清单
with engine.connect() as conn:
    tables = conn.execute(text("SHOW TABLES")).fetchall()
    print(f"\n[3] 表清单 ({len(tables)} 张表)")
    for row in tables:
        print(f"    - {row[0]}")

# 4. 关键表数据量
with engine.connect() as conn:
    print(f"\n[4] 关键表数据量")
    for table_name in ["roles", "users", "devices", "inspection_orders", "inspection_templates", "maintenance_records", "fault_reports"]:
        try:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"    {table_name}: {count} 条")
        except Exception as e:
            print(f"    {table_name}: 查询失败 - {e}")

# 5. 默认管理员检查
with engine.connect() as conn:
    admin = conn.execute(text("SELECT id, username, real_name, is_active FROM users WHERE username = 'admin'")).fetchone()
    print(f"\n[5] 默认管理员")
    if admin:
        print(f"    ID: {admin[0]}, 用户名: {admin[1]}, 姓名: {admin[2]}, 启用: {admin[3]}")
    else:
        print(f"    ❌ 未找到 admin 用户")

# 6. 角色检查
with engine.connect() as conn:
    roles = conn.execute(text("SELECT id, name, description FROM roles")).fetchall()
    print(f"\n[6] 角色 ({len(roles)} 个)")
    for r in roles:
        print(f"    ID:{r[0]}  {r[1]}  ({r[2]})")

print(f"\n{'=' * 50}")
print("  检查完成")
print("=" * 50)
