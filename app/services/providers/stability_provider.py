import base64
import logging
from typing import Optional
import httpx
from app.services.providers.base import BaseImageProvider

logger = logging.getLogger(__name__)


class StabilityProvider(BaseImageProvider):
    """
    Stability AI (SDXL) Provider Adapter.
    Directly leverages exact SDXL pixel dimension buckets (1344x768, 1024x1024, 768x1344).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @property
    def name(self) -> str:
        return "stability_sdxl"

    def _map_style_preset(self, style: str) -> Optional[str]:
        preset_map = {
            "cinematic": "cinematic",
            "anime": "anime",
            "digital_art": "digital-art",
            "photorealistic": "photographic",
            "cyberpunk": "neon-punk",
            "watercolor": "analog-film",
        }
        return preset_map.get(style.lower())

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
            raise ValueError("Stability API Key is missing. Please set STABILITY_API_KEY in your .env file.")

        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        text_prompts = [{"text": prompt, "weight": 1.0}]
        if negative_prompt:
            text_prompts.append({"text": negative_prompt, "weight": -1.0})

        body = {
            "text_prompts": text_prompts,
            "width": width,
            "height": height,
            "samples": 1,
            "steps": 30,
            "cfg_scale": 7,
        }

        if seed is not None:
            body["seed"] = seed

        style_preset = self._map_style_preset(style)
        if style_preset:
            body["style_preset"] = style_preset

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        logger.info("Dispatching SDXL payload: dimensions=%sx%s, style=%s", width, height, style_preset)

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(url, json=body, headers=headers)

            if resp.status_code != 200:
                err_msg = f"Stability API error [{resp.status_code}]: {resp.text}"
                logger.error(err_msg)
                raise RuntimeError(err_msg)

            data = resp.json()
            artifacts = data.get("artifacts", [])
            if not artifacts:
                raise RuntimeError("Stability API returned empty artifacts array.")

            base64_img = artifacts[0]["base64"]
            return base64.b64decode(base64_img)
