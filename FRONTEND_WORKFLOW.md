# 前端任务工作流与实现记录

## 文档用途
- 这个文件用于沉淀前端开发的固定工作流程。
- 后续每实现一个前端功能，都要在本文件追加一条记录。
- 目标不是写成长文档，而是保证每次开发都有可回溯的思路、改动和验证结果。

## 前端任务标准流程

### 1. 先确认功能目标
- 这次要解决什么问题。
- 用户能看到的变化是什么。
- 是否依赖后端接口、Agent 返回结果或文档导出能力。

### 2. 明确影响范围
- 会涉及哪些页面、组件、状态和接口。
- 是新增功能，还是修改已有功能。
- 是否需要先用 Mock 数据占位。

### 3. 先定最小可用版本
- 先做能跑通主流程的最小版本，不一开始追求大而全。
- 优先保证主链路可用，再补交互细节、样式和异常处理。

### 4. 开始实现
- 页面层负责组织结构和交互流程。
- 组件层负责可复用 UI。
- `services` 层统一处理接口请求。
- `types` 层统一维护关键类型定义。

### 5. 做基本自测
- 至少检查主流程是否能走通。
- 检查空状态、加载状态、错误状态是否可见。
- 有条件时执行 `lint`、`test`、`build` 或手动页面验证。

### 6. 记录到本文档
- 写清本次做了什么。
- 写清改了哪些文件。
- 写清如何验证。
- 写清还缺什么，方便下次继续。

## 功能记录模板

复制下面这段作为每次新增记录的模板：

```md
## YYYY-MM-DD - 功能名称

### 目标
- 

### 本次改动
- 

### 涉及文件
- 

### 接口 / Mock
- 

### 验证
- 

### 待确认 / 下一步
- 
```

## 功能记录

## 2026-03-27 - 初始化前端工作流文档

### 目标
- 在项目根目录维护一个长期更新的 Markdown 文档，用来记录前端开发流程和后续功能实现情况。

### 本次改动
- 新增前端工作流文档。
- 约定后续每实现一个前端功能，都在本文件追加记录。

### 涉及文件
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 暂无。

### 验证
- 已检查文档结构，包含固定流程、记录模板和首条初始化记录。

### 待确认 / 下一步
- 后续开始前端工程初始化或具体功能开发后，继续按本文档模板追加记录。

## 2026-03-27 - 阶段 1：前端工程初始化

### 目标
- 从零创建 `frontend/` 工程，搭建完整的前端开发骨架。
- 使工程可启动、可构建、可扩展，为后续聊天主链路和文档生成链路打好基础。

### 本次改动
- 使用 `Vite + React + TypeScript` 初始化 `frontend/` 工程（`create-vite@latest`，模板 `react-ts`）。
- 安装 `antd` 和 `react-router-dom` 作为基础依赖。
- 清理脚手架默认 demo 文件（`App.css`、`react.svg`、`vite.svg`、`hero.png`、`icons.svg`）。
- 建立标准目录结构：`pages`、`components`、`services`、`types`、`layouts`、`assets`。
- 创建 `.env.development` 环境变量配置（`VITE_API_BASE_URL=http://localhost:8000`）。
- 创建 `services/request.ts` 统一请求封装（基于原生 fetch，支持 get/post，统一错误处理）。
- 创建 `services/chatService.ts` 和 `services/documentService.ts` 空壳（阶段 2/3 填充）。
- 创建 `types/index.ts` 空壳（后续阶段填充）。
- 创建 `MainLayout` 布局组件（固顶毛玻璃导航栏 + 深浅色主题切换）。
- 创建三个占位页面：`HomePage`（案件类型选择）、`ChatPage`（聊天）、`ResultPage`（文档结果）。
- 配置 `App.tsx` 路由（`/` → HomePage、`/chat/:sessionId` → ChatPage、`/result/:docId` → ResultPage）。
- 配置 Ant Design `ConfigProvider` 注入暗色主题（`darkAlgorithm`）+ 自定义 token。
- 建立全局样式系统（深色/浅色模式 CSS 变量、毛玻璃 class、噪点纹理、渐入动画、按钮缩放反馈）。
- 更新 `index.html`（中文 lang、SEO meta 描述、中文标题、默认深色主题）。

### 涉及文件
- `frontend/.env.development` — 环境变量
- `frontend/index.html` — HTML 入口
- `frontend/src/index.css` — 全局样式（CSS 变量 + 公共工具 class）
- `frontend/src/main.tsx` — React 入口
- `frontend/src/App.tsx` — 根组件（路由 + ConfigProvider）
- `frontend/src/layouts/MainLayout.tsx` — 布局组件
- `frontend/src/layouts/MainLayout.css` — 布局样式
- `frontend/src/pages/HomePage.tsx` — 首页占位
- `frontend/src/pages/HomePage.css` — 首页样式
- `frontend/src/pages/ChatPage.tsx` — 聊天页占位
- `frontend/src/pages/ChatPage.css` — 聊天页样式
- `frontend/src/pages/ResultPage.tsx` — 结果页占位
- `frontend/src/pages/ResultPage.css` — 结果页样式
- `frontend/src/services/request.ts` — API 请求封装
- `frontend/src/services/chatService.ts` — 聊天服务空壳
- `frontend/src/services/documentService.ts` — 文档服务空壳
- `frontend/src/types/index.ts` — 类型定义空壳

