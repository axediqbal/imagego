# Technical Requirements Document (TRD)

## Project Name: ImageGo — Multimodal AI Studio
**Architecture Level:** Application & Systems Engineering  
**Version:** 1.0.0  
**Author:** Ahmed Iqbal (DecodeLab Internship — Week 3 Milestone)  

---

## 1. System Architecture Overview

The system follows a modern client-server architecture utilizing **FastAPI (ASGI)** on the backend and a **Vanilla HTML5/CSS3/JavaScript (ES6+)** client on the frontend, with no heavy framework overhead.

```
+-------------------------------------------------------------+
|                      Client Layer (Browser)                 |
|   - Vanilla ES6+ State Management & LocalStorage History     |
|   - Touch-Optimized Glassmorphic UI & Theater Lightbox      |
|   - Interactive Code Generator & Testing Console            |
+------------------------------+------------------------------+
                               | HTTPS / REST (JSON & Blobs)
+------------------------------v------------------------------+
|                     FastAPI Backend (ASGI)                  |
|   - CORS Middleware & Static File Mounting                  |
|   - Prompt Enhancement Agent (Rule-based / Semantic Parser) |
|   - Resolution & Aspect-Ratio Conformance Engine            |
|   - Pillow Stream Verification & Auto-Retry Shield          |
+------------------------------+------------------------------+
                               | Asynchronous HTTP (httpx)
+------------------------------v------------------------------+
|                   Upstream Model Providers                   |
|   - Pollinations AI (Flux.1 / Stable Diffusion XL)          |
|   - Together AI (Black-Forest-Labs Flux Schnell)            |
|   - HuggingFace Inference API                               |
+-------------------------------------------------------------+
```

---

## 2. Technology Stack & Dependencies

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | FastAPI | `>=0.110.0` | Asynchronous REST routing and OpenAPI documentation |
| **ASGI Web Server** | Uvicorn | `>=0.28.0` | High-throughput asynchronous server |
| **Validation & Schema** | Pydantic v2 | `>=2.6.0` | Strict type checking and request payload validation |
| **Image Processing** | Pillow (PIL) | `>=10.2.0` | Stream validation, byte conforamnce, dimension validation |
| **HTTP Client** | HTTPX | `>=0.27.0` | Non-blocking async client for upstream AI inference calls |
| **Configuration** | python-dotenv | `>=1.0.1` | Environment variable management |
| **Frontend Core** | Vanilla HTML5 / CSS3 / JS | ES2022+ | Zero-dependency, ultra-fast render with custom design tokens |
| **Deployment Engine** | Vercel / Python Serverless | V2 | Multi-target deployability (Vercel, Render, Railway, Docker) |

---

## 3. Core Engine Components & Algorithms

### 3.1 Prompt Enhancement Agent (`enhance_prompt`)
The prompt agent enriches vague or sparse input into structured diffusion tokens:
- **Atmosphere & Illumination:** Volumetric lighting, ray tracing, chiaroscuro, golden hour, neon subsurface scattering.
- **Composition & Optics:** 85mm lens, f/1.4 aperture, rule of thirds, wide-angle cinematic framing.
- **Render Engine Modifiers:** Octane Render 3D, Unreal Engine 5 render, hyper-detailed photorealistic 8K, intricate textures.

### 3.2 Aspect Ratio Conformance Matrix
To ensure 1080p Ultra-HD without warping:
- **16:9 Landscape:** Maps to `width=1344, height=768` (Total: ~1,032,192 pixels)
- **1:1 Square:** Maps to `width=1024, height=1024` (Total: 1,048,576 pixels)
- **9:16 Portrait:** Maps to `width=768, height=1344` (Total: ~1,032,192 pixels)

### 3.3 Pillow Stream Verification Layer (`verify_and_load_image`)
```python
def verify_image_stream(raw_bytes: bytes) -> Image.Image:
    """
    Verifies that the downloaded byte stream represents a valid,
    non-corrupted image file before saving or streaming to client.
    """
    try:
        image_stream = io.BytesIO(raw_bytes)
        img = Image.open(image_stream)
        img.load()  # Forces full raster decoding of pixels
        img.verify() # Validates internal headers and checksums
        return img
    except Exception as exc:
        raise ImageVerificationError("Corrupt payload received from upstream engine")
```

---

## 4. Security & Performance Guidelines
1. **Zero Client Leakage:** Upstream API keys passed by clients are forwarded directly in memory over TLS; never persisted to backend logs.
2. **Local Storage Isolation:** Saved generations and gallery metadata are kept in the user's browser `localStorage` and `outputs/` directory.
3. **Concurrency:** All upstream network requests utilize `asyncio` and `httpx.AsyncClient` to avoid thread blocking.
4. **Static Cache Invalidation:** Client assets utilize version query hashes (`style.css?v=10.1`) to ensure instant CSS updates upon deployment.
