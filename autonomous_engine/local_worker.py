"""
autonomous_engine/local_worker.py
AGENTE 09 — Senior Video Editor
AGENTE 12 — Quality Control (QA Técnico e Editorial)

Executor de produção pesada (Heavy Worker). Consome jobs da fila persistente,
gera a narração neural Edge-TTS, monta as legendas sincronizadas, renderiza o vídeo
vertical 1080x1920 com FFmpeg e valida os padrões de qualidade antes de aprovar.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from autonomous_engine.production_queue import ProductionQueue, QueueJob
from video_pipeline.ffmpeg_resolver import create_synthetic_video, get_ffmpeg_exe
from video_pipeline.ingestion import get_video_info
from video_pipeline.renderer import render_vertical_video
from video_pipeline.subtitler import export_subtitles
from video_pipeline.transcriber import TranscriptSegment
from video_pipeline.voice_engine import VoiceEngine

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
STORAGE_BASE = Path(r"C:\Users\victo\NOITE86_FACTORY")


class LocalProductionWorker:
    """Trabalhador local autônomo para renderização audiovisual e controle de qualidade."""

    def __init__(self, queue: Optional[ProductionQueue] = None):
        self.queue = queue or ProductionQueue()
        self.voice_engine = VoiceEngine(voice="pt-BR-AntonioNeural")
        self.ffmpeg_exe = get_ffmpeg_exe()

    def process_next_job(self) -> Optional[Dict[str, Any]]:
        """Busca o próximo trabalho pendente na fila e executa a produção."""
        job = self.queue.claim_next_job(lock_seconds=900)
        if not job:
            return None

        print(f"\n[Worker] 🚀 Iniciando produção do job: {job.id} ('{job.title}')")
        start_t = time.time()

        try:
            artifacts = self._execute_production(job)
            
            # Executa AGENTE 12 — Quality Control
            qa_report = self._quality_control_audit(artifacts.get("rendered_video"))
            artifacts["qa_report"] = qa_report

            if not qa_report["passed"]:
                raise RuntimeError(f"Reprovado no Quality Control (QA): {qa_report['issues']}")

            # Conclui com sucesso
            self.queue.complete_job(job.id, artifacts)
            elapsed = round(time.time() - start_t, 2)
            print(f"[Worker] ✅ Job {job.id} concluído com sucesso em {elapsed}s! Vídeo: {artifacts['rendered_video']}")
            return artifacts

        except Exception as e:
            print(f"[Worker] ❌ Falha no job {job.id}: {e}")
            self.queue.fail_job(job.id, str(e))
            return None

    def _execute_production(self, job: QueueJob) -> Dict[str, Any]:
        """Gera narração, legendas e renderiza o vídeo vertical final 9:16."""
        briefing = job.briefing_data
        job_slug = f"{job.opportunity_id}_{int(time.time())}"

        # Diretórios dedicados em NOITE86_FACTORY
        voice_dir = STORAGE_BASE / "04_VOICE"
        edit_dir = STORAGE_BASE / "05_EDITING"
        ready_dir = STORAGE_BASE / "06_READY_VIDEOS"
        for d in (voice_dir, edit_dir, ready_dir):
            d.mkdir(parents=True, exist_ok=True)

        script_segments_raw = briefing.get("script_segments", [])
        if not script_segments_raw:
            raise ValueError(f"Briefing do job {job.id} não contém segmentos de roteiro.")

        # Converte para TranscriptSegments do pipeline
        pipeline_segments = []
        for s in script_segments_raw:
            pipeline_segments.append(
                TranscriptSegment(
                    id=s["id"],
                    start=float(s["start_sec"]),
                    end=float(s["end_sec"]),
                    text=s["narration_pt"],
                    words=[]
                )
            )

        # 1. GERAÇÃO DE VOZ NEURAL PT-BR (Edge-TTS)
        narration_mp3 = voice_dir / f"{job_slug}_narration.mp3"
        print(f"[Worker] [1/3] Sintetizando dublagem neural brasileira: {narration_mp3.name}...")
        self.voice_engine.generate_narration_track(
            segments=pipeline_segments,
            output_audio_path=narration_mp3,
        )

        # 2. GERAÇÃO DE LEGENDAS (.srt, .vtt, .ass)
        subs_prefix = edit_dir / f"{job_slug}_subs"
        print(f"[Worker] [2/3] Gerando legendas sincronizadas...")
        sub_files = export_subtitles(
            segments=pipeline_segments,
            output_prefix=subs_prefix,
            formats=("srt", "vtt", "ass")
        )

        # 3. PREPARAÇÃO DO VÍDEO BASE E RENDERIZAÇÃO VERTICAL 9:16 (1080x1920)
        # Se for rota original ou se não houver mídia de terceiro autorizada,
        # cria b-roll sintético cinemático nativo para a narração
        base_video_path = edit_dir / f"{job_slug}_base_visual.mp4"
        total_duration = pipeline_segments[-1].end
        create_synthetic_video(
            output_path=base_video_path,
            duration=max(5.0, total_duration),
            resolution="1280x720",
            fps=24
        )

        final_mp4 = ready_dir / f"{job_slug}_vertical_noite86.mp4"
        cta_text = briefing.get("call_to_action", "COLEÇÃO NOITE 86 // LINK NA BIO")
        header_text = "🚨 NOITE 86 // GTA 6 BRASIL 🚨"

        print(f"[Worker] [3/3] Renderizando MP4 vertical 9:16 com boxblur e CTA...")
        render_vertical_video(
            input_video=base_video_path,
            output_video=final_mp4,
            subtitle_path=sub_files.get("srt"),
            cta_text=cta_text,
            header_text=header_text,
            narration_audio=narration_mp3,
            mode="blur_padding",
            target_width=1080,
            target_height=1920,
        )

        # Salva também cópia no workspace output para servir no dashboard
        workspace_output = PROJECT_ROOT / "output_noite86" / final_mp4.name
        workspace_output.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(final_mp4, workspace_output)
        except Exception:
            pass

        return {
            "job_id": job.id,
            "rendered_video": str(final_mp4),
            "narration_audio": str(narration_mp3),
            "subtitles_srt": str(sub_files.get("srt")),
            "workspace_video_copy": str(workspace_output),
            "duration": total_duration,
        }

    def _quality_control_audit(self, video_path_str: Optional[str]) -> Dict[str, Any]:
        """AGENTE 12 — Quality Control: Auditoria técnica estrita antes da aprovação."""
        if not video_path_str:
            return {"passed": False, "issues": ["Arquivo de vídeo não foi especificado."]}

        p = Path(video_path_str)
        if not p.exists():
            return {"passed": False, "issues": [f"Arquivo final não existe: {p}"]}

        size_bytes = p.stat().st_size
        if size_bytes < 100 * 1024:
            return {"passed": False, "issues": [f"Arquivo corrompido ou muito pequeno: {size_bytes} bytes"]}

        try:
            info = get_video_info(p)
        except Exception as e:
            return {"passed": False, "issues": [f"Falha ao ler metadados com ffprobe: {e}"]}

        issues = []
        if info.get("width") != 1080 or info.get("height") != 1920:
            issues.append(f"Resolução incorreta: {info.get('width')}x{info.get('height')} (exigido 1080x1920)")

        if not info.get("has_audio"):
            issues.append("Trilha de áudio ausente no vídeo final.")

        if info.get("duration", 0.0) < 3.0:
            issues.append(f"Duração insuficiente: {info.get('duration')}s")

        passed = len(issues) == 0
        return {
            "passed": passed,
            "resolution": f"{info.get('width')}x{info.get('height')}",
            "duration": info.get("duration"),
            "size_kb": round(size_bytes / 1024, 1),
            "issues": issues,
            "audited_at": datetime.now(timezone.utc).isoformat()
        }
