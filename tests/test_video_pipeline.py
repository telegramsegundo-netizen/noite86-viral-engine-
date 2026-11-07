"""
tests/test_video_pipeline.py
Comprehensive unit and integration test suite for the video_pipeline package.
Runs deterministically offline in <5 seconds using synthetic FFmpeg test media.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from video_pipeline.cli import process_video_pipeline
from video_pipeline.ffmpeg_resolver import (
    check_ffmpeg_filters,
    create_synthetic_video,
    get_ffmpeg_exe,
    resolve_ffmpeg,
)
from video_pipeline.ingestion import get_video_info, ingest_video, validate_video_path
from video_pipeline.localizer import (
    RuleBasedOfflineLocalizer,
    VideoLocalizer,
    localize_text,
)
from video_pipeline.renderer import (
    build_filtergraph,
    escape_ffmpeg_path,
    render_vertical_video,
)
from video_pipeline.subtitler import (
    export_subtitles,
    generate_ass,
    generate_srt,
    generate_vtt,
)
from video_pipeline.transcriber import (
    MockTranscriber,
    Transcriber,
    TranscriptSegment,
    WordTimestamp,
    extract_audio,
)


class TestVideoPipelineSuite(unittest.TestCase):
    """Test suite covering all video_pipeline components."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = Path(tempfile.mkdtemp(prefix="test_vp_"))
        # Create a shared short 1.0s synthetic video for tests
        cls.sample_video = cls.test_dir / "sample_testsrc.mp4"
        create_synthetic_video(cls.sample_video, duration=1.0, resolution="640x360", fps=24)

    @classmethod
    def tearDownClass(cls):
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. FFmpeg Resolver & Synthetic Video
    # -------------------------------------------------------------------------
    def test_01_ffmpeg_resolution_and_filters(self):
        exe = get_ffmpeg_exe()
        self.assertTrue(Path(exe).exists() or exe == "ffmpeg", f"FFmpeg not found: {exe}")
        self.assertEqual(resolve_ffmpeg(), exe)

        filters = check_ffmpeg_filters(["boxblur", "drawtext", "subtitles"])
        self.assertIn("boxblur", filters)
        self.assertIn("drawtext", filters)
        self.assertIn("subtitles", filters)

    def test_02_synthetic_video_properties(self):
        info = get_video_info(self.sample_video)
        self.assertTrue(info["has_video"])
        self.assertTrue(info["has_audio"])
        self.assertEqual(info["width"], 640)
        self.assertEqual(info["height"], 360)
        self.assertAlmostEqual(info["duration"], 1.0, delta=0.2)

    # -------------------------------------------------------------------------
    # 2. Ingestion & Validation
    # -------------------------------------------------------------------------
    def test_03_ingestion_valid_and_invalid(self):
        # Valid path
        valid_res = validate_video_path(self.sample_video)
        self.assertEqual(valid_res, self.sample_video.resolve())

        # Non-existent path
        with self.assertRaises(FileNotFoundError):
            validate_video_path(self.test_dir / "does_not_exist.mp4")

        # 0-byte path
        empty_file = self.test_dir / "empty.mp4"
        empty_file.write_bytes(b"")
        with self.assertRaises(ValueError):
            validate_video_path(empty_file)

        # Ingest mock video
        mock_out = ingest_video("mock", output_dir=self.test_dir, mock=True)
        self.assertTrue(mock_out.exists())
        self.assertGreater(mock_out.stat().st_size, 0)

    # -------------------------------------------------------------------------
    # 3. Transcriber & Audio Extraction
    # -------------------------------------------------------------------------
    def test_04_audio_extraction(self):
        wav_out = self.test_dir / "extracted_audio.wav"
        extract_audio(self.sample_video, wav_out)
        self.assertTrue(wav_out.exists())
        self.assertGreater(wav_out.stat().st_size, 1000)

    def test_05_mock_transcriber_segments(self):
        transcriber = MockTranscriber()
        segments = transcriber.transcribe()
        self.assertGreaterEqual(len(segments), 3)

        first = segments[0]
        self.assertIsInstance(first, TranscriptSegment)
        self.assertGreaterEqual(first.start, 0.0)
        self.assertGreater(first.end, first.start)
        self.assertTrue(first.text)
        self.assertGreater(len(first.words), 0)

        # Check dict-style access
        self.assertEqual(first["start"], first.start)
        self.assertEqual(first.get("text"), first.text)

        dict_repr = first.to_dict()
        self.assertIn("words", dict_repr)
        self.assertIn("start", dict_repr)

    # -------------------------------------------------------------------------
    # 4. Localizer & pt-BR Gaming Slang
    # -------------------------------------------------------------------------
    def test_06_rule_based_localizer_phrases(self):
        localizer = RuleBasedOfflineLocalizer()

        test_cases = [
            ("Look at this trailer, Vice City is finally back!", ["SE LIGA", "TRAILER", "VICE CITY"]),
            ("The graphics are unbelievable!", ["GRÁFICO", "SURREAL"]),
            ("Check the link in bio for the exclusive drop!", ["DROP EXCLUSIVO", "BIO"]),
        ]

        for en_text, expected_tokens in test_cases:
            pt_text = localizer.localize(en_text)
            for token in expected_tokens:
                self.assertIn(token.lower(), pt_text.lower(), f"Missing token {token} in {pt_text}")

    def test_07_localizer_segments_and_viral_hook(self):
        localizer = RuleBasedOfflineLocalizer(add_viral_hooks=True)
        raw_segs = MockTranscriber().transcribe()
        localized = localizer.localize_segments(raw_segs)

        self.assertEqual(len(localized), len(raw_segs))
        # First segment must contain viral hook prefix
        self.assertTrue(
            any(h in localized[0].text for h in ["SE LIGA", "TÁ MALUCO", "VAZOU", "OLHA"]),
            f"Intro segment missing viral hook: {localized[0].text}",
        )

    def test_08_video_localizer_offline_fallback(self):
        localizer = VideoLocalizer(offline=True)
        res = localizer.localize("Look at this trailer")
        self.assertIn("trailer", res.lower())

    # -------------------------------------------------------------------------
    # 5. Subtitler (.srt, .vtt, .ass)
    # -------------------------------------------------------------------------
    def test_09_subtitler_formats_and_export(self):
        mock_segs = [
            {"id": 1, "start": 0.5, "end": 2.2, "text": "SE LIGA NESSE TRAILER!"},
            {"id": 2, "start": 2.3, "end": 4.8, "text": "O GRÁFICO TÁ SURREAL!"},
        ]

        srt_str = generate_srt(mock_segs)
        self.assertIn("00:00:00,500 --> 00:00:02,200", srt_str)
        self.assertIn("SE LIGA NESSE TRAILER!", srt_str)

        vtt_str = generate_vtt(mock_segs)
        self.assertTrue(vtt_str.startswith("WEBVTT"))
        self.assertIn("00:00:00.500 --> 00:00:02.200", vtt_str)

        ass_str = generate_ass(mock_segs)
        self.assertIn("[Script Info]", ass_str)
        self.assertIn("Dialogue: 0,0:00:00.50,0:00:02.20,ViceCityNeon", ass_str)

        # File export
        prefix = self.test_dir / "sub_export"
        exported = export_subtitles(mock_segs, prefix, formats=("srt", "vtt", "ass"))
        self.assertTrue(exported["srt"].exists())
        self.assertTrue(exported["vtt"].exists())
        self.assertTrue(exported["ass"].exists())

    # -------------------------------------------------------------------------
    # 6. Renderer & Windows Path Escaping
    # -------------------------------------------------------------------------
    def test_10_windows_path_escaping(self):
        win_path = r"C:\Users\tester\video_project\sub.srt"
        escaped = escape_ffmpeg_path(win_path)
        self.assertNotIn("C:", escaped)
        self.assertIn(r"C\:", escaped)
        self.assertNotIn(r"\video_project", escaped)
        self.assertIn("/video_project/", escaped)

    def test_11_filtergraph_builder(self):
        fg = build_filtergraph(cta_text="TEST CTA BANNER")
        self.assertIn("1080", fg)
        self.assertIn("1920", fg)
        self.assertIn("boxblur", fg)
        self.assertIn("TEST CTA BANNER", fg)

    def test_12_vertical_rendering_execution(self):
        out_vertical = self.test_dir / "rendered_vertical_1080x1920.mp4"
        render_vertical_video(
            input_video=self.sample_video,
            output_video=out_vertical,
            cta_text="COLEÇÃO VICE CITY",
            mode="blur_padding",
        )
        self.assertTrue(out_vertical.exists())
        self.assertGreater(out_vertical.stat().st_size, 10000)

        # Inspect geometry
        info = get_video_info(out_vertical)
        self.assertEqual(info["width"], 1080)
        self.assertEqual(info["height"], 1920)

    # -------------------------------------------------------------------------
    # 7. End-to-End CLI Pipeline
    # -------------------------------------------------------------------------
    def test_13_cli_pipeline_e2e_mock(self):
        cli_out_dir = self.test_dir / "cli_output"
        summary = process_video_pipeline(
            input_source="mock",
            output_dir=cli_out_dir,
            mock=True,
            cta_text="LINK NA BIO - VICE CITY",
        )

        self.assertEqual(summary["status"], "success")
        self.assertTrue(Path(summary["transcript_json"]).exists())
        self.assertTrue(Path(summary["localized_json"]).exists())
        self.assertTrue(Path(summary["subtitles_srt"]).exists())
        self.assertTrue(Path(summary["subtitles_vtt"]).exists())
        self.assertTrue(Path(summary["rendered_video"]).exists())

        # Validate JSON content
        trans_data = json.loads(Path(summary["transcript_json"]).read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(trans_data), 3)

        loc_data = json.loads(Path(summary["localized_json"]).read_text(encoding="utf-8"))
        self.assertEqual(len(loc_data), len(trans_data))


if __name__ == "__main__":
    unittest.main()
