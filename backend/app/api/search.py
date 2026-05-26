from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["search"])


def success(data: dict | list | None = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data or {}}


@router.post("", response_model=SearchResponse)
def search_knowledge(
    payload: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        results = SearchService.search(
            db=db,
            query=payload.query,
            top_k=payload.top_k,
            document_type=payload.document_type,
            file_id=payload.file_id,
        )
        return success(
            data={
                "query": payload.query,
                "total": len(results),
                "results": [item.to_dict() for item in results],
            }
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库查询失败：{exc}",
        ) from exc
