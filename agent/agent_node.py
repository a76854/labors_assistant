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


<<<<<<< HEAD
<<<<<<< HEAD
=======
# ============================================================================
# 【工具列表】收集所有可调用的工具
# ============================================================================
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
tools_list = [
    search_public_laws_tool,
    search_public_cases_tool,
    search_private_knowledge_tool,
    generate_legal_doc_tool,
]


<<<<<<< HEAD
<<<<<<< HEAD
=======
# ============================================================================
# 【LLM 初始化】创建大语言模型实例并绑定工具
# ============================================================================
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
llm_with_tools = llm.bind_tools(tools_list)


def call_agent(state: AgentState) -> dict:
    """主节点：组装约束后调用 LLM，并返回单条响应消息。"""

    system_message = SystemMessage(content=SYSTEM_PROMPT)

<<<<<<< HEAD
=======

# 绑定工具：让 LLM 能够识别和调用工具
llm_with_tools = llm.bind_tools(tools_list)


# ============================================================================
# 【核心节点函数】Agent 的主脑 - 在 StateGraph 中作为一个节点执行
# ============================================================================
def call_agent(state: AgentState) -> dict:
    """
    Agent 的主节点函数 - 调用 LLM 进行推理和工具调用
    
    【功能说明】
    这个函数是整个 ReAct 工作流的核心驱动，负责：
    1. 接收当前的 Agent 状态（包含消息历史和收集到的案情要素）
    2. 将系统提示词（SYSTEM_PROMPT）插入消息列表的开头
    3. 调用绑定了工具的大语言模型进行推理
    4. LLM 会根据当前对话上下文决定：
       - 继续与用户对话收集信息
       - 或者调用适当的工具（search_law_tool 或 generate_doc_tool）
    5. 返回 LLM 的响应作为新消息，由 StateGraph 自动追加
    
    【参数说明】
    state : AgentState
        Agent 的当前状态，包含：
        - messages (list): 完整的对话历史消息列表
        - extracted_info (dict): 从对话中收集到的案情要素
          示例：{"plaintiff": "张三", "defendant": "李四", ...}
    
    【返回值说明】
    dict
        必须返回一个包含 "messages" 键的字典：
        {"messages": [response]}
        
        其中 response 是 LLM 的响应消息（可能包含文本、工具调用等）
        StateGraph 会自动将此消息合并到 state["messages"] 中
        （使用 add_messages reducer）
    
    【执行流程详解】
    
    步骤 1：构建系统消息
    ───────────────────
    将 SYSTEM_PROMPT 常量包装成 SystemMessage 对象
    这用于指导 LLM 扮演公益律师助手的角色，遵循特定的 SOP
    
    步骤 2：拼接消息列表
    ───────────────────
    原始顺序：state["messages"] 包含历史对话
    新的顺序：[系统消息] + [历史消息]
    
    这样 LLM 每次调用时都会看到完整的系统指导，避免遗忘角色定位
    
    步骤 3：调用 LLM
    ───────────────
    llm_with_tools.invoke(messages_with_system) 执行推理
    
    LLM 可能的行为：
    - 如果信息不完整：生成问询消息，询问用户获取缺失信息
    - 如果集齐四要素：根据 SYSTEM_PROMPT 的约束，调用工具
      * 先调用 search_law_tool 检索法律
      * 然后调用 generate_doc_tool 生成文书
    - 如果用户给出了新信息：更新 state["extracted_info"]
    
    步骤 4：返回响应
    ───────────────
    将 LLM 的响应包装在 {"messages": [response]} 字典中
    StateGraph 会自动调用 add_messages reducer 将响应合并到状态中
    
    【工作流中的位置】
    
    StateGraph 的执行流程：
    
    用户输入（HumanMessage）
             ↓
        [call_agent 节点]  ← 当前函数
             ↓
        LLM 推理和决策
             ↓
        LLM 是否需要工具？
        ├─ 是 → 工具调用 → 工具返回 → 回到 call_agent
        └─ 否 → 返回最终答案 → 流程结束
    
    【使用示例】
    
    在 StateGraph 中的注册方式：
    graph.add_node("agent", call_agent)
    graph.add_edge("tools", "agent")  # 工具执行后回到此节点
    
    执行时：
    result = graph.invoke({
        "messages": [HumanMessage(content="我想起诉我的邻居")],
        "extracted_info": {}
    })
    
    【关键设计原则】
    
    1. 系统消息永远在最前面
       ✓ 确保 LLM 始终无为公益律师助手
       ✓ 避免用户的一句话就让 LLM 忘记角色
    
    2. 消息不重复构造
       ✓ 使用 state["messages"] 中的历史消息
       ✓ 由 StateGraph 的 add_messages reducer 自动管理去重
    
    3. 返回值遵循 TypedDict 的约定
       ✓ 必须返回 dict，且只能包含在 AgentState 中定义的键
       ✓ StateGraph 会自动合并返回值到原状态
    
    4. 工具绑定不在此函数内部判断
       ✓ LLM 会自动识别何时需要调用工具
       ✓ LLM 会自动构建正确的工具调用格式（function_call）
       ✓ ToolNode 节点会拦截并执行工具
    
    【与其他节点的交互】
    
    此函数与 ToolNode 的交互流程：
    
    1. call_agent 被执行
    2. LLM 识别需要调用工具
    3. LLM 返回 AIMessage，其中包含 tool_calls 属性
    4. StateGraph 的路由逻辑检测到 tool_calls 的存在
    5. 将控制权交给 ToolNode（tools 节点）
    6. ToolNode 执行工具并返回 ToolMessage
    7. StateGraph 自动回到 call_agent
    8. call_agent 再次被调用，state["messages"] 中已包含工具结果
    9. LLM 看到工具的返回结果，继续推理
    10. 直到 LLM 不再需要工具，返回最终答案，流程结束
    
    【调试建议】
    
    如果需要查看 LLM 的推理过程，可以添加日志：
    
    def call_agent(state: AgentState) -> dict:
        system_message = SystemMessage(content=SYSTEM_PROMPT)
        messages_with_system = [system_message] + state["messages"]
        
        print(f"[DEBUG] 消息数: {len(messages_with_system)}")
        print(f"[DEBUG] 最后一条消息: {messages_with_system[-1]}")
        
        response = llm_with_tools.invoke(messages_with_system)
        
        print(f"[DEBUG] LLM 响应类型: {type(response).__name__}")
        if hasattr(response, 'tool_calls'):
            print(f"[DEBUG] 工具调用: {response.tool_calls}")
        
        return {"messages": [response]}
    """
    
    # ========================================================================
    # 步骤 1：构建系统消息
    # ========================================================================
    system_message = SystemMessage(content=SYSTEM_PROMPT)

    # 动态约束：避免重复/遗漏调用三类检索工具
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
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

