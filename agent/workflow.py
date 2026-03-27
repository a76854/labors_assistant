<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage

from agent.agent_node import call_agent, tools_list
from agent.state import AgentState


def build_workflow():
    """构建并编译 ReAct 工作流。"""
    builder = StateGraph(AgentState)
    builder.add_node("agent", call_agent)
    builder.add_node("tools", ToolNode(tools_list))
    builder.set_entry_point("agent")
<<<<<<< HEAD
=======
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from agent.state import AgentState
from agent.agent_node import call_agent, tools_list
from langchain_core.messages import HumanMessage


# ============================================================================
# 【构建 StateGraph 工作流】
# ============================================================================
def build_workflow():
    """
    构建完整的 ReAct Agent 工作流图
    
    【图的结构】
    
    START
      ↓
    agent (call_agent 节点)
      ↓
    [条件判断] tools_condition
      ├─ 有工具调用 → tools (ToolNode 节点)
      │                ↓
      │              tools 执行
      │                ↓
      │              返回工具结果
      │                ↓
      │              agent (第二轮推理)
      │                ↓
      │              [再次判断]...
      │
      └─ 无工具调用（最终答案）→ END
    
    【节点说明】
    
    节点 1: agent (call_agent)
    - 功能：调用 LLM 进行推理
    - 输入：AgentState（包含消息历史）
    - 输出：{"messages": [response]}
    - LLM 可能选择：
      * 继续对话（收集信息）
      * 调用工具（search_public_laws_tool / search_public_cases_tool / search_private_knowledge_tool）
    
    节点 2: tools (ToolNode)
    - 功能：执行 LLM 请求的工具调用
    - 输入：AIMessage（包含 tool_calls 信息）
    - 输出：ToolMessage（工具执行结果）
    - 自动处理工具的识别、调用、错误处理
    
    【边的连接】
    
    edge 1: START → agent
      起点连到 agent，开始整个工作流
    
    edge 2: agent → tools 或 END（条件边）
      使用 tools_condition 判断：
      - 如果 LLM 产生了工具调用 → 去 tools 节点
      - 如果 LLM 没有工具调用 → 去 END 结束
    
    edge 3: tools → agent
      工具执行后回到 agent，LLM 在看到工具结果后继续推理
      这形成了 ReAct 的循环：Agent → Tool → Agent → ...
    
    【工作流示例】
    
    轮次 1:
      用户："我想起诉邻居"
      → agent 调用 LLM
      → LLM 识别信息不完整
      → LLM 生成提问："您能告诉我您的名字吗？"
      → tools_condition 判断：无工具调用 → 继续下一轮对话
    
    轮次 2:
      用户："我叫张三"
      → agent 调用 LLM
      → LLM 更新收集到的信息，继续询问
      → LLM 生成："好的，接下来被告的信息是什么？"
      → 继续...
    
    轮次 N:
      用户："[四项信息已全部提供]"
      → agent 调用 LLM
      → LLM 检查 SYSTEM_PROMPT：四项齐全 → 调用公域/私域检索工具
      → tools_condition 判断：有工具调用 → 去 tools 节点
      → ToolNode 执行对应工具
      → tools 返回法律检索结果
      → 回到 agent，LLM 看到检索结果
      → LLM 继续：必要时补充调用其他检索工具
      → 再次去 tools 节点执行
      → 回到 agent
      → LLM 整理最终答案，不再调用工具
      → tools_condition 判断：无工具调用 → END
      → 流程结束
    
    【tools_condition 说明】
    
    tools_condition 是 LangGraph 内置的路由函数：
    
    def tools_condition(state):
        # 检查最后一条消息是否有工具调用
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"  # 有工具调用 → 去 tools 节点
        else:
            return END  # 无工具调用 → 结束流程
    """
    
    # ========================================================================
    # 步骤 1：初始化 StateGraph
    # ========================================================================
    builder = StateGraph(AgentState)
    
    # ========================================================================
    # 步骤 2：添加节点
    # ========================================================================
    # 添加 agent 节点：LLM 推理的核心
    builder.add_node("agent", call_agent)
    
    # 添加 tools 节点：工具执行
    builder.add_node("tools", ToolNode(tools_list))
    
    # ========================================================================
    # 步骤 3：设置入口点
    # ========================================================================
    # 工作流从 agent 节点开始（START → agent）
    builder.set_entry_point("agent")
    
    # ========================================================================
    # 步骤 4：添加条件边
    # ========================================================================
    # 从 agent 节点出发，根据 tools_condition 决定去向
    # - 如果 LLM 产生了工具调用，去 tools 节点
    # - 否则流程结束（END）
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
            "tools": "tools",
            END: END,
        },
    )
    builder.add_edge("tools", "agent")
    return builder.compile()


