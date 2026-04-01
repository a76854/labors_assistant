import os
import re
from typing import Any, Dict, List

import requests
from langchain_core.tools import tool


APP_ID = "QthdBErlyaYvyXul"
APP_SECRET = "EC5D455E6BD348CE8E18BE05926D2EBE"
BASE_HEADERS: Dict[str, str] = {
    "appid": APP_ID,
    "secret": APP_SECRET,
    "Content-Type": "application/json",
}


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = str(value)

    # 清理检索结果中的 HTML 高亮标签（如 <em>...</em>）并规范空白字符。
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_items(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []

    candidate_keys: List[str] = [
        "body",
        "records",
        "list",
        "items",
        "rows",
        "data",
        "result",
        "content",
    ]

    for key in candidate_keys:
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = _extract_items(value)
            if nested:
                return nested
    return []


def _pick_field(item: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        value = item.get(key)
        text = _safe_text(value)
        if text:
            return text
    return ""


@tool
def search_public_laws_tool(query: str) -> str:
    """当用户询问国家法律条文、通用法规规定时，必须调用此工具。输入参数 query 为具体的法律问题描述。"""
    try:
        payload: Dict[str, Any] = {
            "pageNo": 1,
            "pageSize": 3,
            "sortField": "correlation",
            "sortOrder": "desc",
            "condition": {
                "keywords": [query],
                "fieldName": "semantic",
            },
        }

        response = requests.post(
            "https://openapi.delilegal.com/api/qa/v3/search/queryListLaw",
            headers=BASE_HEADERS,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        body: Dict[str, Any] = response.json()

        items: List[Dict[str, Any]] = _extract_items(body)
        if not items:
            return "【公域法规检索】未检索到相关法律条款，请尝试更具体的关键词。"

        lines: List[str] = ["【公域法规检索结果】"]
        for index, item in enumerate(items[:3], start=1):
            title = _pick_field(item, ["title", "lawName", "name", "docTitle"])
            article = _pick_field(item, ["article", "articleName", "chapter", "section"])
            content = _pick_field(item, ["content", "summary", "snippet", "abstract"])
            source = _pick_field(item, ["source", "publishOrg", "org", "from"])

            if not article:
                highlights = item.get("highlights")
                if isinstance(highlights, list) and highlights:
                    first_hl = highlights[0] if isinstance(highlights[0], dict) else {}
                    article = _safe_text(first_hl.get("name"))
                    if not content:
                        content = _safe_text(first_hl.get("text"))

            lines.append(f"{index}. 标题：{title or '（未提供）'}")
            if article:
                lines.append(f"   条款：{article}")
            if source:
                lines.append(f"   来源：{source}")
            if content:
                lines.append(f"   内容：{content}")

        return "\n".join(lines)
    except requests.Timeout:
        return "【公域法规检索】请求超时，请稍后重试。"
    except requests.RequestException as exc:
        return f"【公域法规检索】网络请求失败：{_safe_text(exc) or '未知网络错误'}"
    except ValueError:
        return "【公域法规检索】响应解析失败，返回内容不是合法 JSON。"
    except Exception as exc:
        return f"【公域法规检索】处理异常：{_safe_text(exc) or '未知错误'}"


@tool
def search_public_cases_tool(query: str) -> str:
    """当需要为用户的纠纷寻找历史上真实的法院判决案例参考、胜诉率时，调用此工具。输入参数 query 为案情摘要。"""
    try:
        payload: Dict[str, Any] = {
            "pageNo": 1,
            "pageSize": 3,
            "sortField": "correlation",
            "sortOrder": "desc",
            "condition": {
                "keywordArr": [query],
            },
        }

        response = requests.post(
            "https://openapi.delilegal.com/api/qa/v3/search/queryListCase",
            headers=BASE_HEADERS,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        body: Dict[str, Any] = response.json()

        items: List[Dict[str, Any]] = _extract_items(body)
        if not items:
            return "【公域判例检索】未检索到相关案例，请更换案情关键词后重试。"

        lines: List[str] = ["【公域历史判例检索结果】"]
        for index, item in enumerate(items[:3], start=1):
            case_no = _pick_field(item, ["caseNo", "caseNumber", "案号", "id"])
            title = _pick_field(item, ["title", "caseTitle", "name"])
            gist = _pick_field(item, ["gist", "summary", "content", "judgmentPoints", "snippet"])
            court = _pick_field(item, ["court", "courtName", "org"])

            lines.append(f"{index}. 案号：{case_no or '（未提供）'}")
            if title:
                lines.append(f"   标题：{title}")
            if court:
                lines.append(f"   法院：{court}")
            if gist:
                lines.append(f"   裁判要点：{gist}")

        return "\n".join(lines)
    except requests.Timeout:
        return "【公域判例检索】请求超时，请稍后重试。"
    except requests.RequestException as exc:
        return f"【公域判例检索】网络请求失败：{_safe_text(exc) or '未知网络错误'}"
    except ValueError:
        return "【公域判例检索】响应解析失败，返回内容不是合法 JSON。"
    except Exception as exc:
        return f"【公域判例检索】处理异常：{_safe_text(exc) or '未知错误'}"


@tool
def search_private_knowledge_tool(query: str) -> str:
    """【极度重要】当用户询问特定的地方调解政策、企业内部规章，或者要求核对已上传的私有合同、卷宗、证据材料时，绝对不能用公域工具，必须调用此工具检索腾讯元器私有知识库。输入参数 query 为检索问题。"""
    try:
        yuanqi_api_url = _safe_text(os.environ.get("YUANQI_API_URL"))
        yuanqi_api_key = _safe_text(os.environ.get("YUANQI_API_KEY"))

        if not yuanqi_api_url:
            return "【专属知识库检索结果】未配置 YUANQI_API_URL，请先在环境变量中设置后重试。"
        if not yuanqi_api_key:
            return "【专属知识库检索结果】未配置 YUANQI_API_KEY，请先在环境变量中设置后重试。"

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {yuanqi_api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "query": query,
            "top_k": 3,
            "filters": {},
        }

        response = requests.post(
            yuanqi_api_url,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        body: Dict[str, Any] = response.json()

        items: List[Dict[str, Any]] = _extract_items(body)
        if not items:
            return f"【专属知识库检索结果】{body}"

        lines: List[str] = ["【专属知识库检索结果】"]
        for index, item in enumerate(items[:3], start=1):
            title = _pick_field(item, ["title", "name", "docName"])
            content = _pick_field(item, ["content", "summary", "snippet", "text"])
            source = _pick_field(item, ["source", "fileName", "path", "docId"])

            lines.append(f"{index}. 标题：{title or '（未提供）'}")
            if source:
                lines.append(f"   来源：{source}")
            if content:
                lines.append(f"   内容：{content}")

        return "\n".join(lines)
    except requests.Timeout:
        return "【专属知识库检索结果】请求超时，请稍后重试。"
    except requests.RequestException as exc:
        return f"【专属知识库检索结果】网络请求失败：{_safe_text(exc) or '未知网络错误'}"
    except ValueError:
        return "【专属知识库检索结果】响应解析失败，返回内容不是合法 JSON。"
    except Exception as exc:
        return f"【专属知识库检索结果】处理异常：{_safe_text(exc) or '未知错误'}"


@tool
def search_law_tool(query: str) -> str:
    """兼容旧工作流的法律检索入口，当前默认复用公域法规检索工具。"""
    return search_public_laws_tool.invoke({"query": query})
