"""
聊天服务 - 处理对话逻辑
"""

import uuid
from typing import Any, Dict, List

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from backend.db.models import Session as SessionModel, Message
from backend.utils.timezone import now_beijing


DOCUMENT_READY_SIGNAL = "请点击右上角生成诉状"


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
        now = now_beijing()
        message = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            timestamp=now
        )
        db.add(message)

        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            session.updated_at = now

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
    def _assistant_has_document_ready_signal(messages: List[Message]) -> bool:
        """判断助手消息中是否已明确提示可以生成诉状。"""
        normalized_signal = "".join(DOCUMENT_READY_SIGNAL.split())

        for message in messages:
            if getattr(message, "role", "") != "assistant":
                continue

            content = str(getattr(message, "content", "") or "")
            normalized_content = "".join(content.split())
            if normalized_signal and normalized_signal in normalized_content:
                return True

        return False

    @staticmethod
    def get_document_readiness(db: Session, session_id: str) -> Dict[str, Any]:
        """判断当前会话是否已收到助手明确的文书生成提示。"""
        messages = ChatService.get_messages(db, session_id, limit=500, offset=0)
        ready = ChatService._assistant_has_document_ready_signal(messages)

        return {
            "ready": ready,
            "missing_fields": [] if ready else [f"等待助手明确提示“{DOCUMENT_READY_SIGNAL}”"],
            "collected_fields": {"agent_signal": DOCUMENT_READY_SIGNAL} if ready else {},
        }

    @staticmethod
    def _sessions_with_messages_subquery(db: Session):
        """返回至少包含一条消息的会话子查询。"""
        return (
            db.query(Message.session_id.label("session_id"))
            .group_by(Message.session_id)
            .subquery()
        )

    @staticmethod
    def get_sessions_count(db: Session) -> int:
        """获取有历史消息的会话总数。"""
        sessions_with_messages = ChatService._sessions_with_messages_subquery(db)
        return (
            db.query(func.count(SessionModel.id))
            .join(sessions_with_messages, SessionModel.id == sessions_with_messages.c.session_id)
            .scalar()
            or 0
        )

    @staticmethod
    def _build_message_preview(content: str | None, max_length: int = 72) -> str | None:
        """构建适合首页展示的最近消息摘要。"""
        if not content:
            return None

        normalized = " ".join(str(content).split())
        if not normalized:
            return None

        if len(normalized) <= max_length:
            return normalized
        return normalized[: max_length - 1] + "…"

    @staticmethod
    def list_sessions(db: Session, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """获取首页历史会话列表，按最近活跃时间倒序排列。"""
        sessions_with_messages = ChatService._sessions_with_messages_subquery(db)
        sessions = (
            db.query(SessionModel)
            .join(sessions_with_messages, SessionModel.id == sessions_with_messages.c.session_id)
            .order_by(SessionModel.updated_at.desc(), SessionModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        if not sessions:
            return []

        session_ids = [session.id for session in sessions]

        message_count_rows = (
            db.query(Message.session_id, func.count(Message.id))
            .filter(Message.session_id.in_(session_ids))
            .group_by(Message.session_id)
            .all()
        )
        message_counts = {session_id: count for session_id, count in message_count_rows}

        latest_message_time_subquery = (
            db.query(
                Message.session_id.label("session_id"),
                func.max(Message.timestamp).label("latest_timestamp"),
            )
            .filter(Message.session_id.in_(session_ids))
            .group_by(Message.session_id)
            .subquery()
        )

        latest_message_rows = (
            db.query(Message)
            .join(
                latest_message_time_subquery,
                and_(
                    Message.session_id == latest_message_time_subquery.c.session_id,
                    Message.timestamp == latest_message_time_subquery.c.latest_timestamp,
                ),
            )
            .all()
        )

        latest_messages: Dict[str, Message] = {}
        for message in latest_message_rows:
            previous = latest_messages.get(message.session_id)
            if previous is None or message.timestamp >= previous.timestamp:
                latest_messages[message.session_id] = message

        session_items: List[Dict[str, Any]] = []
        for session in sessions:
            latest_message = latest_messages.get(session.id)
            session_items.append(
                {
                    "id": session.id,
                    "case_type": session.case_type,
                    "status": session.status,
                    "description": session.description,
                    "created_at": session.created_at,
                    "updated_at": session.updated_at,
                    "message_count": message_counts.get(session.id, 0),
                    "last_message_preview": ChatService._build_message_preview(
                        getattr(latest_message, "content", None)
                    ),
                    "last_message_role": getattr(latest_message, "role", None),
                    "last_message_at": getattr(latest_message, "timestamp", None),
                }
            )

        return session_items
    
    @staticmethod
    def clear_session_history(db: Session, session_id: str) -> None:
        """清空对话历史"""
        db.query(Message).filter(Message.session_id == session_id).delete()
        db.commit()

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        """删除会话及其关联数据。"""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            return False

        db.delete(session)
        db.commit()
        return True