<<<<<<< HEAD
=======
            "tools": "tools",  # 有工具调用 → 去 tools 节点
            END: END,          # 无工具调用 → 结束
        }
    )
    
    # ========================================================================
    # 步骤 5：添加普通边
    # ========================================================================
    # 从 tools 节点回到 agent，形成 ReAct 循环
    builder.add_edge("tools", "agent")
    
    # ========================================================================
    # 步骤 6：编译图成可执行的 runnable
    # ========================================================================
    app = builder.compile()
    
    return app


# ============================================================================
# 编译并保存应用
# ============================================================================
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
app = build_workflow()


class LegalAgentWorkflow:
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
    """法律 Agent 工作流包装器。"""

    def __init__(self):
        self.app = app

    def run(self, user_query: str, max_iterations: int = 10, verbose: bool = False) -> dict:
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "extracted_info": {},
        }
        result = self.app.invoke(initial_state, config={"recursion_limit": max_iterations})

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
            "extracted_info": {},
        }
        yield from self.app.stream(initial_state, config={"recursion_limit": max_iterations})


def get_legal_agent_workflow() -> LegalAgentWorkflow:
    """获取法律 Agent 工作流对象。"""
    return LegalAgentWorkflow()


def execute_legal_query(user_query: str, max_iterations: int = 10, verbose: bool = False) -> dict:
    """快捷函数：执行一次法律查询并返回结果。"""
    workflow = get_legal_agent_workflow()
    return workflow.run(user_query=user_query, max_iterations=max_iterations, verbose=verbose)


if __name__ == "__main__":
<<<<<<< HEAD
=======
  """法律 Agent 工作流包装器，提供 run/stream 接口。"""

  def __init__(self):
    self.app = app

  def run(self, user_query: str, max_iterations: int = 10, verbose: bool = False) -> dict:
    initial_state = {
      "messages": [HumanMessage(content=user_query)],
      "extracted_info": {},
    }
    result = self.app.invoke(initial_state, config={"recursion_limit": max_iterations})

    messages = result.get("messages", [])
    final_answer = ""
    if messages:
      last_message = messages[-1]
      final_answer = getattr(last_message, "content", "") or ""

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
      "extracted_info": {},
    }
    yield from self.app.stream(initial_state, config={"recursion_limit": max_iterations})


def get_legal_agent_workflow() -> LegalAgentWorkflow:
  """获取法律 Agent 工作流对象。"""
  return LegalAgentWorkflow()


def execute_legal_query(user_query: str, max_iterations: int = 10, verbose: bool = False) -> dict:
  """快捷函数：执行一次法律查询并返回结果。"""
  workflow = get_legal_agent_workflow()
  return workflow.run(user_query=user_query, max_iterations=max_iterations, verbose=verbose)


# ============================================================================
# 【终端交互测试】
# ============================================================================
if __name__ == "__main__":
    """
    终端测试循环：与法律 Agent 进行交互式对话
    
    【功能】
    - 在终端中逐行输入案情描述
    - 实时显示 Agent 的思考过程
    - 高亮显示工具调用（如法律检索、文书生成）
    - 最后输出 Agent 的完整回答
    
    【使用方法】
    python workflow.py
    
    然后在提示符下输入：
    "我想起诉我的邻居"
    
    按 Enter 后会看到：
    1. Agent 的思考过程
    2. 工具的调用（如果有）
    3. 工具的执行结果
    4. Agent 的最终回答
    
    继续输入新的案情，或按 Ctrl+C 退出
    
    【显示格式】
    
    ▶ [USER] 用户输入的内容
    
    ▶ [AGENT THINKING] ...
    
    🔴 [TOOL CALL] search_public_laws_tool
      Input: ...
    
    ✅ [TOOL RESULT] ...
    
    ▶ [AGENT RESPONSE] ...
    
    ═══════════════════════════════════════════
    """
    
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
    print("\n" + "═" * 70)
    print("  法律 AI Agent - 终端交互测试")
    print("═" * 70)
    print("\n输入您的法律问题或案情描述（按 Ctrl+C 退出）\n")

    conversation_messages = []
    extracted_info = {}
    seen_message_ids = set()

    def append_unique_message(message):
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
        message_id = getattr(message, "id", None)
        if message_id:
            if message_id in seen_message_ids:
                return
            seen_message_ids.add(message_id)
        conversation_messages.append(message)

    while True:
        try:
            user_input = input("▶ [USER] ").strip()
            if not user_input:
                continue

