import re
from dataclasses import dataclass

import jieba
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeChunk, KnowledgeFile


DOCUMENT_TYPE_WEIGHTS = {
    "repair_manual": 1.08,
    "fault_case": 1.06,
    "maintenance_standard": 1.04,
    "inspection_template": 1.02,
    "maintenance_record_template": 1.01,
}


@dataclass
class SearchResult:
    chunk_id: int
    file_id: int | None
    source_file_name: str
    document_type: str
    chunk_index: int
    title: str | None
    content: str
    score: float

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "file_id": self.file_id,
            "source_file_name": self.source_file_name,
            "document_type": self.document_type,
            "chunk_index": self.chunk_index,
            "title": self.title,
            "content": self.content,
            "score": self.score,
        }


class SearchService:
    @staticmethod
    def _compact_text(text: str) -> str:
        return re.sub(r"[\s\W_]+", "", text.lower())

    @staticmethod
    def _append_keyword(words: list[str], seen: set[str], token: str) -> None:
        if not token or len(token) < 2:
            return
        if re.fullmatch(r"[\W_]+", token):
            return
        if token not in seen:
            words.append(token)
            seen.add(token)

    @staticmethod
    def preprocess_query(query: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", query.strip())
        if not normalized:
            return []

        words = []
        seen = set()
        for word in jieba.cut(normalized):
            token = word.strip().lower()
            SearchService._append_keyword(words, seen, token)

        for phrase in re.findall(r"[\u4e00-\u9fff]{2,}", normalized):
            for index in range(0, len(phrase) - 1):
                SearchService._append_keyword(words, seen, phrase[index : index + 2].lower())
        return words

    @staticmethod
    def calculate_score(
        query: str,
        query_keywords: list[str],
        title: str | None,
        content: str,
        document_type: str | None = None,
    ) -> float:
        if not query_keywords:
            return 0.0

        normalized_query = SearchService._compact_text(query)
        normalized_title = SearchService._compact_text(title or "")
        normalized_content = SearchService._compact_text(content)

        score = 0.0
        matched_keywords = 0

        for keyword in query_keywords:
            title_hits = normalized_title.count(keyword)
            content_hits = normalized_content.count(keyword)
            if title_hits or content_hits:
                matched_keywords += 1
                score += title_hits * 3.0
                score += content_hits * 1.0

        score += matched_keywords * 1.5

        if normalized_query:
            if normalized_query in normalized_title:
                score += 8.0
            if normalized_query in normalized_content:
                score += 5.0

        if matched_keywords == len(query_keywords):
            score += 2.0

        weight = DOCUMENT_TYPE_WEIGHTS.get(document_type or "", 1.0)
        return round(score * weight, 4)

    @staticmethod
    def search(
        db: Session,
        query: str,
        top_k: int = 5,
        document_type: str | None = None,
        file_id: int | None = None,
    ) -> list[SearchResult]:
        query_keywords = SearchService.preprocess_query(query)
        if not query_keywords:
            return []

        stmt = (
            select(KnowledgeChunk, KnowledgeFile)
            .outerjoin(KnowledgeFile, KnowledgeChunk.file_id == KnowledgeFile.id)
            .order_by(KnowledgeChunk.created_at.desc(), KnowledgeChunk.chunk_index.asc())
        )
        if document_type:
            if document_type == "fault_case":
                stmt = stmt.where(or_(KnowledgeFile.document_type == document_type, KnowledgeChunk.file_id.is_(None)))
            else:
                stmt = stmt.where(KnowledgeFile.document_type == document_type)
        if file_id:
            stmt = stmt.where(KnowledgeChunk.file_id == file_id)

        results: list[SearchResult] = []
        for chunk, knowledge_file in db.execute(stmt).all():
            score = SearchService.calculate_score(
                query=query,
                query_keywords=query_keywords,
                title=chunk.title,
                content=chunk.content,
                document_type=knowledge_file.document_type if knowledge_file else "fault_case",
            )
            if score <= 0:
                continue
            results.append(
                SearchResult(
                    chunk_id=chunk.id,
                    file_id=chunk.file_id,
                    source_file_name=knowledge_file.original_filename if knowledge_file else "repair_case",
                    document_type=knowledge_file.document_type if knowledge_file else "fault_case",
                    chunk_index=chunk.chunk_index,
                    title=chunk.title,
                    content=chunk.content,
                    score=score,
                )
            )

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]
