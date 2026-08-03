# 劳动维权平台 (labors_assistant)

> 用AI技术帮助劳动者维权，一键生成高质量诉状，让法律援助不再是奢侈品。

## 📖 用户故事

### 故事1：快速生成诉状
**角色：** 拖欠工资的劳动者  
**场景：** 小王在某互联网公司工作8个月，被拖欠4个月工资，想起诉公司。  
**需求：** 通过简单的对话收集信息，系统自动生成一份格式正确、法律用语准确的诉状。  
**验收标准：** 
- 5轮以内的对话完成信息收集
- 生成的诉状包含完整的"当事人""事实和理由""诉讼请求"
- 诉状引用适用法律条款（《劳动法》《劳动合同法》等）
- 导出PDF/Word格式可供法院提交

### 故事2：多轮精化诉状
**角色：** 需要补充细节的劳动者  
**场景：** 首次对话后生成诉状，但发现细节不清楚，想修改并重新生成。  
**需求：** 支持多轮对话补充/修改信息，系统更新诉状内容。  
**验收标准：**
- 用户可编辑已收集的信息字段
- 修改后能快速重新生成诉状（<10s）
- 诉状版本有清晰的变更记录

### 故事3：参考相似案例
**角色：** 想了解法律胜诉可能性的劳动者  
**场景：** 想知道"拖欠工资"案件通常的判决结果和赔偿标准。  
**需求：** 系统自动检索相似的历史案例和适用法规条款，展示给用户参考。  
**验收标准：**
- 能从赛方法律API检索相似案例（2-3个）
- 展示案例的当事人、判决结果、法律依据
- 用户可点击"应用此案例"快速填充信息

### 故事4：下载和编辑诉状
**角色：** 准备提交法院的劳动者  
**场景：** 诉状生成后，想以Word格式下载，在律师帮助下做最后调整，然后打印提交法院。  
**需求：** 支持Word (.docx) 和PDF格式导出，用户可在Word中编辑。  
**验收标准：**
- 导出的Word格式排版规范，可被法院系统识别
- 所有法律术语和计算结果正确
- 用户可在Word中编辑，格式不破坏

---

## 🎯 核心功能

### P0 MVP必须
| 功能 | 说明 | 负责人 | 截止日期 |
|------|------|-------|---------|
| **多轮对话** | AI助手通过交互式对话收集诉讼信息 | 前端 + Agent | 4月10日 |
| **意图识别** | 自动识别纠纷类型（拖欠工资/劳动合同纠纷/工伤赔偿） | Agent | 4月10日 |
| **要素提取** | 智能提取当事人、事实、法律要素 | Agent | 4月10日 |
| **法律分析** | 检索赛方API的适用法条和相似案例 | Agent | 4月10日 |
| **诉状生成** | 格式规范、法律用语准确的诉状 | 文档系统 | 4月13日 |
| **多格式导出** | 支持Word (.docx) 和PDF格式下载 | 文档系统 + 后端 | 4月13日 |

### P1 如时间允许
| 功能 | 说明 | 负责人 | 截止日期 |
|------|------|-------|---------|
| **会话管理** | 用户保存对话历史，多次编辑和重新生成 | 后端 | 4月18日 |
| **案例查询** | 检索相似案例，参考判决结构 | Agent | 4月18日 |
| **用户账户** | 简单的用户注册和登录 | 后端 | 4月18日 |

### P2 平台化扩展
| 功能 | 说明 |
|------|------|
| **用户系统** | 劳动者/律师/超级管理员三角色，JWT 认证，会话按用户隔离 |
| **地区规则适配** | 北京/上海/广东 3 地区模板切换，文书受理机构按地区渲染 |
| **案件分诊** | 规则启发式证据完整度/风险评分（0-100），缺失证据清单，复杂度分级 |
| **智能推荐** | 按律师专长+地区自动匹配线索，匹配度评分+推荐理由，非全量展示 |
| **律师工作台** | 系统推荐线索首页 / 线索市场 / 我的接单 / 接单 / 一键补材料 |
| **超级管理后台** | 全平台数据概览、用户/线索/会话管理 |

