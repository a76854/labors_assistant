"""
FastAPI 路由定义
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.api.schema import (
    SessionCreateRequest, SessionResponse,
    MessageCreateRequest, MessageResponse, ChatHistoryResponse,
    DocumentGenerateRequest, DocumentResponse,
    ErrorResponse
)
from backend.services.chat import ChatService
from backend.services.document import DocumentService
from backend.services.agent_service import AgentService
from datetime import datetime
from typing import List, Optional


router = APIRouter(prefix="/api/v1", tags=["core"])


# ============================================================================
# 会话管理接口
# ============================================================================

@router.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session(req: SessionCreateRequest, db: Session = Depends(get_db)):
    """创建新的对话会话"""
    try:
        session = ChatService.create_session(db, req.case_type, req.description)
        return SessionResponse.model_validate(session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """获取会话详情"""
    session = ChatService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return SessionResponse.model_validate(session)


# ============================================================================
# 对话接口
# ============================================================================

@router.post("/sessions/{session_id}/messages", response_model=MessageResponse, status_code=201)
def send_message(
    session_id: str,
    req: MessageCreateRequest,
    db: Session = Depends(get_db)
):
    """发送消息"""
    # 验证会话存在
    session = ChatService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    try:
        # 存储用户消息
        user_msg = ChatService.add_message(db, session_id, "user", req.content)
        
        # 调用 Agent 生成回复
        agent_result = AgentService.process_user_message(
            user_input=req.content,
            session_id=session_id
        )
        assistant_reply = agent_result.get("final_answer", "Agent 处理出错，请重试")
        ChatService.add_message(db, session_id, "assistant", assistant_reply)
        
        return MessageResponse.model_validate(user_msg)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    session = ChatService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    messages = ChatService.get_messages(db, session_id, limit, offset)
    return ChatHistoryResponse(
        session_id=session_id,
        messages=[MessageResponse.model_validate(msg) for msg in messages],
        total=ChatService.get_messages_count(db, session_id)
    )


# ============================================================================
# 文档生成接口
# ============================================================================

@router.post("/sessions/{session_id}/generate-document", response_model=DocumentResponse, status_code=202)
def generate_document(
    session_id: str,
    req: DocumentGenerateRequest,
    db: Session = Depends(get_db)
):
    """生成诉状文档（异步）"""
    session = ChatService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    try:
        # 创建文档记录（初始状态为 pending）
        doc = DocumentService.create_document(
            db,
            session_id=session_id,
            template_id=req.template_id,
            title=f"{session.case_type} - 诉状"
        )
        
        # 调用 Agent 生成文档
        document_url = AgentService.generate_document(
            session_id=session_id,
            case_type=str(session.case_type),
            template_id=req.template_id
        )
        
        # 更新文档状态
        if document_url:
            DocumentService.update_document_status(
                db,
                str(doc.id),
                status="generated",
                file_url=document_url
            )
        else:
            DocumentService.update_document_status(
                db,
                str(doc.id),
                status="failed"
            )
        
        # 返回更新后的文档
        updated_doc = DocumentService.get_document(db, str(doc.id))
        return DocumentResponse.model_validate(updated_doc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate document: {str(e)}"
        )


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    """获取文档"""
    doc = DocumentService.get_document(db, doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found"
        )
    return DocumentResponse.model_validate(doc)


@router.get("/documents/{doc_id}/export")
def export_document(
    doc_id: str,
    db: Session = Depends(get_db)
):
    """导出文档（下载）"""
    doc = DocumentService.get_document(db, doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found"
        )
    
    if getattr(doc, "status", None) != "generated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is not ready for export"
        )
    
    # TODO: 实现文件下载逻辑
    return {"message": "Download feature coming soon"}


# ============================================================================
# 健康检查
# ============================================================================

@router.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }
