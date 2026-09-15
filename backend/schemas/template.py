"""模板 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List


class TemplateResponse(BaseModel):
    """模板响应。

    用于展示可用模板列表，帮助前端选择文书生成模板。
    """
    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    case_type: str = Field(..., description="对应案件类型")
    description: Optional[str] = Field(None, description="模板说明")
    fields: Optional[List[str]] = Field(None, description="模板需要的字段列表")
    example_content: Optional[str] = Field(None, description="模板示例内容")

    class Config:
        from_attributes = True
