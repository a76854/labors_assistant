"""超级管理员 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from backend.schemas.lawyer import LeadListItem


class AdminStatsResponse(BaseModel):
    """管理员数据概览。"""
    total_users: int = Field(..., description="用户总数")
    total_lawyers: int = Field(..., description="律师数")
    total_workers: int = Field(..., description="劳动者数")
    total_sessions: int = Field(..., description="会话数")
    total_leads: int = Field(..., description="线索数")
    open_leads: int = Field(..., description="待接单线索")
    claimed_leads: int = Field(..., description="已接单线索")
    completed_leads: int = Field(..., description="已完成线索")
    total_documents: int = Field(..., description="文档数")
    generated_documents: int = Field(..., description="已生成文档数")


class AdminUserListItem(BaseModel):
    """管理员用户列表项。"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="角色")
    name: Optional[str] = Field(None, description="姓名")
    phone: Optional[str] = Field(None, description="电话")
    specialty: Optional[List[str]] = Field(None, description="擅长案由")
    region: Optional[str] = Field(None, description="地区")
    created_at: datetime = Field(..., description="注册时间")
    session_count: int = Field(default=0, description="会话数")
    lead_count: int = Field(default=0, description="线索数")


class AdminUserListResponse(BaseModel):
    """管理员用户列表响应。"""
    users: List[AdminUserListItem] = Field(..., description="用户列表")
    total: int = Field(..., description="用户总数")


class AdminLeadListItem(LeadListItem):
    """管理员线索列表项（含发布者/接单律师）。"""
    user_username: Optional[str] = Field(None, description="发布者用户名")
    lawyer_username: Optional[str] = Field(None, description="接单律师用户名")


class AdminLeadListResponse(BaseModel):
    """管理员线索列表响应。"""
    leads: List[AdminLeadListItem] = Field(..., description="线索列表")
    total: int = Field(..., description="总数")


class AdminSessionListItem(BaseModel):
    """管理员会话列表项。"""
    id: str = Field(..., description="会话ID")
    case_type: str = Field(..., description="案件类型")
    region: Optional[str] = Field(None, description="地区")
    status: str = Field(..., description="会话状态")
    user_username: Optional[str] = Field(None, description="所属用户")
    message_count: int = Field(default=0, description="消息数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class AdminSessionListResponse(BaseModel):
    """管理员会话列表响应。"""
    sessions: List[AdminSessionListItem] = Field(..., description="会话列表")
    total: int = Field(..., description="总数")
