"""律师后台 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# 律师后台 Schemas
# ============================================================================

class LeadListItem(BaseModel):
    """律师线索列表项。"""
    id: str = Field(..., description="线索ID")
    session_id: str = Field(..., description="会话ID")
    status: str = Field(..., description="线索状态: open|claimed|completed")
    case_type: str = Field(..., description="案件类型")
    region: Optional[str] = Field("beijing", description="地区")
    evidence_score: Optional[int] = Field(None, description="证据完整度")
    risk_score: Optional[int] = Field(None, description="风险评分")
    complexity: Optional[str] = Field(None, description="复杂度")
    missing_evidence: Optional[List[str]] = Field(None, description="缺失证据")
    summary: Optional[str] = Field(None, description="案情摘要（脱敏）")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    material_request_count: int = Field(default=0, description="补充材料请求数")

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """线索列表响应。"""
    leads: List[LeadListItem] = Field(..., description="线索列表")
    total: int = Field(..., description="线索总数")


class LeadDetailResponse(LeadListItem):
    """线索详情。"""
    user_username: Optional[str] = Field(None, description="线索发布者用户名（脱敏）")
    user_phone: Optional[str] = Field(None, description="发布者联系电话（脱敏）")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="对话摘要（最近10条）")
    material_requests: List[Dict[str, Any]] = Field(default_factory=list, description="补充材料请求列表")


class MaterialRequestCreate(BaseModel):
    """发起补充材料请求。"""
    items: List[Dict[str, str]] = Field(..., description="材料清单，如 [{name, description}]")
    note: Optional[str] = Field(None, description="律师备注")


class LeadActionResponse(BaseModel):
    """线索操作响应。"""
    id: str = Field(..., description="线索ID")
    status: str = Field(..., description="操作后的状态")
    message: str = Field(..., description="操作结果说明")


class MaterialRequestResponse(BaseModel):
    """补充材料请求响应。"""
    id: str = Field(..., description="请求ID")
    lead_id: str = Field(..., description="线索ID")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="材料清单")
    note: Optional[str] = Field(None, description="备注")
    status: str = Field(..., description="状态: pending|satisfied")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# ============================================================================
# 律师推荐 Schemas（法律行业美团：系统推荐合适客户）
# ============================================================================

class LeadRecommendation(BaseModel):
    """推荐线索（带匹配度与推荐理由）。"""
    lead: LeadListItem = Field(..., description="线索")
    match_score: int = Field(..., description="匹配度 0-100")
    reasons: List[str] = Field(default_factory=list, description="推荐理由")
    recommended: bool = Field(default=True, description="是否为系统推荐")


class LeadRecommendationListResponse(BaseModel):
    """推荐线索列表响应。"""
    recommendations: List[LeadRecommendation] = Field(..., description="推荐列表")
    total: int = Field(..., description="推荐总数")


class LeadMarketListResponse(BaseModel):
    """线索市场响应。"""
    leads: List[LeadListItem] = Field(..., description="全部待接单线索")
    total: int = Field(..., description="总数")
