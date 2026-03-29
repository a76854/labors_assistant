import os

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


class LegalAgentWorkflow:
    """法律 Agent 工作流包装器。"""

    def __init__(self):
        self.app = app

    def run(self, user_query: str, max_iterations: int = 10, verbose: bool = False) -> dict:
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "extracted_elements": {},
        }
        result = self.app.invoke(
            initial_state,
            config={
                "recursion_limit": max_iterations,
                "configurable": {"thread_id": "test_user_001"},
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

    def stream(self, user_query: str, max_iterations: int = 10):
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "extracted_elements": {},
        }
        yield from self.app.stream(
            initial_state,
            config={
                "recursion_limit": max_iterations,
                "configurable": {"thread_id": "test_user_001"},
            },
        )


def get_legal_agent_workflow() -> LegalAgentWorkflow:
    """获取法律 Agent 工作流对象。"""
    return LegalAgentWorkflow()


def execute_legal_query(user_query: str, max_iterations: int = 10, verbose: bool = False) -> dict:
    """快捷函数：执行一次法律查询并返回结果。"""
    workflow = get_legal_agent_workflow()
    return workflow.run(user_query=user_query, max_iterations=max_iterations, verbose=verbose)


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
    """为消息生成稳定指纹，避免流式事件重复打印同一条内容。"""
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
    print("\n输入您的法律问题或案情描述（按 Ctrl+C 退出）\n")

    conversation_messages = []
    extracted_elements = {}
    seen_message_keys = set()

    def append_unique_message(message):
        key = _message_fingerprint(message)
        if key in seen_message_keys:
            return
        seen_message_keys.add(key)
        conversation_messages.append(message)

    while True:
        try:
            user_input = input("▶ [USER] ").strip()
            if not user_input:
                continue

            human_message = HumanMessage(content=user_input)
            append_unique_message(human_message)

            initial_state = {
                "messages": conversation_messages,
                "extracted_elements": extracted_elements,
            }

            print()
            current_turn_messages = []
            rendered_message_keys = set()

            for event in app.stream(
                initial_state,
                config={"configurable": {"thread_id": "test_user_001"}},
            ):
                for node_name, node_output in event.items():
                    if "extracted_elements" in node_output and isinstance(node_output["extracted_elements"], dict):
                        extracted_elements = node_output["extracted_elements"]
                    elif "extracted_info" in node_output and isinstance(node_output["extracted_info"], dict):
                        extracted_elements = node_output["extracted_info"]

                    if node_name == "agent":
                        messages = node_output.get("messages", [])
                        if messages:
                            for message in messages:
                                current_turn_messages.append(message)

                            last_message = messages[-1]
                            last_key = _message_fingerprint(last_message)
                            if last_key in rendered_message_keys:
                                continue
                            rendered_message_keys.add(last_key)

                            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                                print("▶ [AGENT THINKING]")
                                for tool_call in last_message.tool_calls:
                                    tool_name = tool_call.get("name", "unknown")
                                    tool_input = tool_call.get("args", {})
                                    print()
                                    print(f"🔴 [TOOL CALL] {tool_name}")
                                    print(f"   Input: {tool_input}")
                                    print()
                            else:
                                if hasattr(last_message, "content") and last_message.content:
                                    summary, formal_reply = _split_debug_sections(last_message.content)
                                    if DEBUG_THINKING and summary:
                                        print("▶ [THINKING SUMMARY]")
                                        print(f"   {summary}")
                                        print()
                                        print("▶ [AGENT RESPONSE]")
                                        print(f"   {formal_reply}")
                                    else:
                                        print("▶ [AGENT RESPONSE]")
                                        print(f"   {last_message.content}")
                                    print()

                    elif node_name == "tools":
                        messages = node_output.get("messages", [])
                        if messages:
                            for message in messages:
                                current_turn_messages.append(message)
                            for message in messages:
                                message_key = _message_fingerprint(message)
                                if message_key in rendered_message_keys:
                                    continue
                                rendered_message_keys.add(message_key)
                                if hasattr(message, "tool_call_id"):
                                    tool_result = getattr(message, "content", "")
                                    if tool_result:
                                        print("✅ [TOOL RESULT]")
                                        preview = str(tool_result)[:500]
                                        if len(str(tool_result)) > 500:
                                            preview += "\n   ... [输出过长，已截断] ..."
                                        print(f"   {preview}")
                                        print()

            for message in current_turn_messages:
                append_unique_message(message)

            print("═" * 70)
            print()

        except KeyboardInterrupt:
            print("\n\n感谢使用！再见。")
            break
        except Exception as exc:
            print(f"\n❌ 错误: {str(exc)}\n")
            print("═" * 70)
            print()
