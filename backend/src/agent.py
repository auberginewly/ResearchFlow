from collections.abc import AsyncIterator
import asyncio
from uuid import uuid4

from src.core.state import ResearchStateStore
from src.models import ResearchEvent, ResearchState
from src.services.executor import ExecutorService
from src.services.planner import PlannerService
from src.services.reporter import ReporterService


class ResearchAgent:
    def __init__(self) -> None:
        self.planner = PlannerService()
        self.executor = ExecutorService()
        self.reporter = ReporterService()
        self.state_store = ResearchStateStore()

    async def run(self, topic: str) -> AsyncIterator[ResearchEvent]:
        async def emit(event_type: str, data: dict) -> AsyncIterator[ResearchEvent]:
            message = data.get("message")
            if isinstance(message, str) and message:
                print(f"[ResearchFlow] {message}", flush=True)
            yield ResearchEvent(type=event_type, data=data)

        state = ResearchState(id=str(uuid4()), topic=topic, tasks=[])
        self.state_store.save(state)

        try:
            reusable = self.state_store.find_reusable(topic)
            if reusable is not None:
                reusable.id = state.id
                self.state_store.save(reusable)
                async for event in emit(
                    "history_reused",
                    {
                        "message": f"命中历史复用，直接加载已完成研究：{topic}",
                        "research_id": reusable.id,
                        "tasks": [task.model_dump() for task in reusable.tasks],
                        "report": reusable.report,
                        "progress": 100,
                        "reused": True,
                    },
                ):
                    yield event
                return

            async for event in emit(
                "planning_started",
                {"message": f"正在为主题《{topic}》规划研究任务", "progress": 0},
            ):
                yield event

            tasks = await self.planner.plan(topic)
            state.tasks = tasks
            state.total_steps = len(tasks)
            self.state_store.save(state)

            async for event in emit(
                "planning",
                {
                    "research_id": state.id,
                    "message": f"已为主题《{topic}》生成 {len(tasks)} 个子任务",
                    "tasks": [task.model_dump() for task in tasks],
                    "progress": 5,
                },
            ):
                yield event

            for index, task in enumerate(state.tasks, start=1):
                task.status = "running"
                async for event in emit(
                    "task_started",
                    data={
                        "message": f"开始执行：{task.title}",
                        "task": task.model_dump(),
                        "progress": int(((index - 1) / state.total_steps) * 100),
                    },
                ):
                    yield event

                async for event in emit(
                    "task_log",
                    {
                        "message": f"正在改写搜索词，准备更精准地检索：{task.title}",
                        "task_id": task.id,
                    },
                ):
                    yield event

                rewritten_queries, query_cache_hit = await self.executor.rewrite_queries(task)
                task.trace.rewritten_queries = rewritten_queries
                task.trace.query_cache_hit = query_cache_hit

                async for event in emit(
                    "task_log",
                    {
                        "message": (
                            f"搜索词已生成：{' | '.join(rewritten_queries)}"
                            + ("（query cache hit）" if query_cache_hit else "")
                        ),
                        "task_id": task.id,
                    },
                ):
                    yield event

                provider_name = self.executor.get_search_provider_name()
                task.trace.provider = provider_name
                async for event in emit(
                    "task_log",
                    {
                        "message": f"正在使用 {provider_name} 搜索 {len(rewritten_queries)} 个查询词",
                        "task_id": task.id,
                    },
                ):
                    yield event

                task.sources, search_trace = await self.executor.search_queries(rewritten_queries)
                task.trace.provider = search_trace["active_provider"]
                task.trace.fallback_provider = search_trace["fallback_provider"]
                task.trace.used_fallback = search_trace["used_fallback"]
                task.trace.result_count = search_trace["result_count"]
                task.trace.search_cache_hit = search_trace["cache_hit"]
                task.notes, note_cache_hit = self.executor.build_notes(task)
                task.trace.note_cache_hit = note_cache_hit
                self.state_store.save(state)

                async for event in emit(
                    "task_log",
                    {
                        "message": (
                            f"已命中 {len(task.sources)} 条去重后的来源，生成 {len(task.notes)} 条研究笔记，开始总结"
                            + ("（search cache hit）" if task.trace.search_cache_hit else "")
                            + ("（note cache hit）" if task.trace.note_cache_hit else "")
                        ),
                        "task_id": task.id,
                        "task": task.model_dump(),
                    },
                ):
                    yield event

                task.summary = await self.executor.summarize_task(task)
                task.status = "completed"
                state.completed_steps = index
                self.state_store.save(state)

                async for event in emit(
                    "task_completed",
                    data={
                        "message": f"完成：{task.title}",
                        "task": task.model_dump(),
                        "progress": int((state.completed_steps / state.total_steps) * 100),
                    },
                ):
                    yield event

            async for event in emit(
                "report_started",
                {"message": "所有子任务已完成，正在生成最终研究报告", "progress": 95},
            ):
                yield event

            report = await self.reporter.build_report(topic, state.tasks)
            state.report = report
            state.status = "completed"
            self.state_store.save(state)
            export_path = self.state_store.export_markdown(state)
            async for event in emit(
                "report_ready",
                data={
                    "message": "研究报告已生成",
                    "report": report,
                    "progress": 100,
                    "research_id": state.id,
                    "export_path": export_path,
                },
            ):
                yield event
        except asyncio.CancelledError as exc:
            state.status = "cancelled"
            state.error = "研究任务被中断"
            self.state_store.save(state)
            raise exc
        except Exception as exc:
            state.status = "failed"
            state.error = str(exc)
            self.state_store.save(state)
            raise
