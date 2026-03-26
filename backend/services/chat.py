"""
聊天服务 - 处理对话逻辑
"""

from sqlalchemy.orm import Session
from backend.db.models import Session as SessionModel, Message
from typing import List
import uuid
from datetime import datetime, timezone

class ChatService:
    """聊天服务"""
    
    @staticmethod
    def create_session(db: Session, case_type: str, description: str | None = None) -> SessionModel:
        """创建新会话"""
        session = SessionModel(
            id=str(uuid.uuid4()),
            case_type=case_type,
            description=description,
            status="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: str) -> SessionModel:
        """获取会话"""
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    @staticmethod
    def add_message(db: Session, session_id: str, role: str, content: str) -> Message:
        """添加消息到对话"""
        message = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_messages(db: Session, session_id: str, limit: int = 100, offset: int = 0) -> List[Message]:
        """获取对话历史"""
        return db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp.asc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_messages_count(db: Session, session_id: str) -> int:
        """获取对话数量"""
        return db.query(Message).filter(Message.session_id == session_id).count()
    
    @staticmethod
    def clear_session_history(db: Session, session_id: str) -> None:
        """清空对话历史"""
        db.query(Message).filter(Message.session_id == session_id).delete()
        db.commit()
