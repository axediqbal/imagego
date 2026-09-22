import io
import logging
from typing import Optional
import httpx
from PIL import Image
from app.services.providers.base import BaseImageProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseImageProvider):
    """
    OpenAI DALL-E 3 API Provider Adapter.
    Translates aspect ratio dimensions to DALL-E 3 accepted sizes,
    downloads the resulting binary stream, and conforms to target dimensions.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @property
    def name(self) -> str:
        return "openai_dall_e_3"

    def _resolve_dalle_size(self, width: int, height: int) -> str:
        """Map target width/height to DALL-E 3 supported dimension parameters."""
        if width > height:
            return "1792x1024"
        elif height > width:
            return "1024x1792"
        else:
            return "1024x1024"

    async def generate_single(
        self,
        prompt: str,
        width: int,
        height: int,
        style: str,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
        simulate_corruption: bool = False,
    ) -> bytes:
        if not self.api_key or not self.api_key.strip():
            raise ValueError("OpenAI API Key is missing. Please set OPENAI_API_KEY in your .env file.")

        dalle_size = self._resolve_dalle_size(width, height)
        dalle_style = "vivid" if style in ["vivid", "cyberpunk", "anime"] else "natural"

        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": dalle_size,
            "quality": "hd",
            "style": dalle_style,
            "response_format": "b64_json",
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        logger.info("Dispatching DALL-E 3 request: size=%s, style=%s", dalle_size, dalle_style)

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/images/generations",
                json=payload,
                headers=headers,
            )

            if resp.status_code != 200:
                err_text = resp.text
                logger.error("OpenAI API Handshake Failure [%d]: %s", resp.status_code, err_text)
                raise RuntimeError(f"OpenAI API error ({resp.status_code}): {err_text}")

            result = resp.json()
            import base64
            b64_data = result["data"][0]["b64_json"]
            raw_bytes = base64.b64decode(b64_data)

        # Conform to exact target resolution requested by the caller (e.g. 1344x768 or 768x1344)
        with Image.open(io.BytesIO(raw_bytes)) as img:
            if (img.width, img.height) != (width, height):
                logger.info("Resizing DALL-E output from %sx%s to target %sx%s", img.width, img.height, width, height)
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                out_buf = io.BytesIO()
                resized.save(out_buf, format="PNG")
                raw_bytes = out_buf.getvalue()

        return raw_bytes
