from abc import ABC, abstractmethod
from typing import Optional


class BaseImageProvider(ABC):
    """Abstract interface defining the contract for text-to-image API providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass

    @abstractmethod
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
        """
        Generate a single image asset and return its raw binary bytes.

        Args:
            prompt: Text prompt describing the target artwork.
            width: Exact width in pixels.
            height: Exact height in pixels.
            style: Artistic style preset.
            seed: Optional integer seed for reproducibility.
            negative_prompt: Negative guidance prompt.
            simulate_corruption: Test flag to intentionally corrupt stream.

        Returns:
            Raw image bytes (e.g. PNG or JPEG).
        """
        pass