---

## 系统架构

![系统架构](img/architecture.png)

## 💻 技术栈

| 模块 | 技术选择 | 版本/说明 |
|------|--------|----------|
| **后端API** | FastAPI | >=0.100 (异步、自动文档) |
| **ORM** | SQLAlchemy | >=2.0 (异步支持) |
| **数据库** | SQLite/PostgreSQL | 开发SQLite，生产Postgres |
| **AI工作流** | LangGraph | >=0.1.x (状态机、编排) |
| **LLM调用** | LangChain | >=0.1.x (模型适配) |
| **前端框架** | Vue 3 + TypeScript | ^3.5 |
| **UI组件** | Naive UI | ^2.44 |
| **前端状态** | Pinia + Vue Router | ^4 / ^5 |
| **文档处理** | python-docx | >=0.8.11 |
| **测试框架** | pytest | >=7.0 |
| **CI/CD** | GitHub Actions | 自动化集成测试 |

---

## 🚀 快速启动

### 前置条件
```
Python 3.10+  |  Node 18+  |  Git
```

### 环境搭建

**1. 克隆仓库**
```bash
git clone https://github.com/labors-assistant/labors_assistant.git
cd labors_assistant
```

**2. 后端启动**
```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements-backend.txt
cp .env.example .env          # 编辑.env，填入赛方API密钥
python scripts/init_db.py

# 启动FastAPI (http://localhost:8000)
uvicorn backend.main:app --reload
# API文档: http://localhost:8000/docs
```

**3. 前端启动**
```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

**4. 验证系统**
```bash
curl http://localhost:8000/api/health
# 浏览 http://localhost:5173
```

### 演示账号（由 init_db.py 自动创建）
| 角色 | 用户名 | 密码 | 用途 |
|------|--------|------|------|
| 劳动者 | `worker_demo` | `demo123456` | 体验咨询→分诊→发布线索→补充材料 |
| 律师 | `lawyer01` ~ `lawyer10` | `demo123456` | 体验律师工作台：系统推荐→接单→一键补材料 |
| 管理员 | `admin` | `admin123456` | 体验平台管理后台：数据概览/用户/线索/会话 |

### 运行测试
```bash
.venv/bin/python scripts/test_api.py   # 后端+Agent 全链路冒烟测试
cd frontend && npm run lint            # 前端 lint
cd frontend && npm run build           # 前端类型检查 + 构建
```

---

## 📁 项目结构

```
labors_assistant/
├── README.md
├── LICENSE
├── requirements-backend.txt
├── .env.example
│
├── backend/                 # FastAPI业务服务
│   ├── main.py
│   ├── api/routes.py, auth_routes.py, triage_routes.py, lawyer_routes.py, schema.py
│   ├── services/chat.py, document.py, agent_service.py, auth.py, triage.py, regions.py
│   ├── db/models.py, database.py
│   └── config.py
│
├── agent/                   # LangGraph AI工作流
│   ├── workflow.py
│   ├── state.py
│   ├── agent_node.py
│   ├── prompts.py
│   └── tools/doc_generator.py, legal_search.py
│
├── frontend/                # Vue3 前端 (Vite + Naive UI + Pinia)
│   ├── src/pages/HomePage.vue, ChatPage.vue, ResultPage.vue
│   ├── src/pages/LoginPage.vue, RegisterPage.vue
│   ├── src/pages/lawyer/LeadsPage.vue, LeadDetailPage.vue
│   ├── src/layouts/MainLayout.vue, LawyerLayout.vue
│   ├── src/services/*.ts, src/stores/*.ts
│   └── package.json
│
├── scripts/                 # 初始化与测试脚本
│   ├── init_db.py           # 建表 + 迁移 + 地区模板 + 演示账号
│   └── test_api.py          # 全链路冒烟测试（含新功能）
│
└── generated_docs/          # 生成的 .docx 文书
```
