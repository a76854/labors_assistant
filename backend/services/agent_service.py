"""
Agent 服务 - 与 LangGraph 法律 Agent 交互
调用 agent 处理用户查询，生成法律建议和诉状内容
"""

import re
from agent.workflow import run_agent_for_backend
from typing import Optional, Dict, Any, List
from agent.tools.doc_generator import generate_legal_doc_tool


class AgentService:
    """法律 Agent 服务"""
    
    @staticmethod
    def process_user_message(user_input: str, session_id: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        处理用户查询，调用 Agent 生成回复
        
        这是后端与 agent 的主要交互点。
        用户在对话中的输入会通过这个方法发送到 agent，
        agent 会基于工具调用（法律查询、文档生成等）返回回复。
        
        Args:
            user_input: 用户输入的文本（如"我被拖欠工资3个月，怎么办？"）
            session_id: 会话 ID（用于保持对话上下文，后端数据库的 session.id）
            max_iterations: 最大迭代次数，限制 agent 推理步骤数（此参数当前未使用，需要在工作流中支持）
        
        Returns:
            包含以下字段的字典：
            {
                "final_answer": "Agent 给出的最终答案和建议",
                "tools_used": ["tool1", "tool2"],  # 使用过的工具
                "generated_document": "document_url 如果有生成诉状",
                "extracted_elements": {...},  # 提取的案件要素
            }
        
        Raises:
            Exception: Agent 执行失败时抛出
        """
        try:
            # 调用 agent workflow
            result = run_agent_for_backend(user_input=user_input, thread_id=session_id)
            
            return {
                "final_answer": result.get("final_answer", ""),
                "tools_used": result.get("tools_used", []),
                "reasoning_steps": [f"调用工具: {tool}" for tool in result.get("tools_used", [])],
                "generated_document": result.get("generated_document"),
                "extracted_elements": result.get("extracted_elements", {}),
            }
        
        except Exception as e:
            # 如果 agent 执行出错，返回错误信息
            return {
                "final_answer": f"Agent 处理出错: {str(e)}",
                "tools_used": [],
                "reasoning_steps": [],
                "generated_document": None,
                "extracted_elements": {},
            }
    
    @staticmethod
    def generate_document(
        session_id: str,
        case_type: str,
        template_id: str,
        messages: Optional[List[Any]] = None,
    ) -> Optional[str]:
        """
        调用 agent 生成诉状文档
        
        Args:
            session_id: 会话 ID
            case_type: 案件类型（如 "wage_arrears", "labor_contract", "work_injury"）
            template_id: 模板 ID
        
        Returns:
            生成的文档 URL，失败返回 None
        """
        history_text = ""
        if messages:
            lines: List[str] = []
            for msg in messages[-40:]:
                role = getattr(msg, "role", "unknown")
                content = str(getattr(msg, "content", "") or "").strip()
                if not content:
                    continue
                lines.append(f"{role}: {content}")
            history_text = "\n".join(lines)

        prompt = (
            f"请基于当前会话信息，生成一份{case_type}的诉状，使用模板 {template_id}。\n"
            "你必须调用 generate_legal_doc_tool 输出可下载的 .docx 文件。\n"
            "若个别字段缺失，请基于上下文做最保守补全（例如填'待补充'），但仍需先生成文书。"
        )

        if history_text:
            prompt += f"\n\n【会话历史】\n{history_text}"
        
        result = AgentService.process_user_message(
            user_input=prompt,
            session_id=session_id,
            max_iterations=15
        )

        generated_document = result.get("generated_document")
        if generated_document:
            return generated_document

        # 兜底：部分模型会把下载链接写在 final_answer 中，而不是 ToolMessage。
        final_answer = result.get("final_answer", "")
        if isinstance(final_answer, str) and ".docx" in final_answer:
            return final_answer

        # 返回文本兜底，便于上层记录失败原因。
        if isinstance(final_answer, str) and final_answer.strip():
            fallback = AgentService._fallback_generate_document(history_text, case_type)
            return fallback or final_answer

        fallback = AgentService._fallback_generate_document(history_text, case_type)
        if fallback:
            return fallback

        return None

    @staticmethod
    def _pick_by_patterns(text: str, patterns: List[str], default: str) -> str:
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = (match.group(1) or "").strip()
                if value:
                    return value
        return default

    @staticmethod
    def _fallback_generate_document(history_text: str, case_type: str) -> Optional[str]:
        """兜底策略：直接调用文书工具，避免前端长期处于 failed 状态。"""
        try:
            plaintiff = AgentService._pick_by_patterns(
                history_text,
                [r"原告[：:]\s*([^；;。\n]+)", r"我叫\s*([^，,。；;\n]+)"],
                "原告（待补充）",
            )
            defendant = AgentService._pick_by_patterns(
                history_text,
                [r"被告[：:]\s*([^；;。\n]+)", r"公司[：:]\s*([^；;。\n]+)"],
                "被告（待补充）",
            )
            amount = AgentService._pick_by_patterns(
                history_text,
                [r"([0-9０-９,，.．]+\s*元)", r"金额[：:]\s*([^；;。\n]+)"],
                "待补充",
            )

            cause_map = {
                "wage_arrears": "拖欠工资纠纷",
                "labor_contract": "劳动合同纠纷",
                "work_injury": "工伤赔偿纠纷",
            }
            cause_of_action = cause_map.get(case_type, "劳动争议")

            return generate_legal_doc_tool.invoke(
                {
                    "plaintiff": plaintiff,
                    "defendant": defendant,
                    "claim": "请求依法支持原告诉讼请求并判令被告承担相应责任。",
                    "amount": amount,
                    "cause_of_action": cause_of_action,
                    "facts_and_reasons": "根据会话记录整理，部分信息待补充。",
                    "court_name": "有管辖权的人民法院",
                }
            )
        except Exception:
            return None
