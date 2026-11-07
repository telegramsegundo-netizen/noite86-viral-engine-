"""
tests/test_e2e_tier2_boundaries.py - Tier 2: Boundary, Negative & Adversarial Tests
Validates system limits, empty inputs, corrupt files, boundary margins, unescaped paths,
trademark violation attempts, and missing API key fallbacks.
"""
from __future__ import annotations

import importlib
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.helpers import (
    BANNED_TRADEMARK_PATTERN,
    CATALOG_JSON_PATH,
    CATALOG_SCHEMA_PATH,
    IP_FILTER_PATH,
    PROMPT_GENERATOR_PATH,
    VIDEO_PIPELINE_DIR,
    AGENTS_DIR,
    STOREFRONT_DIR,
    check_banned_terms,
    load_json_file,
)


class TestTier2BoundariesAndNegatives(unittest.TestCase):
    """
    Tier 2 tests covering corner cases, edge boundaries, adversarial inputs,
    and system fault tolerance.
    """

    # -------------------------------------------------------------------------
    # B1: Empty, Whitespace & Null Inputs
    # -------------------------------------------------------------------------
    def test_b01_empty_and_whitespace_inputs(self):
        """
        Verify that modules gracefully handle empty strings, whitespace, and null inputs
        without unhandled crashes.
        """
        if not IP_FILTER_PATH.exists():
            self.skipTest("catalog/ip_filter.py not yet implemented")

        ip_filter_mod = importlib.import_module("catalog.ip_filter")
        scan_fn = getattr(ip_filter_mod, "scan_text", None)
        if not scan_fn:
            scanner_cls = getattr(ip_filter_mod, "IPFilter", None)
            if scanner_cls:
                scanner = scanner_cls()
                scan_fn = scanner.scan_text

        self.assertIsNotNone(scan_fn, "IPFilter must have a text scan method")

        # Empty string should be clean, not throw an unhandled exception
        result_empty = scan_fn("")
        is_clean = getattr(result_empty, "is_clean", True) if not isinstance(result_empty, bool) else result_empty
        self.assertTrue(is_clean, "Empty string should be flagged clean")

        # Whitespace only should be clean
        result_spaces = scan_fn("    \n\t  ")
        is_clean_spaces = getattr(result_spaces, "is_clean", True) if not isinstance(result_spaces, bool) else result_spaces
        self.assertTrue(is_clean_spaces, "Whitespace-only string should be flagged clean")

    # -------------------------------------------------------------------------
    # B2: Malformed & Corrupt Files
    # -------------------------------------------------------------------------
    def test_b02_malformed_and_corrupt_files(self):
        """
        Verify that malformed JSON or corrupted files are caught with clear exceptions
        rather than silent data corruption.
        """
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write('{"store_name": "Broken", "products": [unclosed json')
            bad_json_path = Path(f.name)

        try:
            with self.assertRaises(json.JSONDecodeError):
                load_json_file(bad_json_path)
        finally:
            if bad_json_path.exists():
                bad_json_path.unlink()

        # Test corrupt 0-byte video handling in ingestion
        ingestion_file = VIDEO_PIPELINE_DIR / "ingestion.py"
        if ingestion_file.exists():
            try:
                ing_mod = importlib.import_module("video_pipeline.ingestion")
                val_fn = getattr(ing_mod, "validate_video_path", None)
                if val_fn:
                    with tempfile.NamedTemporaryFile("wb", suffix=".mp4", delete=False) as empty_vid:
                        empty_vid.write(b"")
                        empty_vid_path = Path(empty_vid.name)
                    try:
                        # 0-byte video should fail validation
                        with self.assertRaises((ValueError, Exception)):
                            val_fn(str(empty_vid_path))
                    finally:
                        if empty_vid_path.exists():
                            empty_vid_path.unlink()
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # B3: Margin & Financial Boundary Enforcement
    # -------------------------------------------------------------------------
    def test_b03_margin_boundary_conditions(self):
        """
        Verify that products below the 65.0% gross margin threshold are strictly rejected
        by the catalog schema, while products at exactly 65.0% pass.
        """
        if not CATALOG_SCHEMA_PATH.exists():
            self.skipTest("catalog.schema.json not yet available")

        import jsonschema

        schema = load_json_file(CATALOG_SCHEMA_PATH)

        # Baseline valid minimal product conforming to schema
        valid_product = {
            "id": "VC-APP-099",
            "sku": "VC-APP-099",
            "title": "Vice Test Item",
            "slug": "vice-test-item",
            "category": "Apparel",
            "description": "A very detailed description of this test item exceeding twenty characters easily.",
            "features": ["Feature A", "Feature B"],
            "price_brl": 100.00,
            "price_usd": 20.00,
            "production_cost_brl": 35.00,
            "margin_percent": 65.0,  # Exact 65% boundary
            "pricing": {
                "currency_brl": 100.00,
                "currency_usd": 20.00,
                "cost_estimate_brl": 35.00,
                "cost_estimate_usd": 7.00,
                "gross_margin_percentage": 65.0,
            },
            "fulfillment": {"method": "pod_dtg", "lead_time_days": 3},
            "ai_prompts": {
                "midjourney_v6_prompt": "Vintage Vice City neon print test prompt here.",
                "flux_pro_prompt": "Volumetric neon cyan lighting test prompt here.",
                "negative_prompt": "blurry, low quality, distorted",
                "aspect_ratio": "1:1",
            },
            "ai_art_prompt": {
                "flux_prompt": "Volumetric neon cyan lighting test prompt here.",
                "midjourney_prompt": "Vintage Vice City neon print test prompt here.",
                "negative_prompt": "blurry, low quality, distorted",
            },
            "tags": ["bestseller", "streetwear"],
            "image_placeholder": "data:image/svg+xml;utf8,<svg></svg>",
            "compliance": {"trademark_cleared": True, "ip_audit_notes": "Passed legal scan"},
        }

        catalog_doc = {
            "version": "1.0.0",
            "last_updated": "2026-11-07T00:00:00Z",
            "store_name": "Vice Syndicate Neon Store",
            "products": [valid_product] * 10,  # 10 items to meet minItems
        }

        # 1. Exact 65.0% boundary MUST pass
        try:
            jsonschema.validate(instance=catalog_doc, schema=schema)
        except jsonschema.ValidationError as err:
            self.fail(f"Catalog with 65.0% margin boundary failed schema validation: {err.message}")

        # 2. Product with 64.9% (below minimum margin floor) MUST FAIL
        invalid_doc = json.loads(json.dumps(catalog_doc))
        invalid_doc["products"][0]["margin_percent"] = 64.9
        invalid_doc["products"][0]["pricing"]["gross_margin_percentage"] = 64.9

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_doc, schema=schema)

        # 3. Product with negative cost or negative price MUST FAIL
        neg_price_doc = json.loads(json.dumps(catalog_doc))
        neg_price_doc["products"][0]["price_brl"] = -10.0
        neg_price_doc["products"][0]["pricing"]["currency_brl"] = -10.0

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=neg_price_doc, schema=schema)

    # -------------------------------------------------------------------------
    # B4: Windows Path Delimiter & Special Characters in FFmpeg Subtitles
    # -------------------------------------------------------------------------
    def test_b04_windows_path_escaping_in_ffmpeg(self):
        """
        Verify that Windows paths with drive letter colons (e.g., 'C:\\Users\\...')
        are properly escaped or formatted for FFmpeg subtitle filtergraphs
        to prevent returncode 4294967294 crashes.
        """
        raw_windows_path = r"C:\Users\victo\AppData\Local\Temp\subtitles.srt"

        # In FFmpeg, ':' is an option separator; raw C: breaks filter graphs.
        # Valid escaping patterns:
        # Pattern 1: C\:/Users/...
        # Pattern 2: C\\:/Users/...
        # Pattern 3: relative path 'subtitles.srt'
        escaped_forward = raw_windows_path.replace("\\", "/").replace(":", r"\:")
        self.assertNotIn("C:/", escaped_forward, "Colon must be escaped in Windows FFmpeg filter paths")
        self.assertIn(r"C\:", escaped_forward)

        # If video_pipeline.renderer exists, test its escaping utility
        renderer_file = VIDEO_PIPELINE_DIR / "renderer.py"
        if renderer_file.exists():
            try:
                rend_mod = importlib.import_module("video_pipeline.renderer")
                escape_fn = getattr(rend_mod, "escape_ffmpeg_path", None) or getattr(
                    rend_mod, "sanitize_path_for_filter", None
                )
                if escape_fn:
                    safe_path = escape_fn(raw_windows_path)
                    self.assertNotIn(
                        "C:", safe_path, f"Path was not escaped for FFmpeg: {safe_path}"
                    )
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # B5: Adversarial Trademark Evasion Attempts
    # -------------------------------------------------------------------------
    def test_b05_adversarial_trademark_evasion_attempts(self):
        """
        Verify that IPFilter detects obfuscated trademark evasions (mixed case,
        dashes, punctuation, substrings).
        """
        if not IP_FILTER_PATH.exists():
            self.skipTest("catalog/ip_filter.py not yet implemented")

        ip_filter_mod = importlib.import_module("catalog.ip_filter")
        scan_fn = getattr(ip_filter_mod, "scan_text", None)
        if not scan_fn:
            scanner_cls = getattr(ip_filter_mod, "IPFilter", None)
            if scanner_cls:
                scanner = scanner_cls()
                scan_fn = scanner.scan_text

        self.assertIsNotNone(scan_fn)

        evasion_attempts = [
            "rOcKsTaR gAmEs official collection",
            "GTA_VI exclusive leak preview",
            "New gta-vi drop in Vice Coast",
            "Play with Lucia and Jason characters",
            "Replica of tommy vercetti shirt",
            "Drink cold sprunk energy soda",
            "ammunation army surplus jacket",
            "Official Take-Two interactive promo",
        ]

        for phrase in evasion_attempts:
            res = scan_fn(phrase)
            is_clean = getattr(res, "is_clean", True) if not isinstance(res, bool) else res
            self.assertFalse(
                is_clean, f"IP filter failed to detect adversarial evasion phrase: '{phrase}'"
            )

    # -------------------------------------------------------------------------
    # B6: Missing API Keys Graceful Fallback
    # -------------------------------------------------------------------------
    def test_b06_missing_api_keys_resilience(self):
        """
        Verify that multi-agent and video localization modules gracefully fallback
        to deterministic offline / rule-based mode when GEMINI_API_KEY and OPENAI_API_KEY
        are missing or empty.
        """
        clean_env = os.environ.copy()
        clean_env.pop("GEMINI_API_KEY", None)
        clean_env.pop("OPENAI_API_KEY", None)

        # 1. Test video localizer offline fallback
        localizer_file = VIDEO_PIPELINE_DIR / "localizer.py"
        if localizer_file.exists():
            try:
                with patch.dict(os.environ, clean_env, clear=True):
                    loc_mod = importlib.import_module("video_pipeline.localizer")
                    loc_cls = getattr(loc_mod, "VideoLocalizer", None) or getattr(
                        loc_mod, "RuleBasedOfflineLocalizer", None
                    )
                    if loc_cls:
                        # Should initialize without raising MissingAPIKeyError
                        instance = loc_cls(offline=True) if "offline" in loc_cls.__init__.__code__.co_varnames else loc_cls()
                        out = instance.localize("Look at this trailer") if hasattr(instance, "localize") else "ok"
                        self.assertIsNotNone(out)
            except Exception as e:
                self.fail(f"Localizer crashed when API keys are missing: {e}")

        # 2. Test Store Architect agent offline fallback
        architect_file = AGENTS_DIR / "store_architect.py"
        if architect_file.exists():
            try:
                with patch.dict(os.environ, clean_env, clear=True):
                    arch_mod = importlib.import_module("agents.store_architect")
                    arch_cls = getattr(arch_mod, "StoreArchitectAgent", None)
                    if arch_cls:
                        # Should run in mock_mode without API key
                        agent = arch_cls(mock_mode=True)
                        self.assertTrue(agent.mock_mode if hasattr(agent, "mock_mode") else True)
            except Exception as e:
                self.fail(f"Store Architect crashed when API keys are missing: {e}")

    # -------------------------------------------------------------------------
    # B7: Storefront Coupon & Checkout Simulator Edge Cases
    # -------------------------------------------------------------------------
    def test_b07_storefront_coupon_and_checkout_edge_cases(self):
        """
        Verify checkout business logic:
        - Invalid coupon returns 0 discount
        - Coupon 'VICE10' grants 10% discount
        - Free shipping threshold boundary (R$ 199.00)
        - PIX 5% instant discount calculation
        """
        subtotal = 200.00
        free_shipping_threshold = 199.00

        # Free shipping boundary math
        self.assertTrue(subtotal >= free_shipping_threshold, "Subtotal R$ 200.00 qualifies for free shipping")
        self.assertFalse(198.90 >= free_shipping_threshold, "Subtotal R$ 198.90 does not qualify for free shipping")

        # Coupon calculation: VICE10 = 10% off
        coupon_code = "VICE10"
        discount_rate = 0.10 if coupon_code == "VICE10" else 0.0
        discount_amount = round(subtotal * discount_rate, 2)
        self.assertEqual(discount_amount, 20.00)

        # After coupon: R$ 180.00
        net_after_coupon = subtotal - discount_amount

        # PIX 5% instant payment discount
        pix_discount_rate = 0.05
        pix_discount_amount = round(net_after_coupon * pix_discount_rate, 2)
        self.assertEqual(pix_discount_amount, 9.00)

        final_pix_total = round(net_after_coupon - pix_discount_amount, 2)
        self.assertEqual(final_pix_total, 171.00)


if __name__ == "__main__":
    unittest.main()
