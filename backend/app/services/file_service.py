from pathlib import Path, PurePosixPath
from uuid import uuid4

from fastapi import UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings


SUPPORTED_IMAGE_TYPES = {"jpg", "jpeg", "png", "webp"}
IMAGE_MEDIA_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


class FileService:
    @staticmethod
    def upload_root() -> Path:
        return Path(settings.upload_dir).resolve()

    @staticmethod
    def validate_safe_path(relative_path: str) -> Path:
        if not relative_path or not relative_path.strip():
            raise ValueError("非法文件路径")

        normalized_text = relative_path.replace("\\", "/")
        if ":" in normalized_text:
            raise ValueError("非法文件路径")
        normalized_path = PurePosixPath(normalized_text)
        if normalized_path.is_absolute() or ".." in normalized_path.parts:
            raise ValueError("非法文件路径")

        upload_root = FileService.upload_root()
        target_path = (upload_root / Path(*normalized_path.parts)).resolve()
        try:
            target_path.relative_to(upload_root)
        except ValueError as exc:
            raise ValueError("非法文件路径") from exc
        return target_path

    @staticmethod
    def get_file_response(relative_path: str, as_attachment: bool = False) -> FileResponse:
        file_path = FileService.validate_safe_path(relative_path)
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError("文件不存在")

        suffix = file_path.suffix.lower().lstrip(".")
        media_type = IMAGE_MEDIA_TYPES.get(suffix)
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=file_path.name if as_attachment else None,
        )

    @staticmethod
    def save_uploaded_image(file: UploadFile, sub_dir: str) -> tuple[str, int, str]:
        original_filename = Path(file.filename or "").name
        file_type = Path(original_filename).suffix.lower().lstrip(".")
        if file_type not in SUPPORTED_IMAGE_TYPES:
            raise ValueError("仅支持jpg、jpeg、png、webp图片")

        normalized_sub_dir = sub_dir.replace("\\", "/")
        if ":" in normalized_sub_dir:
            raise ValueError("非法文件路径")
        safe_sub_dir = PurePosixPath(normalized_sub_dir)
        if safe_sub_dir.is_absolute() or ".." in safe_sub_dir.parts:
            raise ValueError("非法文件路径")

        upload_root = FileService.upload_root()
        target_dir = (upload_root / Path(*safe_sub_dir.parts)).resolve()
        try:
            target_dir.relative_to(upload_root)
        except ValueError as exc:
            raise ValueError("非法文件路径") from exc
        target_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4().hex}_{original_filename}" if original_filename else f"{uuid4().hex}.{file_type}"
        target_path = (target_dir / stored_filename).resolve()
        try:
            target_path.relative_to(upload_root)
        except ValueError as exc:
            raise ValueError("非法文件路径") from exc

        try:
            with target_path.open("wb") as target:
                while chunk := file.file.read(1024 * 1024):
                    target.write(chunk)
        except OSError as exc:
            raise RuntimeError(f"图片保存失败：{exc}") from exc
        finally:
            file.file.close()

        relative_path = target_path.relative_to(upload_root).as_posix()
        return relative_path, target_path.stat().st_size, file_type

    @staticmethod
    def build_file_url(relative_path: str) -> str:
        return f"/api/files/view?path={relative_path}"
