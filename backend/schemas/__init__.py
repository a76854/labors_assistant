"""Pydantic 数据验证 schemas（请求/响应模型）聚合入口。"""

from backend.schemas.admin import (
    AdminLeadListItem, AdminLeadListResponse, AdminSessionListItem,
    AdminSessionListResponse, AdminStatsResponse, AdminUserListItem, AdminUserListResponse,
)
from backend.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from backend.schemas.case import (
    ApplicableLaw, CaseElementsResponse, CaseElementsUpdateRequest, Claim, DefendantInfo, PlaintiffInfo,
)
from backend.schemas.common import ErrorResponse
from backend.schemas.document import DocumentExportRequest, DocumentGenerateRequest, DocumentResponse
from backend.schemas.lawyer import (
    LeadActionResponse, LeadDetailResponse, LeadListItem, LeadListResponse,
    LeadMarketListResponse, LeadRecommendation, LeadRecommendationListResponse,
    MaterialRequestCreate, MaterialRequestResponse,
)
from backend.schemas.message import (
    ChatHistoryResponse, MessageCreateRequest, MessageResponse, MessageSyncItem, MessageSyncRequest,
)
from backend.schemas.region import RegionInfo, RegionListResponse
from backend.schemas.search import CaseSearchRequest, CaseSearchResult, LawSearchRequest, LawSearchResult
from backend.schemas.session import (
    DocumentReadinessResponse, SessionCreateRequest, SessionListItem, SessionListResponse, SessionResponse,
)
from backend.schemas.template import TemplateResponse
from backend.schemas.triage import LawyerProfile, TriageResponse

__all__ = [
    "AdminLeadListItem",
    "AdminLeadListResponse",
    "AdminSessionListItem",
    "AdminSessionListResponse",
    "AdminStatsResponse",
    "AdminUserListItem",
    "AdminUserListResponse",
    "ApplicableLaw",
    "CaseElementsResponse",
    "CaseElementsUpdateRequest",
    "CaseSearchRequest",
    "CaseSearchResult",
    "ChatHistoryResponse",
    "Claim",
    "DefendantInfo",
    "DocumentExportRequest",
    "DocumentGenerateRequest",
    "DocumentReadinessResponse",
    "DocumentResponse",
    "ErrorResponse",
    "LawSearchRequest",
    "LawSearchResult",
    "LawyerProfile",
    "LeadActionResponse",
    "LeadDetailResponse",
    "LeadListItem",
    "LeadListResponse",
    "LeadMarketListResponse",
    "LeadRecommendation",
    "LeadRecommendationListResponse",
    "LoginRequest",
    "MaterialRequestCreate",
    "MaterialRequestResponse",
    "MessageCreateRequest",
    "MessageResponse",
    "MessageSyncItem",
    "MessageSyncRequest",
    "PlaintiffInfo",
    "RegionInfo",
    "RegionListResponse",
    "RegisterRequest",
    "SessionCreateRequest",
    "SessionListItem",
    "SessionListResponse",
    "SessionResponse",
    "TemplateResponse",
    "TokenResponse",
    "TriageResponse",
    "UserResponse",
]
