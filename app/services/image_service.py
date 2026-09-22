import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import Settings, get_settings
from app.models.schemas import (
    GenerationRequest,
    GenerationResponse,
    ImageArtifact,
)
from app.services.providers.base import BaseImageProvider
from app.services.providers.mock_provider import MockProvider
from app.services.providers.openai_provider import OpenAIProvider
from app.services.providers.pollinations_provider import PollinationsProvider
from app.services.providers.stability_provider import StabilityProvider
from app.services.prompt_intelligence import PromptIntelligenceEngine
from app.services.prompt_agent import PromptUnderstandingAgent
from app.services.verifier import BrokenDataStreamError, verify_image_stream
from app.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """
    Central orchestration service managing aspect ratio resolution,
    provider dispatch, stream integrity verification, and auto-retry workflows.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.output_dir = self.settings.get_output_path()

    def get_provider(
        self,
        override_provider: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> BaseImageProvider:
        """Instantiate and return the configured AI image generation provider with optional user API key."""
        provider_name = (override_provider or self.settings.ai_provider).lower()

        if "openai" in provider_name:
            effective_key = (api_key or "").strip() or (self.settings.openai_api_key or "").strip()
            if not effective_key:
                raise ValueError("OpenAI DALL-E 3 requires an API key. Please enter your OPENAI_API_KEY in Config or request payload.")
            return OpenAIProvider(effective_key)

        elif "stability" in provider_name:
            effective_key = (api_key or "").strip() or (self.settings.stability_api_key or "").strip()
            if not effective_key:
                raise ValueError("Stability AI (SDXL) requires an API key. Please enter your STABILITY_API_KEY in Config or request payload.")
            return StabilityProvider(effective_key)

        elif "mock" in provider_name:
            return MockProvider()

        elif "turbo" in provider_name:
            return PollinationsProvider(model_flavor="turbo")

        elif "sana" in provider_name:
            return PollinationsProvider(model_flavor="sana")

        # Default: Free Live AI Engine (Flux)
        return PollinationsProvider(model_flavor="flux")

    async def generate_images(self, request: GenerationRequest) -> GenerationResponse:
        """
        Orchestrate end-to-end generation across the requested image count,
        enforcing pixel dimensions and self-healing stream integrity checks.
        """
        start_time = time.perf_counter()
        width, height = request.resolve_dimensions()
        provider = self.get_provider(
            override_provider=request.provider,
            api_key=request.api_key,
        )

        logger.info(
            "Initiating generation: prompt='%s', aspect_ratio=%s (%dx%d), count=%d, provider=%s",
            request.prompt[:50],
            request.aspect_ratio.value,
            width,
            height,
            request.count,
            provider.name,
        )

        artifacts: list[ImageArtifact] = []
        total_retries_across_batch = 0

        # Execute generations concurrently or iteratively up to requested count
        tasks = [
            self._generate_single_with_retry(
                provider=provider,
                request=request,
                width=width,
                height=height,
                index=i,
            )
            for i in range(request.count)
        ]

        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in batch_results:
            if isinstance(result, Exception):
                logger.error("Batch item generation failed: %s", str(result))
                raise result
            artifact, retries = result
            artifacts.append(artifact)
            total_retries_across_batch += retries

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return GenerationResponse(
            success=True,
            message=f"Successfully generated {len(artifacts)} artwork(s) with {total_retries_across_batch} retry event(s).",
            images=artifacts,
            total_retries=total_retries_across_batch,
            latency_ms=latency_ms,
            provider=provider.name,
        )

    async def _generate_single_with_retry(
        self,
        provider: BaseImageProvider,
        request: GenerationRequest,
        width: int,
        height: int,
        index: int,
    ) -> tuple[ImageArtifact, int]:
        """
        Execute single image generation with auto-retry on stream corruption.
        Ensures Image.open().load() verifies integrity before persisting to disk.
        """
        attempt = 0
        max_retries = self.settings.max_retries
        retries_used = 0

        # Offset seed per item in batch if seed is specified
        item_seed = request.seed + index if request.seed is not None else None

        # Autonomous AI Prompt Agent: Understand intent, translate, and expand
        effective_prompt = request.prompt
        effective_negative = request.negative_prompt
        if request.enable_ai_enhancer and "mock" not in provider.name.lower():
            agent_res = await PromptUnderstandingAgent.understand_and_refine(
                raw_prompt=request.prompt,
                style=request.style.value,
                user_negative=request.negative_prompt,
                openai_key=request.api_key,
            )
            effective_prompt = agent_res["final_prompt"]
            effective_negative = agent_res["negative_prompt"]
            logger.info("Agent [%s] synthesized prompt: '%s...'", agent_res.get("agent_type"), effective_prompt[:80])

        while attempt <= max_retries:
            try:
                # Should we simulate corruption for testing stream recovery?
                simulate_corruption = request.simulate_corruption and (attempt == 0)

                raw_bytes = await provider.generate_single(
                    prompt=effective_prompt,
                    width=width,
                    height=height,
                    style=request.style.value,
                    seed=item_seed,
                    negative_prompt=effective_negative,
                    simulate_corruption=simulate_corruption,
                )

                # PIPELINE INTEGRITY GATE: Force stream decoding via Pillow
                # If stream is severed or invalid, BrokenDataStreamError is raised
                verified_image = verify_image_stream(
                    raw_data=raw_bytes,
                    expected_dimensions=(width, height),
                    enforce_exact_dimensions=False,
                )

                # Successfully verified! Persist asset to disk
                artifact_id = str(uuid.uuid4())
                filename = f"{artifact_id}.png"
                meta_filename = f"{artifact_id}.json"

                file_path = self.output_dir / filename
                meta_path = self.output_dir / meta_filename

                # Save verified image to local outputs directory
                verified_image.save(file_path, format="PNG")
                file_size = file_path.stat().st_size

                created_iso = datetime.now(timezone.utc).isoformat()
                final_url = f"/api/outputs/{filename}"

                # If Supabase is connected, upload to Supabase Storage and get CDN URL
                if supabase_service.is_configured:
                    try:
                        with open(file_path, "rb") as img_f:
                            cloud_url = await supabase_service.upload_image_bytes(
                                filename=filename,
                                image_bytes=img_f.read(),
                                content_type="image/png",
                            )
                            if cloud_url:
                                final_url = cloud_url
                    except Exception as sb_err:
                        logger.warning("Supabase storage upload failed: %s. Falling back to local URL.", str(sb_err))

                artifact = ImageArtifact(
                    id=artifact_id,
                    filename=filename,
                    url=final_url,
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt,
                    aspect_ratio=request.aspect_ratio.value,
                    width=verified_image.width,
                    height=verified_image.height,
                    format=verified_image.format or "PNG",
                    style=request.style.value,
                    created_at=created_iso,
                    retry_count=retries_used,
                    file_size_bytes=file_size,
                )

                # Save metadata companion JSON file
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(artifact.model_dump(), f, indent=2)

                # If Supabase is connected, sync metadata record to Supabase PostgreSQL table
                if supabase_service.is_configured:
                    try:
                        await supabase_service.insert_artwork_record(artifact.model_dump())
                    except Exception as sb_db_err:
                        logger.warning("Supabase table insert failed: %s", str(sb_db_err))

                return artifact, retries_used

            except BrokenDataStreamError as stream_err:
                retries_used += 1
                attempt += 1
                logger.warning(
                    "Integrity check failed: %s. Discarding corrupt data stream. Attempt %d/%d...",
                    str(stream_err),
                    attempt,
                    max_retries,
                )

                if attempt > max_retries:
                    logger.error("Exhausted maximum retry limit (%d) due to stream corruption.", max_retries)
                    raise RuntimeError(
                        f"Pipeline integrity failure: Image stream corrupted repeatedly after {max_retries} retries."
                    ) from stream_err

                # Exponential backoff
                await asyncio.sleep(0.3 * (2 ** (attempt - 1)))

            except Exception as unhandled_err:
                logger.error("Unrecoverable generation error: %s", str(unhandled_err))
                raise unhandled_err

        raise RuntimeError("Generation loop exited unexpectedly without result.")

    def get_history(self) -> list[ImageArtifact]:
        """Load list of previously generated and verified image artifacts from Supabase DB or outputs directory."""
        # 1. If Supabase is configured, fetch from cloud database
        if supabase_service.is_configured:
            try:
                cloud_records = supabase_service.fetch_history(limit=50)
                if cloud_records:
                    cloud_history: list[ImageArtifact] = []
                    for row in cloud_records:
                        try:
                            cloud_history.append(
                                ImageArtifact(
                                    id=row.get("id"),
                                    filename=row.get("filename") or f"{row.get('id')}.png",
                                    url=row.get("url"),
                                    prompt=row.get("prompt"),
                                    negative_prompt=row.get("negative_prompt"),
                                    aspect_ratio=row.get("aspect_ratio", "16:9"),
                                    width=row.get("width", 1344),
                                    height=row.get("height", 768),
                                    format="PNG",
                                    style=row.get("style", "cinematic"),
                                    created_at=row.get("created_at"),
                                    retry_count=row.get("retry_count", 0),
                                    file_size_bytes=row.get("file_size_bytes", 0),
                                )
                            )
                        except Exception as parse_err:
                            logger.warning("Error parsing cloud row: %s", str(parse_err))
                    if cloud_history:
                        return cloud_history
            except Exception as e:
                logger.warning("Could not fetch cloud history from Supabase: %s. Falling back to local.", str(e))

        # 2. Fall back to local outputs directory
        history: list[ImageArtifact] = []
        if not self.output_dir.exists():
            return history

        for meta_file in sorted(self.output_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    history.append(ImageArtifact(**data))
            except Exception as e:
                logger.warning("Could not parse metadata file %s: %s", meta_file.name, str(e))

        return history

    def delete_artifact(self, identifier: str) -> bool:
        """
        Delete an image artifact and its metadata companion file from Supabase and local storage.
        identifier can be an artifact id or filename (e.g. 'uuid' or 'uuid.png').
        """
        clean_id = identifier.replace(".png", "").replace(".json", "")
        deleted = False

        # 1. Delete from Supabase if configured
        if supabase_service.is_configured:
            try:
                supabase_service.delete_record_and_file(clean_id)
                deleted = True
            except Exception as sb_del_err:
                logger.warning("Supabase delete failed: %s", str(sb_del_err))

        # 2. Delete from local disk
        png_path = self.output_dir / f"{clean_id}.png"
        json_path = self.output_dir / f"{clean_id}.json"

        if png_path.exists():
            png_path.unlink()
            deleted = True
        if json_path.exists():
            json_path.unlink()
            deleted = True

        logger.info("Deleted artifact %s: success=%s", clean_id, deleted)
        return deleted
