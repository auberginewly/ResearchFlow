from src.core.registry import ToolRegistry
from src.models import ResearchTask
from src.services.summarizer import SummarizerService
from src.tools.note_tool import NoteTool
from src.tools.search_tool import SearchTool
from src.tools.source_tool import SourceTool


class ExecutorService:
    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self.registry.register("search", SearchTool())
        self.registry.register("note", NoteTool())
        self.registry.register("source", SourceTool())
        self.summarizer_service = SummarizerService()

    def get_search_provider_name(self) -> str:
        search_tool = self.registry.get("search")
        return search_tool.get_provider_name()

    async def rewrite_queries(self, task: ResearchTask) -> tuple[list[str], bool]:
        search_tool = self.registry.get("search")
        return await search_tool.rewrite_queries(task.title)

    async def search_queries(self, queries: list[str]):
        search_tool = self.registry.get("search")
        return await search_tool.search_queries(queries)

    def build_notes(self, task: ResearchTask):
        note_tool = self.registry.get("note")
        return note_tool.build_notes(task.sources)

    def summarize_sources(self, task: ResearchTask):
        source_tool = self.registry.get("source")
        return source_tool.summarize_sources(task.sources)

    async def summarize_task(self, task: ResearchTask) -> str:
        source_summary = self.summarize_sources(task)
        return await self.summarizer_service.summarize(
            task.title,
            task.notes,
            task.sources,
            source_summary,
        )
