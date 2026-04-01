from src.models import SearchResult


class SourceDeduplicator:
    def deduplicate(self, results: list[SearchResult]) -> list[SearchResult]:
        seen_urls: set[str] = set()
        unique_results: list[SearchResult] = []

        for result in results:
            normalized_url = result.url.strip().rstrip("/")
            if not normalized_url or normalized_url in seen_urls:
                continue
            seen_urls.add(normalized_url)
            unique_results.append(result)

        return unique_results
