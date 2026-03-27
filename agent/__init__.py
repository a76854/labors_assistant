# ============================================================================
# __init__.py - Agent 模块初始化
# ============================================================================
# 这个文件使 agent 目录成为 Python 包
# 可以在这里集中导出主要的类和函数
# ============================================================================

from .state import AgentState, LawsuitElementsSchema
from .prompts import SYSTEM_PROMPT

__all__ = [
    # 状态模型
    "AgentState",
    "LawsuitElementsSchema",
    "SYSTEM_PROMPT",
]
