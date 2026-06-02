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
- `POST /api/devices`
- `GET /api/devices`
- `GET /api/devices/{device_id}`
- `PUT /api/devices/{device_id}`
- `DELETE /api/devices/{device_id}`
- `POST /api/inspections/templates`
- `GET /api/inspections/templates`
- `GET /api/inspections/templates/{template_id}`
- `PUT /api/inspections/templates/{template_id}`
- `DELETE /api/inspections/templates/{template_id}`
- `POST /api/inspections/orders`
- `GET /api/inspections/orders`
- `GET /api/inspections/orders/{order_id}`
- `PUT /api/inspections/orders/{order_id}/start`
- `PUT /api/inspections/orders/{order_id}/steps/{step_id}`
- `POST /api/inspections/orders/{order_id}/steps/{step_id}/photo`
- `PUT /api/inspections/orders/{order_id}/complete`
- `DELETE /api/inspections/orders/{order_id}`
- `POST /api/maintenance/records/from-order/{order_id}`
- `GET /api/maintenance/records`
- `GET /api/maintenance/records/{record_id}`
- `GET /api/maintenance/records/{record_id}/report`
- `DELETE /api/maintenance/records/{record_id}`
- `POST /api/faults`
- `POST /api/faults/{fault_id}/images`
- `GET /api/faults`
- `GET /api/faults/{fault_id}`
- `PUT /api/faults/{fault_id}/status`
- `POST /api/faults/{fault_id}/images/{image_id}/analyze`
- `POST /api/faults/{fault_id}/repair-advice`
- `DELETE /api/faults/{fault_id}`
- `POST /api/cases`
- `GET /api/cases`
- `GET /api/cases/{case_id}`
- `PUT /api/cases/{case_id}`
- `POST /api/cases/{case_id}/audit`
- `DELETE /api/cases/{case_id}`
- `GET /api/cases/{case_id}/audit-records`
- `GET /api/dashboard/summary`
- `GET /api/dashboard/device-status`
- `GET /api/dashboard/fault-status`
- `GET /api/dashboard/order-status`
- `GET /api/dashboard/case-status`
- `GET /api/dashboard/recent-faults`
- `GET /api/dashboard/recent-orders`
- `GET /api/dashboard/recent-maintenance-records`
- `GET /api/dashboard/monthly-trend`
- `GET /api/files/view`
- `GET /api/files/download`
- `POST /api/search`
- `POST /api/qa/repair-advice`

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

## RAG检修建议接口测试

本模块会先调用 `/api/search` 从 `knowledge_chunks` 检索相关片段，再将检索上下文提交给 OpenAI 兼容格式的大模型服务生成检修建议。不会使用 faiss、chromadb、torch、CUDA 等重依赖。

安装依赖：

```powershell
pip install -r requirements.txt
```

初始化数据库：

```powershell
python -m app.init_db
```

配置 `.env`：

```env
LLM_API_KEY=你的API Key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

也可以使用其他兼容 OpenAI 格式的大模型服务。

启动服务：

```powershell
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

确保已经上传知识库文档，并且 `/api/search` 能检索到结果。

测试接口：

```text
POST /api/qa/repair-advice
```

请求示例：

```json
{
  "device_name": "曳引电梯",
  "device_model": "TX-1000",
  "fault_description": "电梯停在层站，不关门",
  "top_k": 5
}
```

返回示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "record_id": 1,
    "answer": "...",
    "references": [
      {
        "chunk_id": 1,
        "file_id": 1,
        "source_file_name": "test_elevator.txt",
        "document_type": "repair_manual",
        "chunk_index": 0,
        "score": 26.46
      }
    ]
  }
}
```

如果未配置大模型参数，接口会返回明确错误：

```text
大模型API未配置，请检查LLM_API_KEY、LLM_BASE_URL、LLM_MODEL
```

## 设备管理接口测试

设备管理模块用于维护电梯、扶梯、自动人行道等设备台账，后续故障上报、点检工单、维保记录和检修建议都可以关联具体设备。

安装依赖：

```powershell
pip install -r requirements.txt
```

初始化数据库：

```powershell
python -m app.init_db
```

启动服务：

```powershell
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

