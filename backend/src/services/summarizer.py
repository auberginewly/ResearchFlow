from src.models import ResearchNote, SearchResult
from src.prompts import SUMMARIZER_PROMPT
from src.services.llm_client import LLMClient


class SummarizerService:
    def __init__(self) -> None:
        self.llm_client = LLMClient()

    async def summarize(
        self,
        task_title: str,
        notes: list[ResearchNote],
        sources: list[SearchResult],
        source_summary: dict,
    ) -> str:
        source_lines = "\n".join(
            [
                "\n".join(
                    [
                        f"- 标题：{source.title}",
                        f"  摘要：{source.snippet or '无摘要'}",
                        f"  链接：{source.url}",
                        f"  来源：{source.provider or 'unknown'}",
                    ]
                )
                for source in sources
            ]
        )
        note_lines = "\n".join(
            f"- [{note.category}] {note.title}: {note.content}" for note in notes
        )
        user_prompt = f"""
任务标题：
{task_title}

研究笔记：
{note_lines or '暂无研究笔记'}

搜索结果：
{source_lines}

来源统计：
{source_summary}

请输出一段可直接写入研究报告的中文总结。
"""
        return await self.llm_client.chat(SUMMARIZER_PROMPT, user_prompt)
