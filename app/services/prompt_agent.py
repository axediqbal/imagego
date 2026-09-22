"""
Prompt Understanding & Semantic Reasoning Agent
Translates natural user queries (including Roman Urdu, colloquial expressions, and terse keywords)
into rich, photorealistic, diffusion-optimized visual directives.
"""

import logging
import re
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class PromptUnderstandingAgent:
    """
    Autonomous Prompt Engineering Agent.
    Interprets user intent, translates Roman Urdu/informal phrasing,
    identifies scene mechanics (subject, setting, lighting, motion),
    and synthesizes production-grade diffusion prompts with negative guardrails.
    """

    # Common Roman Urdu to English semantic vocabulary
    ROMAN_URDU_VOCAB = {
        # Pronouns & Connectors
        "mujhe": "",
        "chahiye": "",
        "ek": "a",
        "aik": "a",
        "koi": "a",
        "wali": "",
        "wala": "",
        "karo": "",
        "banao": "create",
        "kare": "",
        "raha": "",
        "rahi": "",
        "hain": "",
        "hai": "",
        "hay": "",
        "aur": "and",
        "saath": "with",
        "ke": "of",
        "ki": "of",
        "ka": "of",
        "par": "on",
        "pe": "on",
        "se": "from",
        "me": "in",
        "mein": "in",
        "andar": "inside",

        # Actions & Verbs
        "jo": "which is",
        "ho": "",
        "chal": "driving smoothly",
        "chalti": "driving smoothly",
        "chalne": "moving",
        "udti": "flying",
        "udta": "flying",
        "bana": "synthesize",
        "banao": "create",
        "rakho": "",
        "hoti": "",
        "hota": "",
        "lagi": "",
        "laga": "",
        "khari": "parked elegantly",
        "khara": "standing majestically",
        "baithi": "sitting gracefully",
        "baitha": "sitting comfortably",
        "soyi": "sleeping peacefully",
        "soya": "sleeping peacefully",
        "khel": "playing energetically",
        "khelta": "playing playfully",
        "khelti": "playing playfully",
        "dorti": "speeding in high acceleration",
        "dorta": "speeding in high acceleration",
        "bhagti": "running gracefully",
        "bhagta": "running dynamically",
        "kar": "",
        "karna": "",
        "kare": "",

        # Subjects
        "larki": "beautiful young woman with detailed expressive eyes",
        "larka": "handsome young man with detailed features",
        "aurat": "elegant woman",
        "mard": "confident man",
        "bacha": "cute smiling child",
        "billi": "cute playful kitten with fluffy fur",
        "kutta": "loyal dog with shiny coat",
        "sher": "majestic wild lion with golden mane",
        "ghora": "graceful wild stallion with flowing mane",
        "parinda": "colorful exotic bird with iridescent feathers",
        "machli": "glowing exotic tropical fish",

        # Vehicles & Objects
        "gadi": "luxury sports car with aerodynamic curves",
        "gaadi": "luxury sports car with aerodynamic curves",
        "jahaz": "supersonic futuristic aircraft with glowing engines",
        "talwar": "gleaming medieval Damascus steel sword",
        "teer": "glowing crystal arrow",

        # Environment & Nature
        "barish": "dramatic rainstorm, wet ground reflections, atmospheric water droplets",
        "pahad": "majestic mountain range",
        "pahar": "majestic mountain range",
        "jheel": "crystal-clear alpine lake with reflections",
        "samandar": "scenic ocean beach with gentle waves",
        "samundar": "scenic ocean beach with gentle waves",
        "sahil": "beautiful sandy beach coastline",
        "kinara": "shoreline",
        "kinare": "on the scenic shoreline",
        "darya": "flowing clear river",
        "jangal": "dense forest with sunbeams",
        "darakht": "ancient towering green tree",
        "asman": "dramatic open sky with atmospheric clouds",
        "badal": "volumetric fluffy clouds",
        "chand": "luminescent full moon",
        "suraj": "golden hour setting sun",
        "shehar": "modern metropolis city skyline",

        # Mood & Time
        "raat": "atmospheric nighttime ambiance",
        "din": "bright sunny daytime, natural lighting",
        "subah": "crisp morning sunrise",
        "sham": "warm golden sunset",
        "andhera": "dramatic shadows, chiaroscuro contrast",
        "roshni": "radiant volumetric lighting",
        "khubsurat": "breathtakingly aesthetic, masterpiece",
        "dhamaka": "explosive dynamic shockwave and glowing embers",
        "tezi": "high-speed motion blur, dynamic panning",
    }

    # Negative prompt guardrails to guarantee high resolution
    UNIVERSAL_NEGATIVE_PROMPT = (
        "blurry, low resolution, 480p, 720p, bad anatomy, deformed limbs, extra fingers, "
        "missing arms, poorly drawn face, poorly drawn hands, disfigured, text, watermark, "
        "logo, banner, signature, cropped, artifacts, duplicate, distorted, squashed, stretched, morbid"
    )

    @classmethod
    def _translate_roman_urdu(cls, text: str) -> str:
        """Replace Roman Urdu words and typos with visual descriptors."""
        clean_text = re.sub(r"\bveiw\b", "view", text, flags=re.IGNORECASE)
        clean_text = re.sub(r"\bbech\b", "beach", clean_text, flags=re.IGNORECASE)
        words = clean_text.split()
        translated_words = []
        for word in words:
            clean_word = re.sub(r"[^\w]", "", word.lower())
            if clean_word in cls.ROMAN_URDU_VOCAB:
                replacement = cls.ROMAN_URDU_VOCAB[clean_word]
                if replacement:
                    translated_words.append(replacement)
            else:
                translated_words.append(word)
        return " ".join(translated_words)

    @classmethod
    async def interpret_with_llm(
        cls,
        prompt: str,
        style: str = "cinematic",
        openai_key: Optional[str] = None,
    ) -> Optional[str]:
        """
        Attempt fast LLM prompt refinement using OpenAI (if user key supplied)
        or Pollinations free text API with short timeout. Discards refusals.
        """
        system_instruction = (
            "You are an expert AI Prompt Engineer & Vision Director. Convert user prompts "
            "(including Roman Urdu, broken English, or brief keywords) into an articulate, "
            "photorealistic, 1080p English image generation prompt. Describe subject, composition, "
            "lighting (volumetric/studio), lens specs (e.g. 85mm f/1.4, 35mm), and environmental textures. "
            "Output ONLY the final expanded prompt. Do not output conversational filler or quotes."
        )

        user_content = f"User concept: {prompt}\nStyle preference: {style}\nResolution: 1080p Full HD"

        # Tier 1A: User provided OpenAI Key
        if openai_key and openai_key.startswith("sk-"):
            try:
                headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
                body = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200,
                }
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        result = data["choices"][0]["message"]["content"].strip()
                        if result and not any(w in result.lower() for w in ["sorry", "cannot", "as an ai"]):
                            logger.info("Agent refined prompt via OpenAI LLM: %s...", result[:60])
                            return result
            except Exception as e:
                logger.warning("OpenAI LLM prompt agent call skipped: %s", str(e))

        # Tier 1B: Free Public Text API (2.5 second timeout)
        try:
            body = {
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content},
                ],
                "model": "openai",
            }
            async with httpx.AsyncClient(timeout=2.5) as client:
                resp = await client.post("https://text.pollinations.ai/", json=body)
                if resp.status_code == 200 and len(resp.text.strip()) > 10:
                    text_out = resp.text.strip().replace('"', "")
                    # Check for refusal messages
                    if not any(w in text_out.lower() for w in ["sorry", "cannot help", "as an ai", "i cannot"]):
                        logger.info("Agent refined prompt via Pollinations Text LLM: %s...", text_out[:60])
                        return text_out
                    else:
                        logger.warning("LLM gave refusal response, discarding: %s", text_out[:60])
        except Exception:
            logger.info("Free text LLM reached timeout; switching seamlessly to Neural Semantic Agent tier.")

        return None

    @classmethod
    async def understand_and_refine(
        cls,
        raw_prompt: str,
        style: str = "cinematic",
        user_negative: Optional[str] = None,
        openai_key: Optional[str] = None,
    ) -> dict:
        """
        Main Agent Execution Pipeline:
        1. Translates Roman Urdu / colloquialisms into visual keywords.
        2. Tries fast LLM reasoning (OpenAI/Pollinations).
        3. If unavailable, applies heuristic semantic domain expansion.
        4. Synthesizes quality boosters and negative prompt guardrails.
        """
        prompt_trimmed = raw_prompt.strip()

        # Step 1: Detect and translate Roman Urdu
        translated_concept = cls._translate_roman_urdu(prompt_trimmed)
        detected_language = "Roman Urdu / Mixed" if translated_concept != prompt_trimmed else "English"

        # Step 2: Try LLM reasoning
        refined_by_llm = await cls.interpret_with_llm(translated_concept, style=style, openai_key=openai_key)
        agent_type = "LLM Neural Reasoning (GPT)" if refined_by_llm else "Semantic Heuristic Reasoning"

        final_prompt = refined_by_llm

        # Step 3: Heuristic Fallback & Enhancement
        if not final_prompt:
            from app.services.prompt_intelligence import PromptIntelligenceEngine
            expanded, _ = PromptIntelligenceEngine.optimize_prompt(
                raw_prompt=translated_concept,
                style=style,
                user_negative=user_negative,
            )
            final_prompt = expanded

        # Step 4: Negative prompt guardrail
        if user_negative and user_negative.strip():
            combined_negative = f"{user_negative.strip()}, {cls.UNIVERSAL_NEGATIVE_PROMPT}"
        else:
            combined_negative = cls.UNIVERSAL_NEGATIVE_PROMPT

        return {
            "original_prompt": raw_prompt,
            "translated_concept": translated_concept,
            "final_prompt": final_prompt,
            "negative_prompt": combined_negative,
            "detected_language": detected_language,
            "agent_type": agent_type,
        }
