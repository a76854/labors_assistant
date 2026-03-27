from typing import Annotated, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Agent 执行过程中的状态容器"""
    # 对话历史消息，使用 add_messages 作为 reducer 以支持增量更新
    messages: Annotated[list, add_messages]
    
    # 从对话中收集的案情要素
    extracted_info: dict


class LawsuitElementsSchema(BaseModel):
    """诉讼要素数据模型"""
    
    plaintiff: str = Field(
        ...,
        description="原告信息（名称、身份证号、联系方式等）"
    )
    
    defendant: str = Field(
        ...,
        description="被告信息（名称、身份证号、联系方式等）"
    )
    
    claim: str = Field(
        ...,
        description="诉讼请求（原告要求被告做什么或赔偿什么）"
    )
    
    amount: str = Field(
        ...,
        description="诉讼金额或其他具体数值（如赔偿金、欠款额等）"
    )

    cause_of_action: str = Field(
        ...,
        description="案由（如：民间借贷纠纷、劳动争议）"
    )

    facts_and_reasons: str = Field(
        ...,
        description="事实与理由（详细叙述案件经过、证据情况与法律依据）"
    )

    court_name: str = Field(
        ...,
        description="管辖法院名称（如：深圳市南山区人民法院）"
    )
