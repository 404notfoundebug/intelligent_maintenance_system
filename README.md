# 面向电梯扶梯维保场景的多模态知识检索与标准化作业辅助系统

本项目面向电梯、扶梯日常维保和故障处置场景，建设一个集知识库管理、故障检索、智能检修建议生成、标准化点检与维保记录管理于一体的作业辅助系统。系统目标是帮助维保人员更快定位相关规程、手册和历史案例，生成可追溯、可复核的检修建议，并为后续维保闭环、审核与数据统计提供基础。

## 快速启动概览

克隆项目后，需要分别启动后端和前端。真实密钥和数据库连接只写在 `backend/.env` 中，不要提交到 Git。

后端：

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.init_db
uvicorn main:app --reload
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

默认后端地址：

```text
http://127.0.0.1:8000
```

默认前端开发地址：

```text
http://127.0.0.1:5173
```

默认管理员账号：

```text
admin / admin123456
```

## 项目目的

电梯和扶梯维保工作具有安全要求高、现场情况复杂、资料分散、经验依赖强等特点。传统维保过程中，工作人员往往需要在检修手册、维保规程、故障案例和历史记录中人工查找资料，效率较低，也不利于标准化管理。

本系统希望通过知识库检索与大模型辅助生成能力，将已有规程、故障案例、检修手册和点检模板组织起来，为持证维保人员提供面向现场问题的辅助建议。系统不替代人工判断，而是提供基于知识库的参考信息，并强调安全规范和人工复核。

## 核心功能

系统建议包含以下最终模块：

1. 用户登录与角色管理
2. 电梯/扶梯设备管理
3. 检修知识库管理
4. 多模态故障检索
5. 智能检修建议生成
6. 标准化点检工单管理
7. 维保记录与自检报告生成
8. 故障案例审核入库
9. 知识图谱可视化
10. 系统数据统计

当前后端已实现的基础能力包括：

- FastAPI 后端基础框架
- 本地 MySQL 8.0 + SQLAlchemy 数据库连接
- 用户登录与 JWT 认证
- `admin`、`worker`、`auditor` 三类角色权限
- 知识库文档上传、解析、文本切分与入库
- 基于关键词和简单相似度的知识库检索接口
- 基于知识库检索结果的 RAG 检修建议生成接口

## 角色设计

| 角色 | 主要功能 |
| --- | --- |
| 管理员 | 用户管理、设备管理、知识库管理、系统数据维护 |
| 维保人员 | 标准化点检、故障上报、知识检索、查看检修建议、提交维保记录 |
| 审核员 | 审核检修案例、审核维保记录、管理知识入库质量 |

## 业务流程

典型使用流程如下：

1. 管理员或审核员上传检修手册、维保规程、故障案例等知识库文档。
2. 系统解析文档内容，将文本切分为知识片段并写入数据库。
3. 维保人员输入故障现象，例如“电梯停在层站，不关门”。
4. 系统从知识库中检索相关规程、手册和案例片段。
5. RAG 模块将检索结果作为上下文，调用兼容 OpenAI 格式的大模型 API。
6. 系统生成结构化检修建议，包括可能原因、检修步骤、工具检测项、安全注意事项和参考来源。
7. 维保人员结合现场情况进行人工复核和标准化作业记录。
8. 审核员对有价值的故障案例进行审核，并沉淀回知识库。

## 技术架构

当前项目后端采用轻量、可部署、易扩展的技术路线：

- Web 框架：FastAPI
- 数据库：本地 MySQL 8.0
- ORM：SQLAlchemy
- 认证方式：JWT
- 文档解析：TXT、PDF、DOCX
- 中文分词：jieba
- 检索方式：关键词匹配 + 简单相似度评分
- 大模型调用：OpenAI 兼容 API
- HTTP 客户端：httpx

系统暂不使用 `torch`、`faiss`、`chromadb`、`CUDA` 等重依赖，便于在 LoongArch + 银河麒麟等国产化服务器环境中部署。后续可在 `SearchService` 层平滑替换为 embedding 向量检索。

