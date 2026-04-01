from src.core.cache import FileCache
from src.config import settings
from src.prompts import QUERY_REWRITE_PROMPT
from src.services.search_components.query_templates import QueryTemplates
from src.services.llm_client import LLMClient


class QueryRewriter:
    def __init__(self) -> None:
        self.llm_client = LLMClient()
        self.templates = QueryTemplates()
        self.cache = FileCache("query")

    async def rewrite(self, task_title: str) -> tuple[list[str], bool]:
        cached = self.cache.get(task_title)
        if isinstance(cached, list) and cached:
            return cached, True

        if not settings.llm_enable_query_rewrite:
            queries = self.templates.build(task_title)
            self.cache.set(task_title, queries)
            return queries, False

        user_prompt = f"""
研究子任务：
{task_title}

请将这个子任务改写为 3 条更适合搜索引擎的查询词。
"""
        content = await self.llm_client.chat(QUERY_REWRITE_PROMPT, user_prompt)
        queries = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("QUERY:"):
                value = line.replace("QUERY:", "", 1).strip()
                if value:
                    queries.append(value)

        if len(queries) >= 3:
            queries = queries[:3]
            self.cache.set(task_title, queries)
            return queries, False

        fallback = [line.strip("-• 1234567890. ") for line in content.splitlines() if line.strip()]
        fallback = [line for line in fallback if line]
        queries = fallback[:3] or self.templates.build(task_title)
        self.cache.set(task_title, queries)
        return queries, False
