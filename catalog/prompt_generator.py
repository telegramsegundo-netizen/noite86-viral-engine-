"""
Generative AI Prompt Generator & Parameterization Engine

Generates photographic, cinematic, and print-vector prompts for modern generative
AI models (Midjourney v6.1, Flux.1 Pro, and SDXL) with strict parameterization of
camera optics, volumetric neon lighting, 300 DPI textures, and automatic IP clearance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from catalog.ip_filter import IPFilter


@dataclass
class PromptSpecification:
    """Complete multi-engine prompt specification for a catalog item."""
    product_id: str
    title: str
    midjourney_prompt: str
    flux_prompt: str
    negative_prompt: str
    aspect_ratio: str
    print_texture_notes: str
    optics_preset: str
    lighting_preset: str
    environment_preset: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert specification to dictionary."""
        return {
            "product_id": self.product_id,
            "title": self.title,
            "midjourney_prompt": self.midjourney_prompt,
            "flux_prompt": self.flux_prompt,
            "negative_prompt": self.negative_prompt,
            "aspect_ratio": self.aspect_ratio,
            "print_texture_notes": self.print_texture_notes,
            "optics_preset": self.optics_preset,
            "lighting_preset": self.lighting_preset,
            "environment_preset": self.environment_preset,
        }