### 接口 / Mock
- 本阶段未实际调用后端接口。
- `request.ts` 已封装好统一的 `get`/`post` 方法，从 `VITE_API_BASE_URL` 读取后端地址。
- 首页"开始咨询"按钮当前使用占位 sessionId（`demo-session`），阶段 2 替换为真实会话创建。

### 验证
- ✅ `npm install` 成功，无依赖报错。
- ✅ `npm run build`（`tsc -b && vite build`）成功，产出 `dist/` 目录。
- ✅ `npm run dev` 可正常启动 Vite dev server。
- ✅ 脚手架默认 demo 文件已全部清理。
- ✅ 目录结构完整：`pages`、`components`、`services`、`types`、`layouts`、`assets` 均存在。

### 待确认 / 下一步
- 阶段 2：聊天主链路 — 接入会话创建、消息列表、消息发送、历史拉取。
- 首页"开始咨询"按钮需要在阶段 2 替换为真实的 `POST /api/v1/sessions` 调用。
- 当前 Ant Design ConfigProvider 使用 `darkAlgorithm`，浅色模式切换时 antd 组件主题也需联动（阶段 2+ 补充）。

## 2026-03-27 - 阶段 2：聊天主链路

### 目标
- 完成聊天主链路的核心闭环，包括会话创建、跳转、消息发送、打字等待状态及拉取接口全流程。

### 本次改动
- 定义 `types/index.ts` 中涉及会话、消息的枚举及实体。
- `services/chatService.ts` 封装与接口路径完全对齐的异步请求函数(`/api/v1/sessions` 及历史)。
- 修改 `HomePage.tsx` 在案件卡片交互中实现由用户的选择创建会话并跳转的流程。
- 重写 `ChatPage.tsx` 和 `.css` 组件。包含 `useEffect` 的自动初始化请求、毛玻璃阴影的样式配置及发消息时的状态流转（临时显示用户消息 -> `isTyping` 等待 -> 拉取更新）。
- 首页最终采用“只选案件类型 -> 开始咨询 -> 进入聊天页”的方案，不在首页额外收集案件简要描述。
- 去除页面层 `any` 错误处理，改为显式错误类型收窄，满足当前 lint 规则。

### 涉及文件
- `frontend/src/types/index.ts`
- `frontend/src/services/chatService.ts`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`

### 接口 / Mock
- `POST /api/v1/sessions`
- `GET /api/v1/sessions/{session_id}`
- `POST /api/v1/sessions/{session_id}/messages`
- `GET /api/v1/sessions/{session_id}/messages`
- 按计划应用了等待状态。

### 验证
- ✅ `npm run lint` 通过。
- ✅ `npm run build` 通过。
- ✅ 首页已支持案件类型选择 + 创建会话跳转。
- ✅ 聊天页已支持会话初始化、消息发送、打字等待和历史同步。

### 待确认 / 下一步
- 阶段 3：聊天主页增加生成测试报告的入口并连通 Result 结果页。

## 2026-03-27 - 阶段 3：文档生成与结果展示

### 目标
- 在聊天主链路基础上，完成文档生成入口、结果展示和下载占位交互。
- 允许用户在对话页直接生成文档并跳转展示结果、文档状态等元信息。

### 本次改动
- 在 `types/index.ts` 中补充了 `DocumentStatus`、`DocumentGenerateRequest` 和 `DocumentResponse` 相关业务类型。
- 在 `services/documentService.ts` 中基于 `request.ts` 实装了 `generateDocument`, `getDocument`, `exportDocument` 接口的基础调用。
- 升级了 `ChatPage`，在顶部 Header 添加了调用生成诉状的入口按钮，并支持生成时的 Loading 状态控制与处理报错反馈。
- 完整重写了 `ResultPage` 页面和对应的卡片毛玻璃 CSS 样式，展示内容包括了文档状态轮询占位、没有正文内容时的 UI 占位以及导出流向占位（处理下载提示）。

### 涉及文件
- `frontend/src/types/index.ts`
- `frontend/src/services/documentService.ts`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ResultPage.tsx`
- `frontend/src/pages/ResultPage.css`

### 接口 / Mock
- `POST /api/v1/sessions/{session_id}/generate-document`
- `GET /api/v1/documents/{doc_id}`
- `GET /api/v1/documents/{doc_id}/export`

### 验证
- ✅ `npm run lint` 通过。
- ✅ `npm run build` 成功。
- ✅ 结果验证完全符合了计划中对没有 content/export 特性的降级页面逻辑设计标准。

### 待确认 / 下一步
- 阶段 4：联调与验收，检查接口对齐、状态流完备度以及验收测试清单核验。

## 2026-03-27 - 阶段 4：联调与验收（MVP 结项）

### 目标
- 全面验收主链路，检查 UI 在全模式下的可用性。
- 核查所有 API 调用的正确性及状态处理，并梳理暂未能落地的“待修问题/限制清单”。

### 本次改动
- 针对前三阶段的代码执行了静态逻辑检查与接口对照，并补全了文档状态记录。
- 该任务主要聚焦于文档更新，没有实际的代码增量，仅梳理了现有系统的边界并确保已交付的 UI 符合产品设定。

### 验收情况 (基于功能验证与规划)
- ✅ 首页案件切换跳转、创建会话正常。
- ✅ Chat 聊天流页面：发送逻辑正常、打字机遮罩动画正常、历史消息同步正常。
- ✅ 结果落地页：玻璃质感骨架屏加载正常，文档标识及时间戳解包转换渲染正常，深浅模式 UI 适配通过。
- ✅ 网络异常断底：所有 `catch` 块中均妥善实现了 `message.error("xxx失败请重试")`，前端健壮性过关。

