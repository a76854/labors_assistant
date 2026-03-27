# ============================================================================
# calculator.py - 法律赔偿金计算工具
# ============================================================================
# 根据法律规定，自动计算各类赔偿金额
# 支持：违约金、侵权赔偿、劳动赔偿、交通事故赔偿等
# ============================================================================

from typing import Optional, Dict, Any
from langchain_core.tools import tool


# ============================================================================
# 综合赔偿计算工具
# ============================================================================
@tool(return_direct=False)
def calculate_compensation(
    case_type: str,
    base_amount: float,
    calculation_factors: Optional[str] = None,
) -> str:
    """
    计算法律赔偿金额
    
    根据案件类型和法律规定，自动计算应赔偿金额。
    支持多种案件类型的赔偿计算。
    
    参数说明：
    -----------
    case_type : str
        案件类型，必填。支持的类型包括：
        
        违约类：
        - "contract_breach": 合同违约赔偿
        - "breach_with_penalty": 带有违约金条款的违约
        
        侵权类：
        - "property_damage": 财产损害赔偿
        - "personal_injury": 人身伤害赔偿
        - "reputation_damage": 名誉毁损赔偿
        - "privacy_violation": 隐私侵害赔偿
        
        劳动类：
        - "unlawful_dismissal": 非法解除劳动合同
        - "work_injury": 工伤事故赔偿
        - "unpaid_wages": 拖欠工资赔偿
        
        交通类：
        - "traffic_accident": 交通事故赔偿
        - "vehicle_damage": 车辆损害赔偿
        
        其他：
        - "consumer_rights": 消费者权益侵害赔偿
        - "fraud": 欺诈成立的赔偿
    
    base_amount : float
        基础计算数额，单位为元。含义根据 case_type 而定：
        
        - contract_breach: 合同价款或约定赔偿额
        - property_damage: 财产实际损失额
        - personal_injury: 医疗费、误工费等基础费用
        - unpaid_wages: 拖欠的工资总額
        - traffic_accident: 医疗费或车辆维修费
        
        示例值：50000 （表示50,000元）
    
    calculation_factors : str, optional
        影响赔偿计算的因素，用逗号或换行分隔。
        应包含以下信息：
        
        通用因素：
        - "过错程度=轻微|一般|严重"（用于过错赔偿）
        - "过错比例=30%"（多方责任情况）
        - "守法性=守法|违法"（是否违反法律）
        
        违约类特有因素：
        - "约定违约金=5万元"
        - "法定利息率=4.8%"
        - "延迟履行天数=60"
        
        人身伤害特有因素：
        - "伤残等级=一级|二级|...十级"
        - "城镇居民年均收入=60000"
        - "被扶养人数=2"
        - "被扶养人年收入=30000"
        - "生活费支出比例=30%"
        
        交通事故特有因素：
        - "责任比例=70%"（本方责任占比）
        - "保险赔偿额=50000"
        - "医疗费=20000"
        - "误工天数=100"
        - "日工资=500"
        
        示例：
        "过错程度=严重,延迟履行天数=60,法定利息率=4.8%"
    
    返回值：
    -------
    str
        包含以下内容的赔偿计算结果：
        - 赔偿项目明细表
        - 各项费用的具体计算过程
        - 适用的法律条款
        - 最终赔偿总額
        - 支付期限建议（如有）
        
        格式为易读的中文文本，包括具体数字和法律依据
    
    使用场景：
    --------
    1. 合同违约赔偿（包含违约金条款）
       calculate_compensation(
           case_type="breach_with_penalty",
           base_amount=100000,
           calculation_factors="约定违约金=5万元,延迟履行天数=30,法定利息率=4.8%"
       )
       
       返回：违约金为5万元，加上逾期付款利息约1200元，
             总赔偿额约51,200元
    
    2. 工伤事故赔偿（含伤残等级）
       calculate_compensation(
           case_type="work_injury",
           base_amount=200000,
           calculation_factors="伤残等级=五级,城镇职工平均工资=80000"
       )
       
       返回：一次性伤残补助金、一次性工伤医疗补助金等，
             总额计算清单
    
    3. 交通事故责任赔偿
       calculate_compensation(
           case_type="traffic_accident",
           base_amount=50000,
           calculation_factors="责任比例=60%,医疗费=30000,误工天数=30,日工资=400"
       )
       
       返回：按本方责任比例计算的赔偿额，包括医疗费、
             误工费等明细
    
    4. 人身伤害赔偿（含被扶养人）
       calculate_compensation(
           case_type="personal_injury",
           base_amount=100000,
           calculation_factors=\"\"\"
           伤残等级=八级
           城镇居民年均收入=70000
           被扶养人数=1
           被扶养人年收入=0
           被扶养人生活费支出比例=30%
           \"\"\"
       )
    
    注意事项：
    --------
    - 计算结果仅供参考，具体赔偿额以法院判决为准
    - 不同地区的伤残赔偿标准可能有差异
    - 复杂案件建议咨询专业律师
    - 计算使用的费用标准应基于最新的法律规定
    
    【法律依据举例】
    - 违约赔偿：《民法典》第五百八十条、第五百八十二条
    - 伤残赔偿：《民法典》第一千一百七十九条、第一千一百八十六条
    - 工伤赔偿：《工伤保险条例》
    - 交通事故：《民法典》第一千二百一十二条等
    
    示例代码：
    ----------
    # 示例 1：简单的合同违约赔偿
    result = calculate_compensation(
        case_type="contract_breach",
        base_amount=100000,
        calculation_factors="过错程度=严重,法定利息率=4.8%"
    )
    
    # 示例 2：工伤事故综合赔偿
    result = calculate_compensation(
        case_type="work_injury",
        base_amount=50000,
        calculation_factors=\"\"\"
        伤残等级=七级
        城镇职工平均工资=90000
        \"\"\"
    )
    
    # 示例 3：交通事故责任赔偿
    result = calculate_compensation(
        case_type="traffic_accident",
        base_amount=200000,
        calculation_factors=\"\"\"
        责任比例=100%
        医疗费=50000
        误工天数=90
        日工资=600
        被扶养人抚养费=1000/月
        \"\"\"
    )
    """
    
    # ========================================================================
    # 【第一阶段】参数验证
    # ========================================================================
    valid_case_types = {
        "contract_breach", "breach_with_penalty", "property_damage",
        "personal_injury", "reputation_damage", "privacy_violation",
        "unlawful_dismissal", "work_injury", "unpaid_wages",
        "traffic_accident", "vehicle_damage", "consumer_rights", "fraud"
    }
    
    if case_type not in valid_case_types:
        return f"错误：不支持的案件类型 '{case_type}'"
    
    if base_amount <= 0:
        return "错误：基础金额必须大于 0"
    
    # ========================================================================
    # 【第二阶段】参数解析
    # ========================================================================
    factors = {}
    if calculation_factors:
        # 解析以逗号或换行分隔的因素
        factor_items = calculation_factors.replace('\n', ',').split(',')
        for item in factor_items:
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                factors[key.strip()] = value.strip()
    
    # ========================================================================
    # 【第三阶段】赔偿计算（占位符实现）
    # ========================================================================
    # 实际部署时，这里会根据具体的法律条款进行精确计算
    # 当前提供模拟实现
    
    mock_calculation = f"""
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

【支付建议】
建议债务人在判决生效之日起 15 日内支付上述款项，
逾期按照法律规定支付逾期利息。

【免责说明】
此计算为 AI 自动生成，仅供参考。
实际赔偿额以法院判决书为准。
复杂案件应咨询专业律师。

【更新于】: 2024年
"""
    
    return mock_calculation


