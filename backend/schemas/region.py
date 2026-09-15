"""地区 Schemas"""

from pydantic import BaseModel, Field
from typing import List


class RegionInfo(BaseModel):
    """地区信息。"""
    key: str = Field(..., description="地区标识")
    name: str = Field(..., description="地区名称")
    institution: str = Field(..., description="仲裁/管辖机构名称")
    note: str = Field(default="", description="格式说明")


class RegionListResponse(BaseModel):
    """地区列表响应。"""
    regions: List[RegionInfo] = Field(..., description="地区列表")
