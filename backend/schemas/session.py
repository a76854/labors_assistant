"""会话相关 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class SessionCreateRequest(BaseModel):
    """创建会话请求。

    用于开启一个新的案件咨询会话，前端通常在用户选择案件类型并填写简要描述后提交。
    """
    case_type: str = Field(..., description="案件类型，取值范围: wage_arrears|labor_contract|work_injury")
    region: str = Field(default="beijing", description="地区，取值范围: beijing|shanghai|guangdong")
    description: Optional[str] = Field(None, description="案件的简要描述，便于后续生成建议和文书")


class SessionResponse(BaseModel):
    """会话响应。

    返回会话的基础信息，供前端展示会话列表、详情页和状态标签。
    """
    id: str = Field(..., description="会话ID")
    case_type: str = Field(..., description="案件类型")
    region: Optional[str] = Field("beijing", description="地区")
    status: str = Field(..., description="会话状态，例如 active|closed|draft")
    description: Optional[str] = Field(None, description="会话对应的案件描述")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    class Config:
        from_attributes = True


class SessionListItem(BaseModel):
    """首页历史会话列表项。"""

    id: str = Field(..., description="会话ID")
    case_type: str = Field(..., description="案件类型")
    region: Optional[str] = Field("beijing", description="地区")
    status: str = Field(..., description="会话状态")
    description: Optional[str] = Field(None, description="案件描述")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最近更新时间")
    message_count: int = Field(default=0, description="消息总数")
    last_message_preview: Optional[str] = Field(None, description="最近一条消息摘要")
    last_message_role: Optional[str] = Field(None, description="最近一条消息的角色")
    last_message_at: Optional[datetime] = Field(None, description="最近一条消息时间")


class SessionListResponse(BaseModel):
    """首页历史会话列表响应。"""

    sessions: List[SessionListItem] = Field(..., description="会话列表")
    total: int = Field(..., description="会话总数")


class DocumentReadinessResponse(BaseModel):
    """文书生成就绪状态。"""

    ready: bool = Field(..., description="助手是否已明确提示可以生成诉状")
    missing_fields: List[str] = Field(default_factory=list, description="未满足条件时的提示项")
    collected_fields: Dict[str, str] = Field(default_factory=dict, description="当前命中的就绪信号")
