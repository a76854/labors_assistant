import os
import uuid
import json
from typing import Any, AsyncGenerator, Dict, List, Optional

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agent.agent_node import call_agent, tools_list
from agent.state import AgentState


DEBUG_THINKING = os.getenv("DEBUG_THINKING", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


# Token优化与记忆模块：LangGraph 内存检查点，用于线程级会话持久化。
memory = MemorySaver()


def build_workflow():
    """构建并编译 ReAct 工作流。"""
    builder = StateGraph(AgentState)
    builder.add_node("agent", call_agent)
    builder.add_node("tools", ToolNode(tools_list))
    builder.set_entry_point("agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )
    builder.add_edge("tools", "agent")
    return builder.compile(checkpointer=memory)


app = build_workflow()


# FastAPI 对接入口：统一封装 LangGraph 调用，外部只需传入 user_input 与 thread_id。
def run_agent(user_input: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    final_state = {}
    for state in app.stream(
        {"messages": [("user", user_input)]},
        config=config,
        stream_mode="values",
    ):
        if isinstance(state, dict):
            final_state = state
    return final_state


def _chunk_to_text(chunk: Any) -> str:
    """将模型流式 chunk 统一转换为字符串 token。"""
    content = getattr(chunk, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return str(content) if content is not None else ""


async def run_agent_stream(user_input: str, thread_id: str) -> AsyncGenerator[str, None]:
    """FastAPI/SSE 对接入口：按 LangGraph v2 事件流输出 token 与工具事件。"""
    config = {"configurable": {"thread_id": thread_id}}
    try:
        async for event in app.astream_events(
            {"messages": [("user", user_input)]},
            config=config,
            version="v2",
        ):
            if not isinstance(event, dict):
                continue

            event_type = event.get("event")

            if event_type == "on_chat_model_stream":
                data = event.get("data", {})
                if not isinstance(data, dict):
                    data = {}
                chunk = data.get("chunk")
                token = _chunk_to_text(chunk)
                if token:
                    yield f"data: {json.dumps({'type': 'token', 'content': token}, ensure_ascii=False)}\n\n"

            elif event_type == "on_tool_start":
                tool_name = event.get("name", "unknown_tool")
                yield f"data: {json.dumps({'type': 'tool_start', 'tool_name': tool_name}, ensure_ascii=False)}\n\n"

            elif event_type == "on_tool_end":
                tool_name = event.get("name", "unknown_tool")
                yield f"data: {json.dumps({'type': 'tool_end', 'tool_name': tool_name}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
    except Exception as exc:
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)}, ensure_ascii=False)}\n\n"


def _extract_final_answer_from_state(state: Dict[str, Any]) -> str:
    messages = state.get("messages", []) if isinstance(state, dict) else []
    for message in reversed(messages):
        content = getattr(message, "content", "")
        if isinstance(content, str) and content.strip():
            _, formal_reply = _split_debug_sections(content)
            return formal_reply.strip() if isinstance(formal_reply, str) else ""
    return ""


def _extract_tools_used_from_state(state: Dict[str, Any]) -> List[str]:
    messages = state.get("messages", []) if isinstance(state, dict) else []
    tools_used: List[str] = []
    for message in messages:
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call.get("name")
                if isinstance(tool_name, str) and tool_name:
                    tools_used.append(tool_name)
    return list(dict.fromkeys(tools_used))


def _extract_generated_document_from_state(state: Dict[str, Any]) -> Optional[str]:
    messages = state.get("messages", []) if isinstance(state, dict) else []
    for message in reversed(messages):
        if hasattr(message, "tool_call_id"):
            content = getattr(message, "content", "")
            if isinstance(content, str) and ".docx" in content:
                return content
    return None


def run_agent_for_backend(user_input: str, thread_id: str) -> Dict[str, Any]:
    """
    FastAPI 对接标准入口。

    输入：
    - user_input: 当前用户输入
    - thread_id: 建议直接使用 backend 的 session_id，确保多会话隔离

    输出：
    - final_answer: 助手最终回复（已去除调试分段头）
    - tools_used: 本轮触发的工具列表
    - generated_document: 若生成文书，返回相关路径/URL文本
    - extracted_elements: 结构化白板信息
    - state: 原始 LangGraph 最终状态（便于排障）
    """
    final_state = run_agent(user_input=user_input, thread_id=thread_id)
    return {
        "final_answer": _extract_final_answer_from_state(final_state),
        "tools_used": _extract_tools_used_from_state(final_state),
        "generated_document": _extract_generated_document_from_state(final_state),
        "extracted_elements": final_state.get("extracted_elements", {}) if isinstance(final_state, dict) else {},
        "state": final_state,
    }