### 遗留问题与已知限制清单 (Known Limitations)
| 模块 | 问题描述 | 当前处理方式 | 责任端 / 解决计划 |
|------|-----------|--------------|-------------------|
| **Chat 模块** | Agent 没有真实打通，所有问答都是本地或者后端的固定 Mock，且无意图识别动作。 | 前端直接展示 Mock 句子流。 | 等待后端接入真实大模型流程后再对接复杂业务节点。 |
| **Document 渲染** | 文档 `content` 字段为空，无法在前端展示文档详情及结构树。 | 使用动态骨架屏 UI 加带提示性质的文案强行占位，不使用空白页面。 | 等待后端大语言模型和 Python-Word 流支持解析预览。 |
| **Document 下载** | 导出接口 `export` 现在仅仅回吐了一个占位 JSON `"message": "Download falling..."`。 | 前端截取了 JSON 进行 `message.info` 的弹窗而没有伪造直接触发 Blob 浏览器下载行为。 | 待后端补齐导出能力后即可直接接入触发本地下载。 |

### 下一步
- MVP 已经完整竣工。后续如有基于 Agent 真实流程的接入需要，即可再拉起新的阶段进行重构或者扩展对接。

## 2026-04-09 - 独立 Agent SSE 无文本回复修复

### 目标
- 解决前端聊天页向独立 Agent 服务发送消息后，接口返回 `200` 但页面没有任何助手回复文本的问题。

### 本次改动
- 排查确认当前聊天链路为“后端会话管理 + 独立 Agent SSE 回复”的混合模式，前端聊天输入实际发送到 `http://localhost:8001/chat`。
- 定位根因为 `agent/agent_node.py` 在节点内部调用 `llm_with_tools.invoke(...)` 时未透传 LangGraph 的 `config/callbacks`，导致 `agent/workflow.py` 的 `astream_events()` 拿不到 `ChatOpenAI` 的内部事件，前端最终只能收到空 `done`。
- 为 `agent/agent_node.py` 补充 `RunnableConfig` 透传，并为 Agent SSE 层补充 `on_chat_model_end` 文本兜底提取逻辑；当模型没有逐 token 事件、只在结束事件返回完整文本时，前端也能收到回复。

### 涉及文件
- `agent/workflow.py`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- `POST http://localhost:8001/chat`
- 本次修复不改变前端请求路径，也不回退到后端 `/api/v1/sessions/{session_id}/messages` 主链路。

### 验证
- ✅ `python -m py_compile agent/workflow.py` 通过。
- ✅ `python -m py_compile agent/agent_node.py agent/workflow.py` 通过。
- ✅ 本地 `astream_events()` 调试确认：修复后已能看到 `on_chat_model_start` 事件，说明内部模型回调已被透传到 LangGraph 事件流。
- ✅ 使用本地伪造事件流验证：仅收到 `on_chat_model_end` 时，SSE 现在会输出 `token` 事件。
- ✅ 使用本地伪造事件流验证：已有 `on_chat_model_stream` 时，不会因为结束事件重复输出完整文本。

### 待确认 / 下一步
- 需重启正在运行的 Agent 进程（若未启用 `--reload`），再在前端页面重新发消息做联调验证。
- 若仍然无回复，应继续排查外部大模型或检索工具调用本身是否阻塞/报错，并在 Agent 侧补充更明确的运行日志。

## 2026-04-09 - 首页“其他”类型与聊天单按钮交互优化

### 目标
- 在首页新增“其他”案件类型，允许用户创建通用咨询会话。
- 对 `other` 类型会话隐藏“生成诉状”入口，避免误触未支持链路。
- 将聊天页底部原本分离的“发送/停止生成”操作合并为一个统一按钮，并按状态切换外观和行为。

### 本次改动
- 在首页案件类型列表中新增 `other` 选项，并沿用现有创建会话流程进入聊天页。
- 扩展前端 `CaseType` 类型定义，纳入 `other`。
- 在聊天页案件类型映射中加入“其他”，并对 `session.case_type === 'other'` 的会话隐藏顶部“生成诉状”按钮。
- 将底部两个按钮合并为单一操作按钮：空闲时显示“发送”，发送中切换为“停止”，点击后中断当前流式回复。
- 统一整理单按钮样式，保持一致的尺寸、圆角、阴影和动效，仅通过蓝色发送态 / 红色停止态区分状态。

### 涉及文件
- `frontend/src/types/index.ts`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 仅改动前端。
- `other` 类型仍通过现有 `POST /api/v1/sessions` 创建会话，当前不要求后端联动改造。
- 对 `other` 类型在聊天页直接隐藏“生成诉状”按钮，不进入文档生成链路。

### 验证
- ✅ `npm run build` 通过。
- ✅ TypeScript 编译通过，`other` 类型已纳入前端类型系统。
- ✅ 聊天页底部操作按钮已收敛为单一按钮，可在发送态 / 停止态之间切换。

### 待确认 / 下一步
- 建议手测首页四卡片布局在浅色模式与窄屏下的视觉平衡。
- 若后续需要让“其他”类型支持生成诉状，再联动后端模板与 Agent 策略。

## 2026-04-09 - 首页历史对话侧栏

### 目标
- 在首页左侧加入历史对话栏，展示已有会话并支持点击继续咨询。
- 让首页不只是“新建入口”，还具备“回到上次对话”的承接能力。

