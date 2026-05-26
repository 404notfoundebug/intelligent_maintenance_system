from typing import Any

import httpx

from app.core.config import settings


LLM_CONFIG_ERROR = "大模型API未配置，请检查LLM_API_KEY、LLM_BASE_URL、LLM_MODEL"


class LLMClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.llm_api_key
        self.base_url = base_url if base_url is not None else settings.llm_base_url
        self.model = model if model is not None else settings.llm_model
        self.timeout = timeout

    def _validate_config(self) -> None:
        if not self.api_key or not self.base_url or not self.model:
            raise RuntimeError(LLM_CONFIG_ERROR)

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        self._validate_config()
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500] if exc.response is not None else str(exc)
            raise RuntimeError(f"大模型API请求失败：HTTP {exc.response.status_code}，{detail}") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"大模型API请求异常：{exc}") from exc
        except ValueError as exc:
            raise RuntimeError("大模型API返回内容不是有效JSON") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("大模型API返回格式不符合OpenAI兼容格式") from exc

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("大模型API返回内容为空")
        return content.strip()
