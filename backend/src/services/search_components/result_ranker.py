from src.models import SearchResult


class ResultRanker:
    def rank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        query_terms = {term.lower() for term in query.split() if term.strip()}
        ranked_results = []

        for result in results:
            haystack = f"{result.title} {result.snippet or ''}".lower()
            score = sum(1 for term in query_terms if term in haystack)
            ranked_results.append(result.model_copy(update={"score": float(score)}))

        ranked_results.sort(key=lambda item: item.score, reverse=True)
        return ranked_results
