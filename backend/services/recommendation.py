"""
律师推荐服务 - 法律行业美团模式

系统根据律师的擅长案由与所在地区，自动匹配合适的待接单线索，
并按匹配度排序推荐（不展示全部线索）。
"""

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from backend.db.models import Lead, User

# 案由显示名
CASE_TYPE_NAMES = {
    "wage_arrears": "劳动报酬",
    "labor_contract": "劳动合同",
    "work_injury": "工伤赔偿",
}

# 地区显示名
REGION_NAMES = {
    "beijing": "北京",
    "shanghai": "上海",
    "guangdong": "广东",
}


class RecommendationService:
    """律师线索推荐服务"""

    @staticmethod
    def _lead_to_dict(db: Session, lead: Lead, lawyer: User) -> Dict[str, Any]:
        """线索转字典（供推荐列表使用）。"""
        lawyer_name = None
        if lead.lawyer_id:
            claimed_by = db.query(User).filter(User.id == lead.lawyer_id).first()
            lawyer_name = claimed_by.name or claimed_by.username if claimed_by else None

        return {
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
            "lawyer_username": lawyer_name,
        }

    @staticmethod
    def match_score(lead: Lead, lawyer: User) -> tuple[int, List[str]]:
        """计算线索与律师的匹配度 0-100，并给出推荐理由。"""
        score = 0
        reasons: List[str] = []

        specialties = lawyer.specialty or []
        region = lawyer.region or ""

        # 1. 案由专长匹配（权重最高）
        if lead.case_type in specialties:
            score += 45
            case_name = CASE_TYPE_NAMES.get(lead.case_type, lead.case_type)
            reasons.append(f"擅长{case_name}纠纷")
        elif not specialties:
            reasons.append("未设置专长，按综合实力推荐")
        else:
            reasons.append("非擅长案由，谨慎接单")

        # 2. 地区匹配
        if region and lead.region == region:
            score += 25
            region_name = REGION_NAMES.get(region, region)
            reasons.append(f"熟悉{region_name}地区流程")
        elif region:
            reasons.append("跨地区案件，注意管辖规则")

        # 3. 案件价值（风险高 = 更需专业律师）
        risk = lead.risk_score or 0
        score += min(risk, 100) * 0.3

        # 4. 证据充分度奖励（更易成案）
        evidence = lead.evidence_score or 0
        if evidence >= 60:
            score += 5
            reasons.append("证据较完整，成案率高")

        score = max(0, min(100, round(score)))
        return score, reasons

    @staticmethod
    def recommend_leads(db: Session, lawyer: User, limit: int = 20) -> List[Dict[str, Any]]:
        """为律师推荐合适的待接单线索（推荐模式，非全量）。"""
        leads = (
            db.query(Lead)
            .filter(Lead.status == "open")
            .order_by(Lead.created_at.desc())
            .all()
        )

        scored: List[Dict[str, Any]] = []
        for lead in leads:
            score, reasons = RecommendationService.match_score(lead, lawyer)
            item = RecommendationService._lead_to_dict(db, lead, lawyer)
            item["match_score"] = score
            item["reasons"] = reasons
            item["recommended"] = True
            scored.append(item)

        # 匹配度排序：同分按风险高优先
        scored.sort(key=lambda x: (x["match_score"], x.get("risk_score") or 0), reverse=True)
        return scored[:limit]

    @staticmethod
    def market_leads(db: Session, status_filter: str | None = None, limit: int = 100, offset: int = 0) -> tuple[List[Dict[str, Any]], int]:
        """线索市场（全部线索，供律师浏览补充）。"""
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
        return [RecommendationService._lead_to_dict(db, lead, None) for lead in leads], total
