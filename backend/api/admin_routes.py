"""
超级管理员路由 - 全平台数据概览 / 用户管理 / 线索管理 / 会话管理
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.api.schema import (
    AdminLeadListResponse,
    AdminSessionListResponse,
    AdminStatsResponse,
    AdminUserListResponse,
)
from backend.db.database import get_db
from backend.db.models import (
    CaseElement,
    Document,
    Lead,
    Message,
    Session as SessionModel,
    User,
)
from backend.services.auth import get_current_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def admin_stats(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """全平台数据概览。"""
    return AdminStatsResponse(
        total_users=db.query(User).count(),
        total_lawyers=db.query(User).filter(User.role == "lawyer").count(),
        total_workers=db.query(User).filter(User.role == "user").count(),
        total_sessions=db.query(SessionModel).count(),
        total_leads=db.query(Lead).count(),
        open_leads=db.query(Lead).filter(Lead.status == "open").count(),
        claimed_leads=db.query(Lead).filter(Lead.status == "claimed").count(),
        completed_leads=db.query(Lead).filter(Lead.status == "completed").count(),
        total_documents=db.query(Document).count(),
        generated_documents=db.query(Document)
        .filter(Document.status.in_(["generated", "exported"]))
        .count(),
    )


@router.get("/users", response_model=AdminUserListResponse)
def admin_users(
    role: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """用户列表（按角色过滤，带会话/线索统计）。"""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    user_ids = [user.id for user in users]

    session_counts = dict(
        db.query(SessionModel.user_id, func.count(SessionModel.id))
        .filter(SessionModel.user_id.in_(user_ids))
        .group_by(SessionModel.user_id)
        .all()
    ) if user_ids else {}
    lead_counts = dict(
        db.query(Lead.user_id, func.count(Lead.id))
        .filter(Lead.user_id.in_(user_ids))
        .group_by(Lead.user_id)
        .all()
    ) if user_ids else {}

    items = [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "name": user.name,
            "phone": user.phone,
            "specialty": user.specialty or [],
            "region": user.region,
            "created_at": user.created_at,
            "session_count": session_counts.get(user.id, 0),
            "lead_count": lead_counts.get(user.id, 0),
        }
        for user in users
    ]
    return AdminUserListResponse(users=items, total=total)


@router.get("/leads", response_model=AdminLeadListResponse)
def admin_leads(
    status_filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """全部线索（含发布者与接单律师）。"""
    query = db.query(Lead)
    if status_filter:
        query = query.filter(Lead.status == status_filter)
    total = query.count()
    leads = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()

    items = []
    for lead in leads:
        publisher = db.query(User).filter(User.id == lead.user_id).first()
        lawyer = (
            db.query(User).filter(User.id == lead.lawyer_id).first()
            if lead.lawyer_id
            else None
        )
        items.append(
            {
                "id": lead.id,
                "session_id": lead.session_id,
                "status": lead.status,
                "case_type": lead.case_type,
                "region": lead.region,
                "evidence_score": lead.evidence_score,
                "risk_score": lead.risk_score,
                "complexity": lead.complexity,
                "missing_evidence": lead.missing_evidence or [],
                "summary": lead.summary,
                "created_at": lead.created_at,
                "updated_at": lead.updated_at,
                "material_request_count": len(lead.material_requests),
                "user_username": publisher.username if publisher else None,
                "lawyer_username": (lawyer.name or lawyer.username) if lawyer else None,
            }
        )
    return AdminLeadListResponse(leads=items, total=total)


@router.get("/sessions", response_model=AdminSessionListResponse)
def admin_sessions(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """全部会话（含所属用户）。"""
    query = db.query(SessionModel)
    total = query.count()
    sessions = query.order_by(SessionModel.updated_at.desc()).offset(offset).limit(limit).all()

    session_ids = [s.id for s in sessions]
    message_counts = dict(
        db.query(Message.session_id, func.count(Message.id))
        .filter(Message.session_id.in_(session_ids))
        .group_by(Message.session_id)
        .all()
    ) if session_ids else {}

    user_map = {u.id: u for u in db.query(User).all()}

    items = [
        {
            "id": s.id,
            "case_type": s.case_type,
            "region": s.region,
            "status": s.status,
            "user_username": (
                user_map[s.user_id].username
                if s.user_id and s.user_id in user_map
                else None
            ),
            "message_count": message_counts.get(s.id, 0),
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in sessions
    ]
    return AdminSessionListResponse(sessions=items, total=total)
