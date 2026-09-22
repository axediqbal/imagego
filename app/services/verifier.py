import io
import logging
from typing import Optional, Tuple
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)


class BrokenDataStreamError(OSError):
    """Raised when the image stream is truncated, cut off, or corrupt."""
    pass


class DimensionMismatchError(ValueError):
    """Raised when decoded image dimensions do not match the expected payload."""
    pass


def verify_image_stream(
    raw_data: bytes,
    expected_dimensions: Optional[Tuple[int, int]] = None,
    enforce_exact_dimensions: bool = False,
) -> Image.Image:
    """
    Verify the binary stream integrity of a downloaded or generated image.

    Pillow's Image.open() is lazy and only parses headers. By calling .load()
    within a try-except block, we force the full byte stream to decode. If the
    data stream was terminated prematurely, an OSError ('broken data stream')
    or SyntaxError is raised.

    Args:
        raw_data: Binary image bytes from generation engine.
        expected_dimensions: Optional (width, height) tuple to check against.
        enforce_exact_dimensions: If True, raises DimensionMismatchError on size difference.

    Returns:
        Verified, decoded PIL Image object.

    Raises:
        BrokenDataStreamError: When binary data is incomplete, truncated, or corrupt.
        DimensionMismatchError: When decoded dimensions deviate from the expected payload.
    """
    if not raw_data or len(raw_data) < 100:
        logger.error("Image stream buffer is empty or too small (%d bytes).", len(raw_data) if raw_data else 0)
        raise BrokenDataStreamError("Payload buffer underflow: insufficient binary image data.")

    try:
        buffer = io.BytesIO(raw_data)
        image = Image.open(buffer)

        # Force full decoding of all scanlines / image frames
        # If the stream was severed mid-transfer, this triggers OSError: broken data stream
        image.load()

        logger.info(
            "Image stream verified successfully: format=%s, size=%s, mode=%s",
            image.format,
            image.size,
            image.mode,
        )

    except (OSError, SyntaxError, UnidentifiedImageError, ValueError) as exc:
        error_msg = f"Broken data stream detected during image load: {str(exc)}"
        logger.warning(error_msg)
        raise BrokenDataStreamError(error_msg) from exc

    if expected_dimensions:
        exp_w, exp_h = expected_dimensions
        if (image.width, image.height) != (exp_w, exp_h):
            msg = (
                f"Dimension mismatch: expected ({exp_w}, {exp_h}), "
                f"received ({image.width}, {image.height})."
            )
            if enforce_exact_dimensions:
                logger.error(msg)
                raise DimensionMismatchError(msg)
            else:
                logger.warning(msg)

    return image
