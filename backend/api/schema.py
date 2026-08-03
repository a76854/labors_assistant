"""
Pydantic 数据验证schemas（请求/响应模型）
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from backend.utils.timezone import now_beijing


# ============================================================================
# 会话相关 Schemas
# ============================================================================

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


# ============================================================================
# 消息/对话相关 Schemas
# ============================================================================

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


# ============================================================================
# 案件要素提取 Schemas
# ============================================================================

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


# ============================================================================
# 文档生成 Schemas
# ============================================================================

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


# ============================================================================
# 模板 Schemas
# ============================================================================

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


# ============================================================================
# 错误响应 Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """错误响应。

    统一前后端错误返回格式，便于展示和日志定位。
    """
    code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=now_beijing, description="错误发生时间")


# ============================================================================
# 搜索相关 Schemas
# ============================================================================

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


# ============================================================================
# 用户认证 Schemas
# ============================================================================

class RegisterRequest(BaseModel):
    """注册请求。"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    role: str = Field(default="user", description="角色，取值范围: user|lawyer")
    name: Optional[str] = Field(None, max_length=50, description="姓名/机构名称")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")


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
    created_at: datetime = Field(..., description="注册时间")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登录令牌响应。"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")


# ============================================================================
# 案件分诊 Schemas
# ============================================================================

class LawyerProfile(BaseModel):
    """律师信息（推荐用）。"""
    id: str = Field(..., description="律师ID")
    name: str = Field(..., description="姓名")
    license_no: str = Field(default="", description="执业证号")
    specialties: List[str] = Field(default_factory=list, description="擅长案由")
    years: int = Field(default=0, description="执业年限")
    rating: float = Field(default=0.0, description="评分")
    desc: str = Field(default="", description="简介")


class TriageResponse(BaseModel):
    """案件分诊结果。"""
    session_id: str = Field(..., description="会话ID")
    case_type: str = Field(..., description="案件类型")
    region: Optional[str] = Field("beijing", description="地区")
    evidence_score: int = Field(..., description="证据完整度 0-100")
    evidence_covered: List[str] = Field(default_factory=list, description="已覆盖的证据类别")
    missing_evidence: List[str] = Field(default_factory=list, description="缺失证据类别")
    risk_score: int = Field(..., description="风险评分 0-100")
    complexity: str = Field(..., description="复杂度: high|medium|low")
    recommended_lawyers: List[LawyerProfile] = Field(default_factory=list, description="推荐律师")


# ============================================================================
# 律师后台 Schemas
# ============================================================================

class LeadListItem(BaseModel):
    """律师线索列表项。"""
    id: str = Field(..., description="线索ID")
    session_id: str = Field(..., description="会话ID")
    status: str = Field(..., description="线索状态: open|claimed|completed")
    case_type: str = Field(..., description="案件类型")
    region: Optional[str] = Field("beijing", description="地区")
    evidence_score: Optional[int] = Field(None, description="证据完整度")
    risk_score: Optional[int] = Field(None, description="风险评分")
    complexity: Optional[str] = Field(None, description="复杂度")
    missing_evidence: Optional[List[str]] = Field(None, description="缺失证据")
    summary: Optional[str] = Field(None, description="案情摘要（脱敏）")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    material_request_count: int = Field(default=0, description="补充材料请求数")

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """线索列表响应。"""
    leads: List[LeadListItem] = Field(..., description="线索列表")
    total: int = Field(..., description="线索总数")


class LeadDetailResponse(LeadListItem):
    """线索详情。"""
    user_username: Optional[str] = Field(None, description="线索发布者用户名（脱敏）")
    user_phone: Optional[str] = Field(None, description="发布者联系电话（脱敏）")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="对话摘要（最近10条）")
    material_requests: List[Dict[str, Any]] = Field(default_factory=list, description="补充材料请求列表")


class MaterialRequestCreate(BaseModel):
    """发起补充材料请求。"""
    items: List[Dict[str, str]] = Field(..., description="材料清单，如 [{name, description}]")
    note: Optional[str] = Field(None, description="律师备注")


class LeadActionResponse(BaseModel):
    """线索操作响应。"""
    id: str = Field(..., description="线索ID")
    status: str = Field(..., description="操作后的状态")
    message: str = Field(..., description="操作结果说明")


class MaterialRequestResponse(BaseModel):
    """补充材料请求响应。"""
    id: str = Field(..., description="请求ID")
    lead_id: str = Field(..., description="线索ID")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="材料清单")
    note: Optional[str] = Field(None, description="备注")
    status: str = Field(..., description="状态: pending|satisfied")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# ============================================================================
# 地区 Schemas
# ============================================================================

class RegionInfo(BaseModel):
    """地区信息。"""
    key: str = Field(..., description="地区标识")
    name: str = Field(..., description="地区名称")
    institution: str = Field(..., description="仲裁/管辖机构名称")
    note: str = Field(default="", description="格式说明")


class RegionListResponse(BaseModel):
    """地区列表响应。"""
    regions: List[RegionInfo] = Field(..., description="地区列表")