## 本地 MySQL 数据库配置

当前项目使用本机 MySQL 8.0，后端使用：

```text
SQLAlchemy + PyMySQL + mysql+pymysql://...
```

首次运行时，需要先创建本地业务库：

```sql
CREATE DATABASE IF NOT EXISTS intelligent_maintenance
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

然后在 `backend/.env` 中配置连接串：

```env
DATABASE_URL=mysql+pymysql://maintenance_app:your_mysql_password@127.0.0.1:3306/intelligent_maintenance?charset=utf8mb4
```

可以从模板复制：

```powershell
cd backend
copy .env.example .env
```

配置完成后初始化数据库：

```powershell
python -m app.init_db
```

初始化脚本会创建业务表、迁移旧库缺失的字段和外键、初始化默认角色和管理员，并且可以重复执行。更多说明见 [docs/local-mysql-setup.md](docs/local-mysql-setup.md)。

## 后端目录

```text
backend/
  app/
    api/          # FastAPI 路由
    core/         # 配置、数据库、安全相关能力
    models/       # SQLAlchemy 数据模型
    schemas/      # Pydantic 请求与响应模型
    services/     # 业务服务层
    utils/        # 通用工具
  main.py         # FastAPI 应用入口
  requirements.txt
  README.md       # 后端接口与测试说明
```

## 快速启动

进入后端目录：

```bash
cd backend
```

安装依赖：

```bash
pip install -r requirements.txt
```

配置 `.env`：

```env
DATABASE_URL=mysql+pymysql://maintenance_app:your_mysql_password@127.0.0.1:3306/intelligent_maintenance?charset=utf8mb4
LLM_API_KEY=你的API Key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

初始化数据库：

```bash
python -m app.init_db
```

启动服务：

```bash
uvicorn main:app --reload
```

访问接口文档：

```text
http://127.0.0.1:8000/docs
```

默认管理员账号：

```text
username: admin
password: admin123456
```

## 当前重点接口

- `POST /api/auth/login`
- `POST /api/auth/login-json`
- `GET /api/auth/me`
- `POST /api/knowledge/upload`
- `GET /api/knowledge/files`
- `GET /api/knowledge/files/{file_id}/chunks`
- `POST /api/search`
- `POST /api/qa/repair-advice`

## 知识库资料

已整理的公开电梯维保资料位于：

```text
docs/knowledge_sources/
```

建议上传分类：

```text
maintenance_standard_TSG_T5002_2017_elevator_maintenance_regulation.pdf
-> maintenance_standard

maintenance_standard_DB11_T418_2019_elevator_daily_maintenance.pdf
-> maintenance_standard

maintenance_standard_special_equipment_elevator_maintenance_safety_management.pdf
-> maintenance_standard

repair_manual_traction_elevator_maintenance_manual.pdf
-> repair_manual

repair_manual_elevator_maintenance_instruction.pdf
-> repair_manual

repair_manual_elevator_general_fault_troubleshooting_course_standard.pdf
-> repair_manual
```

## 后续规划

- 完善设备台账与设备型号管理
- 增加点检工单和维保记录闭环
- 增加故障案例审核入库流程
- 支持图片、语音等多模态故障信息输入
- 支持知识图谱可视化和关联检索
- 增加系统数据统计、维保质量分析和报表导出
- 在保持轻量部署的前提下，引入可选的向量检索能力

## 安全说明

本系统生成的检修建议仅作为辅助参考。电梯、扶梯检修应由具备资质的维保人员执行，现场作业必须遵守相关安全规范，并结合实际设备状态进行人工复核。

代码仓库安全规则：

- 不要提交真实 `.env`
- 不要提交数据库密码或 API Key
- `.gitignore` 已忽略 `.env`、`.env.*`、`uploads/`、`*.log`、虚拟环境、前端依赖和构建产物
- 只允许提交 `.env.example` 这类无密钥模板
- 如果本地数据库密码曾在截图或聊天中暴露，应立即重置密码并更新 `backend/.env`
