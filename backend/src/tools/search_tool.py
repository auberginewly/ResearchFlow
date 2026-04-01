from src.models import SearchResult
from src.services.search import SearchService


class SearchTool:
    def __init__(self) -> None:
        self.service = SearchService()

    def get_provider_name(self) -> str:
        return self.service.get_provider_name()

    async def rewrite_queries(self, task_title: str) -> list[str]:
        return await self.service.rewrite_queries(task_title)

    async def search_queries(self, queries: list[str]) -> tuple[list[SearchResult], dict]:
        return await self.service.search_queries(queries)
