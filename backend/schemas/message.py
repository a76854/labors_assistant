"""消息/对话相关 Schemas"""

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class MessageCreateRequest(BaseModel):
    """发送消息请求。

    用户在会话中提交一条消息时使用，通常是事实补充、问题描述或材料说明。
    """
    content: str = Field(..., min_length=1, description="消息内容")


class MessageSyncItem(BaseModel):
    """前端同步到数据库的消息项。"""

    role: str = Field(..., description="消息角色，取值范围: user|assistant")
    content: str = Field(..., min_length=1, description="消息内容")


class MessageSyncRequest(BaseModel):
    """消息同步请求。"""

    messages: List[MessageSyncItem] = Field(..., min_length=1, description="需要持久化的消息列表")


class MessageResponse(BaseModel):
    """消息响应。

    用于渲染对话气泡，区分用户消息和助手回复。
    """
    id: str = Field(..., description="消息ID")
    session_id: str = Field(..., description="所属会话ID")
    role: str = Field(..., description="消息角色，取值范围: user|assistant")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(..., description="消息创建时间")

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """对话历史响应。

    返回某个会话下的消息列表，供聊天窗口回显历史消息。
    """
    session_id: str = Field(..., description="会话ID")
    messages: List[MessageResponse] = Field(..., description="消息列表")
    total: int = Field(..., description="消息总数")
