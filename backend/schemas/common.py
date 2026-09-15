"""错误响应 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from backend.utils.timezone import now_beijing


class ErrorResponse(BaseModel):
    """错误响应。

    统一前后端错误返回格式，便于展示和日志定位。
    """
    code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=now_beijing, description="错误发生时间")
