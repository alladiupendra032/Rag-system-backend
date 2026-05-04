import time
from typing import Any

from groq import Groq

from app.config import get_settings


def _retry_call(fn, max_retries: int):
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception:
            if attempt >= max_retries:
                raise
            time.sleep(0.5 * (attempt + 1))


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = Groq(api_key=self.settings.groq_api_key)

    def generate_answer(self, prompt: str) -> tuple[str, dict[str, Any]]:
        def _call():
            return self.client.chat.completions.create(
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )

        stream = _retry_call(_call, self.settings.max_retries)
        parts: list[str] = []
        usage_payload: dict[str, Any] = {}
        for chunk in stream:
            usage = getattr(chunk, "usage", None)
            if usage:
                usage_payload = {
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                }
            choices = getattr(chunk, "choices", None) or []
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            text = getattr(delta, "content", None) if delta else None
            if text:
                parts.append(text)

        content = "".join(parts)
        answer = (content or "").strip() or "I don't know."
        return answer, usage_payload
