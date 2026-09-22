# UI/UX Design System Document

## Project Name: ImageGo — Multimodal AI Studio
**Design Paradigm:** Dark Glassmorphism & Webflow Motion Aesthetics  
**Author:** Ahmed Iqbal (DecodeLab Internship — Week 3 Milestone)  

---

## 1. Visual Theme & Design Philosophy
The user interface is modeled after premier modern design systems (e.g., Webflow, Linear, Apple Developer Studio). It combines **deep cosmic charcoal backgrounds** (`#090b10`), **translucent frosted-glass panels**, **vibrant neon purple-to-coral gradients**, and **hardware-accelerated continuous micro-interactions** (such as 360° rotating star emblems and sliding text marquees).

---

## 2. Color Palette & Design Tokens

### 2.1 Core Colors
- **Cosmic Deep Background:** `#090b10` / `#060810`
- **Electric Violet Accent:** `#6c1afd` (RGB: `108, 26, 253`)
- **Light Coral Accent:** `#ed746c` (RGB: `237, 116, 108`)
- **Emerald Green (Verification Status):** `#10b981`
- **Rose Red (Error / Delete Warning):** `#ef4444`
- **White (Primary Text & Headings):** `#ffffff`
- **Muted Gray (Secondary Text & Labels):** `#a9a9ac` / `#71717a`

### 2.2 Glassmorphic Tokens
```css
--glass-surface: rgba(16, 19, 26, 0.75);
--glass-surface-hover: rgba(22, 27, 38, 0.85);
--glass-border: rgba(255, 255, 255, 0.08);
--glass-border-hover: rgba(108, 26, 253, 0.55);
--glass-blur: blur(20px);
--shadow-elevation: 0 25px 60px rgba(0, 0, 0, 0.7);
--shadow-glow: 0 0 30px rgba(108, 26, 253, 0.28);
```

---

## 3. Typography & Hierarchy
- **Primary Display Font:** `Plus Jakarta Sans`, 700/800 weight, tight letter-spacing (`-0.03em`)
- **Body Text:** `Inter`, 400/500/600 weight, line height 1.6
- **Code & Telemetry:** `JetBrains Mono`, 500/600 weight

---

## 4. Key Interactive Components

### 4.1 Top Mode Options Strip (`.tr-create-option-holder`)
- **Design:** Frosted pill container housing selectable capability badges (`AI Image`, `1080p HD`, `Prompt Agent`, `AI Models`, `Stream Gate`).
- **Mobile Behavior:** Touch-scrollable horizontally with `flex-shrink: 0` to completely eliminate text clipping on small viewports.

### 4.2 Master Studio Prompter Card (`.generator-studio-card`)
- Large glassmorphic container containing the dynamic textarea with expanding focus ring.
- Real-time character counter and 7 inspiration prompt chips with one-click injection.
- Signature Webflow button (`.rt-button-main-v2`) with radial hover expansion and active state spring animation.

### 4.3 3×3 Showcase Gallery Matrix
- Responsive grid (3 columns desktop, 2 columns tablet, 1 column mobile).
- Image hover overlay displaying inspection and direct delete action icons with 360° rotational micro-interactions on hover.
- Footer metadata showing aspect ratio, timestamp, and model tag.

### 4.4 Theater Lightbox Modal
- Split view dialog: left pane for full-resolution unconstrained image inspection, right pane for generation telemetry, prompt metadata, and single-click download.

---

## 5. Responsive Design Breakpoints

| Breakpoint | Target Devices | Adaptations |
| :--- | :--- | :--- |
| **`> 1024px`** | Desktop & Laptops | Full 3-column matrix, 32px padding, expanded controls |
| **`768px – 1024px`** | Tablets & iPads | 2-column matrix, side-by-side prompt card, compact navigation |
| **`< 768px`** | Mobile Phones | 1-column matrix, horizontal swipe strips, full-width action buttons, simplified header |
| **`< 480px`** | Small Phones (iPhone SE, etc.) | Compact badge typography, zero horizontal wobble (`overflow-x: hidden`) |
