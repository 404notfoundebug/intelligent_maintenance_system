# 本地 MySQL 8.0 配置

本项目固定使用本机 MySQL 8.0，后端通过 SQLAlchemy 和 PyMySQL 连接
`127.0.0.1:3306`。

## 1. 创建数据库和项目账户

使用 MySQL Workbench 或 MySQL 命令行，以管理员账户执行：

```sql
CREATE DATABASE IF NOT EXISTS intelligent_maintenance
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'maintenance_app'@'localhost'
  IDENTIFIED BY '请替换为本地密码';

GRANT ALL PRIVILEGES ON intelligent_maintenance.*
  TO 'maintenance_app'@'localhost';

FLUSH PRIVILEGES;
```

如果项目连接地址使用 `127.0.0.1`，而账户只能从 `localhost` 登录，可额外创建：

```sql
CREATE USER IF NOT EXISTS 'maintenance_app'@'127.0.0.1'
  IDENTIFIED BY '请替换为本地密码';

GRANT ALL PRIVILEGES ON intelligent_maintenance.*
  TO 'maintenance_app'@'127.0.0.1';
```

## 2. 配置后端

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

编辑 `.env`：

```env
DATABASE_URL=mysql+pymysql://maintenance_app:你的密码@127.0.0.1:3306/intelligent_maintenance?charset=utf8mb4
```

密码中的 `@`、`:`、`/` 等字符需要进行 URL 编码。

## 3. 初始化和迁移

```powershell
python -m app.init_db
```

初始化命令可以重复执行。它会创建缺失的表，补齐旧数据库缺少的字段、索引和外键，
并创建默认角色和管理员。

默认管理员：

```text
admin / admin123456
```

首次登录后应立即修改默认密码。

## 4. 验证

```powershell
python test_db_conn.py
```

通过后启动服务：

```powershell
uvicorn main:app --reload
```

数据库健康检查地址：

```text
http://127.0.0.1:8000/api/health/db
```