<<<<<<< HEAD
=======
      message_id = getattr(message, "id", None)
      if message_id:
        if message_id in seen_message_ids:
          return
        seen_message_ids.add(message_id)
      conversation_messages.append(message)
    
    while True:
        try:
            # ====================================================================
            # 获取用户输入
            # ====================================================================
            user_input = input("▶ [USER] ").strip()
            
            if not user_input:
                continue
            
            # ====================================================================
            # 初始化状态
            # ====================================================================
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
            human_message = HumanMessage(content=user_input)
            append_unique_message(human_message)

            initial_state = {
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
                "messages": conversation_messages,
                "extracted_info": extracted_info,
            }

            print()
            current_turn_messages = []

            for event in app.stream(initial_state):
<<<<<<< HEAD
=======
              "messages": conversation_messages,
              "extracted_info": extracted_info,
            }
            
            print()  # 空行
            
            # ====================================================================
            # 流式执行工作流
            # ====================================================================
            # app.stream() 会逐步返回每个节点的执行结果
            # 我们对每个事件进行处理和展示
            
            current_turn_messages = []

            for event in app.stream(initial_state):
                # 事件格式：{"node_name": {...output...}}
                # 例如：{"agent": {"messages": [...]}}
                
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
                for node_name, node_output in event.items():
                    if "extracted_info" in node_output and isinstance(node_output["extracted_info"], dict):
                        extracted_info = node_output["extracted_info"]

                    if node_name == "agent":
<<<<<<< HEAD
<<<<<<< HEAD
=======
                        # ================================================
                        # Agent 节点的输出
                        # ================================================
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
                        messages = node_output.get("messages", [])
                        if messages:
                            current_turn_messages.extend(messages)
                            last_message = messages[-1]

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
                            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                                print("▶ [AGENT THINKING]")
                                for tool_call in last_message.tool_calls:
                                    tool_name = tool_call.get("name", "unknown")
                                    tool_input = tool_call.get("args", {})
<<<<<<< HEAD
=======
                            # 检查是否包含工具调用
                            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                                # 有工具调用
                                print("▶ [AGENT THINKING]")

                                # 打印工具调用信息
                                for tool_call in last_message.tool_calls:
                                    tool_name = tool_call.get("name", "unknown")
                                    tool_input = tool_call.get("args", {})

>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
                                    print()
                                    print(f"🔴 [TOOL CALL] {tool_name}")
                                    print(f"   Input: {tool_input}")
                                    print()
<<<<<<< HEAD
<<<<<<< HEAD
                            else:
=======

                            else:
                                # 没有工具调用，这是 Agent 的最终答案
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
                            else:
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
                                if hasattr(last_message, "content") and last_message.content:
                                    print("▶ [AGENT RESPONSE]")
                                    print(f"   {last_message.content}")
                                    print()

                    elif node_name == "tools":
<<<<<<< HEAD
<<<<<<< HEAD
=======
                        # ================================================
                        # Tools 节点的输出
                        # ================================================
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
                        messages = node_output.get("messages", [])
                        if messages:
                            current_turn_messages.extend(messages)
                            for message in messages:
                                if hasattr(message, "tool_call_id"):
<<<<<<< HEAD
<<<<<<< HEAD
                                    tool_result = getattr(message, "content", "")
                                    if tool_result:
                                        print("✅ [TOOL RESULT]")
=======
                                    # 这是工具的返回消息
                                    tool_result = getattr(message, "content", "")
                                    if tool_result:
                                        print("✅ [TOOL RESULT]")
                                        # 只打印前 500 个字符，避免输出过长
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
                                    tool_result = getattr(message, "content", "")
                                    if tool_result:
                                        print("✅ [TOOL RESULT]")
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
                                        preview = str(tool_result)[:500]
                                        if len(str(tool_result)) > 500:
                                            preview += "\n   ... [输出过长，已截断] ..."
                                        print(f"   {preview}")
                                        print()

            for message in current_turn_messages:
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
                append_unique_message(message)

            print("═" * 70)
            print()

        except KeyboardInterrupt:
            print("\n\n感谢使用！再见。")
            break
        except Exception as exc:
            print(f"\n❌ 错误: {str(exc)}\n")
<<<<<<< HEAD
=======
              append_unique_message(message)
            
            # ====================================================================
            # 分隔线
            # ====================================================================
            print("═" * 70)
            print()
        
        except KeyboardInterrupt:
            # 用户按 Ctrl+C，优雅退出
            print("\n\n感谢使用！再见。")
            break
        
        except Exception as e:
            # 捕获并显示错误
            print(f"\n❌ 错误: {str(e)}\n")
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
            print("═" * 70)
            print()
