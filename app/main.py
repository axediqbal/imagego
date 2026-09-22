import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models.schemas import (
    GenerationRequest,
    GenerationResponse,
    ImageArtifact,
)
from app.services.image_service import ImageGenerationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("studio_app")

settings = get_settings()
app = FastAPI(
    title="ImageGo // Multimodal AI Studio",
    description="DecodeLab Week 3: Text-to-Image Generation with aspect ratio mapping and Pillow stream integrity verification.",
    version="1.0.0",
    docs_url=None,  # Custom glassmorphic documentation portal served at /docs
    redoc_url="/redoc",
)

# Enable CORS for flexible development environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

image_service = ImageGenerationService(settings)
static_dir = Path(__file__).parent / "static"


@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint exposing active AI provider, supported engines, and readiness."""
    provider = image_service.get_provider()
    return {
        "status": "healthy",
        "provider": provider.name,
        "supported_models": [
            {"id": "pollinations_flux", "name": "Pollinations Flux (HD)", "free": True, "requires_key": False},
            {"id": "pollinations_sana", "name": "Pollinations Sana (Fast)", "free": True, "requires_key": False},
            {"id": "pollinations_turbo", "name": "Pollinations Turbo (Instant)", "free": True, "requires_key": False},
            {"id": "openai", "name": "OpenAI DALL-E 3", "free": False, "requires_key": True},
            {"id": "stability", "name": "Stability AI SDXL", "free": False, "requires_key": True},
            {"id": "mock", "name": "Local Mock Engine", "free": True, "requires_key": False},
        ],
        "max_retries": settings.max_retries,
        "outputs_ready": settings.get_output_path().exists(),
    }


@app.get("/docs", include_in_schema=False)
async def serve_custom_docs():
    """Serve custom dark glassmorphic API documentation portal with orbit astronaut background."""
    docs_file = static_dir / "docs.html"
    if docs_file.exists():
        return FileResponse(docs_file)
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Documentation - Multimodal Studio")


@app.get("/swagger", include_in_schema=False)
async def serve_swagger():
    """Standard raw Swagger UI explorer."""
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Raw Swagger UI - Multimodal Studio")


@app.post("/api/generate", response_model=GenerationResponse, tags=["Generation"])
async def generate_artwork(request: GenerationRequest):
    """
    Generate digital artwork from natural language prompts.
    Maps aspect ratios to exact dimensions, executes the generation pipeline,
    and runs Pillow stream validation with auto-retry.
    """
    try:
        response = await image_service.generate_images(request)
        return response
    except Exception as exc:
        logger.exception("Generation endpoint error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(exc)}",
        )


@app.get("/api/history", response_model=list[ImageArtifact], tags=["History"])
async def get_history():
    """Fetch history of all verified generated artwork stored in outputs directory."""
    return image_service.get_history()


@app.delete("/api/history/{identifier}", tags=["History"])
async def delete_history_item(identifier: str):
    """Delete a generated image artifact and its metadata companion from archive."""
    success = image_service.delete_artifact(identifier)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact '{identifier}' not found or already deleted.",
        )
    return {"success": True, "message": f"Artifact '{identifier}' permanently deleted."}


@app.post("/api/prompt/optimize", tags=["Intelligence"])
async def optimize_prompt_endpoint(payload: dict):
    """Intelligently optimize a user prompt using domain-aware semantic synthesis."""
    from app.services.prompt_intelligence import PromptIntelligenceEngine
    raw_prompt = payload.get("prompt", "")
    style = payload.get("style", "cinematic")
    negative_prompt = payload.get("negative_prompt", None)
    
    optimized, suggested_neg = PromptIntelligenceEngine.optimize_prompt(
        raw_prompt=raw_prompt,
        style=style,
        user_negative=negative_prompt,
    )
    return {
        "original_prompt": raw_prompt,
        "optimized_prompt": optimized,
        "suggested_negative_prompt": suggested_neg,
    }


@app.post("/api/agent/understand", tags=["Agent"])
async def agent_understand_prompt_endpoint(payload: dict):
    """
    Autonomous AI Agent that interprets, translates Roman Urdu/colloquial text,
    and structures prompts for 1080p photorealistic diffusion.
    """
    from app.services.prompt_agent import PromptUnderstandingAgent
    raw_prompt = payload.get("prompt", "")
    style = payload.get("style", "cinematic")
    negative_prompt = payload.get("negative_prompt", None)
    api_key = payload.get("api_key", None)

    result = await PromptUnderstandingAgent.understand_and_refine(
        raw_prompt=raw_prompt,
        style=style,
        user_negative=negative_prompt,
        openai_key=api_key,
    )
    return result


@app.get("/api/outputs/{filename}", tags=["Assets"])
async def get_output_file(filename: str):
    """Securely serve verified image asset files with path-traversal prevention."""
    output_dir = settings.get_output_path()
    file_path = (output_dir / filename).resolve()

    # Prevent directory traversal attacks
    if not str(file_path).startswith(str(output_dir.resolve())):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image asset not found.")

    return FileResponse(file_path, media_type="image/png")


# Serve static assets (HTML, CSS, JS)
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", tags=["UI"])
async def serve_index():
    """Serve the primary Multimodal Studio Web UI."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "Multimodal Studio API is running. Static frontend assets are loading...",
        "docs": "/docs",
    }
