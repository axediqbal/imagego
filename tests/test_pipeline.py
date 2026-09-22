import asyncio
import io
from pathlib import Path
import sys
import unittest

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from app.models.schemas import (
    ASPECT_RATIO_DIMENSIONS,
    AspectRatio,
    GenerationRequest,
    StylePreset,
)
from app.services.image_service import ImageGenerationService
from app.services.verifier import (
    BrokenDataStreamError,
    verify_image_stream,
)


class TestMultimodalStudioPipeline(unittest.TestCase):
    """Test suite for payload mapping, stream integrity, and auto-retry mechanics."""

    def test_aspect_ratio_pixel_payload_mapping(self):
        """Verify exact resolution mapping required to prevent API handshake failures."""
        self.assertEqual(ASPECT_RATIO_DIMENSIONS[AspectRatio.LANDSCAPE_16_9], (1920, 1080))
        self.assertEqual(ASPECT_RATIO_DIMENSIONS[AspectRatio.SQUARE_1_1], (1080, 1080))
        self.assertEqual(ASPECT_RATIO_DIMENSIONS[AspectRatio.PORTRAIT_9_16], (1080, 1920))

        req_16_9 = GenerationRequest(prompt="Test landscape", aspect_ratio=AspectRatio.LANDSCAPE_16_9)
        self.assertEqual(req_16_9.resolve_dimensions(), (1920, 1080))

        req_1_1 = GenerationRequest(prompt="Test square", aspect_ratio=AspectRatio.SQUARE_1_1)
        self.assertEqual(req_1_1.resolve_dimensions(), (1080, 1080))

        req_9_16 = GenerationRequest(prompt="Test vertical", aspect_ratio=AspectRatio.PORTRAIT_9_16)
        self.assertEqual(req_9_16.resolve_dimensions(), (1080, 1920))

    def test_verifier_accepts_valid_image_stream(self):
        """Verify that a complete and valid image byte stream decodes without error."""
        img = Image.new("RGB", (1024, 1024), color=(30, 40, 50))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        valid_bytes = buffer.getvalue()

        verified = verify_image_stream(valid_bytes, expected_dimensions=(1024, 1024))
        self.assertEqual(verified.width, 1024)
        self.assertEqual(verified.height, 1024)

    def test_verifier_catches_broken_data_stream(self):
        """Verify that an interrupted or truncated byte stream raises BrokenDataStreamError."""
        img = Image.new("RGB", (1344, 768), color=(200, 100, 50))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        full_bytes = buffer.getvalue()

        # Intentionally sever the stream halfway through the IDAT chunk
        corrupted_bytes = full_bytes[: len(full_bytes) // 3]

        with self.assertRaises(BrokenDataStreamError):
            verify_image_stream(corrupted_bytes, expected_dimensions=(1344, 768))

    def test_pipeline_auto_retry_on_stream_corruption(self):
        """
        Verify that when stream corruption is encountered, the service
        automatically discards the bad asset, logs, retries, and returns a verified result.
        """
        service = ImageGenerationService()
        request = GenerationRequest(
            prompt="Cyberpunk street in neon rain",
            aspect_ratio=AspectRatio.LANDSCAPE_16_9,
            count=1,
            style=StylePreset.CYBERPUNK,
            simulate_corruption=True,  # Triggers 1 stream corruption on attempt 0
        )

        response = asyncio.run(service.generate_images(request))

        self.assertTrue(response.success)
        self.assertEqual(len(response.images), 1)
        # Auto-retry must have triggered and recorded at least 1 retry event
        self.assertGreaterEqual(response.total_retries, 1)
        artifact = response.images[0]
        self.assertEqual(artifact.width, 1920)
        self.assertEqual(artifact.height, 1080)
        self.assertEqual(artifact.aspect_ratio, "16:9")
        self.assertGreater(artifact.file_size_bytes, 0)


if __name__ == "__main__":
    unittest.main()