新增设备：

```text
POST /api/devices
```

请求示例：

```json
{
  "device_name": "1号楼客梯",
  "device_code": "ELV-001",
  "device_type": "traction_elevator",
  "device_model": "TX-1000",
  "manufacturer": "某某电梯有限公司",
  "installation_location": "1号楼东侧",
  "maintenance_company": "某某维保公司",
  "responsible_person": "张三",
  "contact_phone": "13800000000",
  "status": "normal",
  "remark": "测试设备"
}
```

设备列表：

```text
GET /api/devices?page=1&page_size=10
```

支持查询参数：

- `keyword`：按设备名称、设备编号、安装位置模糊查询
- `device_type`：设备类型过滤，支持 `traction_elevator`、`hydraulic_elevator`、`escalator`、`moving_walkway`
- `status`：设备状态过滤，支持 `normal`、`maintenance`、`fault`、`disabled`

设备详情：

```text
GET /api/devices/{device_id}
```

修改设备：

```text
PUT /api/devices/{device_id}
```

删除设备：

```text
DELETE /api/devices/{device_id}
```

权限说明：

- `admin`：可以新增、查询、修改、删除设备。
- `auditor`：可以新增、查询、修改设备。
- `worker`：只能查询设备。

## 点检模板与点检工单接口测试

点检模块用于维护标准化点检模板，并根据具体设备和模板生成点检工单。创建工单时，系统会自动复制模板步骤，维保人员可逐项填写检查结果，全部步骤填写后才能完成工单。

安装依赖：

```powershell
pip install -r requirements.txt
```

初始化数据库：

```powershell
python -m app.init_db
```

启动服务：

```powershell
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

确保已经有一台设备：

```text
GET /api/devices
```

创建点检模板：

```text
POST /api/inspections/templates
```

请求示例：

```json
{
  "template_name": "曳引电梯月度点检模板",
  "device_type": "traction_elevator",
  "inspection_type": "monthly",
  "description": "适用于曳引电梯的月度维保点检",
  "is_active": true,
  "steps": [
    {
      "step_order": 1,
      "area": "机房",
      "item_name": "控制柜检查",
      "item_content": "检查控制柜运行状态、报警信息和接线情况",
      "standard": "控制柜无异常报警，接线无松动",
      "required_photo": true,
      "required_remark": false
    },
    {
      "step_order": 2,
      "area": "层站",
      "item_name": "层门检查",
      "item_content": "检查层门开关是否顺畅，门锁触点是否正常",
      "standard": "层门开关顺畅，门锁触点可靠",
      "required_photo": false,
      "required_remark": false
    }
  ]
}
```

查询模板：

```text
GET /api/inspections/templates
GET /api/inspections/templates/{template_id}
```

创建点检工单：

```text
POST /api/inspections/orders
```

请求示例：

```json
{
  "device_id": 1,
  "template_id": 1,
  "order_name": "1号楼客梯月度点检工单",
  "assigned_to": 1,
  "remark": "测试工单"
}
```

查看工单详情：

```text
GET /api/inspections/orders/{order_id}
```

开始工单：

```text
PUT /api/inspections/orders/{order_id}/start
```

填写步骤结果：

```text
PUT /api/inspections/orders/{order_id}/steps/{step_id}
```

请求示例：

```json
{
  "result": "normal",
  "remark": "检查正常",
  "photo_path": ""
}
```

完成工单：

```text
PUT /api/inspections/orders/{order_id}/complete
```

删除工单：

```text
DELETE /api/inspections/orders/{order_id}
```

权限说明：

- `admin`：可以管理模板和全部工单。
- `auditor`：可以创建、修改模板，创建、查看、处理和删除工单。
- `worker`：只能查看、创建和处理分配给自己的工单，不能管理模板，不能删除工单。

## 维保记录与自检报告接口测试

维保记录模块用于将已完成的点检工单转化为正式维保记录，并生成结构化自检报告正文。当前版本先返回文本内容，为后续 PDF/Word 导出和前端报告展示预留数据基础。

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

初始化数据库：

```powershell
python -m app.init_db
```

启动服务：

```powershell
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

