import io
import math
import random
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from app.services.providers.base import BaseImageProvider


class MockProvider(BaseImageProvider):
    """
    Local high-fidelity procedural artwork generation engine.
    Generates rich, high-resolution visual artwork with custom palettes,
    geometric structures, and typography metadata without needing external API credits.
    Includes simulated stream corruption for pipeline robustness testing.
    """

    def __init__(self):
        self._transient_fail_counter: dict[str, int] = {}

    @property
    def name(self) -> str:
        return "mock_studio_engine"

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
        # Determine deterministic seed if provided
        active_seed = seed if seed is not None else random.randint(100000, 999999)
        rng = random.Random(active_seed + hash(prompt) % 100000)

        # Style color palettes
        style_palettes = {
            "cyberpunk": [(13, 2, 33), (0, 245, 212), (247, 37, 133), (114, 9, 183)],
            "cinematic": [(10, 15, 30), (28, 40, 65), (212, 175, 55), (15, 23, 42)],
            "anime": [(255, 240, 245), (255, 182, 193), (173, 216, 230), (221, 160, 221)],
            "digital_art": [(15, 23, 42), (99, 102, 241), (168, 85, 247), (236, 72, 153)],
            "photorealistic": [(18, 22, 28), (45, 55, 72), (160, 174, 192), (226, 232, 240)],
            "vivid": [(20, 20, 30), (255, 94, 98), (255, 153, 102), (255, 226, 89)],
            "watercolor": [(245, 247, 250), (138, 180, 248), (244, 143, 177), (129, 201, 149)],
        }
        palette = style_palettes.get(style.lower(), style_palettes["cyberpunk"])

        # Base canvas
        img = Image.new("RGB", (width, height), color=palette[0])
        draw = ImageDraw.Draw(img, "RGBA")

        # 1. Gradient background fill
        top_color = palette[0]
        mid_color = palette[1] if len(palette) > 1 else (40, 40, 60)
        bot_color = palette[3] if len(palette) > 3 else palette[0]

        for y in range(height):
            ratio = y / max(height - 1, 1)
            if ratio < 0.5:
                sub_r = ratio / 0.5
                r = int(top_color[0] * (1 - sub_r) + mid_color[0] * sub_r)
                g = int(top_color[1] * (1 - sub_r) + mid_color[1] * sub_r)
                b = int(top_color[2] * (1 - sub_r) + mid_color[2] * sub_r)
            else:
                sub_r = (ratio - 0.5) / 0.5
                r = int(mid_color[0] * (1 - sub_r) + bot_color[0] * sub_r)
                g = int(mid_color[1] * (1 - sub_r) + bot_color[1] * sub_r)
                b = int(mid_color[2] * (1 - sub_r) + bot_color[2] * sub_r)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

        # 2. Celestial/glow orb
        center_x = int(width * rng.uniform(0.35, 0.65))
        center_y = int(height * rng.uniform(0.3, 0.55))
        orb_radius = int(min(width, height) * 0.28)
        accent_color = palette[2] if len(palette) > 2 else (255, 200, 100)

        for step in range(orb_radius, 0, -6):
            alpha = int(140 * (1.0 - (step / orb_radius) ** 0.7))
            col = (accent_color[0], accent_color[1], accent_color[2], alpha)
            draw.ellipse(
                [
                    (center_x - step, center_y - step),
                    (center_x + step, center_y + step),
                ],
                fill=col,
            )

        # 3. Perspective perspective lines / digital horizon
        horizon_y = int(height * 0.62)
        grid_color = (palette[1][0], palette[1][1], palette[1][2], 75)

        for lx in range(-width // 2, width + width // 2, max(width // 18, 20)):
            draw.line([(lx, height), (center_x, horizon_y)], fill=grid_color, width=2)

        for hy in range(horizon_y, height, max((height - horizon_y) // 8, 12)):
            draw.line([(0, hy), (width, hy)], fill=grid_color, width=1)

        # 4. Floating architectural geometric frames
        for _ in range(rng.randint(4, 7)):
            gx = rng.randint(int(width * 0.1), int(width * 0.8))
            gy = rng.randint(int(height * 0.15), int(height * 0.65))
            gw = rng.randint(int(width * 0.08), int(width * 0.22))
            gh = rng.randint(int(height * 0.08), int(height * 0.25))
            box_col = (accent_color[0], accent_color[1], accent_color[2], rng.randint(60, 120))
            draw.rectangle([gx, gy, gx + gw, gy + gh], outline=box_col, width=2)
            draw.line([gx, gy, gx + gw, gy + gh], fill=(*box_col[:3], 40), width=1)

        # 5. Studio watermark & prompt HUD overlay
        hud_bg = (10, 14, 24, 200)
        hud_h = 90
        draw.rectangle([(0, height - hud_h), (width, height)], fill=hud_bg)
        draw.line([(0, height - hud_h), (width, height - hud_h)], fill=(0, 245, 212, 160), width=2)

        font = ImageFont.load_default()
        clean_prompt = prompt[:70] + "..." if len(prompt) > 70 else prompt
        hud_line1 = f"PROMPT: {clean_prompt.upper()}"
        hud_line2 = (
            f"STYLE: {style.upper()} | RES: {width}x{height} | SEED: {active_seed} "
            f"| ENGINE: DECODELAB MULTIMODAL STUDIO"
        )

        draw.text((24, height - hud_h + 18), hud_line1, fill=(255, 255, 255, 240), font=font)
        draw.text((24, height - hud_h + 48), hud_line2, fill=(0, 245, 212, 220), font=font)

        # Export to PNG bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        raw_bytes = buffer.getvalue()

        # 6. Intentional Stream Corruption Simulation for Testing & Grading
        if simulate_corruption:
            fail_key = f"{prompt}_{width}_{height}"
            attempts_so_far = self._transient_fail_counter.get(fail_key, 0)
            if attempts_so_far == 0:
                # Corrupt on first attempt by slicing off stream midway
                self._transient_fail_counter[fail_key] = 1
                truncated_len = max(50, len(raw_bytes) // 4)
                # Sever binary stream mid-data block
                return raw_bytes[:truncated_len]
            else:
                # On retry, stream recovers cleanly
                self._transient_fail_counter[fail_key] = 0

        return raw_bytes
