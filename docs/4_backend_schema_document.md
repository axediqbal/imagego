# Backend Schema & API Documentation

## Project Name: ImageGo — Multimodal AI Studio
**Framework:** FastAPI 0.110+ (Pydantic v2)  
**Author:** Ahmed Iqbal (DecodeLab Internship — Week 3 Milestone)  

---

## 1. REST Endpoints Overview

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the main ImageGo Studio Web Application (`index.html`) |
| `GET` | `/docs` | Serves the Custom Glassmorphic API Documentation Portal (`docs.html`) |
| `POST` | `/api/generate` | Generates 1 to 4 AI images with prompt enhancement and stream verification |
| `POST` | `/api/enhance-prompt` | Analyzes and enriches raw user input into high-detail prompt tokens |
| `GET` | `/api/history` | Returns the list of locally saved generation metadata |
| `DELETE` | `/api/history/{filename}` | Deletes a specific saved image and its associated metadata |
| `GET` | `/api/health` | Service health status and upstream provider availability |

---

## 2. Request & Response Schemas

### 2.1 `/api/generate` (Image Generation Endpoint)

#### Request Body Schema (`GenerateRequest`)
```json
{
  "prompt": "Cyberpunk samurai standing in neon rain in futuristic Tokyo",
  "aspect_ratio": "16:9",
  "style": "cyberpunk",
  "batch_size": 1,
  "enhance_prompt": true,
  "model_provider": "pollinations",
  "api_key": null
}
```

| Field | Type | Required | Default | Allowed Values / Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `prompt` | `string` | **Yes** | — | Min 3 chars, Max 2000 chars |
| `aspect_ratio` | `string` | No | `"16:9"` | `"16:9"`, `"1:1"`, `"9:16"` |
| `style` | `string` | No | `"cinematic"` | `"cinematic"`, `"photoreal"`, `"cyberpunk"`, `"anime"`, `"digital"`, `"vivid"`, `"watercolor"` |
| `batch_size` | `integer` | No | `1` | `1`, `2`, `3`, `4` |
| `enhance_prompt`| `boolean` | No | `true` | `true`, `false` |
| `model_provider`| `string` | No | `"pollinations"`| `"pollinations"`, `"together"`, `"huggingface"` |
| `api_key` | `string` | No | `null` | Optional custom provider API key |

#### Response Body Schema (`GenerateResponse`)
```json
{
  "status": "success",
  "data": {
    "images": [
      {
        "id": "img_20260922_214530_1a2b",
        "url": "/static/outputs/img_20260922_214530_1a2b.jpg",
        "dimensions": {
          "width": 1344,
          "height": 768
        },
        "aspect_ratio": "16:9",
        "original_prompt": "Cyberpunk samurai standing in neon rain in futuristic Tokyo",
        "enhanced_prompt": "Cyberpunk samurai standing in neon rain in futuristic Tokyo, volumetric neon lighting, cinematic 8k, detailed textures, reflections on wet pavement, masterpiece",
        "style": "cyberpunk",
        "model": "flux-schnell",
        "verified": true,
        "created_at": "2026-09-22T21:45:30Z"
      }
    ],
    "count": 1,
    "elapsed_seconds": 3.82
  }
}
```

---

### 2.2 `/api/enhance-prompt` (Prompt Enrichment Endpoint)

#### Request Body (`EnhancePromptRequest`)
```json
{
  "prompt": "a cute puppy on the beach",
  "style": "photoreal"
}
```

#### Response Body (`EnhancePromptResponse`)
```json
{
  "status": "success",
  "original_prompt": "a cute puppy on the beach",
  "enhanced_prompt": "A cute golden retriever puppy sitting on golden sand at a sunny beach, detailed fur texture, natural ocean daylight, 85mm portrait lens, shallow depth of field, 8k resolution",
  "injected_keywords": ["golden sand", "detailed fur texture", "natural ocean daylight", "85mm lens"]
}
```

---

### 2.3 Error Responses

All endpoints adhere to standardized HTTP status codes:

- `400 Bad Request`: Validation failure (e.g. empty prompt or invalid aspect ratio).
```json
{
  "status": "error",
  "error_code": "INVALID_PARAMETERS",
  "message": "The prompt cannot be empty or exceed 2000 characters."
}
```
- `502 Bad Gateway`: Upstream AI provider handshake failure or timeout.
```json
{
  "status": "error",
  "error_code": "UPSTREAM_TIMEOUT",
  "message": "Upstream AI model timed out. Automatic retry was attempted without success."
}
```
- `500 Internal Server Error`: Byte verification failed or filesystem write error.
```json
{
  "status": "error",
  "error_code": "VERIFICATION_FAILURE",
  "message": "Image failed Pillow byte-stream integrity check."
}
```
