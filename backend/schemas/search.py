"""搜索相关 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class CaseSearchRequest(BaseModel):
    """案例搜索请求。"""
    keyword: str = Field(..., min_length=1, description="搜索关键词")
    limit: int = Field(default=5, ge=1, le=20, description="返回结果数量上限")


class CaseSearchResult(BaseModel):
    """案例搜索结果。"""
    id: str = Field(..., description="案例ID")
    title: str = Field(..., description="案例标题")
    description: str = Field(..., description="案例简介")
    parties: Dict[str, str] = Field(..., description="当事人信息，包含原告和被告")
    verdict: str = Field(..., description="裁判结果摘要")
    damages: Optional[Dict[str, float]] = Field(None, description="赔偿项目及金额")


class LawSearchRequest(BaseModel):
    """法律条文搜索请求。"""
    keyword: str = Field(..., min_length=1, description="搜索关键词")
    limit: int = Field(default=5, ge=1, le=20, description="返回结果数量上限")


class LawSearchResult(BaseModel):
    """法律条文搜索结果。"""
    laws: List[Dict[str, str]] = Field(..., description="法律条文列表，每项包含 law、article、content")
