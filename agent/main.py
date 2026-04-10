from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent.workflow import run_agent_stream


class ChatRequest(BaseModel):
    """前端聊天请求。"""

    user_input: str = Field(..., min_length=1, description="用户输入")
    thread_id: str = Field(..., min_length=1, description="会话ID，用于隔离上下文")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。"""
    yield


app = FastAPI(
    title="LLM-LAWS Agent Streaming API",
    version="1.0.0",
    description="LangGraph Agent SSE 流式接口",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    """健康检查。"""
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    """SSE 流式聊天接口。"""

    async def event_generator() -> AsyncGenerator[str, None]:
        async for chunk in run_agent_stream(req.user_input, req.thread_id):
            if chunk:
                yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agent.main:app", host="0.0.0.0", port=8001, reload=False)
