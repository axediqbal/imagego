import asyncio
import io
import logging
import random
import urllib.parse
from typing import Optional
import httpx
from PIL import Image, ImageFilter, ImageOps

from app.services.providers.base import BaseImageProvider

logger = logging.getLogger(__name__)


class PollinationsProvider(BaseImageProvider):
    """
    Pollinations AI (Flux / Stable Diffusion) Live Generative Engine.
    Requires ZERO API keys or subscriptions.
    Generates genuine, high-quality photorealistic and stylized AI artwork
    without stretching, squashing, or serving cached stock images.
    """

    def __init__(self, model_flavor: Optional[str] = None):
        self.model_flavor = model_flavor or "flux"
        self._transient_fail_counter: dict[str, int] = {}

    @property
    def name(self) -> str:
        return f"pollinations_{self.model_flavor}"

    def _enrich_prompt_for_style(self, prompt: str, style: str, width: int, height: int) -> str:
        """Append clean stylistic descriptors to steer diffusion toward high fidelity without altering user subject."""
        style_enrichments = {
            "cinematic": "cinematic lighting, 35mm film photograph, dramatic atmospheric depth, photorealistic, 8k, masterpiece",
            "cyberpunk": "cyberpunk aesthetic, vibrant neon reflections, atmospheric volumetric haze, 8k",
            "anime": "high quality anime artwork, makoto shinkai aesthetic, vibrant colors, detailed line art, masterpiece, 8k",
            "digital_art": "digital concept art, trending on artstation, intricate digital painting, sharp focus, 8k render",
            "photorealistic": "hyper-realistic photograph, professional studio lighting, 85mm lens, raw photo, ultra detailed, 8k, sharp focus",
            "vivid": "vivid colors, rich contrast, dynamic lighting, masterpiece composition, 8k",
            "watercolor": "delicate watercolor painting, fluid ink washes, paper texture, soft gradients, masterpiece",
        }
        enrichment = style_enrichments.get(style.lower(), "highly detailed, 8k resolution, award winning, masterpiece")
        
        # Spatial framing cues for clean aspect conformity
        if width > height:
            framing = "wide cinematic framing, panoramic composition"
        elif height > width:
            framing = "vertical portrait framing, centered subject"
        else:
            framing = "centered composition"

        return f"{prompt}, {framing}, {enrichment}"

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
        enriched_prompt = self._enrich_prompt_for_style(prompt, style, width, height)
        encoded_prompt = urllib.parse.quote(enriched_prompt)

        # Dynamic cryptographically non-cached seed ensures true fresh diffusion every time
        active_seed = seed if seed is not None else random.randint(1000000, 99999999)

        # Request native square canvas (1024x1024) to avoid server-side stretching/squashing
        # Pollinations generates un-distorted natural geometry on 1:1, which we then conform to 16:9 or 9:16
        native_size = 1024

        params = {
            "width": native_size,
            "height": native_size,
            "seed": active_seed,
            "nologo": "true",
        }
        if self.model_flavor and self.model_flavor != "default":
            params["model"] = self.model_flavor

        query_string = urllib.parse.urlencode(params)
        request_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?{query_string}"

        logger.info(
            "Requesting live AI generation from Pollinations (%s): seed=%s native_canvas=%sx%s target=%sx%s",
            self.model_flavor, active_seed, native_size, native_size, width, height
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "image/jpeg,image/png,image/*",
        }

        async with httpx.AsyncClient(timeout=45.0, follow_redirects=True) as client:
            resp = await client.get(request_url, headers=headers)

            # Fallback if specific model was congested or 429
            if resp.status_code != 200 or len(resp.content) == 0:
                if resp.status_code == 429:
                    logger.warning("Pollinations IP queue active (429). Sleeping 3.5s to clear queue before retry...")
                    await asyncio.sleep(3.5)
                logger.warning(
                    "Pollinations [%s] returned status %s. Trying fallback default route with new seed...",
                    self.model_flavor, resp.status_code
                )
                fallback_params = {k: v for k, v in params.items() if k != "model"}
                fallback_params["seed"] = random.randint(1000000, 99999999)
                fallback_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?{urllib.parse.urlencode(fallback_params)}"
                resp = await client.get(fallback_url, headers=headers)

            # Secondary fallback if still congested
            if resp.status_code != 200 or len(resp.content) == 0:
                if resp.status_code == 429:
                    logger.warning("Secondary 429 detected. Sleeping 3.0s...")
                    await asyncio.sleep(3.0)
                logger.warning("Trying secondary fallback route for prompt...")
                simple_prompt = urllib.parse.quote(prompt)
                tertiary_url = f"https://image.pollinations.ai/prompt/{simple_prompt}?width={native_size}&height={native_size}&nologo=true&seed={random.randint(1000, 99999)}"
                resp = await client.get(tertiary_url, headers=headers)

            if resp.status_code != 200 or len(resp.content) == 0:
                err_msg = f"Pollinations AI service error [{resp.status_code}]: {resp.text[:200]}"
                logger.error(err_msg)
                raise RuntimeError(err_msg)

            raw_bytes = resp.content

        # Handle intentional corruption simulation for test suite or demo switch
        if simulate_corruption:
            fail_key = f"{prompt}_{width}_{height}"
            attempts_so_far = self._transient_fail_counter.get(fail_key, 0)
            if attempts_so_far == 0:
                self._transient_fail_counter[fail_key] = 1
                truncated_len = max(50, len(raw_bytes) // 4)
                logger.warning("Simulating truncated data stream for pipeline auto-retry demonstration.")
                return raw_bytes[:truncated_len]
            else:
                self._transient_fail_counter[fail_key] = 0

        # Conforming dimensions with ImageOps.fit:
        # 1. Zero stretching or squashing regardless of aspect ratio or orientation!
        # 2. Crops out bottom corner watermark completely for widescreen and portrait!
        with Image.open(io.BytesIO(raw_bytes)) as img:
            logger.info(
                "Conforming image from %sx%s to target %sx%s preserving exact natural geometry with ImageOps.fit",
                img.width, img.height, width, height
            )
            # Use top-biased centering for portrait to keep faces in upper third, center for landscape
            if height > width:
                centering = (0.5, 0.38)
            else:
                centering = (0.5, 0.46)

            conformed = ImageOps.fit(
                img,
                (width, height),
                method=Image.Resampling.LANCZOS,
                centering=centering
            )
            crisp_img = conformed.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
            buf = io.BytesIO()
            crisp_img.save(buf, format="PNG", quality=98)
            raw_bytes = buf.getvalue()

        return raw_bytes

