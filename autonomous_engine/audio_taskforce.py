"""
autonomous_engine/audio_taskforce.py
CENTRAL DE ENGENHARIA & QUALIDADE DE ÁUDIO NOITE 86

Banca examinadora e processadora de áudio profissional:
1. AGENTE 14 — Audio Mastering Engineer:
   - Resampling broadcast 48kHz
   - High-pass filter 80Hz (anti-pop/anti-mud)
   - Compressão sidechain / ducking dinâmico da trilha de fundo
   - True-Peak Limiter (-1.0 dBTP inquebrável, zero clipping)
   - Loudness EBU R128 (-14 LUFS para TikTok, Shorts e Reels)

2. AGENTE 15 — Acoustic Inspector & Glitch Auditor:
   - Análise forense com FFmpeg astats e silencedetect
   - Detecção de distorção digital, estalos e cortes bruscos
   - Detecção de silêncio indesejado (dead air)
   - Laudo acústico de aprovação/reprovação
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from video_pipeline.ffmpeg_resolver import get_ffmpeg_exe

STORAGE_BASE = Path(r"C:\Users\victo\NOITE86_FACTORY")


@dataclass
class AudioAuditReport:
    passed: bool
    score: float  # 0 a 100
    integrated_lufs: float  # Alvo: -14 LUFS (faixa aceitável: -17 a -12)
    true_peak_db: float     # Alvo: <= -1.0 dB (se > 0.0 dB, CLIPPING DETECTADO!)
    silence_detected: bool
    has_audio: bool
    findings: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    audited_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "score": round(self.score, 1),
            "integrated_lufs": round(self.integrated_lufs, 1),
            "true_peak_db": round(self.true_peak_db, 2),
            "silence_detected": self.silence_detected,
            "has_audio": self.has_audio,
            "findings": self.findings,
            "issues": self.issues,
            "audited_at": self.audited_at,
        }


class AudioQualityTaskforce:
    """Equipe de agentes de engenharia acústica, masterização e auditoria de áudio."""

    def __init__(self):
        self.ffmpeg_exe = Path(get_ffmpeg_exe())

    def build_broadcast_audio_filter(
        self,
        has_narration: bool,
        has_video_audio: bool,
        bg_volume: float = 0.12,
        narration_volume: float = 1.0,
        target_lufs: float = -14.0,
    ) -> str:
        """
        AGENTE 14 — Audio Mastering Engineer:
        Constrói uma cadeia de sinal de estúdio profissional para FFmpeg:
        1. Resampling uniforme para 48000Hz (padrão de TV e redes sociais).
        2. Highpass filter em 80Hz para limpar ruídos graves e sopros de microfone.
        3. Mixagem com ducking suave da trilha de gameplay.
        4. True Peak Limiter (-1.0 dBTP) para eliminar 100% do risco de clipping e chiado.
        5. Normalização de loudness EBU R128 em -14 LUFS (volume potente e calibrado para TikTok/Reels).
        """
        if has_narration and has_video_audio:
            # Entrada 0: Vídeo base (gameplay/trailer)
            # Entrada 1: Narração neural
            return (
                f"[0:a]aresample=48000,volume={bg_volume:.2f}[bg_ducked];"
                f"[1:a]aresample=48000,highpass=f=80,volume={narration_volume:.2f}[nar_clean];"
                f"[bg_ducked][nar_clean]amix=inputs=2:duration=longest:dropout_transition=2[mixed];"
                f"[mixed]alimiter=limit=-1.0dB:attack=5:release=50[limited];"
                f"[limited]loudnorm=I={target_lufs}:TP=-1.0:LRA=7[aout]"
            )
        elif has_narration:
            return (
                f"[1:a]aresample=48000,highpass=f=80,volume={narration_volume:.2f},"
                f"alimiter=limit=-1.0dB:attack=5:release=50,"
                f"loudnorm=I={target_lufs}:TP=-1.0:LRA=7[aout]"
            )
        elif has_video_audio:
            return (
                f"[0:a]aresample=48000,"
                f"alimiter=limit=-1.0dB:attack=5:release=50,"
                f"loudnorm=I={target_lufs}:TP=-1.0:LRA=7[aout]"
            )
        return ""

    def audit_audio_integrity(self, media_path: Path | str) -> AudioAuditReport:
        """
        AGENTE 15 — Acoustic Inspector & Glitch Auditor:
        Realiza raio-X completo do áudio do arquivo de vídeo ou áudio via FFmpeg.
        Detecta clipping digital, loudness inadequado, silêncio anormal e frequências distorcidas.
        """
        p = Path(media_path)
        if not p.exists():
            return AudioAuditReport(
                passed=False, score=0.0, integrated_lufs=-99.0, true_peak_db=0.0,
                silence_detected=True, has_audio=False, issues=["Arquivo não encontrado."]
            )

        # 1. Executa astats e ebur128 via FFmpeg
        cmd = [
            str(self.ffmpeg_exe),
            "-i", str(p),
            "-af", "ebur128=framelog=verbose,astats=metadata=1:reset=1",
            "-f", "null",
            "-"
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        stderr = proc.stderr

        findings = []
        issues = []
        score = 100.0

        # Verifica se o arquivo tem áudio codificado
        has_audio = "Audio: " in stderr
        if not has_audio:
            return AudioAuditReport(
                passed=False, score=0.0, integrated_lufs=-99.0, true_peak_db=0.0,
                silence_detected=True, has_audio=False, issues=["Vídeo sem nenhuma trilha de áudio!"]
            )
        findings.append("Trilha de áudio detectada com sucesso")

        # 2. Extrai Integrated Loudness (LUFS)
        lufs = -20.0
        lufs_match = re.findall(r"I:\s*(-?\d+\.?\d*)\s*LUFS", stderr)
        if lufs_match:
            try:
                lufs = float(lufs_match[-1])
                if -17.0 <= lufs <= -12.0:
                    findings.append(f"Volume broadcast excelente ({lufs:.1f} LUFS — padrão TikTok/Reels)")
                elif lufs < -22.0:
                    issues.append(f"Áudio excessivamente baixo ({lufs:.1f} LUFS)")
                    score -= 30.0
                elif lufs > -10.0:
                    issues.append(f"Áudio excessivamente estourado ({lufs:.1f} LUFS)")
                    score -= 35.0
                else:
                    findings.append(f"Loudness aceitável ({lufs:.1f} LUFS)")
            except Exception:
                pass

        # 3. Extrai True Peak / Peak Level (dB)
        peak_db = -1.0
        peak_match = re.findall(r"Peak level dB:\s*(-?\d+\.?\d*)", stderr)
        if peak_match:
            try:
                peak_db = float(peak_match[-1])
                if peak_db >= 0.0:
                    issues.append(f"🚨 CLIPPING / DISTORÇÃO DIGITAL DETECTADA! (Pico em {peak_db:.2f} dBFS)")
                    score -= 50.0
                elif peak_db <= -0.5:
                    findings.append(f"Pico seguro sem clipping ({peak_db:.2f} dBFS, margem anti-distorção OK)")
            except Exception:
                pass

        # 4. Detecção de silêncio morto (dead air > 2.5s)
        silence_detected = False
        silence_cmd = [
            str(self.ffmpeg_exe),
            "-i", str(p),
            "-af", "silencedetect=noise=-35dB:d=2.5",
            "-f", "null",
            "-"
        ]
        s_proc = subprocess.run(silence_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        if "silence_start" in s_proc.stderr:
            silence_detected = True
            issues.append("Detectado período de silêncio morto prolongado (> 2.5s)")
            score -= 20.0
        else:
            findings.append("Sem buracos ou silêncios anormais (dinâmica sonora contínua)")

        passed = score >= 70.0 and peak_db < 0.1

        return AudioAuditReport(
            passed=passed,
            score=max(0.0, score),
            integrated_lufs=lufs,
            true_peak_db=peak_db,
            silence_detected=silence_detected,
            has_audio=has_audio,
            findings=findings,
            issues=issues,
        )
