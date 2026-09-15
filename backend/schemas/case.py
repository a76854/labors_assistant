"""案件要素提取 Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PlaintiffInfo(BaseModel):
    """原告信息。

    用于提取劳动者一方的基础身份与工作信息。
    """
    name: Optional[str] = Field(None, description="姓名")
    id_number: Optional[str] = Field(None, description="身份证号")
    contact: Optional[str] = Field(None, description="联系方式")
    position: Optional[str] = Field(None, description="岗位或职务")
    company: Optional[str] = Field(None, description="所属公司")


class DefendantInfo(BaseModel):
    """被告信息。

    通常指用人单位或相关责任主体的信息。
    """
    name: Optional[str] = Field(None, description="名称")
    id_number: Optional[str] = Field(None, description="统一社会信用代码或身份证号")
    address: Optional[str] = Field(None, description="地址")
    contact: Optional[str] = Field(None, description="联系方式")


class Claim(BaseModel):
    """诉讼请求。

    用于结构化表示用户主张的核心诉求，例如工资、赔偿或损失。
    """
    type: str = Field(..., description="请求类型，取值范围: salary|compensation|damages")
    amount: Optional[float] = Field(None, description="金额，单位通常为人民币")
    description: str = Field(..., description="请求说明")


class ApplicableLaw(BaseModel):
    """适用法律。

    用于记录案件分析时引用的法律依据。
    """
    law: str = Field(..., description="法律名称")
    article: str = Field(..., description="法条编号，例如 第50条")
    content: str = Field(..., description="法条内容摘要")


class CaseElementsResponse(BaseModel):
    """案件要素提取响应。

    这是对聊天内容做结构化抽取后的结果，供后续生成诉状、校验要件和展示摘要。
    """
    session_id: str = Field(..., description="会话ID")
    plaintiff: Optional[Dict[str, Any]] = Field(None, description="原告信息")
    defendant: Optional[Dict[str, Any]] = Field(None, description="被告信息")
    facts: Optional[List[str]] = Field(None, description="案件事实列表")
    claims: Optional[List[Dict[str, Any]]] = Field(None, description="诉讼请求列表")
    applicable_laws: Optional[List[Dict[str, Any]]] = Field(None, description="适用法律列表")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="抽取结果置信度，范围 0 到 1")


class CaseElementsUpdateRequest(BaseModel):
    """更新案件要素请求。

    前端可在人工校正抽取结果后提交该结构，覆盖已有的案件要素。
    """
    plaintiff: Optional[Dict[str, Any]] = Field(None, description="原告信息")
    defendant: Optional[Dict[str, Any]] = Field(None, description="被告信息")
    facts: Optional[List[str]] = Field(None, description="案件事实列表")
    claims: Optional[List[Dict[str, Any]]] = Field(None, description="诉讼请求列表")
    applicable_laws: Optional[List[Dict[str, Any]]] = Field(None, description="适用法律列表")