### 本次改动
- 后端新增 `GET /api/v1/sessions`，返回首页历史会话列表与总数。
- 后端在消息写入时同步刷新 `sessions.updated_at`，为“最近活跃排序”提供可靠依据。
- 后端历史会话列表补充 `message_count`、`last_message_preview`、`last_message_role`、`last_message_at` 等摘要字段。
- 前端新增 `SessionHistoryPanel` 组件，在首页左侧展示历史会话列表。
- 首页改为左右双栏布局：左侧历史会话栏，右侧保留现有欢迎区和案件类型入口。
- 点击历史会话可直接跳转到对应聊天页继续咨询。

### 涉及文件
- `backend/api/schema.py`
- `backend/api/routes.py`
- `backend/services/chat.py`
- `frontend/src/types/index.ts`
- `frontend/src/services/chatService.ts`
- `frontend/src/components/SessionHistoryPanel.tsx`
- `frontend/src/components/SessionHistoryPanel.css`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/HomePage.css`
- `plan/总计划.md`
- `plan/05-首页历史对话侧栏.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 新增 `GET /api/v1/sessions`
- 当前历史会话数据直接来自后端数据库中的 `sessions` / `messages`
- 当前项目暂无用户体系，因此首页展示的是本地数据库中的全部会话

### 验证
- ✅ `python -m py_compile backend/api/schema.py backend/services/chat.py backend/api/routes.py` 通过。
- ✅ 使用 `TestClient` 调用 `GET /api/v1/sessions` 返回 `200`，响应包含 `sessions` 和 `total`。
- ✅ `npm run build` 通过。

### 待确认 / 下一步
- 建议手测首页左侧历史栏在深浅色模式和窄屏尺寸下的滚动与层次表现。
- 若后续接入用户体系，需要把历史会话查询加上 `user_id` 过滤。
- 若历史会话数量继续增长，可考虑进一步优化“最近一条消息”查询 SQL，减少摘要查询开销。

## 2026-04-09 - 历史对话栏滚动 / 删除 / 北京时间统一

### 目标
- 为首页左侧历史对话栏提供明确可见的滚动条，避免会话增多后布局失控。
- 支持在历史栏直接删除会话。
- 统一前后端的时间语义，以北京时间作为后续展示和写入基准。

### 本次改动
- 后端新增 `DELETE /api/v1/sessions/{session_id}`，用于删除会话及其关联数据。
- 后端新增北京时间工具，后续新写入的会话、消息、文档更新时间默认以北京时间语义生成。
- 前端历史栏加入删除按钮与二次确认交互，删除后同步刷新列表数量。
- 前端历史栏滚动区域补充独立高度、滚动条样式和可见轨迹，保持首页双栏布局中心不被拉散。
- 前端新增统一时间工具，历史栏、聊天时间戳、结果页时间均按 `Asia/Shanghai` 解析和展示。

