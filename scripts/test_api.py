"""
后端 + Agent 集成冒烟测试（已适配用户认证 / 分诊 / 律师后台）
使用方法: python scripts/test_api.py
前置: 后端(8000) + Agent(8001) 已启动, 数据库已初始化
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
AGENT_URL = "http://localhost:8001"


def _print(label, response):
    print(f"\n>>> {label} [{response.status_code}]")
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2)[:1200])
    except Exception:
        print(response.text[:500])
    return response


def login(username, password):
    resp = _print("登录", requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password},
    ))
    data = resp.json()
    return data["access_token"], data["user"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def sse_chat(thread_id, user_input, timeout=180):
    """调用 Agent SSE 流式对话，返回拼接文本与工具列表。"""
    import json as _json
    resp = requests.post(
        f"{AGENT_URL}/chat",
        json={"user_input": user_input, "thread_id": thread_id},
        stream=True,
        timeout=timeout,
    )
    tokens, tools, done = [], [], False
    for raw_line in resp.iter_lines(decode_unicode=True):
        line = (raw_line or "").strip()
        if not line.startswith("data:"):
            continue
        try:
            payload = _json.loads(line[5:].strip())
        except Exception:
            continue
        t = payload.get("type")
        if t == "token":
            tokens.append(payload.get("content", ""))
        elif t == "tool_start":
            tools.append(payload.get("tool_name"))
        elif t == "done":
            done = True
    print(f"\n>>> SSE 对话 done={done} tools={tools}")
    print("    回复预览:", "".join(tokens)[:200])
    return "".join(tokens), tools, done


def main():
    print("=" * 60)
    print("Backend + Agent Integration Tests")
    print("=" * 60)

    # 1. 健康检查
    _print("健康检查", requests.get(f"{BASE_URL}/health"))

    # 2. 登录（演示账号由 init_db.py 创建）
    worker_token, worker = login("worker_demo", "demo123456")
    lawyer_token, lawyer = login("lawyer_demo", "demo123456")
    worker_headers = auth_header(worker_token)
    lawyer_headers = auth_header(lawyer_token)

    # 3. 地区列表
    _print("地区列表", requests.get(f"{BASE_URL}/regions"))

    # 4. 创建会话（带地区）
    resp = _print("创建会话", requests.post(
        f"{BASE_URL}/sessions",
        headers=worker_headers,
        json={"case_type": "wage_arrears", "region": "shanghai", "description": "被拖欠3个月工资"},
    ))
    session_id = resp.json()["id"]

    # 5. Agent SSE 流式对话
    reply, _, _ = sse_chat(session_id, "我叫张伟，在上海XX科技有限公司工作，公司拖欠我3个月工资共45000元，我有劳动合同和工资条，还有银行流水和考勤记录，请问怎么办？")

    # 6. 同步消息回写数据库
    _print("同步消息", requests.post(
        f"{BASE_URL}/sessions/{session_id}/messages/sync",
        headers=worker_headers,
        json={"messages": [
            {"role": "user", "content": "我叫张伟，公司拖欠我3个月工资共45000元，有劳动合同和工资条。"},
            {"role": "assistant", "content": reply[:500]},
        ]},
    ))

    # 7. 案件分诊（自动发布线索）
    resp = _print("案件分诊", requests.post(
        f"{BASE_URL}/sessions/{session_id}/triage",
        headers=worker_headers,
        json={},
    ))
    triage = resp.json()
    print("    证据完整度:", triage["evidence_score"], "风险:", triage["risk_score"], "复杂度:", triage["complexity"])
    print("    推荐律师:", [l["name"] for l in triage["recommended_lawyers"]])

    # 8. 劳动者查看线索状态
    _print("劳动者线索状态", requests.get(
        f"{BASE_URL}/sessions/{session_id}/lead",
        headers=worker_headers,
    ))

    # 9. 律师查看线索列表
    resp = _print("律师线索列表", requests.get(
        f"{BASE_URL}/lawyer/leads",
        headers=lawyer_headers,
    ))
    leads = resp.json().get("leads", [])
    if not leads:
        print("\n⚠️  无可用线索，跳过律师操作")
        return
    lead_id = leads[0]["id"]

    # 10. 线索详情
    _print("线索详情", requests.get(
        f"{BASE_URL}/lawyer/leads/{lead_id}",
        headers=lawyer_headers,
    ))

    # 11. 律师接单
    _print("律师接单", requests.post(
        f"{BASE_URL}/lawyer/leads/{lead_id}/claim",
        headers=lawyer_headers,
        json={},
    ))

    # 12. 一键发起补充材料请求
    _print("发起补充材料请求", requests.post(
        f"{BASE_URL}/lawyer/leads/{lead_id}/request-materials",
        headers=lawyer_headers,
        json={
            "items": [
                {"name": "劳动合同原件", "description": "完整劳动合同扫描件"},
                {"name": "银行流水", "description": "近6个月工资银行流水"},
            ],
            "note": "请尽快补充，方便立案",
        },
    ))

    # 13. 劳动者端查看补充材料提醒
    _print("劳动者补充材料提醒", requests.get(
        f"{BASE_URL}/sessions/{session_id}/lead",
        headers=worker_headers,
    ))

    # 14. 权限校验：普通用户访问律师接口应 403
    _print("权限校验(普通用户访问律师接口)", requests.get(
        f"{BASE_URL}/lawyer/leads",
        headers=worker_headers,
    ))

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
