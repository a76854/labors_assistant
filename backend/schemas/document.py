"""文档生成 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentGenerateRequest(BaseModel):
    """生成文档请求。

    用于根据会话内容和模板生成诉状或其他法律文书。
    """
    template_id: str = Field(..., description="模板ID，取值范围: wage_arrears|labor_contract|work_injury")
    format: str = Field(default="docx", description="输出格式，取值范围: docx|pdf")


class DocumentResponse(BaseModel):
    """文档响应。

    描述系统生成出来的文书，以及它的状态、内容和文件信息。
    """
    id: str = Field(..., description="文档ID")
    session_id: str = Field(..., description="所属会话ID")
    template_id: str = Field(..., description="使用的模板ID")
    title: Optional[str] = Field(None, description="文档标题")
    status: str = Field(..., description="文档状态，取值范围: pending|generated|exported")
    content: Optional[str] = Field(None, description="文档正文或结构化内容")
    file_url: Optional[str] = Field(None, description="文件下载地址")
    file_size: Optional[int] = Field(None, description="文件大小，单位字节")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    class Config:
        from_attributes = True


class DocumentExportRequest(BaseModel):
    """导出文档请求。"""
    format: str = Field(default="docx", description="导出格式，取值范围: docx|pdf")
    include_metadata: bool = Field(default=True, description="导出时是否包含元数据")
