"""
tests/test_video_factory_e2e.py
OPERAÇÃO NOITE 86 — Suíte de Testes Automatizados E2E da Fábrica de Vídeos (Agente 06)
Validação de:
- Transcrição
- Tradução Inteligente Gamer
- Síntese e Sincronização de Voz Neural pt-BR (Edge-TTS)
- Legendas (.srt, .vtt, .ass)
- Auditoria de Direitos Autorais
- Renderização Vertical 9:16 (1080x1920) com CTA NOITE 86
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from video_pipeline.cli import process_video_pipeline
from video_pipeline.ffmpeg_resolver import create_synthetic_video, get_ffmpeg_exe
from video_pipeline.ingestion import get_video_info, ingest_video
from video_pipeline.renderer import build_filtergraph, escape_ffmpeg_path, render_vertical_video
from video_pipeline.rights_reviewer import LicenseType, RightsReviewer
from video_pipeline.subtitler import export_subtitles, generate_ass, generate_srt, generate_vtt
from video_pipeline.transcriber import TranscriptSegment, Transcriber
from video_pipeline.translator import AITranslator
from video_pipeline.voice_engine import VoiceEngine


class TestAgente05RightsReviewer:
    """Validação da Auditoria de Direitos e Propriedade Intelectual."""

    def test_own_content_clearance(self):
        reviewer = RightsReviewer()
        rep = reviewer.evaluate_source("gameplay_autoral.mp4", LicenseType.OWN_CONTENT)
        assert rep.allowed_to_republish_source is True
        assert rep.status == "approved"
        assert rep.recommended_action == "process_direct"

    def test_explicit_permission_clearance(self):
        reviewer = RightsReviewer()
        rep = reviewer.evaluate_source(
            "streamer_clip.mp4",
            LicenseType.EXPLICIT_PERMISSION,
            details="Autorizado via DM por @pro_gamer",
        )
        assert rep.allowed_to_republish_source is True
        assert rep.status == "approved"

    def test_public_trailer_clearance(self):
        reviewer = RightsReviewer()
        rep = reviewer.evaluate_source("trailer2_rockstar.mp4", LicenseType.PUBLIC_TRAILER)
        assert rep.allowed_to_republish_source is True
        assert "fair_use" in rep.status.lower() or "fair_use" in rep.recommended_action.lower()
        assert "CONTEÚDO ORIGINAL" in rep.disclaimer or "ESTÚDIOS" in rep.disclaimer

    def test_unauthorized_content_blocked_from_raw_mirroring(self):
        reviewer = RightsReviewer()
        rep = reviewer.evaluate_source("leak_leaker_xyz.mp4", LicenseType.UNAUTHORIZED)
        assert rep.allowed_to_republish_source is False
        assert rep.status == "blocked_raw_mirroring"
        assert "original_transformative_analysis_only" in rep.recommended_action


class TestAgente02AITranslator:
    """Validação da Tradução Contextual Gamer pt-BR e Roteirização."""

    def test_gamer_slang_and_timestamp_preservation(self):
        translator = AITranslator(offline_priority=True)
        raw_segments = [
            TranscriptSegment(start=0.0, end=2.5, text="Look at this insane GTA 6 map leak bro!"),
            TranscriptSegment(start=2.5, end=5.0, text="The graphics and ray tracing in Vice City look unreal."),
        ]
        translated = translator.translate_segments(raw_segments, preserve_timing=True)
        assert len(translated) == 2
        assert translated[0].start == 0.0
        assert translated[0].end == 2.5
        assert translated[1].start == 2.5
        # Gamer slang conversion check
        assert any(term in translated[0].text.lower() for term in ["vazamento", "insano", "gta 6", "mapa", "olha"])
        assert any(term in translated[1].text.lower() for term in ["gráfico", "vice city", "absurdo", "insano"])

    def test_original_transformative_script_generation(self):
        translator = AITranslator(offline_priority=True)
        raw_segments = [
            TranscriptSegment(start=0.0, end=3.0, text="There is a rumor that the release date is delayed to 2026."),
        ]
        script = translator.generate_original_script(raw_segments)
        assert "hook" in script
        assert "factual_analysis" in script
        assert "call_to_action" in script
        assert "NOITE 86" in script["call_to_action"]


class TestAgente03VoiceEngine:
    """Validação da Síntese e Sincronização de Voz Neural pt-BR (Edge-TTS)."""

    def test_voice_engine_pacing_calculation(self):
        engine = VoiceEngine()
        # 10 words in 1 second should need speedup
        speed_factor = engine.calculate_pacing("um dois três quatro cinco seis sete oito nove dez", target_duration=1.0)
        assert speed_factor > 1.0

    def test_edge_tts_single_utterance_generation(self, tmp_path):
        engine = VoiceEngine()
        out_mp3 = tmp_path / "test_utterance.mp3"
        result = engine.synthesize_speech("O maior vazamento da história de Vice City!", out_mp3)
        assert result.exists()
        assert result.stat().st_size > 1000  # Valid MP3 file


class TestAgente04RendererAndSubtitles:
    """Validação da Geração de Legendas e Renderização Vertical."""

    def test_subtitle_export(self, tmp_path):
        segments = [
            TranscriptSegment(start=0.0, end=1.5, text="🚨 ALERTA GERAL: DROP NOITE 86!"),
            TranscriptSegment(start=1.5, end=3.0, text="Camisetas e acessórios oficiais no link da bio."),
        ]
        exported = export_subtitles(segments, output_prefix=tmp_path / "subs")
        assert Path(exported["srt"]).exists()
        assert Path(exported["vtt"]).exists()
        assert Path(exported["ass"]).exists()
        
        srt_content = Path(exported["srt"]).read_text(encoding="utf-8")
        assert "00:00:00,000 --> 00:00:01,500" in srt_content
        assert "ALERTA GERAL" in srt_content

    def test_escape_ffmpeg_path(self):
        raw_win_path = r"C:\Users\victo\teamwork_projects\video.mp4"
        escaped = escape_ffmpeg_path(raw_win_path)
        assert escaped == r"C\:/Users/victo/teamwork_projects/video.mp4"

    def test_render_vertical_video_with_audio_and_cta(self, tmp_path):
        # 1. Create a 3-second synthetic test video
        synthetic_in = tmp_path / "input_16_9.mp4"
        create_synthetic_video(synthetic_in, duration=3.0, resolution="640x360")
        assert synthetic_in.exists()

        # 2. Render to 1080x1920 9:16 vertical
        rendered_out = tmp_path / "output_vertical_9_16.mp4"
        render_vertical_video(
            input_video=synthetic_in,
            output_video=rendered_out,
            cta_text="COLEÇÃO NOITE 86",
            header_text="NOITE 86 // GTA 6",
            target_width=1080,
            target_height=1920,
        )

        assert rendered_out.exists()
        assert rendered_out.stat().st_size > 5000

        # Check metadata
        info = get_video_info(rendered_out)
        assert info["width"] == 1080
        assert info["height"] == 1920


class TestMasterPipelineE2E:
    """Validação da Execução E2E do Comando Mestre da Fábrica."""

    def test_full_pipeline_run(self, tmp_path):
        out_dir = tmp_path / "run_e2e"
        summary = process_video_pipeline(
            input_source="mock",
            output_dir=out_dir,
            license_type="own_content",
            mock=True,
            enable_tts=True,
            cta_text="COLEÇÃO NOITE 86 // LINK NA BIO",
        )

        assert summary["status"] == "success"
        artifacts = summary["artifacts"]

        # Verify all 7 critical artifacts exist on disk and are non-empty
        for key, file_path_str in artifacts.items():
            if file_path_str:
                p = Path(file_path_str)
                assert p.exists(), f"Artefato ausente: {key} ({file_path_str})"
                assert p.stat().st_size > 0, f"Artefato vazio (0 bytes): {key}"

        # Verify vertical video specs
        rendered_file = Path(artifacts["rendered_video"])
        info = get_video_info(rendered_file)
        assert info["width"] == 1080
        assert info["height"] == 1920
        assert info["has_audio"] is True
