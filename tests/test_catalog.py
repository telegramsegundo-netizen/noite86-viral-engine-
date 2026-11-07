"""
Comprehensive Test Suite for Vice City E-Commerce Catalog & Engines

Verifies schema conformance, high-margin economics (>65%), dual-currency pricing,
IP non-infringement scanner accuracy, Midjourney/Flux prompt generation, and SVG placeholders.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Dict

import jsonschema
import pytest

from catalog import (
    IPFilter,
    PromptGenerator,
    get_product_by_id,
    get_products,
    load_catalog,
    load_schema,
    sanitize_text,
    scan_catalog,
    scan_product,
    scan_text,
    validate_catalog,
)


@pytest.fixture
def catalog_data() -> Dict[str, Any]:
    """Fixture providing loaded catalog data."""
    return load_catalog()


@pytest.fixture
def products(catalog_data: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Fixture providing list of products."""
    return catalog_data["products"]


@pytest.fixture
def catalog_schema() -> Dict[str, Any]:
    """Fixture providing catalog JSON Schema Draft-07."""
    return load_schema()


@pytest.fixture
def ip_scanner() -> IPFilter:
    """Fixture providing IP filter instance."""
    return IPFilter()


@pytest.fixture
def prompt_gen() -> PromptGenerator:
    """Fixture providing prompt generator instance."""
    return PromptGenerator()


# -------------------------------------------------------------------------
# Test Group 1: Catalog Structure, Count, and Schema Conformance
# -------------------------------------------------------------------------

def test_catalog_loaded_and_product_count(products: list[Dict[str, Any]]) -> None:
    """Verify catalog loads and contains at least 10 products (specifically 12)."""
    assert len(products) >= 10, f"Expected at least 10 products, found {len(products)}"
    assert len(products) == 12, f"Expected 12 products in out-of-the-box catalog, found {len(products)}"


def test_unique_identifiers(products: list[Dict[str, Any]]) -> None:
    """Verify IDs, SKUs, and slugs are completely unique across all products."""
    ids = [p["id"] for p in products]
    skus = [p["sku"] for p in products]
    slugs = [p["slug"] for p in products]

    assert len(ids) == len(set(ids)), f"Duplicate product IDs detected: {ids}"
    assert len(skus) == len(set(skus)), f"Duplicate SKUs detected: {skus}"
    assert len(slugs) == len(set(slugs)), f"Duplicate slugs detected: {slugs}"


def test_catalog_schema_validation(catalog_data: Dict[str, Any]) -> None:
    """Verify master catalog strictly conforms to JSON Schema Draft-07."""
    assert validate_catalog(catalog_data) is True


def test_catalog_schema_rejection_on_invalid_data(catalog_data: Dict[str, Any], catalog_schema: Dict[str, Any]) -> None:
    """Verify schema rejects invalid data (e.g. missing fields, negative price)."""
    corrupt_data = copy.deepcopy(catalog_data)
    # Remove required title
    del corrupt_data["products"][0]["title"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=corrupt_data, schema=catalog_schema)

    # Negative price
    corrupt_data2 = copy.deepcopy(catalog_data)
    corrupt_data2["products"][0]["price_brl"] = -10.0
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=corrupt_data2, schema=catalog_schema)


# -------------------------------------------------------------------------
# Test Group 2: Financial Economics & High-Margin Verification
# -------------------------------------------------------------------------

def test_profit_margins_exceed_65_percent(products: list[Dict[str, Any]]) -> None:
    """Verify that every single catalog product achieves a profit margin > 65%."""
    for product in products:
        margin = product["margin_percent"]
        p_id = product["id"]
        title = product["title"]
        assert margin >= 65.0, f"Product {p_id} ('{title}') margin {margin}% is below 65.0%"
        # Also check nested pricing object
        assert product["pricing"]["gross_margin_percentage"] >= 65.0


def test_pricing_mathematical_consistency(products: list[Dict[str, Any]]) -> None:
    """Verify mathematical consistency between price, cost, and margin percent."""
    for product in products:
        price_brl = product["price_brl"]
        cost_brl = product["production_cost_brl"]
        declared_margin = product["margin_percent"]

        # Calculate expected margin: ((price - cost) / price) * 100
        calculated_margin = round(((price_brl - cost_brl) / price_brl) * 100, 2)
        assert abs(declared_margin - calculated_margin) < 0.2, (
            f"Product {product['id']} margin mismatch: declared {declared_margin}%, "
            f"calculated {calculated_margin}%"
        )

        # Check positive pricing in both currencies
        assert price_brl > 0
        assert product["price_usd"] > 0
        assert cost_brl > 0
        assert product["pricing"]["cost_estimate_usd"] > 0

        # Price must be strictly greater than production cost
        assert price_brl > cost_brl
        assert product["price_usd"] > product["pricing"]["cost_estimate_usd"]


def test_target_margin_distribution(products: list[Dict[str, Any]]) -> None:
    """Verify margin distribution spans between 67% and 87% as specified in survey."""
    margins = [p["margin_percent"] for p in products]
    min_margin = min(margins)
    max_margin = max(margins)

    assert min_margin >= 67.0, f"Minimum margin {min_margin}% is below expected 67.0%"
    assert max_margin <= 87.0, f"Maximum margin {max_margin}% exceeds expected 87.0%"


