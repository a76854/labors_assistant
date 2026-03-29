import os
import re
from typing import Dict

from agent.state import AgentState
from agent.prompts import SYSTEM_PROMPT
from agent.tools.legal_search import (
    search_public_laws_tool,
    search_public_cases_tool,
    search_private_knowledge_tool,
)
from agent.tools.doc_generator import generate_legal_doc_tool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage


load_dotenv()


DEBUG_THINKING = os.getenv("DEBUG_THINKING", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# Token优化与记忆模块：滑动窗口消息裁剪，仅保留最近若干轮对话。
TRIM_WINDOW_SIZE = 6


def _trim_recent_history(messages: list, window_size: int) -> list:
    """裁剪历史消息并避免以 tool 消息开头导致协议错误。"""
    recent = messages[-window_size:]
    while recent and hasattr(recent[0], "tool_call_id"):
        recent = recent[1:]
    return recent


def _extract_elements_from_text(text: str) -> Dict[str, str]:
    """从用户文本中提取诉讼要素（增量更新）。"""
    extracted: Dict[str, str] = {}
    if not isinstance(text, str):
        return extracted

    compact = text.replace("\n", " ")
    patterns = {
        "plaintiff": [r"原告[：:]\s*([^；;。]+)", r"我叫\s*([^，,。；;]+)"],
        "defendant": [r"被告[：:]\s*([^；;。]+)"],
        "claim": [r"核心诉求[：:]\s*([^。\n]+)", r"诉求[是为：:]\s*([^。\n]+)"],
        "amount": [r"涉案金额[：:]\s*([0-9０-９,，.．]+\s*元?)", r"本金\s*([0-9０-９,，.．]+\s*元?)"],
    }

    for key, regex_list in patterns.items():
        for pattern in regex_list:
            match = re.search(pattern, compact)
            if match:
                value = match.group(1).strip()
                if value:
                    extracted[key] = value
                    break

    return extracted


def _build_whiteboard(state: AgentState) -> Dict[str, str]:
    """构建白板记忆：历史白板 + 兼容旧字段 + 最新用户输入增量提取。"""
    whiteboard: Dict[str, str] = {}

    base_elements = state.get("extracted_elements", {})
    if isinstance(base_elements, dict):
        whiteboard.update({k: str(v) for k, v in base_elements.items() if v})

    legacy_elements = state.get("extracted_info", {})
    if isinstance(legacy_elements, dict):
        for key, value in legacy_elements.items():
            if value and key not in whiteboard:
                whiteboard[key] = str(value)

    for message in state.get("messages", []):
        if message.__class__.__name__ != "HumanMessage":
            continue
        text = getattr(message, "content", "")
        updates = _extract_elements_from_text(text)
        whiteboard.update(updates)

    return whiteboard


tools_list = [
    search_public_laws_tool,
    search_public_cases_tool,
    search_private_knowledge_tool,
    generate_legal_doc_tool,
]


llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
llm_base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL")
llm_model = os.getenv("LLM_MODEL", "qwen-plus")

llm_init_kwargs = {
    "model": llm_model,
    "temperature": 0.1,
    "api_key": llm_api_key,
}
if llm_base_url:
    llm_init_kwargs["base_url"] = llm_base_url

llm = ChatOpenAI(**llm_init_kwargs)
llm_with_tools = llm.bind_tools(tools_list)


def call_agent(state: AgentState) -> dict:
    whiteboard_elements = _build_whiteboard(state)

    public_laws_call_count = 0
    public_cases_call_count = 0
    private_knowledge_call_count = 0
    generate_doc_call_count = 0
    for message in state["messages"]:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.get("name", "")
                if tool_name == "search_public_laws_tool":
                    public_laws_call_count += 1
                elif tool_name == "search_public_cases_tool":
                    public_cases_call_count += 1
                elif tool_name == "search_private_knowledge_tool":
                    private_knowledge_call_count += 1
                elif tool_name in {"generate_legal_doc_tool", "generate_doc_tool"}:
                    generate_doc_call_count += 1

    private_keywords = [
        "上传", "私域", "知识库", "内部制度", "卷宗", "借条", "流水", "合同", "证据", "地方政策",
    ]
    private_intent_required = False
    for message in state["messages"]:
        if message.__class__.__name__ != "HumanMessage":
            continue
        content = getattr(message, "content", "")
        if not isinstance(content, str):
            continue
        normalized = re.sub(r"\s+", "", content)
        if any(keyword in normalized for keyword in private_keywords):
            private_intent_required = True
            break

    dynamic_rules = []
    if public_laws_call_count >= 2:
        dynamic_rules.append(
            "你已经重复调用 search_public_laws_tool。立即停止再次调用该工具，并直接基于现有检索结果输出最终答复。"
        )
    if public_cases_call_count >= 2:
        dynamic_rules.append(
            "你已经重复调用 search_public_cases_tool。立即停止再次调用该工具，并直接基于现有检索结果输出最终答复。"
        )
    if private_knowledge_call_count >= 2:
        dynamic_rules.append(
            "你已经重复调用 search_private_knowledge_tool。立即停止再次调用该工具，并直接基于现有检索结果输出最终答复。"
        )
    if generate_doc_call_count >= 1:
        dynamic_rules.append(
            "你已经调用过 generate_legal_doc_tool。禁止再次调用任何工具，请直接输出最终收尾答复并提供文书链接。"
        )

    if public_laws_call_count >= 1 and public_cases_call_count == 0 and private_knowledge_call_count == 0:
        dynamic_rules.append(
            "你已经调用过 search_public_laws_tool。若案情属于公域检索，下一步应调用 search_public_cases_tool，禁止重复调用 search_public_laws_tool。"
        )
    if public_cases_call_count >= 1 and public_laws_call_count == 0 and private_knowledge_call_count == 0:
        dynamic_rules.append(
            "你已经调用过 search_public_cases_tool。若案情属于公域检索，下一步应调用 search_public_laws_tool，禁止重复调用 search_public_cases_tool。"
        )
    if (
        public_laws_call_count >= 1
        and public_cases_call_count >= 1
        and private_knowledge_call_count >= 1
        and generate_doc_call_count == 0
    ):
        dynamic_rules.append(
            "你已经完成公域法规、公域案例和私域知识库三类检索。现在必须先输出步骤3综合评估，再立刻调用 generate_legal_doc_tool，禁止直接结束对话。"
        )
    if (
        public_laws_call_count >= 1
        and public_cases_call_count >= 1
        and private_knowledge_call_count == 0
        and generate_doc_call_count == 0
    ):
        dynamic_rules.append(
            "你已经完成公域法规与公域案例检索。若无私域检索必要，现在必须先输出步骤3综合评估，再立刻调用 generate_legal_doc_tool，禁止直接结束对话。"
        )

    closure_ready = (
        public_laws_call_count >= 1
        and public_cases_call_count >= 1
        and generate_doc_call_count == 0
        and (
            (private_intent_required and private_knowledge_call_count >= 1)
            or (not private_intent_required)
        )
    )

    debug_instruction = ""
    if DEBUG_THINKING:
        debug_instruction = (
            "调试模式已开启。"
            "当且仅当你本轮不调用任何工具、需要直接回复用户时，"
            "请使用以下结构输出，且不要暴露完整内部推理链：\n"
            "【思考摘要】\n"
            "- 信息完整性：一句话\n"
            "- 工具决策：一句话（说明是否调用及原因）\n"
            "- 下一步：一句话\n"
            "【正式答复】\n"
            "<给用户的正式答复>\n"
            "若本轮需要调用工具，则不要输出思考摘要，直接进行工具调用。"
        )

    system_sections = [
        SYSTEM_PROMPT,
        f"当前白板上已记录的要素为：{whiteboard_elements}",
    ]
    if dynamic_rules:
        system_sections.append("动态约束：\n" + "\n".join(dynamic_rules))
    if debug_instruction:
        system_sections.append(debug_instruction)

    system_message = SystemMessage(content="\n\n".join(system_sections))
    recent_history = _trim_recent_history(state["messages"], TRIM_WINDOW_SIZE)
    messages_with_system = [system_message] + recent_history

    response = llm_with_tools.invoke(messages_with_system)

    # 关键约束：检索完成后禁止重复 search_*，优先收口到文书生成。
    if closure_ready and hasattr(response, "tool_calls") and response.tool_calls:
        called_tool_names = [tool_call.get("name", "") for tool_call in response.tool_calls]
        has_doc_call = any(name in {"generate_legal_doc_tool", "generate_doc_tool"} for name in called_tool_names)
        has_search_call = any(name.startswith("search_") for name in called_tool_names)

        if has_search_call and not has_doc_call:
            forced_rule = SystemMessage(
                content=(
                    "你已经完成进入文书生成前的必要检索。现在只允许调用 generate_legal_doc_tool，"
                    "严禁再次调用任何 search_* 检索工具。"
                )
            )
            forced_system_sections = system_sections + [forced_rule.content]
            forced_system_message = SystemMessage(content="\n\n".join(forced_system_sections))
            forced_messages = [forced_system_message] + recent_history
            response = llm_with_tools.invoke(forced_messages)

    if (
        DEBUG_THINKING
        and not (hasattr(response, "tool_calls") and response.tool_calls)
        and isinstance(getattr(response, "content", None), str)
    ):
        content = response.content.strip()
        if "【思考摘要】" not in content or "【正式答复】" not in content:
            if public_laws_call_count == 0 and public_cases_call_count == 0 and private_knowledge_call_count == 0:
                completeness_text = "关键信息尚未收集完整（未进入检索阶段）"
                decision_text = "不调用工具，先继续补齐案件要素"
                next_step_text = "继续向用户追问缺失要素（原告、被告、诉求、金额）"
            else:
                completeness_text = "基础信息已部分具备（已进入检索/分析流程）"
                decision_text = "根据当前状态决定是否调用下一工具或收口"
                next_step_text = "结合既有工具结果继续输出或进入文书生成"

            response.content = (
                "【思考摘要】\n"
                f"- 信息完整性：{completeness_text}\n"
                f"- 工具决策：{decision_text}\n"
                f"- 下一步：{next_step_text}\n\n"
                "【正式答复】\n"
                f"{content}"
            )

    return {
        "messages": [response],
        "extracted_elements": whiteboard_elements,
    }
