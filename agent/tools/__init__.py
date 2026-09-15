from .doc_generator import generate_legal_doc_tool
from .legal_search import (
    search_law_tool,
    search_private_knowledge_tool,
    search_public_cases_tool,
    search_public_laws_tool,
)

# Backward-compatible alias for older imports.
generate_doc_tool = generate_legal_doc_tool

# 供 LLM 绑定与 LangGraph ToolNode 使用的工具注册表。
tools_list = [
    search_public_laws_tool,
    search_public_cases_tool,
    search_private_knowledge_tool,
    generate_legal_doc_tool,
]

__all__ = [
    "search_law_tool",
    "search_public_laws_tool",
    "search_public_cases_tool",
    "search_private_knowledge_tool",
    "generate_legal_doc_tool",
    "generate_doc_tool",
    "tools_list",
]
