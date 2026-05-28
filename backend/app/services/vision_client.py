import base64
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings


VISION_CONFIG_ERROR = "视觉模型API未配置，请检查VISION_API_KEY、VISION_BASE_URL、VISION_MODEL"

IMAGE_MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


class VisionClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key if api_key is not None else (settings.vision_api_key or settings.llm_api_key)
        self.base_url = base_url if base_url is not None else settings.vision_base_url
        self.model = model if model is not None else settings.vision_model
        self.timeout = timeout

    def _validate_config(self) -> None:
        if not self.api_key or not self.base_url or not self.model:
            raise RuntimeError(VISION_CONFIG_ERROR)

    @staticmethod
    def _image_to_data_url(image_path: Path) -> str:
        suffix = image_path.suffix.lower().lstrip(".")
        mime_type = IMAGE_MIME_TYPES.get(suffix)
        if mime_type is None:
            raise ValueError("不支持的图片格式")
        data = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{data}"

    def analyze_image(self, image_path: str | Path, prompt: str, temperature: float = 0.2) -> str:
        self._validate_config()
        path = Path(image_path)
        if not path.exists() or not path.is_file():
            raise RuntimeError("图片文件不存在")

        data_url = self._image_to_data_url(path)
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
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
            raise RuntimeError(f"视觉模型API请求失败：HTTP {exc.response.status_code}，{detail}") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"视觉模型API请求异常：{exc}") from exc
        except ValueError as exc:
            raise RuntimeError("视觉模型API返回内容不是有效JSON") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("视觉模型API返回格式不符合OpenAI兼容格式") from exc

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("视觉模型API返回内容为空")
        return content.strip()
