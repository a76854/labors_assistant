"""
后端快速启动和测试指南
"""

# ============================================================================
# 快速启动
# ============================================================================

# 1. 安装依赖
# python -m venv venv
# source venv/bin/activate  # Linux/Mac
# pip install -r requirements-backend.txt

# 2. 配置环境变量
# cp .env.example .env

# 3. 初始化数据库
# python scripts/init_db.py

# 4. 启动服务
# uvicorn backend.main:app --reload

# Server will be available at http://localhost:8000
# API Documentation: http://localhost:8000/docs

# ============================================================================
# 测试API
# ============================================================================

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_create_session():
    """测试创建会话"""
    print("Testing: Create Session")
    response = requests.post(
        f"{BASE_URL}/sessions",
        json={
            "case_type": "wage_arrears",
            "description": "被拖欠4个月工资"
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data.get("id")


def test_send_message(session_id):
    """测试发送消息"""
    print(f"\nTesting: Send Message")
    response = requests.post(
        f"{BASE_URL}/sessions/{session_id}/messages",
        json={"content": "我在XXX公司工作了8个月，被拖欠了4个月工资"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_get_chat_history(session_id):
    """测试获取对话历史"""
    print(f"\nTesting: Get Chat History")
    response = requests.get(f"{BASE_URL}/sessions/{session_id}/messages")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_generate_document(session_id):
    """测试生成文档"""
    print(f"\nTesting: Generate Document")
    response = requests.post(
        f"{BASE_URL}/sessions/{session_id}/generate-document",
        json={
            "template_id": "wage_arrears",
            "format": "docx"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_health_check():
    """测试健康检查"""
    print("Testing: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    # 运行测试
    print("=" * 60)
    print("Backend API Tests")
    print("=" * 60)
    
    # 1. 健康检查
    test_health_check()
    
    # 2. 创建会话
    session_id = test_create_session()
    if session_id:
        # 3. 发送消息
        test_send_message(session_id)
        
        # 4. 获取对话历史
        test_get_chat_history(session_id)
        
        # 5. 生成文档
        test_generate_document(session_id)
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
