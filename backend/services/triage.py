"""
案件分诊与风险评分服务

规则启发式实现（不依赖 LLM）：
1. 证据完整度 evidence_score (0-100)：扫描会话消息中的证据类别关键词覆盖度
2. 风险评分 risk_score (0-100)：案由基础风险 + 证据缺失惩罚 + 金额档位 + 要素缺失
3. 复杂度 complexity：由风险评分映射 high / medium / low
4. 律师推荐：按案由从内置律师库筛选后随机推荐

评分规则可解释、可单测，便于比赛答辩说明。
"""

import random
import re
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from backend.db.models import Lead, Message, Session as SessionModel
from backend.services.chat import ChatService


# ============================================================================
# 证据类别定义
# ============================================================================

EVIDENCE_CATEGORIES: List[Dict[str, Any]] = [
    {
        "key": "labor_contract",
        "name": "劳动合同",
        "keywords": ["劳动合同", "劳务合同", "聘用合同", "劳动合同书", "offer"],
        "case_types": ["wage_arrears", "labor_contract", "work_injury"],
    },
    {
        "key": "payroll",
        "name": "工资记录/银行流水",
        "keywords": ["工资条", "工资单", "工资流水", "银行流水", "转账记录", "工资发放", "打卡工资"],
        "case_types": ["wage_arrears", "labor_contract"],
    },
    {
        "key": "attendance",
        "name": "考勤记录",
        "keywords": ["考勤", "打卡", "钉钉", "企业微信", "排班"],
        "case_types": ["wage_arrears", "labor_contract"],
    },
    {
        "key": "chat_records",
        "name": "聊天/沟通记录",
        "keywords": ["聊天记录", "微信记录", "短信", "邮件", "微信截图", "通话录音"],
        "case_types": ["wage_arrears", "labor_contract", "work_injury"],
    },
    {
        "key": "work_identity",
        "name": "工作身份证明",
        "keywords": ["工牌", "工服", "名片", "工作证", "社保", "公积金", "工作照片", "工资卡"],
        "case_types": ["wage_arrears", "labor_contract", "work_injury"],
    },
    {
        "key": "termination",
        "name": "解除/辞退通知",
        "keywords": ["辞退通知", "解除通知", "离职证明", "开除", "劝退", "解除劳动合同通知书"],
        "case_types": ["labor_contract"],
    },
    {
        "key": "injury_proof",
        "name": "工伤认定材料",
        "keywords": ["工伤认定", "工伤认定书", "职业病", "诊断证明", "病历", "医疗费票据", "住院记录", "伤残鉴定"],
        "case_types": ["work_injury"],
    },
    {
        "key": "arbitration",
        "name": "仲裁/诉讼材料",
        "keywords": ["仲裁裁决", "仲裁受理", "法院判决", "判决书", "裁决书"],
        "case_types": ["wage_arrears", "labor_contract", "work_injury"],
    },
]

# 案由基础风险权重
CASE_TYPE_BASE_RISK = {
    "wage_arrears": 35,
    "labor_contract": 30,
    "work_injury": 45,
}

# 金额档位风险加分
AMOUNT_BRACKETS = [
    (1_000_000, 20),
    (500_000, 15),
    (100_000, 10),
    (10_000, 5),
]

# 元素提取正则
_AMOUNT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(万元|万|元)")
_COMPANY_KEYWORDS = ("公司", "单位", "企业", "工厂", "个体户")
_NAME_RE = re.compile(r"(?:我叫|我是|本人姓|劳动者)\s*([\u4e00-\u9fa5]{2,4})")

# ============================================================================
# Mock 律师库
# ============================================================================