# ============================================================================
# 辅助函数：格式化因素显示
# ============================================================================
def format_factors(factors: Dict[str, str]) -> str:
    """
    将因素字典格式化为可读的文本
    """
    if not factors:
        return "  (未提供额外因素)"
    
    lines = []
    for key, value in factors.items():
        lines.append(f"  • {key}: {value}")
    
    return '\n'.join(lines)


# ============================================================================
# 特定类型的赔偿计算（便利函数）
# ============================================================================
@tool(return_direct=False)
def calculate_injury_compensation(
    injury_level: str,
    avg_annual_income: float,
    num_dependents: int = 0,
) -> str:
    """
    计算人身伤害赔偿（包括伤残等级）
    
    参数：
    -----
    injury_level : str
        伤害等级，从"一级"到"十级"，或"death"
    avg_annual_income : float
        受害人（或城镇居民）年均收入
    num_dependents : int
        被扶养人数量
    
    返回：
    -----
    str
        详细的伤害赔偿计算清单
    """
    
    if not injury_level or avg_annual_income <= 0:
        return "错误：参数无效"
    
    # 模拟实现
    mock_result = f"""
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

【详细计算过程】
...提供具体计算数字...

【合计赔偿额】
¥XXX,XXX.XX
    """
    
    return mock_result


@tool(return_direct=False)
def calculate_wage_compensation(
    unpaid_amount: float,
    months_delayed: int,
    base_monthly_income: float,
) -> str:
    """
    计算拖欠工资赔偿（包括经济补偿金）
    
    参数：
    -----
    unpaid_amount : float
        拖欠的工资总额
    months_delayed : int
        拖欠的月数
    base_monthly_income : float
        月均工资
    
    返回：
    -----
    str
        拖欠工资的赔偿计算清单
    """
    
    if unpaid_amount <= 0 or months_delayed <= 0:
        return "错误：参数无效"
    
    # 模拟实现
    mock_result = f"""
【拖欠工资赔偿计算】

拖欠金额: ¥{unpaid_amount:,.2f}
拖欠月数: {months_delayed} 个月
月均工资: ¥{base_monthly_income:,.2f}

【赔偿项目】
1. 拖欠的工资: ¥{unpaid_amount:,.2f}
2. 经济补偿金: ¥{base_monthly_income * months_delayed:,.2f}
3. 赔偿金（如有）: ¥{unpaid_amount * 0.5:,.2f}
4. 逾期利息: ¥{unpaid_amount * 0.05 * months_delayed:,.2f}

【合计赔偿】
¥{unpaid_amount + base_monthly_income * months_delayed + unpaid_amount * 0.5 + unpaid_amount * 0.05 * months_delayed:,.2f}

【法律依据】
《劳动法》《劳动合同法》相关条款
    """
    
    return mock_result
