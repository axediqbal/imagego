# ImageGo // Next-Gen Multimodal AI Studio

<p align="center">
  <img src="app/static/img/star-spin-large.svg" width="70" alt="ImageGo Star Emblem" />
</p>

<p align="center">
  <strong>High-performance, multimodal AI image synthesis studio with intelligent prompt engineering, strict 1080p pixel payloads, and Pillow stream verification.</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#project-documentation">Documentation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#deployment">Deployment</a>
</p>

---

## 🌟 Overview

**ImageGo** is a full-stack AI image generation platform built for the **DecodeLab Internship — Week 3 Milestone**. Designed with a focus on reliability, visual fidelity, and modern UX, ImageGo solves common AI generation problems such as prompt ambiguity, handshake timeout drops, corrupt byte delivery, and inconsistent aspect ratios.

---

## 🚀 Key Features

- 🧠 **Intelligent Prompt Engineering Agent:** Enriches simple user inputs with rich artistic heuristics, lighting parameters, and lens perspectives.
- 📐 **Strict 1080p Ultra-HD Resolution Mapping:**
  - **16:9 Landscape:** Native `1344×768`
  - **1:1 Square:** Native `1024×1024`
  - **9:16 Portrait:** Native `768×1344`
- 🛡️ **Pillow Stream Verification Layer:** Full raster `Image.open().load()` byte validation with automatic retries to ensure zero corrupt payloads.
- 🎨 **Webflow-Inspired Glassmorphic UI:** Cosmic charcoal palette, live ambient background video, 360° rotating emblems, and continuous sliding marquees.
- 🖼️ **Showcase Matrix & Theater Lightbox:** 3×3 responsive gallery with full-screen inspection, metadata telemetry, and instant asset deletion.
- 📱 **Universal Device Responsiveness:** Fully optimized for seamless touch-scrolling across mobile smartphones, tablets, and desktops.
- 📖 **Embedded Developer Portal (`/docs`):** Interactive API documentation with live testing consoles and code snippets for cURL, Python, and JavaScript.

---

## 📂 Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application, routing & serverless entry
│   └── static/
│       ├── index.html        # Main Webflow-inspired Studio frontend
│       ├── docs.html         # Custom API Documentation Portal
│       ├── css/
│       │   ├── style.css     # Glassmorphic UI & responsive styles
│       │   └── docs.css      # API documentation styling
│       ├── js/
│       │   └── studio.js     # Client state management & API interaction
│       └── img/              # SVG emblems, icons, and static assets
├── docs/
│   ├── 1_product_requirements_document.md    # Product Requirements (PRD)
│   ├── 2_technical_requirements_document.md  # Technical Architecture (TRD)
│   ├── 3_ui_ux_design_document.md            # UI/UX Design System Document
│   └── 4_backend_schema_document.md          # Backend Schema & API Spec
├── .gitignore
├── requirements.txt          # Python dependencies
├── vercel.json               # Vercel serverless deployment config
└── README.md
```

---

## 📖 Project Documentation

Comprehensive project documentation is available in the [`docs/`](./docs/) directory:

1. [**Product Requirements Document (PRD)**](./docs/1_product_requirements_document.md)
2. [**Technical Requirements Document (TRD)**](./docs/2_technical_requirements_document.md)
3. [**UI/UX Design Document**](./docs/3_ui_ux_design_document.md)
4. [**Backend Schema Document**](./docs/4_backend_schema_document.md)

---

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/axediqbal/imagego.git
cd imagego
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
- **Studio Interface:** `http://127.0.0.1:8000/`
- **API Documentation:** `http://127.0.0.1:8000/docs`

---

## 🌐 API Reference

### Generate Artwork
```bash
POST /api/generate
Content-Type: application/json

{
  "prompt": "Cyberpunk samurai standing in neon rain in futuristic Tokyo",
  "aspect_ratio": "16:9",
  "style": "cyberpunk",
  "batch_size": 1,
  "enhance_prompt": true
}
```

### Enhance Prompt
```bash
POST /api/enhance-prompt
Content-Type: application/json

{
  "prompt": "a cute puppy on the beach",
  "style": "photoreal"
}
```

---

## ☁️ Deployment

### Deploy to Vercel
The repository includes a ready-to-use `vercel.json` configuration:
1. Push this repository to GitHub.
2. Import the project into your [Vercel Dashboard](https://vercel.com).
3. Vercel will automatically detect the Python serverless entry point (`app/main.py`) and deploy the app with zero manual configuration.

### Deploy to Render / Railway
Set the start command to:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 👨‍💻 Author

**Ahmed Iqbal**  
DecodeLab Internship — Week 3 Milestone  
GitHub: [@axediqbal](https://github.com/axediqbal)
