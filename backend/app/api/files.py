from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse

from app.api.auth import get_current_active_user
from app.models.user import User
from app.services.file_service import FileService

router = APIRouter(prefix="/api/files", tags=["files"])


def build_file_response(path: str, as_attachment: bool) -> FileResponse:
    try:
        return FileService.get_file_response(path, as_attachment=as_attachment)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/view")
def view_file(
    path: str = Query(...),
    current_user: User = Depends(get_current_active_user),
):
    return build_file_response(path, as_attachment=False)


@router.get("/download")
def download_file(
    path: str = Query(...),
    current_user: User = Depends(get_current_active_user),
):
    return build_file_response(path, as_attachment=True)
