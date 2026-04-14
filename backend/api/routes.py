"""
FastAPI 路由定义
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import Message
from backend.api.schema import (
    SessionCreateRequest, SessionResponse, SessionListResponse, DocumentReadinessResponse,
    MessageCreateRequest, MessageSyncRequest, MessageResponse, ChatHistoryResponse,
    DocumentGenerateRequest, DocumentResponse,
    ErrorResponse
)
from backend.services.chat import ChatService
from backend.services.document import DocumentService
from backend.services.agent_service import AgentService
from backend.utils.timezone import now_beijing
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


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """获取历史会话列表。"""
    try:
        sessions = ChatService.list_sessions(db, limit=limit, offset=offset)
        return SessionListResponse(
            sessions=sessions,
            total=ChatService.get_sessions_count(db),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
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


@router.get("/sessions/{session_id}/document-readiness", response_model=DocumentReadinessResponse)
def get_document_readiness(session_id: str, db: Session = Depends(get_db)):
    """获取会话是否满足文书生成前置条件。"""
    session = ChatService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    readiness = ChatService.get_document_readiness(db, session_id)
    return DocumentReadinessResponse(**readiness)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """删除会话及其关联历史。"""
    deleted = ChatService.delete_session(db, session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return Response(status_code=204)


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


@router.post("/sessions/{session_id}/messages/sync", status_code=204)
def sync_messages(
    session_id: str,
    req: MessageSyncRequest,
    db: Session = Depends(get_db),
):
    """同步前端流式对话消息到数据库，不触发 Agent。"""
    session = ChatService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    try:
        for item in req.messages:
            ChatService.add_message(db, session_id, item.role, item.content)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync messages: {str(e)}"
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
    """生成诉状文档（实际文件由 agent/tools/doc_generator.py 产出）"""
    user_friendly_content = "文书已生成成功，欢迎进行下载。"

    session = ChatService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    readiness = ChatService.get_document_readiness(db, session_id)
    user_message_count = (
        db.query(Message.id)
        .filter(Message.session_id == session_id, Message.role == "user")
        .count()
    )

    # 前端当前采用 Agent 直连流式模式，后端数据库中的就绪信号可能滞后。
    # 因此不再阻断生成，仅保留 readiness 作为参考信息。
    _ = readiness
    _ = user_message_count
    
    try:
        # 创建文档记录（初始状态为 pending）
        doc = DocumentService.create_document(
            db,
            session_id=session_id,
            template_id=req.template_id,
            title=f"{session.case_type} - 诉状"
        )
        
        # 调用 Agent 文书工具生成文件（doc_generator.py）
        history_messages = ChatService.get_messages(db, session_id, limit=80, offset=0)
        generated_payload = AgentService.generate_document(
            session_id=session_id,
            case_type=str(session.case_type),
            template_id=req.template_id,
            messages=history_messages,
        )

        file_meta = DocumentService.parse_generated_document_payload(generated_payload)
        generated_file_path = DocumentService.resolve_generated_document_path(file_meta)

        # 将生成结果绑定到当前 session 的文档记录中
        if generated_file_path:
            DocumentService.update_document_status(
                db,
                str(doc.id),
                status="generated",
                file_url=f"/api/v1/download/{generated_file_path.name}",
                file_size=generated_file_path.stat().st_size,
                content=user_friendly_content,
            )
        else:
            DocumentService.update_document_status(
                db,
                str(doc.id),
                status="failed",
                content=generated_payload or "文书生成失败：未返回有效文件信息。",
            )

            # 兜底：若本轮未拿到新文件，但会话中存在可用历史文书，则复用最近一份文件避免直接失败。
            latest_doc = DocumentService.get_latest_available_document(db, session_id)
            if latest_doc and str(getattr(latest_doc, "id", "")) != str(doc.id):
                latest_meta = DocumentService.parse_generated_document_payload(getattr(latest_doc, "content", None))
                if "filename" not in latest_meta:
                    latest_meta.update(
                        DocumentService.parse_generated_document_payload(getattr(latest_doc, "file_url", None))
                    )
                latest_file_path = DocumentService.resolve_generated_document_path(latest_meta)
                if latest_file_path:
                    DocumentService.update_document_status(
                        db,
                        str(doc.id),
                        status="generated",
                        file_url=f"/api/v1/download/{latest_file_path.name}",
                        file_size=latest_file_path.stat().st_size,
                        content=user_friendly_content,
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
    """导出文档（返回下载地址，文件来自 doc_generator.py 产物）"""
    doc = DocumentService.get_document(db, doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found"
        )

    if getattr(doc, "status", None) not in {"generated", "exported"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is not ready for export"
        )

    file_meta = DocumentService.parse_generated_document_payload(getattr(doc, "content", None))
    if "filename" not in file_meta:
        file_meta.update(DocumentService.parse_generated_document_payload(getattr(doc, "file_url", None)))
    file_path = DocumentService.resolve_generated_document_path(file_meta)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated document file not found"
        )

    file_name = file_meta.get("filename") or file_path.name
    download_url = f"/api/v1/download/{file_name}"

    if getattr(doc, "status", None) != "exported":
        DocumentService.update_document_status(
            db,
            str(doc.id),
            status="exported",
            file_url=download_url,
            file_size=file_path.stat().st_size,
        )

    return {
        "download_url": download_url,
        "filename": file_name,
    }


@router.get("/download/{file_name}")
def download_document_file(file_name: str):
    """下载 doc_generator.py 实际生成的文书文件。"""
    if "/" in file_name or "\\" in file_name or ".." in file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file name"
        )

    file_meta = {"filename": file_name}
    file_path = DocumentService.resolve_generated_document_path(file_meta)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found"
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=file_name,
    )


# ============================================================================
# 健康检查
# ============================================================================

@router.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "timestamp": now_beijing().isoformat()
    }
