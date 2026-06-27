from __future__ import annotations

import os

from openai import OpenAI


class LLMService:
    """
    Generic OpenAI-compatible LLM service.

    Cocok untuk:
    - KoboiLLM
    - LiteLLM Proxy
    - OpenRouter-compatible gateway
    - OpenAI direct jika base_url dikosongkan

    ENV:
    LLM_ENABLED=true
    LLM_API_KEY=...
    LLM_BASE_URL=https://api.koboillm.com/v1
    LLM_MODEL=openai/gpt-5.2
    LLM_TIMEOUT_SECONDS=60
    """

    def __init__(self) -> None:
        self.enabled = os.getenv("LLM_ENABLED", "true").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        self.api_key = (
            os.getenv("LLM_API_KEY", "").strip()
            or os.getenv("OPENAI_API_KEY", "").strip()
        )

        self.base_url = os.getenv("LLM_BASE_URL", "").strip()
        self.model = (
            os.getenv("LLM_MODEL", "").strip()
            or os.getenv("OPENAI_MODEL", "openai/gpt-5.2").strip()
        )
        self.timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))

        self._client: OpenAI | None = None

        if self.enabled and self.api_key:
            if self.base_url:
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=self.timeout,
                )
            else:
                self._client = OpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                )

    def is_ready(self) -> bool:
        return self.enabled and self._client is not None and bool(self.api_key)

    def get_model_name(self) -> str:
        return self.model

    def get_base_url(self) -> str:
        return self.base_url or "OpenAI default"

    def generate(self, prompt: str, temperature: float = 0.2) -> str:
        if not self.is_ready() or self._client is None:
            raise RuntimeError(
                "LLM belum siap. Pastikan LLM_ENABLED=true, "
                "LLM_API_KEY terisi, LLM_BASE_URL benar, dan LLM_MODEL sudah diset."
            )

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content or ""

    def generate_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> str:
        if not self.is_ready() or self._client is None:
            raise RuntimeError(
                "LLM belum siap. Pastikan LLM_ENABLED=true, "
                "LLM_API_KEY terisi, LLM_BASE_URL benar, dan LLM_MODEL sudah diset."
            )

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content or ""