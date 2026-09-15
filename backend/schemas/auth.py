"""用户认证 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RegisterRequest(BaseModel):
    """注册请求。"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    role: str = Field(default="user", description="角色，取值范围: user|lawyer")
    name: Optional[str] = Field(None, max_length=50, description="姓名/机构名称")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    specialty: Optional[List[str]] = Field(None, description="律师擅长案由（律师角色填）")
    region: Optional[str] = Field(None, description="所在地区（律师角色填）")


class LoginRequest(BaseModel):
    """登录请求。"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户信息响应。"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="角色")
    name: Optional[str] = Field(None, description="姓名")
    phone: Optional[str] = Field(None, description="联系电话")
    specialty: Optional[List[str]] = Field(None, description="擅长案由")
    region: Optional[str] = Field(None, description="所在地区")
    created_at: datetime = Field(..., description="注册时间")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登录令牌响应。"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")
