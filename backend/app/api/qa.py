from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.qa import RepairAdviceRequest, RepairAdviceResponse
from app.services.qa_service import QAService

router = APIRouter(prefix="/api/qa", tags=["qa"])


def success(data: dict | list | None = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data or {}}


@router.post("/repair-advice", response_model=RepairAdviceResponse)
def generate_repair_advice(
    payload: RepairAdviceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        record, references = QAService.generate_repair_advice(
            db=db,
            user_id=current_user.id,
            device_name=payload.device_name,
            device_model=payload.device_model,
            fault_description=payload.fault_description,
            top_k=payload.top_k,
        )
        return success(
            data={
                "record_id": record.id,
                "answer": record.answer,
                "references": references,
            }
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库操作失败：{exc}",
        ) from exc
