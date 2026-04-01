from __future__ import annotations

import asyncio
from typing import Any

import httpx

from src.config import settings


class LLMClient:
    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url.rstrip("/")
        self.model = settings.llm_model

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("缺少 LLM_API_KEY，请先在 backend/.env 中配置。")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()},
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        retryable_statuses = {429, 500, 502, 503, 504}
        last_error: RuntimeError | None = None

        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            for attempt in range(1, settings.llm_retry_attempts + 1):
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                try:
                    response.raise_for_status()
                    data: dict[str, Any] = response.json()
                    return self._extract_content(data)
                except httpx.HTTPStatusError as exc:
                    status_code = response.status_code
                    last_error = RuntimeError(
                        f"LLM 请求失败: {status_code} {response.text}"
                    )
                    if (
                        status_code in retryable_statuses
                        and attempt < settings.llm_retry_attempts
                    ):
                        delay_seconds = settings.llm_retry_base_delay_seconds * (
                            2 ** (attempt - 1)
                        )
                        print(
                            f"[ResearchFlow] LLM 请求第 {attempt} 次失败，"
                            f"{delay_seconds:.1f}s 后重试: {status_code}",
                            flush=True,
                        )
                        await asyncio.sleep(delay_seconds)
                        continue
                    raise last_error from exc
                except httpx.HTTPError as exc:
                    last_error = RuntimeError(f"LLM 网络请求失败: {exc}")
                    if attempt < settings.llm_retry_attempts:
                        delay_seconds = settings.llm_retry_base_delay_seconds * (
                            2 ** (attempt - 1)
                        )
                        print(
                            f"[ResearchFlow] LLM 网络异常，第 {attempt} 次失败，"
                            f"{delay_seconds:.1f}s 后重试",
                            flush=True,
                        )
                        await asyncio.sleep(delay_seconds)
                        continue
                    raise last_error from exc

        if last_error is not None:
            raise last_error

        raise RuntimeError("LLM 请求失败，未获取到有效响应。")

    def _extract_content(self, data: dict[str, Any]) -> str:
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("LLM 返回结果为空。")

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            text_parts = [
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            ]
            return "\n".join(part for part in text_parts if part).strip()

        raise RuntimeError("无法解析 LLM 返回内容。")
