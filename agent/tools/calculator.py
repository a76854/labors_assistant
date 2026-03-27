from typing import Dict, Optional

from langchain_core.tools import tool


@tool(return_direct=False)
def calculate_compensation(
    case_type: str,
    base_amount: float,
    calculation_factors: Optional[str] = None,
) -> str:
    """综合赔偿计算工具（示例实现）。"""
    valid_case_types = {
        "contract_breach",
        "breach_with_penalty",
        "property_damage",
        "personal_injury",
        "reputation_damage",
        "privacy_violation",
        "unlawful_dismissal",
        "work_injury",
        "unpaid_wages",
        "traffic_accident",
        "vehicle_damage",
        "consumer_rights",
        "fraud",
    }

    if case_type not in valid_case_types:
        return f"错误：不支持的案件类型 '{case_type}'"
    if base_amount <= 0:
        return "错误：基础金额必须大于 0"

    factors: Dict[str, str] = {}
    if calculation_factors:
        for item in calculation_factors.replace("\n", ",").split(","):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                factors[key.strip()] = value.strip()

    return f"""
【法律赔偿金计算明细表】

【案件类型】: {case_type}
【基础金额】: ¥{base_amount:,.2f}

【影响因素】
{format_factors(factors)}

【赔偿项目明细】
├─ 项目 1：基础赔偿额
│  金额：¥{base_amount:,.2f}
│  依据：根据案件类型的法律规定
│
├─ 项目 2：增加/减少因素调整
│  调整额：¥{base_amount * 0.1:,.2f}
│  依据：考虑过错程度、责任比例等
│
└─ 项目 3：其他费用（如诉讼费、律师费）
   金额：待确认
   依据：根据具体案件情况

【最终赔偿总额】
═══════════════════════════════════════
  ¥{base_amount * 1.1:,.2f}
═══════════════════════════════════════
"""


def format_factors(factors: Dict[str, str]) -> str:
    """格式化计算影响因素。"""
    if not factors:
        return "  (未提供额外因素)"
    return "\n".join([f"  • {key}: {value}" for key, value in factors.items()])


@tool(return_direct=False)
def calculate_injury_compensation(
    injury_level: str,
    avg_annual_income: float,
    num_dependents: int = 0,
) -> str:
    """人身伤害赔偿计算工具（示例实现）。"""
    if not injury_level or avg_annual_income <= 0:
        return "错误：参数无效"

    return f"""
【人身伤害赔偿计算】

伤害等级: {injury_level}
年均收入: ¥{avg_annual_income:,.2f}
被扶养人: {num_dependents} 人

【计算清单】
1. 一次性伤残补助金
2. 一次性工伤医疗补助金
3. 一次性伤残就业补助金
4. 被扶养人生活费（如有）
5. 精神损害赔偿
6. 其他费用
"""


@tool(return_direct=False)
def calculate_wage_compensation(
    unpaid_amount: float,
    months_delayed: int,
    base_monthly_income: float,
) -> str:
    """拖欠工资赔偿计算工具（示例实现）。"""
    if unpaid_amount <= 0 or months_delayed <= 0:
        return "错误：参数无效"

    total = (
        unpaid_amount
        + base_monthly_income * months_delayed
        + unpaid_amount * 0.5
        + unpaid_amount * 0.05 * months_delayed
    )
    return f"""
【拖欠工资赔偿计算】

拖欠金额: ¥{unpaid_amount:,.2f}
拖欠月数: {months_delayed} 个月
月均工资: ¥{base_monthly_income:,.2f}

【合计赔偿】
¥{total:,.2f}
"""
