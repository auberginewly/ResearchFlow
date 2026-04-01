import json

from src.config import settings
from src.core.cache import FileCache
from src.models import ResearchTask
from src.prompts import REPORTER_PROMPT
from src.services.llm_client import LLMClient


class ReporterService:
    def __init__(self) -> None:
        self.llm_client = LLMClient()
        self.cache = FileCache("report")

    async def build_report(self, topic: str, tasks: list[ResearchTask]) -> str:
        cache_key = json.dumps(
            {
                "topic": topic,
                "tasks": [task.model_dump() for task in tasks],
                "llm_polish": settings.llm_enable_report_polish,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        cached = self.cache.get(cache_key)
        if isinstance(cached, str) and cached:
            return cached

        if not settings.llm_enable_report_polish:
            report = self._build_template_report(topic, tasks)
            self.cache.set(cache_key, report)
            return report

        task_sections = []
        for index, task in enumerate(tasks, start=1):
            task_sections.append(
                "\n".join(
                    [
                        f"子任务 {index}",
                        f"标题：{task.title}",
                        f"总结：{task.summary or '暂无总结'}",
                    ]
                )
            )

        user_prompt = f"""
研究主题：
{topic}

子任务总结：
{'\n\n'.join(task_sections)}

请输出一份结构化 Markdown 研究报告。
"""
        try:
            report = await self.llm_client.chat(REPORTER_PROMPT, user_prompt)
        except RuntimeError:
            report = self._build_template_report(topic, tasks)
        self.cache.set(cache_key, report)
        return report

    def _build_template_report(self, topic: str, tasks: list[ResearchTask]) -> str:
        lines = [
            f"# {topic} 研究报告",
            "",
            "## 摘要",
            f"本报告基于 {len(tasks)} 个研究子任务、结构化研究笔记与搜索来源生成。",
            "",
            "## 子任务结论",
        ]

        for index, task in enumerate(tasks, start=1):
            lines.extend(
                [
                    f"### {index}. {task.title}",
                    task.summary or "暂无总结",
                    "",
                ]
            )
            if task.notes:
                lines.append("关键笔记：")
                for note in task.notes[:4]:
                    lines.append(f"- [{note.category}] {note.content}")
                lines.append("")
            if task.sources:
                lines.append("主要来源：")
                for source in task.sources[:3]:
                    lines.append(f"- {source.title} ({source.url})")
                lines.append("")

        lines.extend(
            [
                "## 后续建议",
                "- 对重要事件继续核验原始来源与时间线。",
                "- 对高风险信息追加人工复核。",
            ]
        )
        return "\n".join(lines)
