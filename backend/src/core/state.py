from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.config import settings
from src.models import ResearchHistoryItem, ResearchState


class ResearchStateStore:
    PDF_CONTENT_WIDTH = 160 * mm

    def __init__(self) -> None:
        self.history_dir = Path(settings.history_storage_dir)
        self.export_dir = Path(settings.export_storage_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def save(self, state: ResearchState) -> None:
        path = self.history_dir / f"{state.id}.json"
        path.write_text(
            state.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def load(self, research_id: str) -> ResearchState:
        path = self.history_dir / f"{research_id}.json"
        return ResearchState.model_validate_json(path.read_text(encoding="utf-8"))

    def list_history(self) -> list[ResearchHistoryItem]:
        items = []
        for path in sorted(self.history_dir.glob("*.json"), reverse=True):
            state = ResearchState.model_validate_json(path.read_text(encoding="utf-8"))
            timestamp = datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat()
            items.append(
                ResearchHistoryItem(
                    id=state.id,
                    topic=state.topic,
                    status=state.status,
                    created_at=timestamp,
                    updated_at=timestamp,
                    report_ready=bool(state.report),
                    error=state.error,
                    reused=False,
                )
            )
        return items

    def find_reusable(self, topic: str) -> ResearchState | None:
        normalized_topic = topic.strip().lower()
        for path in sorted(self.history_dir.glob("*.json"), reverse=True):
            state = ResearchState.model_validate_json(path.read_text(encoding="utf-8"))
            if state.status != "completed":
                continue
            if state.topic.strip().lower() == normalized_topic:
                return state
        return None

    def export_markdown(self, state: ResearchState) -> str:
        export_path = self.export_dir / f"{state.id}.md"
        export_path.write_text(state.report, encoding="utf-8")
        return str(export_path)

    def export_pdf(self, state: ResearchState) -> str:
        export_path = self.export_dir / f"{state.id}.pdf"
        self._build_pdf(state, export_path)
        return str(export_path)

    def _build_pdf(self, state: ResearchState, export_path: Path) -> None:
        self._register_pdf_fonts()
        styles = self._build_pdf_styles()
        story: list = []
        self._append_markdown_story(story, state.report, styles)

        document = SimpleDocTemplate(
            str(export_path),
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )
        document.build(story)

    def _register_pdf_fonts(self) -> None:
        try:
            pdfmetrics.getFont("STSong-Light")
        except KeyError:
            pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

    def _build_pdf_styles(self) -> dict[str, ParagraphStyle]:
        base = getSampleStyleSheet()
        return {
            "title": ParagraphStyle(
                "ResearchTitle",
                parent=base["Title"],
                fontName="STSong-Light",
                fontSize=20,
                leading=28,
                alignment=TA_LEFT,
                wordWrap="CJK",
                textColor=colors.HexColor("#111827"),
                spaceAfter=6 * mm,
            ),
            "heading": ParagraphStyle(
                "ResearchHeading",
                parent=base["Heading2"],
                fontName="STSong-Light",
                fontSize=14,
                leading=20,
                wordWrap="CJK",
                textColor=colors.HexColor("#111827"),
                spaceBefore=2 * mm,
                spaceAfter=2 * mm,
            ),
            "subheading": ParagraphStyle(
                "ResearchSubheading",
                parent=base["Heading3"],
                fontName="STSong-Light",
                fontSize=12,
                leading=18,
                wordWrap="CJK",
                textColor=colors.HexColor("#1f2937"),
            ),
            "body": ParagraphStyle(
                "ResearchBody",
                parent=base["BodyText"],
                fontName="STSong-Light",
                fontSize=10.5,
                leading=17,
                wordWrap="CJK",
                textColor=colors.HexColor("#1f2937"),
            ),
            "bullet": ParagraphStyle(
                "ResearchBullet",
                parent=base["BodyText"],
                fontName="STSong-Light",
                fontSize=10.5,
                leading=17,
                leftIndent=4 * mm,
                wordWrap="CJK",
                textColor=colors.HexColor("#1f2937"),
            ),
            "quote": ParagraphStyle(
                "ResearchQuote",
                parent=base["BodyText"],
                fontName="STSong-Light",
                fontSize=10.5,
                leading=17,
                leftIndent=5 * mm,
                rightIndent=2 * mm,
                borderPadding=0,
                wordWrap="CJK",
                textColor=colors.HexColor("#374151"),
            ),
            "code": ParagraphStyle(
                "ResearchCode",
                parent=base["Code"],
                fontName="Courier",
                fontSize=9,
                leading=13,
                leftIndent=0,
                textColor=colors.HexColor("#111827"),
            ),
        }

    def _append_markdown_story(
        self, story: list, markdown: str, styles: dict[str, ParagraphStyle]
    ) -> None:
        lines = markdown.splitlines()
        bullet_buffer: list[str] = []
        quote_buffer: list[str] = []
        code_buffer: list[str] = []
        table_buffer: list[str] = []
        in_code_block = False

        def flush_bullets() -> None:
            nonlocal bullet_buffer
            if bullet_buffer:
                story.append(self._build_bullet_list(bullet_buffer, styles))
                story.append(Spacer(1, 3 * mm))
                bullet_buffer = []

        def flush_quotes() -> None:
            nonlocal quote_buffer
            if quote_buffer:
                story.append(self._build_quote_block(quote_buffer, styles))
                story.append(Spacer(1, 3 * mm))
                quote_buffer = []

        def flush_code() -> None:
            nonlocal code_buffer
            if code_buffer:
                story.append(self._build_code_block(code_buffer, styles))
                story.append(Spacer(1, 3 * mm))
                code_buffer = []

        def flush_table() -> None:
            nonlocal table_buffer
            if table_buffer:
                table = self._build_table_block(table_buffer, styles)
                if table is not None:
                    story.append(table)
                    story.append(Spacer(1, 3 * mm))
                else:
                    for line in table_buffer:
                        story.append(Paragraph(self._inline_format(line), styles["body"]))
                        story.append(Spacer(1, 2.5 * mm))
                table_buffer = []

        for raw_line in lines:
            stripped = raw_line.strip()

            if stripped.startswith("```"):
                flush_bullets()
                flush_quotes()
                flush_table()
                if in_code_block:
                    flush_code()
                    in_code_block = False
                else:
                    in_code_block = True
                    code_buffer = []
                continue

            if in_code_block:
                code_buffer.append(raw_line.rstrip("\n"))
                continue

            if not stripped:
                flush_bullets()
                flush_quotes()
                flush_table()
                story.append(Spacer(1, 5 * mm))
                continue

            if self._is_table_line(raw_line):
                flush_bullets()
                flush_quotes()
                table_buffer.append(raw_line)
                continue
            flush_table()

            if stripped.startswith(("- ", "* ")):
                flush_quotes()
                bullet_buffer.append(stripped[2:].strip())
                continue
            flush_bullets()

            if stripped.startswith(">"):
                quote_buffer.append(stripped[1:].strip())
                continue
            flush_quotes()

            if stripped.startswith("# "):
                story.append(Paragraph(self._escape(stripped[2:]), styles["title"]))
            elif stripped.startswith("## "):
                story.append(Paragraph(self._escape(stripped[3:]), styles["heading"]))
            elif stripped.startswith("### "):
                story.append(Paragraph(self._escape(stripped[4:]), styles["subheading"]))
            else:
                story.append(Paragraph(self._inline_format(stripped), styles["body"]))

            story.append(Spacer(1, 2.5 * mm))

        flush_bullets()
        flush_quotes()
        flush_table()
        if code_buffer:
            flush_code()

    def _build_bullet_list(
        self, items: list[str], styles: dict[str, ParagraphStyle]
    ) -> ListFlowable:
        return ListFlowable(
            [
                ListItem(Paragraph(self._inline_format(item), styles["bullet"]))
                for item in items
            ],
            bulletType="bullet",
            leftIndent=6 * mm,
        )

    def _build_quote_block(
        self, lines: list[str], styles: dict[str, ParagraphStyle]
    ) -> Table:
        content = "<br/>".join(self._inline_format(line) for line in lines if line)
        quote = Table(
            [[Paragraph(content, styles["quote"])]],
            colWidths=[self.PDF_CONTENT_WIDTH],
        )
        quote.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f9fafb")),
                    ("LINEBEFORE", (0, 0), (0, -1), 1.5, colors.HexColor("#d1d5db")),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#e5e7eb")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return quote

    def _build_code_block(
        self, lines: list[str], styles: dict[str, ParagraphStyle]
    ) -> Table:
        content = "\n".join(lines).strip("\n")
        code = Table(
            [[Preformatted(content or " ", styles["code"])]],
            colWidths=[self.PDF_CONTENT_WIDTH],
        )
        code.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#d1d5db")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        return code

    def _build_table_block(
        self, lines: list[str], styles: dict[str, ParagraphStyle]
    ) -> Table | None:
        rows = [self._parse_table_row(line) for line in lines if self._is_table_line(line)]
        if len(rows) < 2:
            return None

        if not self._is_table_separator(rows[1]):
            return None

        rows.pop(1)

        if not rows:
            return None

        column_count = max(len(row) for row in rows)
        if column_count > 5:
            return None

        normalized_rows = []
        for row in rows:
            normalized = row + [""] * (column_count - len(row))
            normalized_rows.append(
                [Paragraph(self._inline_format(cell), styles["body"]) for cell in normalized]
            )

        table = Table(
            normalized_rows,
            colWidths=[self.PDF_CONTENT_WIDTH / column_count] * column_count,
            repeatRows=1,
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#d1d5db")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return table

    def _is_table_line(self, line: str) -> bool:
        stripped = line.strip()
        return (
            stripped.count("|") >= 2
            and stripped.startswith("|")
            and stripped.endswith("|")
            and not stripped.startswith(">")
            and not stripped.startswith("```")
        )

    def _parse_table_row(self, line: str) -> list[str]:
        stripped = line.strip().strip("|")
        return [cell.strip() for cell in stripped.split("|")]

    def _is_table_separator(self, row: list[str]) -> bool:
        return all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in row)

    def _inline_format(self, text: str) -> str:
        escaped = self._escape(text)
        escaped = self._format_links(escaped)
        escaped = self._format_bold(escaped)
        escaped = self._format_strike(escaped)
        escaped = self._format_inline_code(escaped)
        return escaped

    def _format_links(self, text: str) -> str:
        pattern = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
        return pattern.sub(
            lambda match: (
                f'<font color="#111827">{match.group(1)}</font>'
                f'<br/><font color="#2563eb" size="8">{self._break_url(match.group(2))}</font>'
            ),
            text,
        )

    def _format_bold(self, text: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    def _format_strike(self, text: str) -> str:
        return re.sub(r"~~(.+?)~~", r'<font color="#6b7280"><strike>\1</strike></font>', text)

    def _format_inline_code(self, text: str) -> str:
        return re.sub(
            r"`([^`]+)`",
            r'<font face="Courier" color="#7c3aed">\1</font>',
            text,
        )

    def _break_url(self, url: str) -> str:
        return (
            url.replace("https://", "https://<br/>")
            .replace("http://", "http://<br/>")
            .replace("/", "/&#8203;")
            .replace("?", "?&#8203;")
            .replace("&", "&amp;&#8203;")
        )

    def _escape(self, text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