# -------------------------------------------------------------------------
# Test Group 3: Product Attributes, Categories, and Fulfillment
# -------------------------------------------------------------------------

def test_category_and_fulfillment_coverage(products: list[Dict[str, Any]]) -> None:
    """Verify diverse category coverage and fulfillment metadata."""
    categories = {p["category"] for p in products}
    # Should cover multiple diverse categories
    assert len(categories) >= 4, f"Expected at least 4 distinct categories, got {categories}"

    for product in products:
        ff = product["fulfillment"]
        assert "method" in ff and len(ff["method"]) > 0
        assert ff["lead_time_days"] >= 1
        assert len(ff["recommended_suppliers_br"]) >= 1
        assert len(ff["recommended_suppliers_global"]) >= 1


def test_svg_image_placeholders(products: list[Dict[str, Any]]) -> None:
    """Verify every product includes a valid, renderable SVG placeholder data URI."""
    for product in products:
        img = product["image_placeholder"]
        assert img.startswith("data:image/svg+xml"), f"Invalid SVG image format in {product['id']}"
        assert "<svg" in img and "</svg>" in img


def test_get_product_by_id_helper(catalog_data: Dict[str, Any]) -> None:
    """Verify helper retrieval by ID, SKU, and case insensitivity."""
    p1 = get_product_by_id("VC-APP-001", catalog_data)
    assert p1 is not None
    assert p1["sku"] == "VC-APP-001"

    # Lowercase lookup
    p2 = get_product_by_id("vc-app-001", catalog_data)
    assert p2 is not None
    assert p2["id"] == "VC-APP-001"

    # Non-existent
    assert get_product_by_id("NON-EXISTENT", catalog_data) is None


# -------------------------------------------------------------------------
# Test Group 4: IP Non-Infringement Scanner & Legal Boundaries Engine
# -------------------------------------------------------------------------

def test_ip_filter_detects_prohibited_terms(ip_scanner: IPFilter) -> None:
    """Verify IPFilter catches all Take-Two and Rockstar proprietary marks."""
    infringing_samples = [
        ("Check out this official Grand Theft Auto shirt!", "grand theft auto"),
        ("New GTA 6 merchandise drop coming soon", "gta 6"),
        ("Powered by Rockstar Games technology", "rockstar games"),
        ("Take-Two Interactive holds the trademark", "take-two"),
        ("Play as Lucia and Jason in Vice City", "lucia"),
        ("Tommy Vercetti bowling shirt replica", "tommy vercetti"),
        ("Visit the Ammu-Nation store downtown", "ammu-nation"),
        ("Drink some cold Sprunk soda", "sprunk"),
        ("Explore the state of Leonida", "leonida"),
    ]

    for text, expected_term in infringing_samples:
        result = ip_scanner.scan_text(text)
        assert result.is_clean is False, f"Failed to detect infringement in: '{text}'"
        assert any(expected_term in term.lower() for term in result.flagged_terms), (
            f"Expected '{expected_term}' in flagged terms {result.flagged_terms}"
        )


def test_ip_filter_punctuation_and_casing_variations(ip_scanner: IPFilter) -> None:
    """Verify IPFilter detects variations with punctuation, dashes, and casing."""
    variations = [
        "g.t.a. vice edition",
        "gta_vi merchandise",
        "GTA-6 drop",
        "ROCKSTAR GAMES",
        "Take Two Interactive",
        "AmmuNation ammo",
    ]

    for var in variations:
        result = ip_scanner.scan_text(var)
        assert result.is_clean is False, f"Expected variation '{var}' to be flagged"


def test_ip_filter_approves_lawful_retro_aesthetic(ip_scanner: IPFilter) -> None:
    """Verify lawful 80s/90s Florida retro synthwave text passes without false alarms."""
    lawful_samples = [
        "Vice Sunset Silk-Touch Camp Collar Bowling Shirt",
        "Neon Mirage Reversible Holographic Bomber Jacket with art deco palms",
        "Miami Overdrive '84 Heavyweight Oversized Tee with 1984 wedge car",
        "Ocean Drive Nocturne laser-etched acrylic desk lamp with bioluminescent cyan glow",
        "South Beach Syndicate corduroy snapback in seafoam turquoise",
        "Pelican Bay Motel authentic diamond rhombus keytag",
        "Biscayne Bay sunset with flamingos and synthwave horizon",
        "Digital guitar with starry aesthetics",  # Contains substrings 'gta', 'star' but shouldn't trigger
    ]

    for text in lawful_samples:
        result = ip_scanner.scan_text(text)
        assert result.is_clean is True, f"False positive triggered for lawful text: '{text}'. Flagged: {result.flagged_terms}"


