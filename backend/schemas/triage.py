"""案件分诊 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List


class LawyerProfile(BaseModel):
    """律师信息（推荐用）。"""
    id: str = Field(..., description="律师ID")
    name: str = Field(..., description="姓名")
    license_no: str = Field(default="", description="执业证号")
    specialties: List[str] = Field(default_factory=list, description="擅长案由")
    years: int = Field(default=0, description="执业年限")
    rating: float = Field(default=0.0, description="评分")
    desc: str = Field(default="", description="简介")


class TriageResponse(BaseModel):
    """案件分诊结果。"""
    session_id: str = Field(..., description="会话ID")
    case_type: str = Field(..., description="案件类型")
    region: Optional[str] = Field("beijing", description="地区")
    evidence_score: int = Field(..., description="证据完整度 0-100")
    evidence_covered: List[str] = Field(default_factory=list, description="已覆盖的证据类别")
    missing_evidence: List[str] = Field(default_factory=list, description="缺失证据类别")
    risk_score: int = Field(..., description="风险评分 0-100")
    complexity: str = Field(..., description="复杂度: high|medium|low")
    recommended_lawyers: List[LawyerProfile] = Field(default_factory=list, description="推荐律师")
