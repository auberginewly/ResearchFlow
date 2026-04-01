from src.models import ResearchTask
from src.prompts import PLANNER_PROMPT
from src.services.llm_client import LLMClient


class PlannerService:
    def __init__(self) -> None:
        self.llm_client = LLMClient()

    async def plan(self, topic: str) -> list[ResearchTask]:
        user_prompt = f"""
研究主题：
{topic}

请输出 3 个贴合该主题的研究子任务。

如果这是一个具体事件，请优先围绕：
- 事件最早来源与时间线
- 信息真实性与证据核验
- 影响范围、涉及内容与官方回应
"""
        content = await self.llm_client.chat(PLANNER_PROMPT, user_prompt)
        task_titles = self._parse_tasks(topic, content)

        return [
            ResearchTask(id=f"task-{index}", title=title)
            for index, title in enumerate(task_titles, start=1)
        ]

    def _parse_tasks(self, topic: str, content: str) -> list[str]:
        task_titles = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("TASK:"):
                title = line.replace("TASK:", "", 1).strip()
                if title:
                    task_titles.append(title)

        if len(task_titles) >= 3:
            return task_titles[:3]

        fallback = [line.strip("-• 1234567890. ") for line in content.splitlines() if line.strip()]
        fallback = [line for line in fallback if line]
        if len(fallback) >= 3:
            return fallback[:3]

        return [
            f"{topic}: 核心概念",
            f"{topic}: 关键应用",
            f"{topic}: 风险与趋势",
        ]
