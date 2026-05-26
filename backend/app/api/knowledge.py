from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.knowledge import KnowledgeFile
from app.models.user import User
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


def success(data: dict | list | None = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data or {}}


def file_to_item(file: KnowledgeFile) -> dict:
    return {
        "id": file.id,
        "original_filename": file.original_filename,
        "stored_filename": file.stored_filename,
        "file_type": file.file_type,
        "document_type": file.document_type,
        "file_size": file.file_size,
        "parse_status": file.parse_status,
        "parse_message": file.parse_message,
        "uploaded_by": file.uploaded_by,
        "created_at": file.created_at,
        "updated_at": file.updated_at,
    }


@router.post("/upload")
def upload_knowledge_file(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor"])),
):
    try:
        knowledge_file, chunk_count = KnowledgeService.create_file_and_chunks(
            db=db,
            file=file,
            document_type=document_type,
            uploaded_by=current_user.id,
        )
        message = "success" if knowledge_file.parse_status == "parsed" else knowledge_file.parse_message
        return success(
            message=message or "success",
            data={
                "file_id": knowledge_file.id,
                "original_filename": knowledge_file.original_filename,
                "file_type": knowledge_file.file_type,
                "parse_status": knowledge_file.parse_status,
                "chunk_count": chunk_count,
                "parse_message": knowledge_file.parse_message,
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库操作失败：{exc}",
        ) from exc


@router.get("/files")
def list_knowledge_files(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    document_type: str | None = None,
    parse_status: str | None = None,
    keyword: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        total, items = KnowledgeService.list_files(
            db=db,
            page=page,
            page_size=page_size,
            document_type=document_type,
            parse_status=parse_status,
            keyword=keyword,
        )
        return success(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [file_to_item(item) for item in items],
            }
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库查询失败：{exc}",
        ) from exc


@router.get("/files/{file_id}")
def get_knowledge_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    knowledge_file = KnowledgeService.get_file(db, file_id)
    if knowledge_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库文件不存在")

    chunk_count = KnowledgeService.count_chunks(db, file_id)
    data = file_to_item(knowledge_file)
    data.update({"file_path": knowledge_file.file_path, "chunk_count": chunk_count})
    return success(data=data)


@router.get("/files/{file_id}/chunks")
def list_knowledge_chunks(
    file_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    knowledge_file = KnowledgeService.get_file(db, file_id)
    if knowledge_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库文件不存在")

    try:
        total, chunks = KnowledgeService.list_chunks(db, file_id, page, page_size)
        return success(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [
                    {
                        "id": chunk.id,
                        "file_id": chunk.file_id,
                        "chunk_index": chunk.chunk_index,
                        "title": chunk.title,
                        "content": chunk.content,
                        "metadata_json": chunk.metadata_json,
                        "created_at": chunk.created_at,
                        "updated_at": chunk.updated_at,
                    }
                    for chunk in chunks
                ],
            }
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库查询失败：{exc}",
        ) from exc


@router.delete("/files/{file_id}")
def delete_knowledge_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    knowledge_file = KnowledgeService.get_file(db, file_id)
    if knowledge_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库文件不存在")

    try:
        KnowledgeService.delete_file(db, knowledge_file)
        return success(data={"file_id": file_id}, message="删除成功")
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库删除失败：{exc}",
        ) from exc
