# 后端开发指南

## 📁 项目结构

```
backend/
├── __init__.py
├── main.py                # FastAPI 应用入口
├── config.py              # 配置管理
├── api/
│   ├── __init__.py
│   ├── schema.py          # Pydantic 数据验证模型
│   └── routes.py          # API 路由定义
├── db/
│   ├── __init__.py
│   ├── database.py        # 数据库连接和会话管理
│   └── models.py          # SQLAlchemy ORM 模型
└── services/
    ├── __init__.py
    ├── chat.py            # 聊天服务（对话管理）
    └── document.py        # 文档服务（诉状生成）
```

## 🚀 快速启动

### 1. 安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

pip install -r requirements-backend.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的API密钥
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 启动服务

```bash
# 开发模式（自动重载）
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python 直接运行
python -m backend.main
```

### 5. 访问API文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🧪 测试API

### 使用脚本测试

```bash
python scripts/test_api.py
```

### 使用 curl 测试

```bash
# 1. 创建会话
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"case_type": "wage_arrears", "description": "被拖欠4个月工资"}'

# 2. 发送消息
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "我的情况是..."}'

# 3. 获取对话历史
curl -X GET http://localhost:8000/api/v1/sessions/{session_id}/messages

# 4. 生成文档
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/generate-document \
  -H "Content-Type: application/json" \
  -d '{"template_id": "wage_arrears", "format": "docx"}'

# 5. 健康检查
curl -X GET http://localhost:8000/api/v1/health
```

## 📊 数据模型关系

```
Session (会话)
├── Message (消息) - 1:N 关系
├── CaseElement (案件要素) - 1:1 关系
└── Document (文档) - 1:N 关系

Template (模板)
└── 独立表，被 Document 引用
```

## 🔧 开发流程

### 1. 添加新的API端点

修改 `backend/api/routes.py`：

```python
@router.post("/sessions/{session_id}/my-endpoint")
def my_endpoint(session_id: str, db: Session = Depends(get_db)):
    """我的新端点描述"""
    # 实现逻辑
    return {"result": "..."}
```

### 2. 添加新的数据模型

a) 在 `backend/db/models.py` 中添加 SQLAlchemy 模型
b) 在 `backend/api/schema.py` 中添加 Pydantic schema
c) 在 `backend/services/` 中添加相应的服务方法

### 3. 运行数据库迁移（如果修改了表结构）

```bash
# 重新初始化
python scripts/init_db.py --reset
```

## 📝 数据库查看

### SQLite（开发环境）

```bash
# 使用 sqlite3 CLI
sqlite3 labors_assistant.db

# 查看所有表
.tables

# 查看表结构
.schema sessions

# 查询数据
SELECT * FROM sessions;
```

## 🐛 调试技巧

### 启用 SQL 调试

在 `.env` 中设置：
```
DEBUG=True
LOG_LEVEL=DEBUG
```

这会在控制台打印所有 SQL 查询。

### 查看数据库日志

```python
# 在 backend/config.py 中已配置
# SQLAlchemy 会在 debug=True 时打印 SQL
echo=settings.debug  
```

## ✅ 测试覆盖率

运行自动化测试：
```bash
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest --cov=backend tests/
```

## 📦 部署

### Docker 部署

```bash
docker build -t labors-backend:latest .
docker run -p 8000:8000 labors-backend:latest
```

### 生产环境配置

在 `.env` 中配置：
```
DEBUG=False
DATABASE_URL=postgresql://user:password@db.example.com/labors_db
OPENAI_API_KEY=your_production_key
```

## 🔗 相关资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [项目 README](../README.md)

## 💡 常见问题

### Q: 如何重置数据库？
A: 运行 `python scripts/init_db.py --reset`

### Q: 如何修改数据库连接？
A: 编辑 `.env` 文件中的 `DATABASE_URL`

### Q: 如何添加新的依赖？
A: `pip install <package>` 然后 `pip freeze > requirements-backend.txt`

---

**Next Steps**: 现在你可以开始实现 Agent 工作流和文档生成服务了！
