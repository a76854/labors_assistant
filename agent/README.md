# 法律 Agent 测试手册

本文档用于团队内部联调与验收，目标是让任何成员在本地都能完成以下动作：

1. 正常启动 Agent
2. 触发双轨检索（公域/私域）
3. 触发规范文书生成
4. 判断结果是否符合预期

---

## 1. 当前能力概览

本 Agent 当前具备以下能力：

- 对话收集案情要素
- 公域法规检索：search_public_laws_tool
- 公域判例检索：search_public_cases_tool
- 私域知识检索：search_private_knowledge_tool
- 规范文书生成：generate_legal_doc_tool（输出 .docx 到 generated_docs 目录）

---

## 2. 运行环境要求

- 操作系统：Windows（当前团队主环境）
- Python：3.10+（建议 3.12）
- 网络：可访问大模型 API 与公域检索接口

---

## 3. 本地启动步骤

在仓库根目录执行：

	cd E:\LLM-laws

### 3.1 激活虚拟环境

	.\.venv\Scripts\Activate.ps1

若未创建虚拟环境，可先执行：

	python -m venv .venv
	.\.venv\Scripts\Activate.ps1

### 3.2 安装依赖

	pip install -r requirements.txt
	pip install python-docx

### 3.3 配置环境变量

编辑根目录 .env，最少需要：

	LLM_MODEL=qwen-plus
	LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
	LLM_API_KEY=你的模型APIKey

如需启用私域检索，再增加：

	YUANQI_API_URL=你的私域检索接口URL
	YUANQI_API_KEY=你的私域检索接口Key

---

## 4. 运行方式

### 4.1 交互式测试（推荐）

	python -m agent.workflow

启动后可在终端持续输入案情，按 Ctrl+C 退出。

### 4.2 程序化单次测试

	python -c "from agent.workflow import execute_legal_query; r=execute_legal_query('你的测试请求', max_iterations=30); print(r)"

---

## 5. 标准测试用例

### 用例 A：信息不完整（应继续追问，不应调用工具）

输入示例：

	我想起诉别人还钱。

预期：

- Agent 继续追问原告/被告/诉求/金额等缺失信息
- 不出现工具调用

### 用例 B：公域检索闭环（法条 + 判例 + 文书）

输入示例：

	原告：张三，身份证号110101199001011234，手机号13800138000，住深圳市南山区科技园科苑路15号。
	被告：李四，身份证号110101198501015678，手机号13900139000，住深圳市福田区福华路88号。
	核心诉求：请求被告返还借款本金80000元，并按年利率8%支付逾期利息。
	涉案金额：80000元。
	补充事实：2025年6月1日转账借款，约定2025年9月1日前还款，现逾期未还。
	请先完成法律检索并输出评估，再生成法律文书下载链接。

预期：

- 至少调用 search_public_laws_tool 与 search_public_cases_tool
- 最终调用 generate_legal_doc_tool
- 输出文书下载链接，且 generated_docs 目录出现新的 .docx 文件

### 用例 C：双轨检索闭环（公域 + 私域 + 文书）

输入示例：

	原告：王五，身份证号110101199102023333，手机号13900001111。
	被告：赵六，身份证号110101198706067777，住深圳市南山区某街道某号。
	核心诉求：返还借款120000元及逾期利息。
	涉案金额：120000元。
	补充：我上传了借条和内部调解方案，请结合私域材料与公域法律检索，给出评估并生成文书。

预期：

- 调用公域工具 + search_private_knowledge_tool
- 最终调用 generate_legal_doc_tool

---

## 6. 验收标准

一次完整成功流程应同时满足：

1. 输出包含案情定性、法律依据、胜诉率分析、调解建议
2. 输出包含文书下载链接（http://127.0.0.1:8000/download/xxx.docx）
3. 本地 generated_docs 下生成对应文书文件
4. 工具调用顺序合理，避免无意义重复检索

---

## 7. 常见问题排查

### 问题 1：启动时报 SyntaxError 且包含 <<<<<<< 或 >>>>>>>

原因：存在 Git 冲突标记未清理。

处理：

- 检查近期 pull/merge 的文件
- 清理冲突标记后再运行

### 问题 2：私域检索返回“未配置 YUANQI_API_URL / YUANQI_API_KEY”

原因：.env 未配置私域参数。

处理：补齐对应环境变量后重启终端。

### 问题 3：文书未生成

检查项：

- 是否安装 python-docx
- generated_docs 目录是否可写
- 输入是否已满足文书生成的 7 个要素

---

## 8. 安全与协作约定

- 严禁将真实 API Key 提交到 Git 仓库。
- 建议把 .env 仅保留在本地，并维护 .env.example 作为团队模板。
- 每次提交前运行：

	python -m py_compile agent/__init__.py agent/agent_node.py agent/prompts.py agent/state.py agent/workflow.py agent/tools/__init__.py agent/tools/calculator.py agent/tools/doc_generator.py agent/tools/legal_search.py

---

## 9. 快速验收命令（复制即用）

	python -c "from agent.workflow import execute_legal_query; q='原告：张三，身份证号110101199001011234，手机号13800138000，住深圳市南山区科技园科苑路15号。被告：李四，身份证号110101198501015678，手机号13900139000，住深圳市福田区福华路88号。核心诉求：请求返还借款本金80000元并支付逾期利息。涉案金额：80000元。补充事实：2025年6月1日转账借款，约定2025年9月1日前还款，现逾期未还；有借条、转账记录、催款聊天记录。请完成检索、输出评估并生成文书。'; r=execute_legal_query(q, max_iterations=30); print('TOOLS_USED=', r.get('tools_used')); print('GENERATED_DOCUMENT=', r.get('generated_document'))"

若输出中包含 generate_legal_doc_tool 且 GENERATED_DOCUMENT 非空，即通过。
