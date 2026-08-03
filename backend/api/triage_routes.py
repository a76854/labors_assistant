"""
案件分诊路由 - 风险评分 / 律师推荐 / 地区列表
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.schema import (
    LeadActionResponse,
    RegionListResponse,
    TriageResponse,
)
from backend.db.database import get_db
from backend.db.models import Lead
from backend.services.auth import get_current_user
from backend.services.regions import get_regions
from backend.services.triage import TriageService

router = APIRouter(prefix="/api/v1", tags=["triage"])


@router.post("/sessions/{session_id}/triage", response_model=TriageResponse)
def triage_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """案件分诊：计算证据完整度/风险评分，生成律师线索并推荐律师。"""
    try:
        triage = TriageService.compute_triage(db, session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    # 自动将案件发布为律师线索
    TriageService.upsert_lead(db, session_id)
    return TriageResponse(**triage)


@router.get("/sessions/{session_id}/lead")
def get_session_lead(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """劳动者端：查询会话对应的线索状态与补充材料请求。"""
    lead = TriageService.get_lead_by_session(db, session_id)
    if not lead:
        return {"lead": None}

    return {
        "lead": {
            "id": lead.id,
            "session_id": lead.session_id,
            "status": lead.status,
            "evidence_score": lead.evidence_score,
            "risk_score": lead.risk_score,
            "complexity": lead.complexity,
            "created_at": lead.created_at,
            "lawyer_id": lead.lawyer_id,
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
    }


@router.get("/regions", response_model=RegionListResponse)
def list_regions():
    """获取支持的地区列表（模板按地区切换）。"""
    return RegionListResponse(regions=get_regions())
