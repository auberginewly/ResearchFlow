from src.models import SearchResult


class SourceTool:
    def summarize_sources(self, sources: list[SearchResult]) -> dict:
        providers = sorted({source.provider for source in sources if source.provider})
        return {
            "count": len(sources),
            "providers": providers,
            "top_titles": [source.title for source in sources[:3]],
        }
