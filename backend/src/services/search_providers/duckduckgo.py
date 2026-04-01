import httpx

from src.config import settings
from src.models import SearchResult


class DuckDuckGoSearchProvider:
    name = "duckduckgo"

    async def search(self, query: str) -> list[SearchResult]:
        params = {
            "q": query,
            "format": "json",
            "no_redirect": "1",
            "no_html": "1",
            "skip_disambig": "1",
        }

        async with httpx.AsyncClient(timeout=settings.search_timeout_seconds) as client:
            response = await client.get("https://api.duckduckgo.com/", params=params)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(
                    f"DuckDuckGo 搜索失败: {response.status_code} {response.text}"
                ) from exc

        data = response.json()
        related_topics = data.get("RelatedTopics", [])
        results: list[SearchResult] = []

        for item in related_topics:
            if not isinstance(item, dict):
                continue

            nested_topics = item.get("Topics")
            if isinstance(nested_topics, list):
                for nested in nested_topics:
                    parsed = self._parse_topic(nested)
                    if parsed:
                        results.append(parsed)
                continue

            parsed = self._parse_topic(item)
            if parsed:
                results.append(parsed)

        return results[: settings.search_top_k]

    def _parse_topic(self, item: dict) -> SearchResult | None:
        text = item.get("Text")
        url = item.get("FirstURL")
        if not text or not url:
            return None

        if " - " in text:
            title, snippet = text.split(" - ", 1)
        else:
            title, snippet = text, text

        return SearchResult(
            title=str(title).strip(),
            url=str(url).strip(),
            snippet=str(snippet).strip() or None,
            provider=self.name,
        )
