from asyncio import CancelledError
from typing import Any, Literal

from pydantic import BaseModel, Field


TaskStatus = Literal["pending", "running", "completed"]


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str | None = None
    provider: str | None = None
    query: str | None = None
    score: float = 0.0


class ResearchNote(BaseModel):
    title: str
    content: str
    category: Literal["fact", "source", "verification", "impact"]
    source_url: str | None = None
    source_title: str | None = None


class ResearchTaskTrace(BaseModel):
    rewritten_queries: list[str] = Field(default_factory=list)
    provider: str | None = None
    fallback_provider: str | None = None
    used_fallback: bool = False
    result_count: int = 0
    query_cache_hit: bool = False
    search_cache_hit: bool = False
    note_cache_hit: bool = False


class ResearchTask(BaseModel):
    id: str
    title: str
    status: TaskStatus = "pending"
    summary: str | None = None
    sources: list[SearchResult] = Field(default_factory=list)
    notes: list[ResearchNote] = Field(default_factory=list)
    trace: ResearchTaskTrace = Field(default_factory=ResearchTaskTrace)


ResearchRunStatus = Literal["running", "completed", "failed", "cancelled"]


class ResearchState(BaseModel):
    id: str
    topic: str
    tasks: list[ResearchTask]
    completed_steps: int = 0
    total_steps: int = 0
    status: ResearchRunStatus = "running"
    report: str = ""
    error: str | None = None


class ResearchEvent(BaseModel):
    type: str
    data: dict[str, Any]


class ResearchHistoryItem(BaseModel):
    id: str
    topic: str
    status: ResearchRunStatus
    created_at: str
    updated_at: str
    report_ready: bool = False
    error: str | None = None
    reused: bool = False
