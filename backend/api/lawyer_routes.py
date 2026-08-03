"""
律师后台路由 - 待接单线索 / 接单 / 补充材料请求
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.schema import (
    LeadActionResponse,
    LeadDetailResponse,
    LeadListResponse,
    MaterialRequestCreate,
    MaterialRequestResponse,
)
from backend.db.database import get_db
from backend.db.models import Lead, MaterialRequest, User
from backend.services.auth import get_current_lawyer
from backend.services.chat import ChatService
from backend.services.triage import TriageService

router = APIRouter(prefix="/api/v1/lawyer", tags=["lawyer"])


def _mask(value: str | None, keep: int = 2) -> str | None:
    """简单脱敏：保留前 keep 位，其余打码。"""
    if not value:
        return None
    if len(value) <= keep + 2:
        return value[0] + "*" * (len(value) - 1)
    return value[:keep] + "*" * (len(value) - keep - 2) + value[-2:]


def _get_lead_or_404(db: Session, lead_id: str) -> Lead:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {lead_id} not found",
        )
    return lead


@router.get("/leads", response_model=LeadListResponse)
def list_leads(
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    lawyer: User = Depends(get_current_lawyer),
):
    """待接单线索列表，按风险评分倒序。"""
    query = db.query(Lead)
    if status_filter:
        query = query.filter(Lead.status == status_filter)

    total = query.count()
    leads = (
        query.order_by(Lead.risk_score.desc(), Lead.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = []
    for lead in leads:
        item = {
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
        }
        items.append(item)

    return LeadListResponse(leads=items, total=total)


@router.get("/leads/{lead_id}", response_model=LeadDetailResponse)
def get_lead_detail(
    lead_id: str,
    db: Session = Depends(get_db),
    lawyer: User = Depends(get_current_lawyer),
):
    """线索详情：评分明细、对话摘要、补充材料请求。"""
    lead = _get_lead_or_404(db, lead_id)
    publisher = db.query(User).filter(User.id == lead.user_id).first()

    messages = ChatService.get_messages(db, lead.session_id, limit=10, offset=0)
    message_summary = [
        {"role": msg.role, "content": (msg.content or "")[:200]}
        for msg in messages
    ]

    item = {
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
        "user_username": _mask(publisher.username) if publisher else None,
        "user_phone": _mask(publisher.phone) if publisher else None,
        "messages": message_summary,
        "material_requests": [
            {
                "id": mr.id,
                "items": mr.items,
                "note": mr.note,
                "status": mr.status,
                "created_at": mr.created_at,
            }
            for mr in lead.material_requests
        ],
    }
    return LeadDetailResponse(**item)


@router.post("/leads/{lead_id}/claim", response_model=LeadActionResponse)
def claim_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    lawyer: User = Depends(get_current_lawyer),
):
    """律师接单。"""
    lead = _get_lead_or_404(db, lead_id)
    if lead.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"线索当前状态为 {lead.status}，无法接单",
        )
    lead.status = "claimed"
    lead.lawyer_id = lawyer.id
    db.commit()
    db.refresh(lead)
    return LeadActionResponse(
        id=lead.id,
        status=lead.status,
        message="接单成功",
    )


@router.post("/leads/{lead_id}/request-materials", response_model=MaterialRequestResponse)
def request_materials(
    lead_id: str,
    req: MaterialRequestCreate,
    db: Session = Depends(get_db),
    lawyer: User = Depends(get_current_lawyer),
):
    """一键发起补充材料请求。"""
    lead = _get_lead_or_404(db, lead_id)

    items = [{"name": item["name"], "description": item.get("description", ""), "status": "pending"} for item in req.items]
    material_request = MaterialRequest(
        lead_id=lead.id,
        lawyer_id=lawyer.id,
        items=items,
        note=req.note,
        status="pending",
    )
    db.add(material_request)
    db.commit()
    db.refresh(material_request)
    return MaterialRequestResponse.model_validate(material_request)


@router.post("/leads/{lead_id}/complete", response_model=LeadActionResponse)
def complete_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    lawyer: User = Depends(get_current_lawyer),
):
    """标记案件完成。"""
    lead = _get_lead_or_404(db, lead_id)
    lead.status = "completed"
    db.commit()
    db.refresh(lead)
    return LeadActionResponse(
        id=lead.id,
        status=lead.status,
        message="案件已完成",
    )
