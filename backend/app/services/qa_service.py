from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.qa import QARecord
from app.services.llm_client import LLMClient
from app.services.search_service import SearchResult, SearchService


class QAService:
    SYSTEM_PROMPT = (
        "你是电梯/扶梯维保知识助手，面向持证维保人员提供检修辅助建议。"
        "你的回答必须基于知识库上下文，强调安全规范和人工复核。"
        "不要编造不存在的标准编号或法规条款，不要输出百分百确定等绝对化表达。"
    )

    @staticmethod
    def _build_references(results: list[SearchResult]) -> list[dict]:
        return [
            {
                "chunk_id": item.chunk_id,
                "file_id": item.file_id,
                "source_file_name": item.source_file_name,
                "document_type": item.document_type,
                "chunk_index": item.chunk_index,
                "score": item.score,
            }
            for item in results
        ]

    @staticmethod
    def _build_context(results: list[SearchResult]) -> str:
        if not results:
            return "当前知识库未检索到直接相关资料。"

        context_items = []
        for index, item in enumerate(results, start=1):
            content = item.content.strip()
            if len(content) > 1200:
                content = f"{content[:1200]}..."
            context_items.append(
                f"[{index}] 来源文件：{item.source_file_name}，文档类型：{item.document_type}，"
                f"chunk_id：{item.chunk_id}，内容：{content}"
            )
        return "\n\n".join(context_items)

    @staticmethod
    def _build_user_prompt(
        device_name: str | None,
        device_model: str | None,
        fault_description: str,
        context: str,
        has_context: bool,
    ) -> str:
        context_instruction = (
            "以下建议基于知识库检索结果生成。"
            if has_context
            else "当前知识库未检索到直接相关资料，以下为通用参考建议。"
        )
        return f"""用户输入：
设备名称：{device_name or "未提供"}
设备型号：{device_model or "未提供"}
故障现象：{fault_description}

知识库上下文：
{context}

输出要求：
请先明确说明：{context_instruction}
请按以下结构输出：
1. 故障现象概述
2. 可能原因分析
3. 推荐检修步骤
4. 所需工具或检测项目
5. 安全注意事项
6. 参考知识来源
7. 人工复核建议

要求：
- 检修步骤要分条列出。
- 安全注意事项必须明确提示：电梯/扶梯检修应由具备资质的维保人员执行。
- 如果引用知识库内容，请在参考知识来源中对应列出来源文件和片段序号。
- 不要编造不存在的标准编号或法规条款。
- 不要输出“百分百确定”等绝对化表达。"""

    @staticmethod
    def _save_record(
        db: Session,
        user_id: int,
        device_name: str | None,
        device_model: str | None,
        fault_description: str,
        retrieved_context: str,
        references: list[dict],
        answer: str | None,
        status: str,
        error_message: str | None = None,
    ) -> QARecord:
        record = QARecord(
            user_id=user_id,
            device_name=device_name,
            device_model=device_model,
            fault_description=fault_description,
            retrieved_context=retrieved_context,
            answer=answer,
            references_json=references,
            llm_model=settings.llm_model,
            status=status,
            error_message=error_message,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def generate_repair_advice(
        db: Session,
        user_id: int,
        device_name: str | None,
        device_model: str | None,
        fault_description: str,
        top_k: int = 5,
    ) -> tuple[QARecord, list[dict]]:
        search_results = SearchService.search(db=db, query=fault_description, top_k=top_k)
        references = QAService._build_references(search_results)
        context = QAService._build_context(search_results)
        user_prompt = QAService._build_user_prompt(
            device_name=device_name,
            device_model=device_model,
            fault_description=fault_description,
            context=context,
            has_context=bool(search_results),
        )

        try:
            answer = LLMClient().chat(QAService.SYSTEM_PROMPT, user_prompt)
            record = QAService._save_record(
                db=db,
                user_id=user_id,
                device_name=device_name,
                device_model=device_model,
                fault_description=fault_description,
                retrieved_context=context,
                references=references,
                answer=answer,
                status="success",
            )
            return record, references
        except Exception as exc:
            db.rollback()
            error_message = str(exc)
            try:
                QAService._save_record(
                    db=db,
                    user_id=user_id,
                    device_name=device_name,
                    device_model=device_model,
                    fault_description=fault_description,
                    retrieved_context=context,
                    references=references,
                    answer=None,
                    status="failed",
                    error_message=error_message,
                )
            except SQLAlchemyError:
                db.rollback()
            raise RuntimeError(error_message) from exc
