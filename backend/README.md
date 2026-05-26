# 智能电梯扶梯维保系统后端

本项目是“面向电梯扶梯维保场景的多模态知识检索与标准化作业辅助系统”的后端基础框架，基于 FastAPI、SQLAlchemy、MySQL 和 JWT 构建。

## 快速启动

Windows：

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Linux / 银河麒麟服务器：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

程序实际读取 `.env`，不会读取 `.env.example`。

## 配置数据库

确认 `.env` 中 `DATABASE_URL` 正确：

```env
DATABASE_URL=mysql+pymysql://root:your_mysql_password@localhost:3306/intelligent_maintenance
```

在 MySQL 中创建数据库：

```sql
create database if not exists intelligent_maintenance
default character set utf8mb4
collate utf8mb4_unicode_ci;
```

## 初始化数据库

初始化脚本会创建所有表，包括 `roles`、`users`、`knowledge_files`、`knowledge_chunks`，并初始化角色和默认管理员。

```powershell
python -m app.init_db
```

默认账号：

```text
admin / admin123456
```

初始化脚本可以重复执行，已有角色和管理员不会重复插入。

## 启动服务

```powershell
uvicorn main:app --reload
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## 健康检查

服务状态：

```powershell
curl http://127.0.0.1:8000/api/health
```

数据库连接：

```powershell
curl http://127.0.0.1:8000/api/health/db
```

`/api/health` 不依赖数据库；数据库未配置或连接失败不会影响 FastAPI 服务启动。

## 登录测试

Swagger 右上角点击 `Authorize`，使用默认账号登录：

```text
username: admin
password: admin123456
```

JSON 登录接口：

```text
POST /api/auth/login-json
```

请求体：

```json
{
  "username": "admin",
  "password": "admin123456"
}
```

获取当前用户：

```text
GET /api/auth/me
Authorization: Bearer <access_token>
```

## 知识库文档上传测试

确认 `.env` 中包含上传目录配置：

```env
UPLOAD_DIR=./uploads
```

测试流程：

```powershell
pip install -r requirements.txt
python -m app.init_db
uvicorn main:app --reload
```

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

先点击右上角 `Authorize` 登录：

```text
username: admin
password: admin123456
```

上传文档：

```text
POST /api/knowledge/upload
```

参数：

- `file`：上传 `txt`、`pdf` 或 `docx` 文档
- `document_type`：文档类型，可选值：
  - `maintenance_standard`
  - `repair_manual`
  - `fault_case`
  - `inspection_template`
  - `maintenance_record_template`

查看文件列表：

```text
GET /api/knowledge/files
```

查看文件详情：

```text
GET /api/knowledge/files/{file_id}
```

查看解析后的文本块：

```text
GET /api/knowledge/files/{file_id}/chunks
```

删除知识库文件：

```text
DELETE /api/knowledge/files/{file_id}
```

权限说明：

- `admin`：上传、查看、删除知识库文档
- `auditor`：上传、查看知识库文档
- `worker`：查看知识库文档

## 当前接口

- `GET /api/health`
- `GET /api/health/db`
- `POST /api/auth/login`
- `POST /api/auth/login-json`
- `GET /api/auth/me`
- `POST /api/knowledge/upload`
- `GET /api/knowledge/files`
- `GET /api/knowledge/files/{file_id}`
- `GET /api/knowledge/files/{file_id}/chunks`
- `DELETE /api/knowledge/files/{file_id}`
- `POST /api/search`

## 知识库检索测试

本模块只实现传统轻量检索，不调用大模型，也不生成最终检修建议。当前检索逻辑基于 `jieba` 中文分词、关键词匹配、标题/正文权重、完整短语命中加分和文档类型轻微加权。

测试流程：

```powershell
pip install -r requirements.txt
python -m app.init_db
uvicorn main:app --reload
```

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

点击右上角 `Authorize` 登录：

```text
username: admin
password: admin123456
```

确保已经上传过知识库文档，并且 `knowledge_chunks` 表中有数据。

测试接口：

```text
POST /api/search
```

请求示例：

```json
{
  "query": "电梯停在层站，不关门",
  "top_k": 5
}
```

可选过滤参数：

```json
{
  "query": "控制柜显示E35故障码",
  "top_k": 5,
  "document_type": "repair_manual",
  "file_id": null
}
```

返回示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "query": "电梯停在层站，不关门",
    "total": 1,
    "results": [
      {
        "chunk_id": 1,
        "file_id": 1,
        "source_file_name": "test_elevator.txt",
        "document_type": "repair_manual",
        "chunk_index": 0,
        "title": null,
        "content": "...",
        "score": 12.5
      }
    ]
  }
}
```

权限说明：

- `admin`、`worker`、`auditor` 均可使用知识库检索。
- 接口必须携带登录后的 Bearer Token。
