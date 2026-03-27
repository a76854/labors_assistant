# 法律 AI Agent 系统（LangGraph ReAct）

基于 LangGraph + LangChain 构建的法律咨询智能体，采用 ReAct 工作流：
- 先通过对话收集四项诉讼要素
- 再调用法律检索工具
- 最后调用文书生成工具并输出结果

当前代码已支持 OpenAI 兼容接口，可直接使用阿里 DashScope（OpenAI 兼容模式）。

---

## 1. 当前实现状态

### 已实现
- ReAct 工作流编排（`StateGraph` + `ToolNode` + 条件路由）
- 两个核心工具：
  - `search_law_tool`（法律检索，当前为 mock 返回）
  - `generate_doc_tool`（文书生成，当前为 mock 返回）
- 工作流包装接口：
  - `LegalAgentWorkflow.run()`
  - `LegalAgentWorkflow.stream()`
  - `get_legal_agent_workflow()`
  - `execute_legal_query()`
- 动态去重策略：防止重复调用 `search_law_tool`
- `main.py` 菜单示例可直接运行

### 未实现（后续）
- 真实法律知识库/RAG 检索
- 真实文书文件生成与存储（当前返回 mock 链接）
- `calculator.py` 工具接入主流程（目前存在但未绑定到 `tools_list`）

---

## 2. 项目结构（与当前代码一致）

```text
LLM-laws/
├── agent/
│   ├── __init__.py
│   ├── state.py
│   ├── prompts.py
│   ├── agent_node.py
│   ├── workflow.py
│   └── tools/
│       ├── __init__.py
│       ├── legal_search.py
│       ├── doc_generator.py
│       └── calculator.py
├── main.py
├── requirements.txt
├── .env
└── README.md
```

---

## 3. 核心流程

### 3.1 State
`AgentState` 仅包含：
- `messages`: 对话消息（使用 `add_messages` reducer）
- `extracted_info`: 案情要素缓存字典

`LawsuitElementsSchema` 定义文书生成所需四要素：
- `plaintiff`
- `defendant`
- `claim`
- `amount`

### 3.2 Prompt 约束
`SYSTEM_PROMPT` 强制两阶段：
1. 收集四要素（禁止工具调用）
2. 信息齐全后按顺序调用：
   - `search_law_tool`
   - `generate_doc_tool`

### 3.3 Graph 编排
`workflow.py` 里的图结构：
`START -> agent -> (tools_condition) -> tools -> agent -> ... -> END`

### 3.4 防重复工具调用（已启用）
在 `call_agent` 中增加动态系统约束：
- 若已调用过 `search_law_tool` 且未调用 `generate_doc_tool`：
  - 禁止再次调用 `search_law_tool`
  - 强制下一步调用 `generate_doc_tool`
- 若两个工具都已调用：
  - 禁止继续调用工具
  - 直接输出最终答案

期望顺序：
1. `search_law_tool`
2. `generate_doc_tool`
3. 最终答复

---

## 4. 环境准备

## 4.1 安装依赖

```bash
pip install -r requirements.txt
```

中国网络可使用镜像：

```bash
pip install -r requirements.txt -i https://pypi.tsinghua.edu.cn/simple
```

推荐使用项目虚拟环境执行：

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4.2 配置模型环境变量

项目通过 `python-dotenv` 读取根目录 `.env`。

推荐使用统一变量（当前代码优先读取 `LLM_*`，兼容 `OPENAI_*`）：

```env
LLM_MODEL=qwen-plus
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=你的有效Key

# 兼容旧变量（可选）
# OPENAI_API_KEY=
# OPENAI_BASE_URL=
```

`agent_node.py` 的读取优先级：
- `api_key`: `LLM_API_KEY` -> `OPENAI_API_KEY`
- `base_url`: `LLM_BASE_URL` -> `OPENAI_BASE_URL`
- `model`: `LLM_MODEL`（默认 `qwen-plus`）

---

## 5. 运行方式

### 5.1 菜单演示

```bash
.\.venv\Scripts\python.exe main.py
```

### 5.2 直接执行单条查询

```python
from agent.workflow import execute_legal_query

result = execute_legal_query(
    user_query="公司拖欠工资15000元，我该怎么办？",
    max_iterations=10,
    verbose=False,
)

print(result["final_answer"])
print(result["tools_used"])
print(result["reasoning_steps"])
print(result["generated_document"])
```

### 5.3 使用工作流对象

```python
from agent.workflow import get_legal_agent_workflow

workflow = get_legal_agent_workflow()

result = workflow.run("你的法律问题", max_iterations=10)

for event in workflow.stream("你的法律问题", max_iterations=10):
    print(event)
```

### 5.4 终端交互式图调试（workflow 直跑）

```bash
.\.venv\Scripts\python.exe agent\workflow.py
```

会在终端输出：
- Agent 思考
- 工具调用输入
- 工具结果预览
- 最终回复

---

## 6. 返回结构说明

`execute_legal_query()` / `LegalAgentWorkflow.run()` 返回：

```python
{
  "final_answer": str,
  "tools_used": list[str],
  "reasoning_steps": list[str],
  "generated_document": str | None,
}
```

说明：
- `tools_used` 会做去重（保留首次出现顺序）
- `generated_document` 当前通过检测工具消息中 `http` + `.docx` 提取

---

## 7. 工具模块说明

### 已接入主流程
- `agent/tools/legal_search.py` -> `search_law_tool`
- `agent/tools/doc_generator.py` -> `generate_doc_tool`

### 暂未接入主流程
- `agent/tools/calculator.py`
  - `calculate_compensation`
  - `calculate_injury_compensation`
  - `calculate_wage_compensation`

如需启用赔偿计算，需要把对应工具加入 `agent/agent_node.py` 中的 `tools_list`。

---

## 8. 常见问题

### Q1: 401 / invalid_api_key
- 检查 `.env` 中的 `LLM_API_KEY`
- 确认 `LLM_BASE_URL` 与服务商匹配
- 修改 `.env` 后重开终端再运行

### Q2: 提示 `.env` 注入未开启
在 `.vscode/settings.json` 中确认：

```json
{
  "python.terminal.useEnvFile": true,
  "python.envFile": "${workspaceFolder}/.env"
}
```

### Q3: 为什么不调用工具
如果四要素不完整，系统会持续追问，不会调用工具（这是 prompt 规则）。

---

## 9. 安全建议

- 不要把真实 API Key 提交到 Git 仓库
- 建议将 `.env` 加入 `.gitignore`
- 如果 Key 曾明文暴露，请立即在平台侧轮换

---

## 10. 版本与依赖

核心依赖见 `requirements.txt`：
- `langgraph>=0.1.0`
- `langchain>=0.1.0`
- `langchain-openai>=0.0.1`
- `openai>=1.0.0`
- `pydantic>=2.0.0`
- `python-dotenv>=1.0.0`

当前文档与现有代码实现对齐于本仓库当前版本。
