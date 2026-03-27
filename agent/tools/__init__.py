<<<<<<< HEAD
<<<<<<< HEAD
=======
# ============================================================================
# __init__.py - Tools 模块初始化
# ============================================================================
# 集中导出所有工具函数，方便在 agent_node 中使用
# ============================================================================

>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
from .legal_search import search_law_tool
from .doc_generator import generate_legal_doc_tool

# Backward-compatible alias for older imports.
generate_doc_tool = generate_legal_doc_tool

__all__ = [
    "search_law_tool",
    "generate_legal_doc_tool",
    "generate_doc_tool",
]