def test_ip_filter_sanitization(ip_scanner: IPFilter) -> None:
    """Verify sanitize_text replaces prohibited trademarks with safe retro homages."""
    dirty_text = "Get your GTA 6 style hoodie from Rockstar Games featuring Lucia!"
    sanitized = ip_scanner.sanitize_text(dirty_text)

    # Check that original trademarks are removed
    assert "GTA 6" not in sanitized
    assert "Rockstar Games" not in sanitized
    assert "Lucia" not in sanitized

    # Check that replacement is clean
    res = ip_scanner.scan_text(sanitized)
    assert res.is_clean is True, f"Sanitized text still flagged: '{sanitized}'"


def test_catalog_100_percent_ip_cleared(catalog_data: Dict[str, Any]) -> None:
    """Verify that every field in the master catalog is 100% cleared of trademarks."""
    all_clean, results = scan_catalog(catalog_data)
    failed_items = {pid: [v.term for v in r.violations] for pid, r in results.items() if not r.is_clean}
    assert all_clean is True, f"Trademark violations found in catalog: {failed_items}"


# -------------------------------------------------------------------------
# Test Group 5: Generative AI Prompt Generator
# -------------------------------------------------------------------------

def test_prompt_generator_midjourney(prompt_gen: PromptGenerator, products: list[Dict[str, Any]]) -> None:
    """Verify Midjourney prompt generation parameterizes optics, lighting, and flags."""
    sample_product = products[0]
    mj_prompt = prompt_gen.generate_midjourney(
        product=sample_product,
        optics="vintage_film_lookbook",
        lighting="golden_hour_sunset",
        aspect_ratio="3:4",
    )

    assert "--v 6.1" in mj_prompt
    assert "--ar" in mj_prompt
    assert "--style raw" in mj_prompt
    # Must be IP clean
    assert scan_text(mj_prompt).is_clean is True


def test_prompt_generator_flux(prompt_gen: PromptGenerator, products: list[Dict[str, Any]]) -> None:
    """Verify Flux.1 Pro prompt generation includes 300 DPI vectors and textures."""
    sample_product = products[2]  # Miami Overdrive Tee
    flux_prompt = prompt_gen.generate_flux(
        product=sample_product,
        lighting="neon_noir_bicolor",
        environment="wet_asphalt_drive",
    )

    assert "300 DPI" in flux_prompt
    assert len(flux_prompt) > 30
    # Must be IP clean
    assert scan_text(flux_prompt).is_clean is True


def test_prompt_generator_negative_prompts(prompt_gen: PromptGenerator) -> None:
    """Verify negative prompts prevent low-quality artifacts and deformities."""
    neg = prompt_gen.generate_negative()
    assert "watermark" in neg
    assert "trademark" in neg
    assert "low quality" in neg

    neg_extra = prompt_gen.generate_negative(extra_negatives=["oversaturated green", "glitch"])
    assert "oversaturated green" in neg_extra
    assert "glitch" in neg_extra


def test_build_specification_for_all_products(prompt_gen: PromptGenerator, products: list[Dict[str, Any]]) -> None:
    """Verify prompt specification generation across all 12 catalog products."""
    for product in products:
        spec = prompt_gen.build_specification(product)
        assert spec.product_id == product["id"]
        assert len(spec.midjourney_prompt) > 20
        assert len(spec.flux_prompt) > 20
        assert len(spec.negative_prompt) > 10
        assert spec.aspect_ratio in ["1:1", "16:9", "3:4", "4:5", "9:16"]
        assert len(spec.print_texture_notes) > 5

        # Check dictionary conversion
        d = spec.to_dict()
        assert d["product_id"] == product["id"]
        assert d["midjourney_prompt"] == spec.midjourney_prompt


def test_ip_filter_aesthetic_alignment(ip_scanner: IPFilter) -> None:
    """Verify aesthetic token validator recognizes authentic 80s/90s Miami tropes."""
    strong_text = "Vibrant synthwave sunset with neon cyan palm trees along Ocean Drive in Biscayne"
    res = ip_scanner.verify_aesthetic_alignment(strong_text)
    assert res["is_aligned"] is True
    assert res["alignment_score"] >= 3
    assert "synthwave" in res["matched_keywords"]
    assert "neon" in res["matched_keywords"]

    weak_text = "A simple plain cotton item"
    res_weak = ip_scanner.verify_aesthetic_alignment(weak_text)
    assert res_weak["is_aligned"] is False


def test_prompt_generator_convenience_helper(products: list[Dict[str, Any]]) -> None:
    """Verify generate_prompts_for_product functional helper."""
    from catalog.prompt_generator import generate_prompts_for_product
    res = generate_prompts_for_product(products[0])
    assert "midjourney_prompt" in res
    assert "flux_prompt" in res
    assert "negative_prompt" in res
    assert res["product_id"] == products[0]["id"]


def test_custom_extra_banned_terms() -> None:
    """Verify IPFilter can be instantiated with custom prohibited terms."""
    custom_filter = IPFilter(extra_banned_terms=["custom_unlawful_brand", "fake_trademark"])
    res = custom_filter.scan_text("Check this custom_unlawful_brand today")
    assert res.is_clean is False
    assert "custom_unlawful_brand" in res.flagged_terms

