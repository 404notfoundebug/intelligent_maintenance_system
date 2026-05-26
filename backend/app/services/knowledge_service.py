import re
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.knowledge import KnowledgeChunk, KnowledgeFile


SUPPORTED_FILE_TYPES = {"pdf", "txt", "docx"}
SUPPORTED_DOCUMENT_TYPES = {
    "maintenance_standard",
    "repair_manual",
    "fault_case",
    "inspection_template",
    "maintenance_record_template",
}


class KnowledgeService:
    @staticmethod
    def save_uploaded_file(file: UploadFile) -> tuple[Path, str, int]:
        original_filename = Path(file.filename or "").name
        file_type = Path(original_filename).suffix.lower().lstrip(".")
        if file_type not in SUPPORTED_FILE_TYPES:
            raise ValueError("仅支持 pdf、txt、docx 文件")

        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4().hex}.{file_type}"
        saved_path = upload_dir / stored_filename

        try:
            with saved_path.open("wb") as target:
                shutil.copyfileobj(file.file, target)
        except OSError as exc:
            raise RuntimeError(f"文件保存失败：{exc}") from exc
        finally:
            file.file.close()

        return saved_path, stored_filename, saved_path.stat().st_size

    @staticmethod
    def parse_document(file_path: Path, file_type: str) -> str:
        if file_type == "pdf":
            return KnowledgeService._parse_pdf(file_path)
        if file_type == "docx":
            return KnowledgeService._parse_docx(file_path)
        if file_type == "txt":
            return KnowledgeService._parse_txt(file_path)
        raise ValueError("不支持的文件类型")

    @staticmethod
    def _parse_pdf(file_path: Path) -> str:
        from pypdf import PdfReader

        reader = PdfReader(str(file_path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)

    @staticmethod
    def _parse_docx(file_path: Path) -> str:
        from docx import Document

        document = Document(str(file_path))
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(paragraphs)

    @staticmethod
    def _parse_txt(file_path: Path) -> str:
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="gbk")

    @staticmethod
    def split_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
        normalized = re.sub(r"\n{3,}", "\n\n", text).strip()
        if not normalized:
            return []

        chunks: list[str] = []
        start = 0
        text_length = len(normalized)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= text_length:
                break
            start = max(end - overlap, start + 1)

        return chunks

    @staticmethod
    def create_file_and_chunks(
        db: Session,
        file: UploadFile,
        document_type: str,
        uploaded_by: int,
    ) -> tuple[KnowledgeFile, int]:
        if document_type not in SUPPORTED_DOCUMENT_TYPES:
            raise ValueError("不支持的文档类型")

        original_filename = Path(file.filename or "").name
        saved_path, stored_filename, file_size = KnowledgeService.save_uploaded_file(file)
        file_type = saved_path.suffix.lower().lstrip(".")

        knowledge_file = KnowledgeFile(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=saved_path.as_posix(),
            file_type=file_type,
            document_type=document_type,
            file_size=file_size,
            parse_status="pending",
            parse_message="文件已上传，等待解析",
            uploaded_by=uploaded_by,
        )

        try:
            db.add(knowledge_file)
            db.flush()

            try:
                text = KnowledgeService.parse_document(saved_path, file_type)
                chunks = KnowledgeService.split_text(text)
                if not chunks:
                    raise ValueError("文档未解析出有效文本内容")

                for index, content in enumerate(chunks):
                    db.add(
                        KnowledgeChunk(
                            file_id=knowledge_file.id,
                            chunk_index=index,
                            title=None,
                            content=content,
                            metadata_json={"source": knowledge_file.original_filename},
                        )
                    )

                knowledge_file.parse_status = "parsed"
                knowledge_file.parse_message = f"解析成功，共生成 {len(chunks)} 个文本块"
                db.commit()
                db.refresh(knowledge_file)
                return knowledge_file, len(chunks)
            except Exception as exc:
                knowledge_file.parse_status = "failed"
                knowledge_file.parse_message = f"解析失败：{exc}"
                db.commit()
                db.refresh(knowledge_file)
                return knowledge_file, 0
        except SQLAlchemyError:
            db.rollback()
            try:
                if saved_path.exists() and saved_path.is_file():
                    saved_path.unlink()
            except OSError:
                pass
            raise

    @staticmethod
    def list_files(
        db: Session,
        page: int,
        page_size: int,
        document_type: str | None = None,
        parse_status: str | None = None,
        keyword: str | None = None,
    ) -> tuple[int, list[KnowledgeFile]]:
        conditions = []
        if document_type:
            conditions.append(KnowledgeFile.document_type == document_type)
        if parse_status:
            conditions.append(KnowledgeFile.parse_status == parse_status)
        if keyword:
            conditions.append(KnowledgeFile.original_filename.like(f"%{keyword}%"))

        count_stmt = select(func.count()).select_from(KnowledgeFile)
        query_stmt = select(KnowledgeFile).order_by(KnowledgeFile.created_at.desc())
        if conditions:
            count_stmt = count_stmt.where(*conditions)
            query_stmt = query_stmt.where(*conditions)

        total = db.scalar(count_stmt) or 0
        items = db.scalars(query_stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return total, list(items)

    @staticmethod
    def get_file(db: Session, file_id: int) -> KnowledgeFile | None:
        return db.get(KnowledgeFile, file_id)

    @staticmethod
    def count_chunks(db: Session, file_id: int) -> int:
        return db.scalar(
            select(func.count()).select_from(KnowledgeChunk).where(KnowledgeChunk.file_id == file_id)
        ) or 0

    @staticmethod
    def list_chunks(
        db: Session,
        file_id: int,
        page: int,
        page_size: int,
    ) -> tuple[int, list[KnowledgeChunk]]:
        total = KnowledgeService.count_chunks(db, file_id)
        stmt = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.file_id == file_id)
            .order_by(KnowledgeChunk.chunk_index.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return total, list(db.scalars(stmt).all())

    @staticmethod
    def delete_file(db: Session, knowledge_file: KnowledgeFile) -> None:
        file_path = Path(knowledge_file.file_path)
        try:
            db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.file_id == knowledge_file.id))
            db.delete(knowledge_file)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
        except OSError as exc:
            raise RuntimeError(f"数据库记录已删除，但本地文件删除失败：{exc}") from exc
