"""
文档服务 - 处理文档生成和导出逻辑
"""

import re
import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.db.models import Document, Session as SessionModel, Template
from backend.utils.timezone import now_beijing


settings = get_settings()
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class DocumentService:
    """文档服务"""
    
    @staticmethod
    def create_document(
        db: Session,
        session_id: str,
        template_id: str,
        title: str = "民事起诉状",
        content: str = ""
    ) -> Document:
        """创建文档记录"""
        doc = Document(
            id=str(uuid.uuid4()),
            session_id=session_id,
            template_id=template_id,
            title=title,
            content=content,
            status="pending"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
    
    @staticmethod
    def get_document(db: Session, doc_id: str) -> Optional[Document]:
        """获取文档"""
        return db.query(Document).filter(Document.id == doc_id).first()
    
    @staticmethod
    def update_document_status(
        db: Session,
        doc_id: str,
        status: str,
        file_url: str | None = None,
        file_size: int | None = None,
        content: str | None = None,
    ) -> Document:
        """更新文档状态"""
        doc = DocumentService.get_document(db, doc_id)
        if doc:
            setattr(doc, "status", status)
            if file_url:
                setattr(doc, "file_url", file_url)
            if file_size is not None:
                setattr(doc, "file_size", file_size)
            if content is not None:
                setattr(doc, "content", content)
            setattr(doc, "updated_at", now_beijing())
            db.commit()
            db.refresh(doc)
        return doc

    @staticmethod
    def build_export_url(doc_id: str) -> str:
        """构建统一的文档导出 API 路径。"""
        return f"/api/v1/documents/{doc_id}/export"

    @staticmethod
    def parse_generated_document_payload(payload: str | None) -> dict[str, str]:
        """
        解析 Agent 文书工具返回文本，提取 filename/local_path/download_url。

        支持格式示例：
        - 文件名：legal_doc_xxx.docx
        - 本地路径：generated_docs/legal_doc_xxx.docx
        - 下载链接：http://127.0.0.1:8000/api/v1/download/legal_doc_xxx.docx
        """
        if not payload or not isinstance(payload, str):
            return {}

        result: dict[str, str] = {}

        file_name_match = re.search(r"(?:文件名|filename)[：:]\s*([^\r\n]+?\.docx)", payload, re.IGNORECASE)
        if file_name_match:
            result["filename"] = file_name_match.group(1).strip()

        local_path_match = re.search(r"(?:本地路径|local_path)[：:]\s*([^\r\n]+?\.docx)", payload, re.IGNORECASE)
        if local_path_match:
            result["local_path"] = local_path_match.group(1).strip()

        download_match = re.search(r"(?:下载链接|download_url)[：:]\s*([^\r\n\s]+)", payload, re.IGNORECASE)
        if download_match:
            result["download_url"] = download_match.group(1).strip()

        # 兼容直接保存为 URL/路径的场景，例如：
        # /api/v1/download/legal_doc_xxx.docx
        # http://127.0.0.1:8000/download/legal_doc_xxx.docx
        direct_url_match = re.search(
            r"(https?://[^\s]+?/(?:api/v1/)?download/([A-Za-z0-9._-]+\.docx))|((?:/api/v1/|/)?download/([A-Za-z0-9._-]+\.docx))",
            payload,
            re.IGNORECASE,
        )
        if direct_url_match and "download_url" not in result:
            result["download_url"] = (direct_url_match.group(1) or direct_url_match.group(3) or "").strip()

        if "filename" not in result:
            if direct_url_match:
                extracted_name = direct_url_match.group(2) or direct_url_match.group(4)
                if extracted_name:
                    result["filename"] = extracted_name.strip()
            else:
                loose_filename_match = re.search(r"([A-Za-z0-9._-]+\.docx)", payload)
                if loose_filename_match:
                    result["filename"] = loose_filename_match.group(1).strip()

        if "local_path" not in result:
            local_doc_path_match = re.search(
                r"((?:[A-Za-z]:)?[^\r\n]*?generated_docs/[^\r\n\s]+?\.docx)",
                payload,
                re.IGNORECASE,
            )
            if local_doc_path_match:
                result["local_path"] = local_doc_path_match.group(1).strip()

        return result

    @staticmethod
    def _candidate_paths_from_payload(file_meta: dict[str, str]) -> list[Path]:
        """根据 payload 解析结果构建本地候选路径。"""
        candidates: list[Path] = []
        file_name = file_meta.get("filename")
        local_path = file_meta.get("local_path")

        if local_path:
            local_candidate = Path(local_path)
            if local_candidate.is_absolute():
                candidates.append(local_candidate)
            else:
                candidates.append((PROJECT_ROOT / local_candidate).resolve())

        if file_name:
            candidates.append((PROJECT_ROOT / "generated_docs" / file_name).resolve())

            configured_storage = Path(settings.document_storage_path)
            if configured_storage.is_absolute():
                candidates.append((configured_storage / file_name).resolve())
            else:
                candidates.append((PROJECT_ROOT / configured_storage / file_name).resolve())

        return candidates

    @staticmethod
    def resolve_generated_document_path(file_meta: dict[str, str]) -> Optional[Path]:
        """从 payload 元数据中解析并验证文档实际文件路径。"""
        for candidate in DocumentService._candidate_paths_from_payload(file_meta):
            if candidate.exists() and candidate.is_file():
                return candidate
        return None
    
    @staticmethod
    def get_session_documents(db: Session, session_id: str) -> list:
        """获取会话的所有文档"""
        return db.query(Document).filter(Document.session_id == session_id).all()

    @staticmethod
    def get_latest_available_document(db: Session, session_id: str) -> Optional[Document]:
        """获取会话中最近一个可导出的文档记录。"""
        return (
            db.query(Document)
            .filter(
                Document.session_id == session_id,
                Document.status.in_(["generated", "exported"]),
            )
            .order_by(Document.updated_at.desc(), Document.created_at.desc())
            .first()
        )
    
    @staticmethod
    def mock_generate_document(
        db: Session,
        session_id: str,
        template_id: str,
        format: str = "docx"
    ) -> Document:
        """
        模拟文档生成（MVP阶段）
        实际生成逻辑应该：
        1. 获取案件要素
        2. 调用LLM生成内容
        3. 用python-docx渲染到模板
        4. 导出为Word/PDF
        """
        doc = DocumentService.create_document(
            db,
            session_id,
            template_id,
            title="民事起诉状"
        )
        
        # Mock 内容
        mock_content = """
        民事起诉状
        
        原告：XXX
        被告：XXX
        
        诉讼请求：
        1. 要求被告支付拖欠工资
        2. 要求被告支付经济补偿
        
        事实和理由：
        原告于2025年入职被告公司，签订了劳动合同。
        自2026年起，被告未按时支付工资。
        
        法律依据：
        《中华人民共和国劳动法》第50条
        """
        
        # 保存文档
        storage_path = Path(settings.document_storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        file_name = f"{doc.id}.{format}"
        file_path = storage_path / file_name
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(mock_content)
        
        # 更新数据库
        file_size = file_path.stat().st_size
        DocumentService.update_document_status(
            db,
            str(doc.id),
            "generated",
            file_url=f"/documents/{file_name}",
            file_size=file_size
        )
        
        return doc
    
    @staticmethod
    def get_template(db: Session, template_id: str) -> Optional[Template]:
        """获取模板"""
        return db.query(Template).filter(Template.id == template_id).first()
    
    @staticmethod
    def get_all_templates(db: Session) -> list:
        """获取所有模板"""
        return db.query(Template).all()
