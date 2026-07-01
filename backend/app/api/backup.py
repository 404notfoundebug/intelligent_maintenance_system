import json
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user, require_roles
from app.core.database import Base, get_db, engine
from app.models.user import User

router = APIRouter(prefix="/api/backup", tags=["backup"])


@router.post("/export")
def export_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    """导出所有表数据为 JSON"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        backup_data = {}

        for table_name in tables:
            # 跳过审计日志表（太大了）
            if table_name == "audit_logs":
                continue
            # 使用原生 SQL 查询
            result = db.execute(text(f"SELECT * FROM `{table_name}`"))
            columns = list(result.keys())
            rows = []
            for row in result.fetchall():
                row_dict = {}
                for col_name, val in zip(columns, row):
                    if isinstance(val, (bytes,)):
                        row_dict[col_name] = val.hex() if val else None
                    elif hasattr(val, 'isoformat'):
                        row_dict[col_name] = val.isoformat()
                    else:
                        row_dict[col_name] = val
                rows.append(row_dict)
            backup_data[table_name] = rows

        return JSONResponse(content={
            "code": 200,
            "message": "success",
            "data": backup_data,
        })
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))


@router.post("/import")
def import_backup(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    """从 JSON 文件恢复数据"""
    if not file.filename or not file.filename.endswith('.json'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请上传 .json 备份文件")

    try:
        content = file.file.read()
        backup_data = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件格式错误，无法解析 JSON")

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    imported = 0
    errors = []

    for table_name, rows in backup_data.items():
        if not isinstance(rows, list):
            continue
        if table_name not in existing_tables:
            errors.append(f"表 '{table_name}' 不存在，已跳过")
            continue

        if not rows:
            continue

        columns = list(rows[0].keys())
        placeholders = ", ".join([f":{col}" for col in columns])
        col_names = ", ".join([f"`{col}`" for col in columns])

        try:
            for row in rows:
                db.execute(
                    text(f"INSERT IGNORE INTO `{table_name}` ({col_names}) VALUES ({placeholders})"),
                    row,
                )
            db.commit()
            imported += len(rows)
        except SQLAlchemyError as exc:
            db.rollback()
            errors.append(f"导入表 '{table_name}' 失败: {exc}")

    return {
        "code": 200,
        "message": f"成功导入 {imported} 条记录" + (f"，{len(errors)} 个错误" if errors else ""),
        "data": {"imported": imported, "errors": errors},
    }