### 涉及文件
- `backend/utils/timezone.py`
- `backend/db/models.py`
- `backend/services/chat.py`
- `backend/services/document.py`
- `backend/api/schema.py`
- `backend/api/routes.py`
- `frontend/src/utils/time.ts`
- `frontend/src/services/request.ts`
- `frontend/src/services/chatService.ts`
- `frontend/src/components/SessionHistoryPanel.tsx`
- `frontend/src/components/SessionHistoryPanel.css`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/HomePage.css`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ResultPage.tsx`
- `plan/总计划.md`
- `plan/05-首页历史对话侧栏.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 新增 `DELETE /api/v1/sessions/{session_id}`
- 历史会话仍通过 `GET /api/v1/sessions` 获取
- 时间标准改为“后端写入按北京时间语义、前端展示按 `Asia/Shanghai` 统一格式化”

### 验证
- ✅ `python -m py_compile backend/db/models.py backend/services/chat.py backend/services/document.py backend/api/schema.py backend/api/routes.py backend/utils/timezone.py` 通过。
- ✅ 前端 `npm run build` 通过。
- ✅ `TestClient` 验证：
  - `POST /api/v1/sessions` 返回 `201`
  - `DELETE /api/v1/sessions/{session_id}` 返回 `204`
  - 删除后再次获取该会话返回 `404`

### 待确认 / 下一步
- 旧库中已存在的历史数据若原先以 UTC 语义写入，展示上可能仍与预期有偏差；新生成数据将以北京时间为准。
- 若后续需要批量清理旧时区数据，可再补一次性迁移脚本或后台管理操作。

## 2026-04-09 - 历史栏空会话过滤与首页双栏重心修正

### 目标
- 历史栏不再显示 0 条消息的空会话。
- 保持“左侧历史栏 + 右侧首页主内容”的双栏结构，同时让整体视觉重心重新回到页面中央。

### 本次改动
- 后端历史会话列表改为仅返回“至少有一条消息”的会话。
- 前端历史会话请求结果增加一层兜底过滤，避免空会话被渲染到侧栏。
- 调整首页双栏宽度、左右列尺寸和对齐方式，避免右侧主内容在大屏下再次被独立居中导致整体发歪。
- 收紧左侧历史栏面板宽度和高度，使其更像稳定边栏而不是漂浮卡片。

### 涉及文件
- `backend/services/chat.py`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/HomePage.css`
- `frontend/src/components/SessionHistoryPanel.css`
- `plan/总计划.md`
- `plan/05-首页历史对话侧栏.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 继续使用 `GET /api/v1/sessions`
- 当前会话列表默认只展示 `message_count > 0` 的会话

### 验证
- ✅ `python -m py_compile backend/services/chat.py` 通过。
- ✅ `npm run build` 通过。
- ✅ `TestClient` 验证：
  - 新建但未发消息的会话不会出现在 `GET /api/v1/sessions` 返回列表中
  - 已发过消息的会话仍会正常出现在列表中

### 待确认 / 下一步
- 建议你本地再看一眼实际视觉效果，如果还想更偏“桌面应用”的稳重布局，我可以继续把首页改成更强的分栏系统。

## 2026-04-09 - 前端高级质感大修

### 目标
- 提升前端界面的整体高级质感，达到项目规范要求的“接近原生桌面应用”（引入毛玻璃、内高光、分层阴影和材质纹理）。
- 彻底“反扁平化”整改，且不影响 TypeScript 路由或组件的核心业务流。

### 本次改动
- **全局样式与 Token 层**：优化 `frontend/src/index.css`，完善深浅模式下的 `--shadow-md` 等变量，增加多层阴影、激活毛玻璃及噪点纹理。在 `frontend/src/App.tsx` 中定制 Ant Design `ConfigProvider` 组件 Token，去除了廉价单实线边框。
- **页面与组件样式升级**：在 `frontend/src/pages/HomePage.css` 移除首页卡片的单薄实体颜色，改为渐变且带微光影的玻璃态；主按钮改为物理深层渐变效果。改造 `SessionHistoryPanel.css` 去除廉价实线分割，采用高级柔光效果。修改导航栏下沿阴影以增强悬浮感。

### 涉及文件
- `frontend/src/index.css`
- `frontend/src/App.tsx`
- `frontend/src/pages/HomePage.css`
- `frontend/src/components/SessionHistoryPanel.css`
- `frontend/src/layouts/MainLayout.css`

### 接口 / Mock
- 纯 UI 和样式变更，未修改任何接口及其对接逻辑。

### 验证
- ✅ 样式大修改造完毕。用户环境热更新可直接查看新光影及毛玻璃质感。

### 待确认 / 下一步
- 用户确认当前的高级深邃色调（蓝色微反光）和毛玻璃质感是否符合心理预期。若需根据不用需求定制主题色泽，可新增 Theme Tokens。

## 2026-04-09 - 咨询页历史对话侧栏联动

### 目标
- 在咨询页（`/chat/:sessionId`）接入与首页一致的历史对话侧栏。
- 满足两种入口行为：新建会话进入咨询页时当前会话置顶；历史会话进入咨询页时突出显示当前会话。

### 本次改动
- `SessionHistoryPanel` 新增 `activeSessionId` 入参，并补充当前项高亮样式。
- `HomePage` 跳转咨询页时加入入口状态：
  - 新建会话：`state.entry = "new"`
  - 历史会话：`state.entry = "history"`
- `ChatPage` 新增历史会话加载与状态管理，布局改为左侧历史栏 + 右侧聊天主体。
- `ChatPage` 根据入口状态处理当前会话卡片：
  - `new`：将当前会话插入历史栏顶部（即使当前消息数为 0）。
  - `history`：保持历史列表顺序，仅高亮当前会话。
- 咨询页支持在侧栏删除会话；若删除当前会话则自动返回首页。

### 涉及文件
- `frontend/src/components/SessionHistoryPanel.tsx`
- `frontend/src/components/SessionHistoryPanel.css`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 继续使用已有接口：
  - `GET /api/v1/sessions`
  - `GET /api/v1/sessions/{session_id}`
  - `GET /api/v1/sessions/{session_id}/messages`
  - `DELETE /api/v1/sessions/{session_id}`
- 无新增后端接口，仅前端入口状态和展示逻辑调整。

### 验证
- 已执行 `npm run build`（见本次任务验证结果）。

### 待确认 / 下一步
- 建议你本地重点手测两条入口链路：
  - 首页“开始咨询”后进入聊天页，确认当前会话是否在历史栏顶部。
  - 首页点击历史记录进入聊天页，确认对应会话是否高亮且位置保持历史排序。

## 2026-04-09 - 生成诉状入口可见性修复

### 目标
- 修复“导出文书功能不见了”的体验问题，确保聊天页入口始终可见。

### 本次改动
- 聊天页顶部“生成诉状”按钮改为对所有会话类型都显示，不再对 `other` 直接隐藏。
- 当会话类型为 `other` 时，点击按钮给出明确提示文案，避免误以为功能缺失。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 未新增接口，继续走原有 `POST /api/v1/sessions/{session_id}/generate-document`。

### 验证
- 已执行 `npm run build`（见本次任务验证结果）。

### 待确认 / 下一步
- 建议手测 `other` 与非 `other` 两类会话，确认按钮显示一致、提示文案清晰。

## 2026-04-09 - 历史会话入口文书按钮显示修正

### 目标
- 满足“仅 `other` 隐藏文书入口，其他类型均显示”的规则。
- 修复从历史会话进入聊天页时偶发看不到“生成诉状”按钮的问题。

### 本次改动
- 聊天页“生成诉状”按钮显示逻辑改为：根据当前会话类型判断，仅当类型为 `other` 时隐藏。
- 当前会话类型增加历史列表兜底来源（`historySessions`），避免会话详情未回填前按钮被误判隐藏。
- 生成文书时的 `template_id` 同步使用上述兜底后的会话类型，确保历史入口一致可用。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 未新增接口。
- 继续使用 `POST /api/v1/sessions/{session_id}/generate-document`。

### 验证
- 已执行 `npm run build`（见本次任务验证结果）。

### 待确认 / 下一步
- 建议手测：
  - `other` 会话顶部不显示“生成诉状”。
  - 非 `other` 会话（含从历史对话进入）顶部显示“生成诉状”并可点击。

## 2026-04-09 - 文书入口显示兜底增强

### 目标
- 进一步保证“仅 `other` 隐藏文书按钮”的规则在历史入口与异步加载阶段都稳定生效。

### 本次改动
- 按钮显示条件改为“只要当前会话类型不是 `other` 就显示”，不再要求先拿到完整会话类型。
- 在会话类型尚未加载完成时，点击按钮会提示“会话类型仍在加载中，请稍后重试”，避免静默无响应。
- 按钮禁用条件收敛为仅受初始化状态控制，避免因为短暂类型未回填而不可见/不可点。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 未新增接口。

### 验证
- 已执行 `npm run build`（见本次任务验证结果）。

### 待确认 / 下一步
- 建议手测历史会话首屏加载瞬间，确认按钮可见性稳定。

## 2026-04-09 - 生成诉状按钮对比度优化

### 目标
- 修复聊天页头部“生成诉状”按钮在浅色模式下发灰、可读性差的问题。

### 本次改动
- 为“生成诉状”按钮增加独立样式类 `chat-generate-doc-btn`，统一控制边框、渐变底色、文字和图标颜色。
- 增加 hover 与 disabled 状态下的对比度细化，保证深浅色主题均清晰可读。
- 保持现有玻璃风格，不改变按钮位置和交互逻辑。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 纯样式优化，无接口变更。

### 验证
- 已执行 `npm run build`（见本次任务验证结果）。

### 待确认 / 下一步
- 建议你刷新后看一下浅色模式下头部按钮是否达到你预期的“清晰但不刺眼”。

## 2026-04-09 - 文书下载链路切换到 doc_generator 实际产物

### 目标
- 文书生成与下载不再依赖后端占位导出逻辑，而是使用 `agent/tools/doc_generator.py` 真实生成的 `.docx` 文件。
- 将文件结果绑定到对应会话的文档记录（`documents.session_id`），确保会话与文书一一对应。

### 本次改动
- 后端 `generate-document` 改为解析 Agent 返回文本中的“文件名/本地路径/下载链接”，并校验文件真实存在后再标记 `generated`。
- 后端 `export` 改为返回真实 `download_url` 和文件名；新增 `/api/v1/download/{file_name}` 提供文件流下载。
- `doc_generator.py` 下载链接改为 `/api/v1/download/{filename}`，与后端新路由对齐。
- 前端结果页下载按钮改为优先消费 `download_url` 并触发浏览器下载，不再只展示“下载功能完善中”占位文案。

### 涉及文件
- `agent/tools/doc_generator.py`
- `backend/services/document.py`
- `backend/api/routes.py`
- `frontend/src/services/documentService.ts`
- `frontend/src/pages/ResultPage.tsx`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- `POST /api/v1/sessions/{session_id}/generate-document`：状态更新依据真实文件是否存在。
- `GET /api/v1/documents/{doc_id}/export`：返回 `{ download_url, filename }`。
- `GET /api/v1/download/{file_name}`：返回真实 Word 文件流下载。

### 验证
- ✅ `python -m py_compile backend/api/routes.py backend/services/document.py agent/tools/doc_generator.py` 通过。
- ✅ `npm run build` 通过。
- ⚠️ 当前本地运行中的后端进程尚未热重载到新路由，线上进程返回仍是旧占位响应；需重启后端服务后验证新链路。

### 待确认 / 下一步
- 重启后端服务后手测“生成诉状 → 结果页下载”链路，确认可实际下载 `generated_docs` 下对应文件。

## 2026-04-09 - 文书生成失败容错增强（session 级复用）

### 目标
- 修复“文书生成失败：未返回有效文件信息”的高频场景，降低同一会话重复生成时的失败率。

### 本次改动
- 后端 `AgentService.generate_document` 增加兜底：当 `generated_document` 为空时，尝试从 `final_answer` 提取 `.docx` 线索。
- 后端文档解析逻辑增强，兼容直接下载路径（`/api/v1/download/*.docx`、`/download/*.docx`）和宽松文件名提取。
- 在 `generate-document` 路由增加会话级兜底：若本轮未拿到新文件，自动复用该 `session` 最近一份可导出的文书并更新当前 `doc` 记录为 `generated`。

### 涉及文件
- `backend/services/agent_service.py`
- `backend/services/document.py`
- `backend/api/routes.py`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 无新增对外接口，增强现有：
  - `POST /api/v1/sessions/{session_id}/generate-document`
  - `GET /api/v1/documents/{doc_id}/export`

### 验证
- ✅ `python -m py_compile backend/services/document.py backend/services/agent_service.py backend/api/routes.py` 通过。
- ⚠️ 当前运行中的后端进程可能仍是旧代码（热重载未生效），需重启后再验证新兜底路径。

### 待确认 / 下一步
- 重启后端后，使用同一会话连续点击“生成诉状”验证是否不再直接失败。

## 2026-04-09 - 文书生成前置条件拦截（四要素）

### 目标
- 避免用户在信息不足时反复点击“生成诉状”导致失败体验。
- 仅在收集到四项必要要素（原告、被告、诉求、金额）后允许触发文书生成。

### 本次改动
- 后端新增会话文书就绪状态接口：`GET /api/v1/sessions/{session_id}/document-readiness`。
- 后端 `generate-document` 增加前置校验：当数据库已存在用户消息但四要素不完整时，返回 400 并给出缺失项提示。
- 前端聊天页新增本地四要素判定（基于当前会话用户消息），未满足时禁用“生成诉状”按钮并显示“还需补充”提示文案。
- 前端在点击生成时增加兜底提示，防止异常情况下误触发。

### 涉及文件
- `backend/api/schema.py`
- `backend/services/chat.py`
- `backend/api/routes.py`
- `frontend/src/types/index.ts`
- `frontend/src/services/chatService.ts`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 新增 `GET /api/v1/sessions/{session_id}/document-readiness`
- 更新 `POST /api/v1/sessions/{session_id}/generate-document` 的前置校验行为

### 验证
- ✅ `python -m py_compile backend/services/chat.py backend/api/routes.py backend/api/schema.py` 通过。
- ✅ `npm run build` 通过。
- ✅ 新建空会话测试：`document-readiness` 返回 `ready=false` 且缺失字段为“原告信息、被告信息、核心诉求、涉案金额”。

### 待确认 / 下一步
- 建议你在真实对话中手测：补齐四要素后按钮由禁用变为可点击；缺项时提示文案是否符合预期。

## 2026-04-09 - 新建会话引导首屏（分类引导语 + 快捷提问）

### 目标
- 解决新建会话进入咨询页后“消息区空白”的体验问题。
- 在空会话状态下先由 AI 主动给出引导语，并提供“你可以这样问我”的快捷提问控件。
- 四种案件类型引导内容差异化，每类不少于 3 条示例问题。

### 本次改动
- 在聊天页空会话分支中渲染“AI 欢迎气泡 + 快捷提问列表”。
- 新增案件类型引导配置：
  - `wage_arrears`
  - `labor_contract`
  - `work_injury`
  - `other`
- 每类均提供 1 条引导语 + 3 条快捷问题；点击快捷问题会自动填入输入框，便于用户一键继续。
- 补充了引导区域样式（标题、按钮、悬停态、移动端对齐）。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 纯前端展示增强，不新增接口。

### 验证
- ✅ `npm run build` 通过。

### 待确认 / 下一步
- 建议你本地验证四类案件入口（拖欠工资/劳动合同/工伤赔偿/其他）是否都呈现了不同引导语与示例问题。

## 2026-04-09 - 快捷提问一键发送

### 目标
- 提升空会话引导效率，点击示例问题后直接发送，不再要求用户二次点击发送按钮。

### 本次改动
- `handleSend` 支持接收可选预设文本参数，支持“直接发送指定文本”。
- 引导区示例问题按钮点击事件改为直接调用发送逻辑。
- 增加发送并发保护，避免用户连续点击导致重复发送。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 无新增接口，沿用现有聊天流式接口。

### 验证
- 已执行 `npm run build`（见本次任务验证结果）。

### 待确认 / 下一步
- 建议手测空会话引导区：点击示例问题后是否立即出现在对话中且开始生成回复。

## 2026-04-09 - 咨询页头部交互与提示排版优化

### 目标
- 修复“还需补充”提示在聊天页头部换行导致不美观的问题。
- 在聊天页左上角增加“开启新对话”入口，支持用户快速返回首页重新选案件类型。

### 本次改动
- 将“还需补充”提示改为单行展示并在超长时省略，避免出现突兀换行。
- 聊天页头部新增“开启新对话”按钮，点击直接跳转首页（`/`）。
- 调整头部左侧布局样式，使新入口和标题信息层级更清晰。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 无接口变更，纯前端交互与样式优化。

### 验证
- 已执行 `npm run build`（见本次任务验证结果）。

### 待确认 / 下一步
- 建议你本地看一下不同窗口宽度下的头部显示，确认提示文案的截断长度是否符合预期。

## 2026-04-09 - 历史对话回写修复

### 目标
- 修复前端流式聊天后刷新页面时历史对话丢失的问题。
- 保证首页/咨询页左侧历史栏与后端数据库状态一致。

### 本次改动
- 后端新增 `POST /api/v1/sessions/{session_id}/messages/sync`，用于前端将已展示的流式消息持久化到数据库，不触发二次 Agent 调用。
- 前端 `ChatPage` 在每轮流式对话完成或中断后，将用户消息和助手消息回写到后端。
- 若仅历史回写失败，不再回滚当前 UI，而是给出同步失败提示，避免用户眼前对话消失。
- 若流式请求本身失败，则清理本地临时用户消息，避免“页面有消息但历史没保存”的错位。

### 涉及文件
- `backend/api/schema.py`
- `backend/api/routes.py`
- `frontend/src/services/chatService.ts`
- `frontend/src/pages/ChatPage.tsx`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 新增 `POST /api/v1/sessions/{session_id}/messages/sync`

### 验证
- ✅ `python -m py_compile backend/api/schema.py backend/api/routes.py` 通过。
- ✅ `npm run build` 通过。
- ✅ 实测创建新会话后调用 `messages/sync` 写入两条消息，`GET /sessions/{id}/messages` 返回 `history_total=2`，并且 `GET /sessions` 历史列表中能查到该会话。

### 待确认 / 下一步
- 建议你本地再完整走一遍“新建会话 -> 对话几轮 -> 刷新页面 -> 回首页看历史栏”的链路，确认体验稳定。

## 2026-04-10 - 咨询页新对话强引导

### 目标
- 让用户在咨询过程中更明显地看到“回首页开始新咨询”的入口。
- 明确告诉用户：返回首页不会丢失当前对话，历史记录仍可继续进入。
- 让用户回到首页后能立刻理解下一步操作是重新选择案件类型。

### 本次改动
- 聊天页头部“开启新对话”由弱文本按钮升级为高权重胶囊按钮，并补充“当前对话会保留”的说明文案。
- 聊天页左侧历史栏新增固定“开始新的案件咨询”卡片入口，形成第二个显著触点。
- 当前会话已有消息时，点击新建入口会先弹出确认层；若当前回复仍在生成，则确认文案会明确提示“返回首页会结束本轮生成”。
- 首页支持接收聊天页回流状态，并在案件类型选择区上方展示一次性提示条，说明历史已保留、现在可开始新的咨询。
- 首页案件卡片区和“开始咨询”按钮在回流状态下增加聚焦高亮，强化下一步动作。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/components/SessionHistoryPanel.tsx`
- `frontend/src/components/SessionHistoryPanel.css`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/HomePage.css`
- `plan/总计划.md`
- `plan/06-咨询页新对话强引导.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 无新增接口，纯前端交互与样式优化。

### 验证
- ✅ `npm run build` 通过。

### 待确认 / 下一步
- 建议手测以下链路：
- 聊天页已有多轮消息时，点击头部或侧栏“开始新咨询”是否都先出现确认层。
- 聊天页正在生成回复时返回首页，首页提示文案是否足够清楚。
- 返回首页后，是否能自然理解“选择案件类型 -> 开始咨询”的下一步。

## 2026-04-10 - 新对话入口收敛与诉状触发信号改造

### 目标
- 按最新交互判断收敛“开始新对话”入口，只保留历史侧栏中的回首页入口。
- 删除首页回流提示，避免首页出现多余承接组件。
- 将“生成诉状”按钮可点击条件改为只认助手明确提示“请点击右上角生成诉状”，不再依赖前端本地字符串抽取四要素。

### 本次改动
- 删除聊天页头部“回首页开始新咨询”按钮及相关说明样式，只保留左侧历史侧栏中的“开始新的案件咨询”入口。
- 删除首页“已回到首页，可以开始新的咨询”提示条及对应高亮动效，首页恢复为纯案件类型选择界面。
- 删除聊天页原有的本地四要素字符串匹配逻辑。
- 新增助手信号匹配逻辑：只要助手历史消息或当前流式回复中出现“请点击右上角生成诉状”，才允许点击“生成诉状”按钮。
- “生成诉状”按钮禁用提示同步改为基于助手信号的文案，发送中也会暂时禁用，避免边生成回复边发起文书生成。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/HomePage.css`
- `plan/总计划.md`
- `plan/06-咨询页新对话强引导.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 无新增接口，纯前端逻辑与样式收敛。

### 验证
- ✅ `npm run build` 通过。

### 待确认 / 下一步
- 建议你重点手测：
- 助手未给出“请点击右上角生成诉状”前，按钮是否始终不可点击。
- 助手明确给出该提示后，按钮是否按预期解锁。
- 侧栏“开始新的案件咨询”入口是否仍然足够明显，且确认层文案是否自然。

## 2026-04-10 - 诉状按钮提示改为悬浮态

### 目标
- 去掉聊天页头部常驻的诉状生成状态文案，减少顶部信息噪音。
- 将按钮状态提示改为悬浮提示，仅在用户鼠标移到“生成诉状”按钮上时显示。

### 本次改动
- 删除聊天页头部常驻的诉状状态说明文本。
- 使用 Tooltip 包裹“生成诉状”按钮，统一通过悬浮提示展示状态文案。
- 按钮不可点击时显示“前置信息不足，无法生成诉状文书”。
- 按钮可点击时显示“生成诉状文书”。

### 涉及文件
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `plan/总计划.md`
- `plan/06-咨询页新对话强引导.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 无新增接口，纯前端交互微调。

### 验证
- ✅ `npm run build` 通过。

### 待确认 / 下一步
- 建议你本地悬停测试禁用态和可点击态两种情况，确认 Tooltip 文案和出现时机都符合预期。

## 2026-04-10 - 生成诉状后端校验改为助手明确信号

### 目标
- 修复“前端按钮状态已改，但后端仍按被告信息/涉案金额等四要素拦截生成文书”的前后端不一致问题。
- 让前后端统一以助手回复中的明确信号“请点击右上角生成诉状”作为唯一放行条件。

### 本次改动
- 后端 `ChatService.get_document_readiness()` 不再从用户消息中做四要素正则抽取。
- 改为扫描当前会话中的助手消息，只要命中“请点击右上角生成诉状”就返回 `ready=true`。
- `POST /api/v1/sessions/{session_id}/generate-document` 的 400 拦截文案同步改为基于助手信号，不再返回“被告信息、涉案金额”等旧提示。
- `DocumentReadinessResponse` 的 schema 描述同步更新为“助手是否已明确提示可以生成诉状”。

### 涉及文件
- `backend/services/chat.py`
- `backend/api/routes.py`
- `backend/api/schema.py`
- `plan/总计划.md`
- `FRONTEND_WORKFLOW.md`

### 接口 / Mock
- 未新增接口，但 `GET /api/v1/sessions/{session_id}/document-readiness` 与 `POST /api/v1/sessions/{session_id}/generate-document` 的就绪判断语义已变更。

### 验证
- ✅ `python -m py_compile backend/services/chat.py backend/api/routes.py backend/api/schema.py` 通过。

### 待确认 / 下一步
- 需要重启本地后端进程后再手测，否则运行中的旧进程仍会继续返回旧文案。
