"""
video_pipeline/localizer.py
Portuguese translation and cultural localization module (pt-BR).
Tailored specifically for Brazilian gaming culture, TikTok/Reels high engagement,
and 80s/90s Miami Vice aesthetics.
Provides RuleBasedOfflineLocalizer for 100% deterministic offline operation
and VideoLocalizer with LLM prompting and automatic offline fallback.
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, Union

from video_pipeline.transcriber import TranscriptSegment, WordTimestamp

# Gamer slang and cultural adaptation dictionary
# Ordered by specificity (longer phrases first)
GAMING_SLANG_MAP: List[tuple[str, str]] = [
    # Full expressions
    (r"\blook at this trailer\b", "SE LIGA NESSE TRAILER, TÁ MALUCO!"),
    (r"\blook at this\b", "SE LIGA NISSO!"),
    (r"\blook at the\b", "OLHA SÓ ESSE"),
    (r"\bthe graphics and lighting are completely unbelievable\b", "O GRÁFICO E A ILUMINAÇÃO TÃO SIMPLESMENTE SURREAIS!"),
    (r"\bthe graphics are unbelievable\b", "O GRÁFICO TÁ SIMPLESMENTE SURREAL!"),
    (r"\bgraphics are unbelievable\b", "GRÁFICO TÁ SURREAL!"),
    (r"\bthe graphics are insane\b", "O GRÁFICO TÁ INSANO!"),
    (r"\bvice city is finally back\b", "VICE CITY TÁ DE VOLTA, QUE NOSTALGIA INSANA!"),
    (r"\bvice city is back\b", "VICE CITY TÁ DE VOLTA!"),
    (r"\bcheck out the cars and neon sunsets\b", "SE LIGA NAS MÁQUINAS E NO PÔR DO SOL NEON!"),
    (r"\bcheck out the cars\b", "OLHA ESSAS MÁQUINAS!"),
    (r"\bcheck the link in bio for the exclusive drop\b", "DROP EXCLUSIVO NA BIO, NÃO MOSCA! LINK NA BIO!"),
    (r"\bcheck the link in bio\b", "DROP EXCLUSIVO NO LINK DA BIO!"),
    (r"\bcheck out the link in bio\b", "LINK NA BIO, CORRE!"),
    (r"\blink in bio\b", "LINK NA BIO"),
    (r"\bexclusive drop\b", "DROP EXCLUSIVO"),
    (r"\bgameplay leak\b", "VAZAMENTO DE GAMEPLAY INSANO"),
    (r"\bleaked scene\b", "CENA VAZADA SURREAL"),
    (r"\bnew trailer\b", "NOVO TRAILER PESADÍSSIMO"),
    (r"\brelease date\b", "DATA DE LANÇAMENTO OFICIAL"),
    (r"\bocean drive\b", "OCEAN DRIVE"),
    (r"\bneon lights\b", "LUZES NEON"),
    (r"\bsunsets\b", "PÔR DO SOL"),
    (r"\bunbelievable\b", "SURREAL E INSANO"),
    (r"\binsane\b", "INSANO"),
    (r"\bcrazy\b", "TÁ MALUCO"),
    (r"\btrailer\b", "TRAILER"),
    (r"\bgraphics\b", "GRÁFICO"),
    (r"\bcars\b", "MÁQUINAS"),
    (r"\bgameplay\b", "GAMEPLAY"),
    (r"\bhype\b", "HYPE SURREAL"),
    (r"\bdrop\b", "DROP"),
]

# Viral 3-second hook prefixes to boost retention on vertical platforms
VIRAL_HOOKS: List[str] = [
    "🚨 SE LIGA NISSO: ",
    "😱 TÁ MALUCO: ",
    "🔥 VAZOU AGORA: ",
    "👀 OLHA ISSO: ",
]


class RuleBasedOfflineLocalizer:
    """
    Deterministic rule-based Portuguese localizer for gaming clips.
    Converts English gaming language into high-energy pt-BR slang without external APIs.
    """

    def __init__(self, add_viral_hooks: bool = True):
        self.add_viral_hooks = add_viral_hooks
        self._compiled_rules = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in GAMING_SLANG_MAP
        ]

    def localize(self, text: str) -> str:
        """Translate and adapt English gaming text into authentic pt-BR gamer slang."""
        if not text or not text.strip():
            return text

        result = text
        for pattern, replacement in self._compiled_rules:
            result = pattern.sub(replacement, result)

        # Fallback keyword pass if no match occurred and words remain English
        if result == text:
            # Word-level fallback
            words = {
                "look": "olha",
                "trailer": "trailer",
                "graphics": "gráfico",
                "game": "jogo",
                "city": "cidade",
                "car": "carro",
                "cars": "carros",
                "link": "link",
                "bio": "bio",
                "drop": "drop",
            }
            for en_word, pt_word in words.items():
                result = re.sub(rf"\b{en_word}\b", pt_word, result, flags=re.IGNORECASE)

        return result

    # Alias for API compatibility
    translate = localize

    def localize_segments(
        self,
        segments: List[Union[Dict[str, Any], TranscriptSegment]],
    ) -> List[TranscriptSegment]:
        """
        Localize a sequence of transcript segments, injecting a viral hook into the 0-3s intro.
        """
        localized: List[TranscriptSegment] = []

        for idx, seg in enumerate(segments):
            seg_id = getattr(seg, "id", None) or seg.get("id", idx + 1)
            start = getattr(seg, "start", None) or seg.get("start", 0.0)
            end = getattr(seg, "end", None) or seg.get("end", 0.0)
            orig_text = getattr(seg, "text", None) or seg.get("text", "")

            adapted_text = self.localize(orig_text)

            # Insert viral hook in the opening 0-3 second segment if not already hooked
            if idx == 0 and self.add_viral_hooks and start < 3.0:
                if not any(hook.strip(" :🚨😱🔥👀") in adapted_text for hook in VIRAL_HOOKS):
                    adapted_text = f"{VIRAL_HOOKS[0]}{adapted_text}"

            localized.append(
                TranscriptSegment(
                    id=seg_id,
                    start=start,
                    end=end,
                    text=adapted_text,
                    words=[],
                )
            )

        return localized


class VideoLocalizer:
    """
    Main Video Localizer supporting LLM translation when API keys are available,
    and seamlessly defaulting to RuleBasedOfflineLocalizer in offline/mock mode.
    """

    def __init__(self, offline: bool = True, model_name: str = "gemini-1.5-flash"):
        self.offline = offline
        self.model_name = model_name
        self.rule_engine = RuleBasedOfflineLocalizer()

        # Check for API keys
        has_gemini = bool(os.getenv("GEMINI_API_KEY"))
        has_openai = bool(os.getenv("OPENAI_API_KEY"))
        self.has_llm = (has_gemini or has_openai) and not offline

    def localize(self, text: str) -> str:
        """Translate and localize string."""
        if self.offline or not self.has_llm:
            return self.rule_engine.localize(text)

        # Live LLM execution if available
        try:
            return self._llm_localize(text)
        except Exception:
            return self.rule_engine.localize(text)

    # Alias for API compatibility
    translate = localize

    def localize_segments(
        self,
        segments: List[Union[Dict[str, Any], TranscriptSegment]],
    ) -> List[TranscriptSegment]:
        """Localize transcript segments with viral pacing."""
        return self.rule_engine.localize_segments(segments)

    def _llm_localize(self, text: str) -> str:
        # Prompting instructions for pt-BR viral gamer style
        system_instruction = (
            "Você é um roteirista viral brasileiro especialista em games e TikTok/Reels. "
            "Traduza o texto de trailers/jogos para português brasileiro com gírias gamers atuais "
            "(ex: 'tá maluco', 'insano', 'hype surreal', 'se liga nisso', 'link na bio'). "
            "Mantenha frases curtas e impactantes para legendas verticais."
        )

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_instruction}\n\nTexto original: {text}\nTradução adaptada:"}
                        ]
                    }
                ]
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()

        return self.rule_engine.localize(text)


def localize_text(text: str, offline: bool = True) -> str:
    """Helper function to localize a text string."""
    loc = VideoLocalizer(offline=offline)
    return loc.localize(text)