class LegalAgentWorkflow:
    """法律 Agent 工作流包装器。"""

    def __init__(self):
        self.app = app

    def run(
        self,
        user_query: str,
        thread_id: str = "default",
        max_iterations: int = 10,
        verbose: bool = False,
    ) -> dict:
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
        }
        result = self.app.invoke(
            initial_state,
            config={
                "recursion_limit": max_iterations,
                "configurable": {"thread_id": thread_id},
            },
        )

        messages = result.get("messages", [])
        final_answer = ""
        if messages:
            final_answer = getattr(messages[-1], "content", "") or ""

        tools_used = []
        reasoning_steps = []
        generated_document = None

        for message in messages:
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.get("name", "unknown")
                    tools_used.append(tool_name)
                    reasoning_steps.append(f"调用工具: {tool_name}")
            if hasattr(message, "tool_call_id"):
                content = getattr(message, "content", "")
                if isinstance(content, str) and "http" in content and ".docx" in content:
                    generated_document = content

        if verbose and final_answer:
            print(final_answer)

        return {
            "final_answer": final_answer,
            "tools_used": list(dict.fromkeys(tools_used)),
            "reasoning_steps": reasoning_steps,
            "generated_document": generated_document,
        }

    def stream(self, user_query: str, thread_id: str = "default", max_iterations: int = 10):
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
        }
        yield from self.app.stream(
            initial_state,
            config={
                "recursion_limit": max_iterations,
                "configurable": {"thread_id": thread_id},
            },
        )


def get_legal_agent_workflow() -> LegalAgentWorkflow:
    """获取法律 Agent 工作流对象。"""
    return LegalAgentWorkflow()


def execute_legal_query(
    user_query: str,
    thread_id: str = "default",
    max_iterations: int = 10,
    verbose: bool = False,
) -> dict:
    """快捷函数：执行一次法律查询并返回结果。"""
    workflow = get_legal_agent_workflow()
    return workflow.run(
        user_query=user_query,
        thread_id=thread_id,
        max_iterations=max_iterations,
        verbose=verbose,
    )


def _split_debug_sections(content: str) -> tuple[str, str]:
    """从调试响应中提取思考摘要与正式答复。"""
    if not isinstance(content, str):
        return "", ""

    marker_summary = "【思考摘要】"
    marker_reply = "【正式答复】"
    if marker_summary not in content or marker_reply not in content:
        return "", content

    try:
        summary_part = content.split(marker_summary, 1)[1].split(marker_reply, 1)[0].strip()
        reply_part = content.split(marker_reply, 1)[1].strip()
        return summary_part, reply_part
    except Exception:
        return "", content


def _message_fingerprint(message) -> str:
    
    message_id = getattr(message, "id", None)
    if message_id:
        return f"id::{message_id}"

    message_type = message.__class__.__name__
    content = getattr(message, "content", "")
    tool_call_id = getattr(message, "tool_call_id", "")
    tool_calls = getattr(message, "tool_calls", None)
    return f"sig::{message_type}::{tool_call_id}::{str(tool_calls)}::{str(content)}"


if __name__ == "__main__":
    print("\n" + "═" * 70)
    print("  法律 AI Agent - 终端交互测试")
    print("═" * 70)
    print("\n输入您的法律问题或案情描述\n")

    # 默认自动生成会话 ID，启动后无需额外回车确认。
    current_thread_id = str(uuid.uuid4())
    print(f"已自动生成会话 ID: {current_thread_id}\n")

    while True:
        try:
            user_input = input("▶ [USER] ").strip()
            if not user_input:
                continue

            if user_input == "/switch":
                print("\n正在切换会话...\n")
                current_thread_id = str(uuid.uuid4())
                print(f"已自动生成新会话 ID: {current_thread_id}\n")
                continue

            final_state = run_agent(user_input, current_thread_id)
            messages = final_state.get("messages", []) if isinstance(final_state, dict) else []

            final_answer = ""
            if messages:
                for message in reversed(messages):
                    content = getattr(message, "content", "")
                    if isinstance(content, str) and content.strip():
                        final_answer = content.strip()
                        break

            print()
            if final_answer:
                summary, formal_reply = _split_debug_sections(final_answer)
                if DEBUG_THINKING and summary:
                    print("▶ [THINKING SUMMARY]")
                    print(f"   {summary}")
                    print()
                    print("▶ [AGENT RESPONSE]")
                    print(f"   {formal_reply}")
                else:
                    print("▶ [AGENT RESPONSE]")
                    print(f"   {final_answer}")
            else:
                print("▶ [AGENT RESPONSE]")
                print("   （本轮未获取到有效回复）")
            print()

            print("═" * 70)
            print()

        except KeyboardInterrupt:
            print("\n\n感谢使用！再见。")
            break
        except Exception as exc:
            print(f"\n❌ 错误: {str(exc)}\n")
            print("═" * 70)
            print()