class PromptGenerator:
    """Builder for parameterized generative AI prompts targeting Midjourney and Flux."""

    OPTICS_PRESETS: Dict[str, str] = {
        "studio_commercial": "Hasselblad H6D-100c, 100mm f/2.2 HC lens, tack sharp, fine texture resolution, clean commercial depth of field",
        "vintage_film_lookbook": "Shot on 35mm Kodak Portra 800, anamorphic cine lens, subtle film grain, optical halation, soft bokeh",
        "editorial_streetwear": "85mm f/1.4 lens, shallow depth of field, high-fashion streetwear editorial lookbook styling",
        "macro_hero": "100mm f/2.8 macro lens, crisp micro-textures, intricate material weaves and stitching details visible",
        "action_wide": "35mm prime lens, f/2.8, dynamic 45-degree angle, sharp foreground focus",
    }

    LIGHTING_PRESETS: Dict[str, str] = {
        "neon_noir_bicolor": "Bioluminescent dual-tone neon lighting, vibrant cyan key light at 45 degrees, hot magenta rim lighting, soft warm tungsten fill, specular highlights on wet reflective surfaces, volumetric atmospheric haze",
        "golden_hour_sunset": "Warm afternoon Florida golden hour sunlight, low angle amber rays, natural soft shadows, pastel sky gradient reflections",
        "ocean_drive_night": "Dramatic nighttime boulevard ambient light, glowing neon hotel signage reflections on wet dark asphalt, deep navy blue shadows, specular rim lights",
        "poolside_sunlight": "Crisp midday tropical sunlight, turquoise pool water caustics reflections, bright white stone highlights, airy luxury atmosphere",
    }

    ENVIRONMENT_PRESETS: Dict[str, str] = {
        "terrazzo_studio": "Placed on luxury Italian terrazzo tile with pink and black marble chips, studio dark gradient backdrop",
        "wet_asphalt_drive": "Resting on wet dark polished asphalt after a tropical Florida rainstorm, soft neon reflections",
        "hotel_nightstand": "Lying on an authentic dark walnut hotel nightstand with warm ambient brass lamp glow",
        "minimalist_plinth": "Resting on a clean white travertine stone plinth, neutral grey minimalist studio background",
        "gaming_battlestation": "Sitting on a dark walnut executive desk alongside a custom mechanical keyboard and ambient violet light",
    }

    DEFAULT_NEGATIVE_PROMPT: str = (
        "text, watermark, logo, brand name, trademark, low quality, blurry, distorted, "
        "cheap plastic look, 3d render CGI, cartoonish, oversaturated flat colors, extra limbs, "
        "deformed geometry, artifacts, compression noise"
    )

    def __init__(self, ip_filter: Optional[IPFilter] = None) -> None:
        self.ip_filter = ip_filter or IPFilter()

    def generate_midjourney(
        self,
        product: Dict[str, Any],
        optics: str = "studio_commercial",
        lighting: str = "neon_noir_bicolor",
        aspect_ratio: str = "1:1",
        stylize: int = 180,
    ) -> str:
        """
        Generate a production-ready Midjourney v6.1 prompt formatted with CLI flags.
        """
        # If product has pre-authored midjourney prompt in dataset, adapt or enhance
        existing = (
            product.get("ai_prompts", {}).get("midjourney_v6_prompt")
            or product.get("ai_art_prompt", {}).get("midjourney_prompt")
        )

        if existing:
            base_prompt = existing
        else:
            title = product.get("title", "Retro Vice Product")
            desc = product.get("description", product.get("headline", ""))
            optics_text = self.OPTICS_PRESETS.get(optics, self.OPTICS_PRESETS["studio_commercial"])
            lighting_text = self.LIGHTING_PRESETS.get(lighting, self.LIGHTING_PRESETS["neon_noir_bicolor"])
            base_prompt = (
                f"Commercial hero product photograph of {title}, {desc}, "
                f"1980s Miami Vice color palette with neon cyan and flamingo pink accents, "
                f"{optics_text}, {lighting_text}, 8k resolution, photorealistic "
                f"--ar {aspect_ratio} --v 6.1 --style raw --stylize {stylize}"
            )

        # Enforce IP compliance
        clean_prompt = self.ip_filter.sanitize_text(base_prompt)
        return clean_prompt

    def generate_flux(
        self,
        product: Dict[str, Any],
        lighting: str = "neon_noir_bicolor",
        environment: str = "terrazzo_studio",
    ) -> str:
        """
        Generate a production-ready Flux.1 Pro prompt with surface print textures and vector specs.
        """
        existing = (
            product.get("ai_prompts", {}).get("flux_pro_prompt")
            or product.get("ai_art_prompt", {}).get("flux_prompt")
        )

        if existing:
            base_prompt = existing
        else:
            title = product.get("title", "Retro Vice Product")
            desc = product.get("description", product.get("headline", ""))
            lighting_text = self.LIGHTING_PRESETS.get(lighting, self.LIGHTING_PRESETS["neon_noir_bicolor"])
            env_text = self.ENVIRONMENT_PRESETS.get(environment, self.ENVIRONMENT_PRESETS["terrazzo_studio"])
            base_prompt = (
                f"Studio product photography of {title}, {desc}, "
                f"retro-futuristic 1980s aesthetic, {env_text}, {lighting_text}, "
                f"300 DPI high resolution vector textures, ultra-detailed fabric micro-texture, "
                f"cinematic vaporwave editorial"
            )

        clean_prompt = self.ip_filter.sanitize_text(base_prompt)
        return clean_prompt

    def generate_negative(self, extra_negatives: Optional[List[str]] = None) -> str:
        """Build universal negative prompt string."""
        if not extra_negatives:
            return self.DEFAULT_NEGATIVE_PROMPT
        combined = f"{self.DEFAULT_NEGATIVE_PROMPT}, {', '.join(extra_negatives)}"
        return combined

    def build_specification(
        self,
        product: Dict[str, Any],
        optics_preset: str = "studio_commercial",
        lighting_preset: str = "neon_noir_bicolor",
        environment_preset: str = "terrazzo_studio",
        aspect_ratio: Optional[str] = None,
    ) -> PromptSpecification:
        """
        Build an authoritative PromptSpecification object for the given product.
        """
        p_id = product.get("id", product.get("sku", "VC-GEN-001"))
        title = product.get("title", "Vice Product")
        ar = (
            aspect_ratio
            or product.get("ai_prompts", {}).get("aspect_ratio")
            or "1:1"
        )
        print_notes = (
            product.get("ai_prompts", {}).get("print_texture_notes")
            or "300 DPI high-gamut vector printing specification."
        )

        mj_prompt = self.generate_midjourney(
            product=product,
            optics=optics_preset,
            lighting=lighting_preset,
            aspect_ratio=ar,
        )
        flux_prompt = self.generate_flux(
            product=product,
            lighting=lighting_preset,
            environment=environment_preset,
        )
        negative_prompt = (
            product.get("ai_prompts", {}).get("negative_prompt")
            or self.generate_negative()
        )

        return PromptSpecification(
            product_id=p_id,
            title=title,
            midjourney_prompt=mj_prompt,
            flux_prompt=flux_prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=ar,
            print_texture_notes=print_notes,
            optics_preset=optics_preset,
            lighting_preset=lighting_preset,
            environment_preset=environment_preset,
        )


# Global default generator instance
_default_generator = PromptGenerator()


def generate_prompts_for_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience helper returning dictionary of prompts for a product."""
    spec = _default_generator.build_specification(product)
    return spec.to_dict()


def generate_prompt(query_or_product: str | Dict[str, Any]) -> str | Dict[str, Any]:
    """
    Generate prompt for a text query (returns Midjourney prompt string)
    or for a product dictionary (returns dictionary of prompts).
    """
    if isinstance(query_or_product, str):
        dummy_product = {
            "id": "VC-GEN-001",
            "title": query_or_product,
            "description": f"Original 1980s Miami aesthetic inspired {query_or_product}",
        }
        return _default_generator.generate_midjourney(dummy_product)
    elif isinstance(query_or_product, dict):
        return generate_prompts_for_product(query_or_product)
    else:
        raise ValueError(f"Expected str or dict, got {type(query_or_product)}")

