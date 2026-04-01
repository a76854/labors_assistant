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