<<<<<<< HEAD
<<<<<<< HEAD
=======
    # 粗粒度识别：用户是否明确提出私域材料检索需求
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0

    messages_with_system = [system_message] + ([dynamic_message] if dynamic_message else []) + state["messages"]

    response = llm_with_tools.invoke(messages_with_system)

    # 关键约束：检索完成后禁止重复 search_*，优先收口到文书生成。
<<<<<<< HEAD
=======
    
    # ========================================================================
    # 步骤 2：拼接消息列表（系统消息在最前面）
    # ========================================================================
    messages_with_system = [system_message] + ([dynamic_message] if dynamic_message else []) + state["messages"]
    
    # ========================================================================
    # 步骤 3：调用 LLM（已绑定工具）
    # ========================================================================
    # llm_with_tools 会自动处理：
    # - 识别何时需要调用工具
    # - 构建正确的工具调用格式
    # - 返回 AIMessage（可能包含 tool_calls）
    response = llm_with_tools.invoke(messages_with_system)

    # 硬约束收口：已满足评估前置检索时，禁止继续检索，必须转入文书生成工具。
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======
>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
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
<<<<<<< HEAD
<<<<<<< HEAD

=======
    
    # ========================================================================
    # 步骤 4：返回响应
    # ========================================================================
    # 返回格式：{"messages": [response]}
    # StateGraph 会自动将 response 合并到 state["messages"] 中
>>>>>>> cb96e38840ba4573142a869926ea3c6135a7b6aa
=======

>>>>>>> 2e2222926815f10fe186225ebab19dff9a1bcae0
    return {"messages": [response]}
