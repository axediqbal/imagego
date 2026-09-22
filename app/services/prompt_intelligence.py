"""
Prompt Intelligence & Semantic Reasoning Engine
Transforms terse user prompts into rich, high-fidelity diffusion prompts
optimized for photorealism, spatial composition, and micro-detail rendering.
"""

import re
from typing import Tuple


class PromptIntelligenceEngine:
    """
    Intelligent prompt synthesis engine.
    Analyzes user intent and automatically crafts production-grade generative prompts
    with lighting, depth of field, surface textures, and optical camera specifications.
    """

    # Domain Knowledge Patterns
    AUTOMOTIVE_KEYWORDS = {"car", "supra", "gtr", "ferrari", "lamborghini", "porsche", "bmw", "audi", "racing", "vehicle", "drift", "supercar"}
    CHARACTER_KEYWORDS = {"girl", "man", "woman", "person", "boy", "warrior", "knight", "cyberpunk", "samurai", "model", "face", "portrait"}
    GAMING_KEYWORDS = {"clash", "clash of clans", "game", "dota", "fortnite", "zelda", "rpg", "dragon", "battle", "dungeon", "quest"}
    SPACE_KEYWORDS = {"space", "astronaut", "orbit", "planet", "galaxy", "nebula", "cosmos", "earth", "moon", "star", "satellite"}
    NATURE_KEYWORDS = {"mountain", "lake", "forest", "river", "ocean", "sunset", "sunrise", "waterfall", "beach", "valley"}

    @classmethod
    def analyze_domain(cls, prompt_lower: str) -> str:
        tokens = set(re.findall(r"\b\w+\b", prompt_lower))
        if any(kw in prompt_lower for kw in cls.GAMING_KEYWORDS) or tokens.intersection(cls.GAMING_KEYWORDS):
            return "gaming"
        if tokens.intersection(cls.AUTOMOTIVE_KEYWORDS):
            return "automotive"
        if tokens.intersection(cls.SPACE_KEYWORDS):
            return "space"
        if tokens.intersection(cls.CHARACTER_KEYWORDS):
            return "character"
        if tokens.intersection(cls.NATURE_KEYWORDS):
            return "nature"
        return "general"

    @classmethod
    def optimize_prompt(
        cls,
        raw_prompt: str,
        style: str = "cinematic",
        user_negative: str = None,
    ) -> Tuple[str, str]:
        """
        Synthesize high-fidelity prompt and negative prompt guardrails.
        """
        prompt_trimmed = raw_prompt.strip()
        # Common typo corrections
        typo_corrections = {
            r"\bveiw\b": "view",
            r"\bbech\b": "beach",
            r"\bmounten\b": "mountain",
            r"\bcarr\b": "car",
            r"\bgirls\b": "girls",
        }
        for pattern, replacement in typo_corrections.items():
            prompt_trimmed = re.sub(pattern, replacement, prompt_trimmed, flags=re.IGNORECASE)

        prompt_lower = prompt_trimmed.lower()
        domain = cls.analyze_domain(prompt_lower)

        # Domain-specific enrichment layers (Pure aesthetic modifiers, never inject foreign objects)
        domain_enhancements = {
            "automotive": (
                "gleaming high-gloss metallic paint, reflections on curved body panels, "
                "detailed alloy rims, low-angle tracking shot, shallow depth of field, 85mm lens, 8k resolution"
            ),
            "gaming": (
                "epic stylized key visual, dynamic composition, vivid particle effects, "
                "intricate detail, volumetric lighting, Unreal Engine 5 render, cinematic 8k"
            ),
            "space": (
                "breathtaking deep space photography, realistic cosmic textures, "
                "earth curvature visible in background, sharp medium format photography, 8k resolution"
            ),
            "character": (
                "masterpiece portrait, hyper-realistic skin texture with natural pores, luminous catchlights in eyes, "
                "individual hair strands rendered in sharp focus, professional three-point studio lighting, 85mm f/1.4 lens, 8k"
            ),
            "nature": (
                "majestic landscape composition, natural outdoor lighting, rich atmospheric depth, "
                "National Geographic award-winning photography, ultra-detailed 8k, crystal clear clarity"
            ),
            "general": (
                "masterpiece composition, volumetric lighting, intricate micro-textures, photorealistic rendering, "
                "sharp focus, cinematic depth, 8k UHD"
            ),
        }

        # Style-specific aesthetic Steerers
        style_steerers = {
            "cinematic": "cinematic 35mm film still, dramatic chiaroscuro contrast, volumetric haze, color graded",
            "photorealistic": "raw DSLR photograph, natural lighting, sharp lens, zero AI artifacts, crisp texture",
            "cyberpunk": "neon cyan and magenta palette, wet rain-slicked ground, holographic reflections, dark moody ambiance",
            "anime": "Makoto Shinkai aesthetic, luminous color grading, immaculate line art, beautiful cloudscapes",
            "digital_art": "trending on ArtStation, dynamic brushwork, intricate digital concept art",
            "vivid": "bold vibrant tones, high dynamic range, punchy saturation, immaculate clarity",
            "watercolor": "delicate pigment bleeding on textured cotton paper, artistic fluid brushstrokes",
        }

        enrichment_parts = []

        # If user prompt is short (< 6 words), gently enrich photographic quality
        word_count = len(prompt_trimmed.split())
        if word_count < 6:
            enrichment_parts.append(domain_enhancements.get(domain, domain_enhancements["general"]))

        enrichment_parts.append(style_steerers.get(style.lower(), style_steerers["cinematic"]))

        full_prompt = f"{prompt_trimmed}, {', '.join(enrichment_parts)}"

        # Default negative guardrails to prevent distorted or low-res outputs
        default_negative = (
            "blurry, low quality, pixelated, jpeg artifacts, low resolution, bad anatomy, "
            "deformed, extra limbs, watermark, signature, poorly drawn hands, duplicate, distorted, squashed"
        )
        if user_negative and user_negative.strip():
            combined_negative = f"{user_negative.strip()}, {default_negative}"
        else:
            combined_negative = default_negative

        return full_prompt, combined_negative
