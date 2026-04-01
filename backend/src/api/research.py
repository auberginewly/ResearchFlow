import json

from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse

from src.agent import ResearchAgent
from src.core.state import ResearchStateStore
from src.models import ResearchRequest

router = APIRouter(prefix="/research", tags=["research"])
agent = ResearchAgent()
state_store = ResearchStateStore()


def to_sse(event_type: str, payload: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def stream_research(request: ResearchRequest) -> StreamingResponse:
    async def event_generator():
        yield to_sse("connected", {"message": "研究任务已创建"})
        try:
            async for event in agent.run(request.topic):
                yield to_sse(event.type, event.data)
            yield to_sse("done", {"message": "研究流程结束"})
        except Exception as exc:
            error_message = str(exc)
            if "429" in error_message:
                error_message = (
                    "模型服务当前繁忙，已自动重试但仍失败，请稍后再试。"
                )
            yield to_sse("error", {"message": error_message})
            yield to_sse("done", {"message": "研究流程结束"})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/history")
def list_research_history():
    return state_store.list_history()


@router.get("/history/{research_id}")
def get_research_history_item(research_id: str):
    return state_store.load(research_id)


@router.get("/history/{research_id}/export")
def export_research_markdown(research_id: str):
    state = state_store.load(research_id)
    export_path = state_store.export_markdown(state)
    return FileResponse(export_path, media_type="text/markdown", filename=f"{research_id}.md")


@router.get("/history/{research_id}/export/pdf")
def export_research_pdf(research_id: str):
    state = state_store.load(research_id)
    export_path = state_store.export_pdf(state)
    return FileResponse(export_path, media_type="application/pdf", filename=f"{research_id}.pdf")