MOCK_LAWYERS: List[Dict[str, Any]] = [
    {
        "id": "lawyer-chen",
        "name": "陈志远",
        "license_no": "13101201010987654",
        "specialties": ["wage_arrears", "labor_contract"],
        "years": 10,
        "rating": 4.9,
        "desc": "专注劳动报酬纠纷，曾代理多起群体性欠薪案件，胜诉率 90%+",
        "region": "beijing",
    },
    {
        "id": "lawyer-li",
        "name": "李婉晴",
        "specialties": ["labor_contract", "wage_arrears"],
        "license_no": "13101201010987655",
        "years": 8,
        "rating": 4.8,
        "desc": "擅长劳动合同解除、竞业限制争议，主张严谨、文书功底扎实",
        "region": "shanghai",
    },
    {
        "id": "lawyer-wang",
        "name": "王建国",
        "specialties": ["work_injury", "wage_arrears"],
        "license_no": "13101201010987656",
        "years": 12,
        "rating": 4.9,
        "desc": "工伤赔偿领域资深律师，熟悉伤残鉴定与赔偿标准",
        "region": "guangdong",
    },
    {
        "id": "lawyer-zhao",
        "name": "赵敏",
        "specialties": ["wage_arrears", "work_injury"],
        "license_no": "13101201010987657",
        "years": 6,
        "rating": 4.7,
        "desc": "青年骨干律师，擅长劳动争议调解与仲裁程序衔接",
        "region": "beijing",
    },
    {
        "id": "lawyer-sun",
        "name": "孙德胜",
        "specialties": ["wage_arrears", "labor_contract", "work_injury"],
        "license_no": "13101201010987658",
        "years": 15,
        "rating": 5.0,
        "desc": "高级合伙人，劳动法领域专家，代理案件 500+",
        "region": "shanghai",
    },
    {
        "id": "lawyer-zhou",
        "name": "周静",
        "specialties": ["labor_contract"],
        "license_no": "13101201010987659",
        "years": 5,
        "rating": 4.6,
        "desc": "专注劳动合同纠纷与女职工权益保护",
        "region": "guangdong",
    },
]