确保已有一个 `completed` 状态的点检工单。如果没有，先按顺序完成：

- 创建设备
- 创建点检模板
- 创建点检工单
- start 工单
- 填写所有工单步骤
- complete 工单

根据工单生成维保记录：

```text
POST /api/maintenance/records/from-order/{order_id}
```

查询维保记录列表：

```text
GET /api/maintenance/records
```

支持查询参数：

- `keyword`：按设备名称、设备编号、记录编号模糊查询
- `device_id`：按设备过滤
- `inspection_type`：按点检类型过滤

查看维保记录详情：

```text
GET /api/maintenance/records/{record_id}
```

查看自检报告正文：

```text
GET /api/maintenance/records/{record_id}/report
```

删除维保记录：

```text
DELETE /api/maintenance/records/{record_id}
```

权限说明：

- `admin`：可以生成、查看、删除所有维保记录。
- `auditor`：可以生成和查看所有维保记录。
- `worker`：只能生成和查看分配给自己的工单对应的维保记录。

## 故障上报与图片识别接口测试

故障上报模块用于记录现场故障现象、上传故障图片，并通过 OpenAI 兼容的视觉大模型识别图片中的故障码、部件状态和可见异常。图片识别结果可以与文字故障描述一起进入 RAG 检修建议生成流程。

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

初始化数据库：

```powershell
python -m app.init_db
```

配置 `.env`：

```env
VISION_API_KEY=你的视觉模型API Key
VISION_BASE_URL=你的视觉模型OpenAI兼容地址
VISION_MODEL=你的视觉模型名称
```

如果 `VISION_API_KEY` 为空，系统会尝试复用 `LLM_API_KEY`。如果视觉模型未配置，故障上报和图片上传仍可正常使用，只有图片识别接口会返回明确配置错误。

启动服务：

```powershell
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

创建故障上报：

```text
POST /api/faults
```

请求示例：

```json
{
  "device_id": 1,
  "device_name": "1号楼客梯",
  "device_model": "TX-1000",
  "fault_description": "电梯停在层站，不关门",
  "fault_code": "",
  "location": "1号楼东侧层站"
}
```

上传故障图片：

```text
POST /api/faults/{fault_id}/images
```

表单参数：

- `file`：图片文件，支持 `jpg`、`jpeg`、`png`、`webp`
- `image_type`：支持 `fault_code`、`control_cabinet`、`door_system`、`escalator_part`、`other`

查看故障详情：

```text
GET /api/faults/{fault_id}
```

识别故障图片：

```text
POST /api/faults/{fault_id}/images/{image_id}/analyze
```

基于故障记录生成检修建议：

```text
POST /api/faults/{fault_id}/repair-advice
```

更新故障状态：

```text
PUT /api/faults/{fault_id}/status
```

请求示例：

```json
{
  "status": "processing"
}
```

删除故障记录：

```text
DELETE /api/faults/{fault_id}
```

权限说明：

- `admin`：可以创建、查看、上传图片、识别图片、生成建议、更新状态和删除所有故障记录。
- `auditor`：可以创建、查看、上传图片、识别图片、生成建议和更新状态。
- `worker`：只能查看和操作自己提交的故障记录，不能删除故障记录。

## 检修案例审核入库接口测试

检修案例模块用于将现场故障处理经验沉淀为结构化案例。案例提交后由管理员或审核员审核，审核通过后会自动写入 `knowledge_chunks`，并可被 `/api/search` 检索，用于后续 RAG 检修建议生成。

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

初始化数据库：

```powershell
python -m app.init_db
```

启动服务：

```powershell
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

提交检修案例：

```text
POST /api/cases
```

请求示例：

