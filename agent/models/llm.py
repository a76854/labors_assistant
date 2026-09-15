import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agent.tools import tools_list

load_dotenv()

# LLM 模型初始化与工具绑定。
llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
llm_base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL")
llm_model = os.getenv("LLM_MODEL", "qwen-plus")

llm_init_kwargs = {
    "model": llm_model,
    "temperature": 0.1,
    "api_key": llm_api_key,
}
if llm_base_url:
    llm_init_kwargs["base_url"] = llm_base_url

llm = ChatOpenAI(**llm_init_kwargs)
llm_with_tools = llm.bind_tools(tools_list)
