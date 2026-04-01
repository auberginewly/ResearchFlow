import json

from src.core.cache import FileCache
from src.config import settings
from src.models import SearchResult
from src.services.search_components.query_rewriter import QueryRewriter
from src.services.search_components.result_ranker import ResultRanker
from src.services.search_components.source_deduplicator import SourceDeduplicator
from src.services.search_providers import DuckDuckGoSearchProvider, TavilySearchProvider


class SearchService:
    def __init__(self) -> None:
        self.query_rewriter = QueryRewriter()
        self.deduplicator = SourceDeduplicator()
        self.ranker = ResultRanker()
        self.search_cache = FileCache("search")
        self.providers = {
            "tavily": TavilySearchProvider(),
            "duckduckgo": DuckDuckGoSearchProvider(),
        }

    def get_provider_name(self) -> str:
        return settings.search_provider.lower()

    def get_provider(self):
        provider_name = settings.search_provider.lower()
        provider = self.providers.get(provider_name)
        if provider is None:
            raise RuntimeError(f"不支持的搜索提供商: {settings.search_provider}")
        return provider

    async def rewrite_queries(self, query: str) -> tuple[list[str], bool]:
        rewritten_queries, cache_hit = await self.query_rewriter.rewrite(query)
        return rewritten_queries or [query], cache_hit

    async def search_queries(self, queries: list[str]) -> tuple[list[SearchResult], dict]:
        cache_key = json.dumps(
            {"provider": self.get_provider_name(), "queries": queries},
            ensure_ascii=False,
            sort_keys=True,
        )
        cached = self.search_cache.get(cache_key)
        if isinstance(cached, list):
            results = [SearchResult.model_validate(item) for item in cached]
            return results, {
                "provider": self.get_provider_name(),
                "active_provider": self.get_provider_name(),
                "fallback_provider": settings.search_fallback_provider.lower(),
                "used_fallback": False,
                "result_count": len(results),
                "cache_hit": True,
            }

        provider = self.get_provider()
        fallback_provider = self.providers.get(settings.search_fallback_provider.lower())
        raw_results: list[SearchResult] = []
        active_provider_name = self.get_provider_name()
        used_fallback = False

        try:
            for rewritten_query in queries:
                raw_results.extend(await provider.search(rewritten_query))
        except RuntimeError:
            if fallback_provider is None or fallback_provider.name == active_provider_name:
                raise
            used_fallback = True
            active_provider_name = fallback_provider.name
            for rewritten_query in queries:
                raw_results.extend(await fallback_provider.search(rewritten_query))

        if not raw_results:
            for candidate_provider_name in [active_provider_name, settings.search_fallback_provider.lower()]:
                candidate_provider = self.providers.get(candidate_provider_name)
                if candidate_provider is None:
                    continue
                fallback_results = await candidate_provider.search(queries[0])
                if fallback_results:
                    raw_results = fallback_results
                    active_provider_name = candidate_provider.name
                    used_fallback = candidate_provider.name != self.get_provider_name()
                    break

        unique_results = self.deduplicator.deduplicate(raw_results)
        ranked_results = self.ranker.rank(" ".join(queries), unique_results)
        trimmed_results = self._trim_results(ranked_results)
        self.search_cache.set(cache_key, [result.model_dump() for result in trimmed_results])
        return trimmed_results, {
            "provider": self.get_provider_name(),
            "active_provider": active_provider_name,
            "fallback_provider": settings.search_fallback_provider.lower(),
            "used_fallback": used_fallback,
            "result_count": len(trimmed_results),
            "cache_hit": False,
        }

    def _trim_results(self, results: list[SearchResult]) -> list[SearchResult]:
        trimmed_results = []
        for result in results[: settings.search_top_k]:
            snippet = (result.snippet or "").strip()
            if len(snippet) > settings.search_snippet_max_chars:
                snippet = f"{snippet[: settings.search_snippet_max_chars].rstrip()}..."

            trimmed_results.append(
                SearchResult(
                    title=result.title.strip(),
                    url=result.url.strip(),
                    snippet=snippet or None,
                    provider=result.provider,
                    query=result.query,
                    score=result.score,
                )
            )

        return trimmed_results
