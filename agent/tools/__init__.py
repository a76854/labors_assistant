from .doc_generator import generate_legal_doc_tool
from .legal_search import search_law_tool

# Backward-compatible alias for older imports.
generate_doc_tool = generate_legal_doc_tool

__all__ = [
    "search_law_tool",
    "generate_legal_doc_tool",
    "generate_doc_tool",
]
