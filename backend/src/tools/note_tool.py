import json
from urllib.parse import urlparse

from src.core.cache import FileCache
from src.models import ResearchNote, SearchResult


class NoteTool:
    def __init__(self) -> None:
        self.cache = FileCache("note")

    def build_notes(self, sources: list[SearchResult]) -> tuple[list[ResearchNote], bool]:
        cache_key = json.dumps(
            [source.model_dump() for source in sources],
            ensure_ascii=False,
            sort_keys=True,
        )
        cached = self.cache.get(cache_key)
        if isinstance(cached, list):
            return [ResearchNote.model_validate(item) for item in cached], True

        notes: list[ResearchNote] = []
        seen_domains: set[str] = set()
        for index, source in enumerate(sources[:5], start=1):
            domain = urlparse(source.url).netloc
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                notes.append(
                    ResearchNote(
                        title=f"关键来源域名 {len(seen_domains)}",
                        category="source",
                        content=f"来源域名：{domain}",
                        source_url=source.url,
                        source_title=source.title,
                    )
                )

            notes.append(
                ResearchNote(
                    title=f"来源 {index}",
                    category="source",
                    content=f"{source.title}：{source.snippet or '无摘要'}",
                    source_url=source.url,
                    source_title=source.title,
                )
            )

            if source.snippet:
                notes.append(
                    ResearchNote(
                        title=f"事实线索 {index}",
                        category="fact",
                        content=source.snippet,
                        source_url=source.url,
                        source_title=source.title,
                    )
                )

        if sources:
            notes.append(
                ResearchNote(
                    title="原始来源判断",
                    category="verification",
                    content="优先关注最早出现的链接、官方博客、代码仓库提交记录和社区首发帖。",
                )
            )
            notes.append(
                ResearchNote(
                    title="待核验点",
                    category="verification",
                    content="需要结合原始来源、发布时间和多来源交叉验证来确认事件真实性。",
                )
            )
            notes.append(
                ResearchNote(
                    title="潜在影响",
                    category="impact",
                    content="需要评估事件对产品、用户、代码资产和官方回应的影响范围。",
                )
            )
        self.cache.set(cache_key, [note.model_dump() for note in notes])
        return notes, False
