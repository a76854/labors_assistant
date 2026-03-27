import os
import re

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
    """主节点：组装约束后调用 LLM，并返回单条响应消息。"""

    system_message = SystemMessage(content=SYSTEM_PROMPT)

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

    dynamic_message = SystemMessage(content="\n".join(dynamic_rules)) if dynamic_rules else None

    messages_with_system = [system_message] + ([dynamic_message] if dynamic_message else []) + state["messages"]

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
            forced_messages = [system_message] + ([dynamic_message] if dynamic_message else []) + [forced_rule] + state["messages"]
            response = llm_with_tools.invoke(forced_messages)

    return {"messages": [response]}
