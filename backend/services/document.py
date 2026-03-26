"""
文档服务 - 处理文档生成和导出逻辑
"""

from sqlalchemy.orm import Session
from backend.db.models import Document, Session as SessionModel, Template
from backend.config import get_settings
from pathlib import Path
import uuid
from datetime import datetime, timezone
from typing import Optional


settings = get_settings()


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
        file_size: int | None = None
    ) -> Document:
        """更新文档状态"""
        doc = DocumentService.get_document(db, doc_id)
        if doc:
            setattr(doc, "status", status)
            if file_url:
                setattr(doc, "file_url", file_url)
            if file_size is not None:
                setattr(doc, "file_size", file_size)
            setattr(doc, "updated_at", datetime.now(timezone.utc))
            db.commit()
            db.refresh(doc)
        return doc
    
    @staticmethod
    def get_session_documents(db: Session, session_id: str) -> list:
        """获取会话的所有文档"""
        return db.query(Document).filter(Document.session_id == session_id).all()
    
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
