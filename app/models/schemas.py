from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AspectRatio(str, Enum):
    """Aspect ratio presets with strict validation."""
    LANDSCAPE_16_9 = "16:9"
    SQUARE_1_1 = "1:1"
    PORTRAIT_9_16 = "9:16"


# Exact pixel mapping to enforce minimum 1080p high-definition standard across all aspect ratios
ASPECT_RATIO_DIMENSIONS: dict[AspectRatio, tuple[int, int]] = {
    AspectRatio.LANDSCAPE_16_9: (1920, 1080),
    AspectRatio.SQUARE_1_1: (1080, 1080),
    AspectRatio.PORTRAIT_9_16: (1080, 1920),
}


class StylePreset(str, Enum):
    """Visual style presets for generation payloads."""
    CINEMATIC = "cinematic"
    VIVID = "vivid"
    NATURAL = "natural"
    ANIME = "anime"
    DIGITAL_ART = "digital_art"
    PHOTOREALISTIC = "photorealistic"
    CYBERPUNK = "cyberpunk"
    WATERCOLOR = "watercolor"


class GenerationRequest(BaseModel):
    """Validated input payload for multimodal image generation requests."""
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language description of the target artwork",
        examples=["Futuristic cyberpunk street in neon rain with reflections"],
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Elements or artifacts to avoid in the generation",
    )
    aspect_ratio: AspectRatio = Field(
        default=AspectRatio.SQUARE_1_1,
        description="Target aspect ratio mapped to strict pixel dimensions",
    )
    count: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of artwork assets to generate (1-4)",
    )
    style: StylePreset = Field(
        default=StylePreset.CINEMATIC,
        description="Visual artistic style tuning preset",
    )
    seed: Optional[int] = Field(
        default=None,
        ge=0,
        description="Optional seed for deterministic generation if supported",
    )
    provider: Optional[str] = Field(
        default="pollinations_flux",
        description="Target AI provider engine (pollinations_flux, pollinations_sana, pollinations_turbo, openai, stability, mock)",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Optional user-provided API key for paid models (OpenAI or Stability)",
    )
    simulate_corruption: bool = Field(
        default=False,
        description="Flag to simulate a broken data stream for pipeline verification and retry demonstration",
    )
    enable_ai_enhancer: bool = Field(
        default=True,
        description="Flag to activate intelligent contextual prompt expansion for hyper-detailed synthesis",
    )

    def resolve_dimensions(self) -> tuple[int, int]:
        """Return the exact (width, height) pixel dimensions for the requested aspect ratio."""
        return ASPECT_RATIO_DIMENSIONS[self.aspect_ratio]


class ImageArtifact(BaseModel):
    """Metadata schema representing a single generated, verified artwork asset."""
    id: str
    filename: str
    url: str
    prompt: str
    negative_prompt: Optional[str] = None
    aspect_ratio: str
    width: int
    height: int
    format: str = "PNG"
    style: str
    created_at: str
    retry_count: int = 0
    file_size_bytes: int


class GenerationResponse(BaseModel):
    """Standardized response payload returned to the frontend studio."""
    success: bool
    message: str
    images: list[ImageArtifact]
    total_retries: int
    latency_ms: float
    provider: str
