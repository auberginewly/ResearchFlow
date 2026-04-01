import httpx

from src.config import settings
from src.models import SearchResult


class TavilySearchProvider:
    name = "tavily"

    async def search(self, query: str) -> list[SearchResult]:
        if not settings.search_api_key:
            raise RuntimeError("缺少 SEARCH_API_KEY，无法使用 Tavily 搜索。")

        payload = {
            "api_key": settings.search_api_key,
            "query": query,
            "max_results": settings.search_top_k,
            "search_depth": "basic",
            "topic": "general",
        }

        async with httpx.AsyncClient(timeout=settings.search_timeout_seconds) as client:
            response = await client.post(
                f"{settings.search_base_url.rstrip('/')}/search",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(
                    f"Tavily 搜索失败: {response.status_code} {response.text}"
                ) from exc

        data = response.json()
        results = data.get("results", [])

        search_results = []
        for item in results:
            if not isinstance(item, dict):
                continue
            url = item.get("url")
            title = item.get("title")
            if not url or not title:
                continue
            search_results.append(
                SearchResult(
                    title=str(title),
                    url=str(url),
                    snippet=str(item.get("content") or item.get("snippet") or "").strip() or None,
                    provider=self.name,
                )
            )
        return search_results
