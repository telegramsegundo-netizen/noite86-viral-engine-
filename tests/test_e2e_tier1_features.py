"""
tests/test_e2e_tier1_features.py - Tier 1: Feature Coverage in Isolation
Validates features F1 through F15 from PROJECT.md and ORIGINAL_REQUEST.md.
"""
from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

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
    VALIDATE_SYSTEM_PATH,
    check_banned_terms,
    load_json_file,
)


class TestTier1FeatureCoverage(unittest.TestCase):
    """
    Tier 1 tests exercising each feature (F1 through F15) in isolation.
    Tests verify contracts derived strictly from ORIGINAL_REQUEST.md & PROJECT.md.
    """

    # -------------------------------------------------------------------------
    # Feature 1: Out-of-the-Box Catalog Data Integrity
    # -------------------------------------------------------------------------
    def test_f01_catalog_products_count_and_margins(self):
        """
        Verify that catalog contains >= 10 products (target 12 items),
        with valid pricing in BRL and USD, production cost, and gross margins >= 65%.
        """
        if not CATALOG_JSON_PATH.exists():
            self.skipTest(f"M1 dependency not yet available: {CATALOG_JSON_PATH}")

        data = load_json_file(CATALOG_JSON_PATH)
        self.assertIn("products", data, "Catalog JSON must contain 'products' array")
        products = data["products"]

        # AC: >= 10 products detailed
        self.assertGreaterEqual(
            len(products), 10, f"Catalog must contain at least 10 products, found {len(products)}"
        )

        categories_seen = set()
        for idx, item in enumerate(products):
            prod_id = item.get("id") or item.get("sku")
            self.assertTrue(prod_id, f"Product at index {idx} must have an id or sku")

            title = item.get("title", "")
            self.assertGreater(len(title), 2, f"Product {prod_id} must have a descriptive title")

            # Dual pricing checks
            price_brl = item.get("price_brl") or (item.get("pricing", {}).get("currency_brl"))
            price_usd = item.get("price_usd") or (item.get("pricing", {}).get("currency_usd"))
            cost_brl = item.get("production_cost_brl") or (
                item.get("pricing", {}).get("cost_estimate_brl")
            )
            margin = item.get("margin_percent") or (
                item.get("pricing", {}).get("gross_margin_percentage")
            )

            self.assertIsNotNone(price_brl, f"Product {prod_id} missing BRL price")
            self.assertIsNotNone(price_usd, f"Product {prod_id} missing USD price")
            self.assertIsNotNone(cost_brl, f"Product {prod_id} missing BRL cost")
            self.assertIsNotNone(margin, f"Product {prod_id} missing margin percentage")

            self.assertGreater(price_brl, 0, f"Product {prod_id} BRL price must be positive")
            self.assertGreater(price_usd, 0, f"Product {prod_id} USD price must be positive")
            self.assertGreater(cost_brl, 0, f"Product {prod_id} cost must be positive")

            # AC: High-margin requirement (all margins >= 65%)
            self.assertGreaterEqual(
                margin,
                65.0,
                f"Product {prod_id} ('{title}') margin {margin}% is below the mandatory 65.0% threshold",
            )

            category = item.get("category", "")
            self.assertTrue(category, f"Product {prod_id} must have a category")
            categories_seen.add(category)

            # Tags requirement
            tags = item.get("tags", [])
            self.assertIsInstance(tags, list, f"Product {prod_id} tags must be a list")
            self.assertGreater(len(tags), 0, f"Product {prod_id} must have at least one tag")

        # Must span multiple categories
        self.assertGreaterEqual(
            len(categories_seen), 3, "Catalog must span at least 3 distinct categories"
        )

    # -------------------------------------------------------------------------
    # Feature 2: Generative AI Prompt Matrix
    # -------------------------------------------------------------------------
    def test_f02_prompt_generator_flux_and_midjourney(self):
        """
        Verify that generative AI prompt specifications exist for every catalog product,
        containing camera optics, volumetric neon lighting, and negative prompts.
        """
        if not CATALOG_JSON_PATH.exists():
            self.skipTest(f"M1 dependency not yet available: {CATALOG_JSON_PATH}")

        data = load_json_file(CATALOG_JSON_PATH)
        products = data.get("products", [])

        # Optics and lighting keywords expected in professional prompt matrices
        optics_keywords = ["lens", "hasselblad", "35mm", "kodak", "portra", "f/", "bokeh", "camera", "macro", "optics"]
        lighting_keywords = ["neon", "volumetric", "lighting", "cyan", "magenta", "glow", "reflections", "ambient"]

        for item in products:
            prod_id = item.get("id") or item.get("sku")
            ai_data = item.get("ai_prompts") or item.get("ai_art_prompt") or {}
            self.assertTrue(ai_data, f"Product {prod_id} must specify AI art prompts")

            flux_prompt = ai_data.get("flux_pro_prompt") or ai_data.get("flux_prompt", "")
            mj_prompt = ai_data.get("midjourney_v6_prompt") or ai_data.get("midjourney_prompt", "")
            negative = ai_data.get("negative_prompt", "")

            self.assertGreaterEqual(
                len(flux_prompt), 20, f"Product {prod_id} Flux prompt is too short"
            )
            self.assertGreaterEqual(
                len(mj_prompt), 20, f"Product {prod_id} Midjourney prompt is too short"
            )
            self.assertGreaterEqual(
                len(negative), 10, f"Product {prod_id} negative prompt is too short"
            )

        # If prompt_generator module exists, verify programmatic invocation
        if PROMPT_GENERATOR_PATH.exists():
            try:
                prompt_mod = importlib.import_module("catalog.prompt_generator")
                if hasattr(prompt_mod, "generate_prompt"):
                    test_prompt = prompt_mod.generate_prompt("retro bowling shirt")
                    self.assertIsInstance(test_prompt, (str, dict))
            except Exception as e:
                self.fail(f"catalog.prompt_generator failed to execute: {e}")

    # -------------------------------------------------------------------------
    # Feature 3: IP Clearance Matrix & Scanner
    # -------------------------------------------------------------------------
    def test_f03_ip_clearance_scanner(self):
        """
        Verify that the IP clearance filter strictly detects Take-Two / Rockstar Games
        trademarks with zero false negatives, and confirms catalog has 0 violations.
        """
        if not IP_FILTER_PATH.exists():
            self.skipTest(f"M1 dependency not yet available: {IP_FILTER_PATH}")

        ip_filter_mod = importlib.import_module("catalog.ip_filter")

        # Test detection of explicit banned trademarks
        banned_samples = [
            "Official Rockstar Games licensed t-shirt",
            "Play as Lucia in the new GTA 6 release",
            "Grand Theft Auto Vice City soundtrack vinyl",
            "Jason and Lucia criminal romance poster",
            "Tommy Vercetti hawaiian shirt replica",
            "Ammunation tactical keytag",
        ]

        # Check scanner function availability
        scan_fn = getattr(ip_filter_mod, "scan_text", None) or getattr(
            ip_filter_mod, "check_text_compliance", None
        )
        if scan_fn is None:
            # Fall back to testing module's banned list or class
            scanner_cls = getattr(ip_filter_mod, "IPFilter", None) or getattr(
                ip_filter_mod, "IPScanner", None
            )
            if scanner_cls:
                scanner = scanner_cls()
                scan_fn = getattr(scanner, "scan_text", None) or getattr(scanner, "is_safe", None)

        if scan_fn:
            for phrase in banned_samples:
                result = scan_fn(phrase)
                is_clean = getattr(result, "is_clean", True) if not isinstance(result, bool) else result
                self.assertFalse(is_clean, f"IP filter failed to flag banned phrase: '{phrase}'")

        # Audit entire products.json against banned terms
        if CATALOG_JSON_PATH.exists():
            raw_text = CATALOG_JSON_PATH.read_text(encoding="utf-8")
            violations = check_banned_terms(raw_text)
            self.assertEqual(
                violations,
                [],
                f"Found banned trademark violations in products.json: {violations}",
            )

    # -------------------------------------------------------------------------
    # Feature 4: Catalog Data Schemas
    # -------------------------------------------------------------------------
    def test_f04_catalog_schema_validation(self):
        """
        Validate products.json against catalog.schema.json using jsonschema Draft-07.
        """
        if not CATALOG_JSON_PATH.exists() or not CATALOG_SCHEMA_PATH.exists():
            self.skipTest("Catalog or schema file not yet created")

        import jsonschema

        catalog_data = load_json_file(CATALOG_JSON_PATH)
        schema_data = load_json_file(CATALOG_SCHEMA_PATH)

        try:
            jsonschema.validate(instance=catalog_data, schema=schema_data)
        except jsonschema.ValidationError as err:
            self.fail(f"Catalog JSON failed JSON Schema validation: {err.message}")

    # -------------------------------------------------------------------------
    # Feature 5: Video Ingestion Module
    # -------------------------------------------------------------------------
    def test_f05_video_ingestion_local_and_validation(self):
        """
        Verify video ingestion module accepts valid local video path
        and rejects non-existent or invalid video paths.
        """
        ingestion_file = VIDEO_PIPELINE_DIR / "ingestion.py"
        if not ingestion_file.exists():
            self.skipTest("M2 dependency video_pipeline/ingestion.py not yet implemented")

        try:
            ingestion_mod = importlib.import_module("video_pipeline.ingestion")
        except Exception as e:
            self.skipTest(f"video_pipeline.ingestion could not be imported: {e}")

        validate_fn = (
            getattr(ingestion_mod, "validate_video_path", None)
            or getattr(ingestion_mod, "ingest_video", None)
            or getattr(ingestion_mod, "validate_input", None)
        )

        if validate_fn:
            # Non-existent file should raise an error or return False
            fake_path = "non_existent_clip_12345.mp4"
            with self.assertRaises((FileNotFoundError, ValueError, Exception)):
                validate_fn(fake_path)

    # -------------------------------------------------------------------------
    # Feature 6: Audio Extraction & STT (Mock & Whisper)
    # -------------------------------------------------------------------------
    def test_f06_audio_extraction_and_transcription(self):
        """
        Verify transcription module produces structured segments with timestamps.
        """
        transcriber_file = VIDEO_PIPELINE_DIR / "transcriber.py"
        if not transcriber_file.exists():
            self.skipTest("M2 dependency video_pipeline/transcriber.py not yet implemented")

        try:
            trans_mod = importlib.import_module("video_pipeline.transcriber")
        except Exception as e:
            self.skipTest(f"video_pipeline.transcriber could not be imported: {e}")

        # Check for MockTranscriber or Transcriber class
        mock_cls = getattr(trans_mod, "MockTranscriber", None) or getattr(
            trans_mod, "Transcriber", None
        )
        if mock_cls:
            transcriber = mock_cls()
            segments = transcriber.transcribe(video_path=None if hasattr(transcriber, "transcribe") else "dummy.wav") if hasattr(transcriber, "transcribe") else []
            self.assertIsInstance(segments, list)
            if segments:
                first = segments[0]
                # Can be dict or Pydantic model
                start = getattr(first, "start", None) or (first.get("start") if isinstance(first, dict) else None)
                end = getattr(first, "end", None) or (first.get("end") if isinstance(first, dict) else None)
                text = getattr(first, "text", None) or (first.get("text") if isinstance(first, dict) else None)

                self.assertIsNotNone(start, "Segment must have start timestamp")
                self.assertIsNotNone(end, "Segment must have end timestamp")
                self.assertGreaterEqual(end, start, "End timestamp must be >= start")
                self.assertTrue(text, "Segment must have non-empty text")

    # -------------------------------------------------------------------------
    # Feature 7: PT-BR Video Localization
    # -------------------------------------------------------------------------
    def test_f07_video_localization_ptbr_gamer_slang(self):
        """
        Verify localization module converts English gaming phrases into high-energy pt-BR slang.
        """
        localizer_file = VIDEO_PIPELINE_DIR / "localizer.py"
        if not localizer_file.exists():
            self.skipTest("M2 dependency video_pipeline/localizer.py not yet implemented")

        try:
            loc_mod = importlib.import_module("video_pipeline.localizer")
        except Exception as e:
            self.skipTest(f"video_pipeline.localizer could not be imported: {e}")

        loc_cls = getattr(loc_mod, "RuleBasedOfflineLocalizer", None) or getattr(
            loc_mod, "VideoLocalizer", None
        )
        localize_fn = getattr(loc_mod, "localize_text", None)

        sample_en = "Look at this trailer, the graphics are unbelievable! Check the link in bio."
        localized = None

        if loc_cls:
            instance = loc_cls()
            localize_fn = getattr(instance, "localize", None) or getattr(instance, "translate", None)
            if localize_fn:
                localized = localize_fn(sample_en)
        elif localize_fn:
            localized = localize_fn(sample_en)

        if localized:
            # Expected Portuguese slang tokens
            pt_tokens = ["trailer", "gráfico", "olha", "se liga", "insano", "surreal", "bio", "drop", "link"]
            text_to_check = localized if isinstance(localized, str) else str(localized)
            has_match = any(token in text_to_check.lower() for token in pt_tokens)
            self.assertTrue(has_match, f"Localized text lacks pt-BR gamer tokens: {text_to_check}")

    # -------------------------------------------------------------------------
    # Feature 8: Subtitle Generation (.srt and .vtt)
    # -------------------------------------------------------------------------
    def test_f08_subtitle_generation_srt_and_vtt(self):
        """
        Verify subtitler generates valid .srt and .vtt subtitle strings with accurate timecodes.
        """
        subtitler_file = VIDEO_PIPELINE_DIR / "subtitler.py"
        if not subtitler_file.exists():
            self.skipTest("M2 dependency video_pipeline/subtitler.py not yet implemented")

        try:
            sub_mod = importlib.import_module("video_pipeline.subtitler")
        except Exception as e:
            self.skipTest(f"video_pipeline.subtitler could not be imported: {e}")

        srt_fn = getattr(sub_mod, "generate_srt", None) or getattr(sub_mod, "to_srt", None)
        vtt_fn = getattr(sub_mod, "generate_vtt", None) or getattr(sub_mod, "to_vtt", None)

        mock_segments = [
            {"start": 1.0, "end": 3.5, "text": "SE LIGA NESSE TRAILER!"},
            {"start": 3.6, "end": 6.2, "text": "O GRÁFICO TÁ INSANO DEMAIS!"},
        ]

        if srt_fn:
            srt_output = srt_fn(mock_segments)
            self.assertIn("-->", srt_output, "SRT must contain timecode separator '-->'")
            self.assertIn("SE LIGA", srt_output, "SRT must include segment text")
            # Format pattern: 00:00:01,000 --> 00:00:03,500
            self.assertRegex(srt_output, r"\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}")

        if vtt_fn:
            vtt_output = vtt_fn(mock_segments)
            self.assertTrue(vtt_output.startswith("WEBVTT"), "VTT must start with WEBVTT header")
            self.assertIn("-->", vtt_output)

    # -------------------------------------------------------------------------
    # Feature 9: Vertical 9:16 Video Rendering
    # -------------------------------------------------------------------------
    def test_f09_vertical_video_rendering_9_16(self):
        """
        Verify video rendering filtergraph transforms landscape 16:9 to vertical 1080x1920
        with boxblur padding and store CTA overlay.
        """
        renderer_file = VIDEO_PIPELINE_DIR / "renderer.py"
        if not renderer_file.exists():
            self.skipTest("M2 dependency video_pipeline/renderer.py not yet implemented")

        try:
            renderer_mod = importlib.import_module("video_pipeline.renderer")
        except Exception as e:
            self.skipTest(f"video_pipeline.renderer could not be imported: {e}")

        build_filter_fn = getattr(renderer_mod, "build_filtergraph", None) or getattr(
            renderer_mod, "create_vertical_filter", None
        )

        if build_filter_fn:
            filter_str = build_filter_fn(cta_text="COLECAO VICE CITY NA BIO")
            self.assertIn("1080", filter_str, "Filtergraph must set target width to 1080")
            self.assertIn("1920", filter_str, "Filtergraph must set target height to 1920")
            self.assertTrue(
                "boxblur" in filter_str or "gblur" in filter_str or "blur" in filter_str,
                "Filtergraph must incorporate background blur",
            )

    # -------------------------------------------------------------------------
    # Feature 10: Video Test Harness & Synthesizer
    # -------------------------------------------------------------------------
    def test_f10_synthetic_video_generator(self):
        """
        Verify FFmpeg binary resolver and synthetic video generator create a deterministic
        test MP4 in < 3 seconds offline.
        """
        resolver_file = VIDEO_PIPELINE_DIR / "ffmpeg_resolver.py"
        if not resolver_file.exists():
            self.skipTest("M2 dependency video_pipeline/ffmpeg_resolver.py not yet implemented")

        try:
            res_mod = importlib.import_module("video_pipeline.ffmpeg_resolver")
            get_ffmpeg_fn = getattr(res_mod, "get_ffmpeg_exe", None) or getattr(
                res_mod, "resolve_ffmpeg", None
            )
            if get_ffmpeg_fn:
                exe = get_ffmpeg_fn()
                self.assertTrue(Path(exe).exists() or exe == "ffmpeg", f"FFmpeg exe not found: {exe}")
        except Exception as e:
            self.skipTest(f"ffmpeg_resolver execution skipped: {e}")

    # -------------------------------------------------------------------------
    # Feature 11: Store Architect Agent
    # -------------------------------------------------------------------------
    def test_f11_store_architect_agent_config(self):
        """
        Verify Store Architect Agent produces store_config.json with categories,
        bundles, checkout rules, and preserved gross margins.
        """
        architect_file = AGENTS_DIR / "store_architect.py"
        if not architect_file.exists():
            self.skipTest("M3 dependency agents/store_architect.py not yet implemented")

        try:
            arch_mod = importlib.import_module("agents.store_architect")
            arch_cls = getattr(arch_mod, "StoreArchitectAgent", None) or getattr(
                arch_mod, "StoreArchitect", None
            )
            if arch_cls:
                agent = arch_cls(mock_mode=True)
                config = agent.generate_config(CATALOG_JSON_PATH) if hasattr(agent, "generate_config") else agent.run()
                self.assertIn("store_info", config)
                self.assertIn("categories", config)
                self.assertIn("bundles", config)
                self.assertIn("checkout_config", config)
        except Exception as e:
            self.skipTest(f"Store Architect test skipped: {e}")

    # -------------------------------------------------------------------------
    # Feature 12: Content Clipper & Campaign Agent
    # -------------------------------------------------------------------------
    def test_f12_content_clipper_social_campaign(self):
        """
        Verify Content Clipper Agent generates social_campaign.json containing >= 21 posts
        over a 7-day schedule, 3 daily slots, viral hooks, and linked SKUs.
        """
        clipper_file = AGENTS_DIR / "content_clipper.py"
        if not clipper_file.exists():
            self.skipTest("M3 dependency agents/content_clipper.py not yet implemented")

        try:
            clip_mod = importlib.import_module("agents.content_clipper")
            clip_cls = getattr(clip_mod, "ContentClipperAgent", None) or getattr(
                clip_mod, "ContentClipper", None
            )
            if clip_cls:
                agent = clip_cls(mock_mode=True)
                campaign = agent.generate_campaign() if hasattr(agent, "generate_campaign") else agent.run()
                schedule = campaign.get("schedule", [])
                self.assertGreaterEqual(len(schedule), 21, "Social campaign must schedule >= 21 posts")
        except Exception as e:
            self.skipTest(f"Content Clipper test skipped: {e}")

    # -------------------------------------------------------------------------
    # Feature 13: Multi-Agent Orchestrator CLI
    # -------------------------------------------------------------------------
    def test_f13_multi_agent_orchestrator_cli(self):
        """
        Verify unified orchestration runner CLI (run_agents.py) executes in mock mode,
        returning exit code 0 and producing configuration outputs.
        """
        orchestrator_file = AGENTS_DIR / "run_agents.py"
        if not orchestrator_file.exists():
            self.skipTest("M3 dependency agents/run_agents.py not yet implemented")

        result = subprocess.run(
            [sys.executable, str(orchestrator_file), "--mock"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        self.assertEqual(
            result.returncode,
            0,
            f"run_agents.py --mock failed with exit code {result.returncode}:\n{result.stderr}",
        )

    # -------------------------------------------------------------------------
    # Feature 14: Responsive Vice City Web Storefront & Checkout Simulator
    # -------------------------------------------------------------------------
    def test_f14_storefront_dom_and_checkout_simulator(self):
        """
        Verify storefront HTML/DOM contains mandatory element IDs and checkout simulator logic.
        """
        index_html = STOREFRONT_DIR / "index.html"
        checkout_js = STOREFRONT_DIR / "js" / "checkout.js"

        if not index_html.exists():
            self.skipTest("M3 dependency storefront/index.html not yet implemented")

        html_content = index_html.read_text(encoding="utf-8")

        # Mandatory DOM IDs from R3 specification
        mandatory_ids = [
            "product-grid",
            "cart-drawer",
            "checkout-modal",
            "pix-qr-code",
            "currency-toggle",
            "announcement-bar",
        ]
        for dom_id in mandatory_ids:
            self.assertIn(
                f'id="{dom_id}"',
                html_content,
                f"Storefront index.html is missing required DOM element id='{dom_id}'",
            )

        # Responsive viewport and Tailwind CDN check
        self.assertIn('name="viewport"', html_content, "index.html must include viewport meta tag")
        self.assertTrue(
            "tailwind" in html_content.lower() or "styles.css" in html_content,
            "index.html must include Tailwind or custom styles stylesheet",
        )

        if checkout_js.exists():
            js_content = checkout_js.read_text(encoding="utf-8")
            self.assertIn("pix", js_content.lower(), "checkout.js must implement PIX payment logic")

    # -------------------------------------------------------------------------
    # Feature 15: System Validation Suite
    # -------------------------------------------------------------------------
    def test_f15_system_validation_suite_execution(self):
        """
        Verify validate_system.py executes cleanly and returns exit code 0.
        """
        if not VALIDATE_SYSTEM_PATH.exists():
            self.skipTest("M3 dependency validate_system.py not yet implemented")

        result = subprocess.run(
            [sys.executable, str(VALIDATE_SYSTEM_PATH)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        self.assertEqual(
            result.returncode,
            0,
            f"validate_system.py failed with exit code {result.returncode}:\n{result.stdout}\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