```json
{
  "device_id": 1,
  "fault_report_id": 3,
  "maintenance_record_id": 1,
  "title": "电梯停在层站不关门故障处理案例",
  "device_name": "1号楼客梯",
  "device_type": "traction_elevator",
  "fault_description": "电梯停在层站，不关门",
  "fault_reason": "门锁回路接触不良，控制柜显示门锁相关异常",
  "repair_process": "检查门区安全状态，排查光幕、门机控制器和门锁触点，重新紧固门锁接线并复测运行状态。",
  "repair_result": "处理后电梯开关门恢复正常，连续运行测试未复现故障。",
  "tools_used": "万用表、绝缘手套、螺丝刀",
  "safety_notes": "检修前应设置警示标识，确认电梯处于安全检修状态。"
}
```

查询案例列表：

```text
GET /api/cases
```

查看案例详情：

```text
GET /api/cases/{case_id}
```

审核通过案例：

```text
POST /api/cases/{case_id}/audit
```

请求示例：

```json
{
  "action": "approve",
  "comment": "审核通过"
}
```

查看审核记录：

```text
GET /api/cases/{case_id}/audit-records
```

测试知识库检索：

```text
POST /api/search
```

请求示例：

```json
{
  "query": "电梯停在层站不关门",
  "top_k": 5
}
```

审核通过后，检索结果中应能看到刚刚入库的检修案例内容。

权限说明：

- `admin`：可以提交、查看、修改、审核和删除所有案例。
- `auditor`：可以提交、查看、修改和审核所有案例。
- `worker`：只能提交、查看和修改自己提交且未审核通过的案例，不能审核和删除案例。

## Dashboard首页统计接口测试

Dashboard 模块用于给前端首页提供设备、故障、点检工单、维保记录、知识库和检修案例的运行概览。该模块不新增业务表，只从已有数据表中做轻量统计。

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

初始化数据库：

```powershell
python -m app.init_db
```

启动服务：

```powershell
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

测试首页综合统计：

```text
GET /api/dashboard/summary
```

测试设备状态统计：

```text
GET /api/dashboard/device-status
```

测试故障状态统计：

```text
GET /api/dashboard/fault-status
```

测试工单状态统计：

```text
GET /api/dashboard/order-status
```

测试案例状态统计：

```text
GET /api/dashboard/case-status
```

测试最近数据：

```text
GET /api/dashboard/recent-faults
GET /api/dashboard/recent-orders
GET /api/dashboard/recent-maintenance-records
```

测试趋势数据：

```text
GET /api/dashboard/monthly-trend
```

权限说明：

- `admin`、`auditor`：可以查看全部统计数据。
- `worker`：仅查看与自己相关的数据，包括自己提交的故障、分配给自己的点检工单、相关维保记录和自己提交的检修案例。

## 文件访问与点检照片上传测试

文件访问模块用于给前端提供上传文件预览和下载能力，并支持在点检工单步骤中上传现场照片。所有文件访问路径都会限制在 `.env` 中配置的 `UPLOAD_DIR` 下，防止路径穿越。

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

初始化数据库：

```powershell
python -m app.init_db
```

启动服务：

```powershell
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

确保已有一个点检工单和工单步骤：

```text
GET /api/inspections/orders/{order_id}
```

上传点检步骤照片：

```text
POST /api/inspections/orders/{order_id}/steps/{step_id}/photo
```

请求参数：

- `file`：图片文件，支持 `jpg`、`jpeg`、`png`、`webp`

返回示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "order_id": 1,
    "step_id": 1,
    "photo_path": "inspections/1/uuid_xxx.jpg",
    "photo_url": "/api/files/view?path=inspections/1/uuid_xxx.jpg"
  }
}
```

查看工单详情，确认 `step.photo_path` 已更新：

```text
GET /api/inspections/orders/{order_id}
```

预览图片：

```text
GET /api/files/view?path=返回的photo_path
```

下载图片：

```text
GET /api/files/download?path=返回的photo_path
```

权限说明：

- `admin`、`auditor`：可以上传所有点检工单步骤照片。
- `worker`：只能上传分配给自己的工单步骤照片。
- 文件访问接口第一版允许所有登录用户访问 `UPLOAD_DIR` 下的安全路径文件。