class TriageService:
    """案件分诊服务"""

    # ============================================================================
    # 证据完整度评分
    # ============================================================================

    @staticmethod
    def _extract_amount(text: str) -> float | None:
        """从文本中提取最大金额（元）。"""
        max_amount = None
        for match in _AMOUNT_RE.finditer(text):
            value = float(match.group(1))
            unit = match.group(2)
            amount = value * 10000 if unit in ("万元", "万") else value
            if max_amount is None or amount > max_amount:
                max_amount = amount
        return max_amount

    @staticmethod
    def _extract_company(text: str) -> bool:
        """是否出现用人单位信息关键词。"""
        return any(keyword in text for keyword in _COMPANY_KEYWORDS)

    @staticmethod
    def _extract_name(text: str) -> bool:
        """是否出现原告姓名（我叫/我是... 句式）。"""
        return bool(_NAME_RE.search(text))

    @staticmethod
    def _evidence_analysis(case_type: str, text: str) -> Dict[str, Any]:
        """分析证据类别覆盖情况。"""
        relevant = [
            cat for cat in EVIDENCE_CATEGORIES if case_type in cat["case_types"]
        ]
        covered = []
        missing = []
        for cat in relevant:
            if any(keyword in text for keyword in cat["keywords"]):
                covered.append({"key": cat["key"], "name": cat["name"]})
            else:
                missing.append({"key": cat["key"], "name": cat["name"]})

        total = len(relevant)
        score = round(len(covered) / total * 100) if total else 0
        return {
            "score": score,
            "covered": covered,
            "missing": missing,
            "total_categories": total,
        }

    @staticmethod
    def compute_evidence_score(case_type: str, text: str) -> Dict[str, Any]:
        """计算证据完整度 0-100。"""
        return TriageService._evidence_analysis(case_type, text)

    # ============================================================================
    # 风险评分
    # ============================================================================

    @staticmethod
    def compute_risk_score(
        case_type: str,
        evidence_score: int,
        text: str,
    ) -> int:
        """计算风险评分 0-100。"""
        score = CASE_TYPE_BASE_RISK.get(case_type, 30)

        # 证据缺失惩罚（最多 +40）
        score += round((100 - evidence_score) * 0.4)

        # 金额档位加分（证据越充分、金额越大风险越高）
        amount = TriageService._extract_amount(text)
        if amount is not None:
            for threshold, bonus in AMOUNT_BRACKETS:
                if amount >= threshold:
                    score += bonus
                    break
        else:
            # 未提及金额：要素缺失 +10
            score += 10

        # 用人单位信息缺失 +10
        if not TriageService._extract_company(text):
            score += 10

        return max(0, min(100, score))

    @staticmethod
    def complexity_of(risk_score: int) -> str:
        """由风险评分映射复杂度。"""
        if risk_score >= 70:
            return "high"
        if risk_score >= 45:
            return "medium"
        return "low"

    # ============================================================================
    # 律师推荐（Mock）
    # ============================================================================

    @staticmethod
    def recommend_lawyers(
        case_type: str, region: str | None = None, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """按案由（优先同地区）从律师库随机推荐 1~limit 名。"""
        candidates = [
            lawyer for lawyer in MOCK_LAWYERS if case_type in lawyer["specialties"]
        ]
        if region:
            same_region = [lawyer for lawyer in candidates if lawyer.get("region") == region]
            if len(same_region) >= 1:
                candidates = same_region + [
                    lawyer for lawyer in candidates if lawyer.get("region") != region
                ]
        if not candidates:
            candidates = MOCK_LAWYERS

        picked = random.sample(candidates, min(limit, len(candidates)))
        return [
            {
                "id": lawyer["id"],
                "name": lawyer["name"],
                "license_no": lawyer.get("license_no", ""),
                "specialties": lawyer["specialties"],
                "years": lawyer.get("years", 0),
                "rating": lawyer.get("rating", 0.0),
                "desc": lawyer.get("desc", ""),
            }
            for lawyer in picked
        ]

    # ============================================================================
    # 分诊主流程
    # ============================================================================

    @staticmethod
    def _session_text(db: Session, session_id: str, limit: int = 500) -> str:
        """拼接会话全部消息文本（含用户与助手）。"""
        messages = ChatService.get_messages(db, session_id, limit=limit, offset=0)
        return "\n".join(str(m.content) for m in messages)

    @staticmethod
    def compute_triage(db: Session, session_id: str) -> Dict[str, Any]:
        """计算会话的完整分诊结果。"""
        session = ChatService.get_session(db, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        text = TriageService._session_text(db, session_id)
        case_type = str(session.case_type)
        region = session.region

        evidence = TriageService.compute_evidence_score(case_type, text)
        risk_score = TriageService.compute_risk_score(case_type, evidence["score"], text)
        complexity = TriageService.complexity_of(risk_score)

        missing_names = [item["name"] for item in evidence["missing"]]
        return {
            "session_id": session_id,
            "case_type": case_type,
            "region": region,
            "evidence_score": evidence["score"],
            "evidence_covered": [item["name"] for item in evidence["covered"]],
            "missing_evidence": missing_names,
            "risk_score": risk_score,
            "complexity": complexity,
            "recommended_lawyers": TriageService.recommend_lawyers(case_type, region),
        }

    # ============================================================================
    # 线索（Lead）持久化
    # ============================================================================

    @staticmethod
    def upsert_lead(db: Session, session_id: str) -> Lead:
        """根据分诊结果 upsert 律师线索。"""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        triage = TriageService.compute_triage(db, session_id)
        lead = (
            db.query(Lead)
            .filter(Lead.session_id == session_id)
            .first()
        )
        if lead is None:
            lead = Lead(
                session_id=session_id,
                user_id=session.user_id or "",
                case_type=str(session.case_type),
                region=session.region,
                status="open",
            )
            db.add(lead)

        lead.evidence_score = triage["evidence_score"]
        lead.risk_score = triage["risk_score"]
        lead.complexity = triage["complexity"]
        lead.missing_evidence = triage["missing_evidence"]
        lead.summary = TriageService._build_summary(triage)
        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def _build_summary(triage: Dict[str, Any]) -> str:
        """构建脱敏案情摘要。"""
        missing = "、".join(triage["missing_evidence"]) if triage["missing_evidence"] else "无"
        return (
            f"{triage['case_type']}案件 | 证据完整度 {triage['evidence_score']}分 | "
            f"风险 {triage['risk_score']}分({triage['complexity']}) | 缺失证据: {missing}"
        )

    @staticmethod
    def get_lead_by_session(db: Session, session_id: str) -> Lead | None:
        """按会话查询线索。"""
        return (
            db.query(Lead)
            .filter(Lead.session_id == session_id)
            .first()
        )
