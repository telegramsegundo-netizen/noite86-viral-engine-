"""
video_pipeline/voice_engine.py
Agente 03 - Brazilian Voice Engineer (TTS & Audio Mixing Engine).

Generates high-energy, natural Brazilian Portuguese voiceovers using edge-tts:
- High-fidelity neural voices (pt-BR-AntonioNeural / pt-BR-FranciscaNeural).
- Automated timecode synchronization and speech-rate calibration.
- Silence padding and multi-track audio ducking/mixing via FFmpeg.
- Cost: R$ 0.
"""
from __future__ import annotations

import asyncio
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import edge_tts
from video_pipeline.ffmpeg_resolver import get_ffmpeg_exe
from video_pipeline.transcriber import TranscriptSegment


class VoiceEngine:
    """Motor de síntese de voz e engenharia de áudio brasileira."""

    DEFAULT_VOICE = "pt-BR-AntonioNeural"      # Voz masculina jovem, energética e gamer
    FEMALE_VOICE = "pt-BR-FranciscaNeural"    # Voz feminina firme e expressiva

    def __init__(self, voice: str = DEFAULT_VOICE, default_voice: Optional[str] = None):
        self.voice = default_voice or voice
        self.ffmpeg_exe = get_ffmpeg_exe()

    def calculate_pacing(self, text: str, target_duration: float) -> float:
        """Calcula o fator de aceleração necessário com base no tempo disponível."""
        words = len(text.split())
        if target_duration <= 0 or words == 0:
            return 1.0
        # Média padrão pt-BR: ~2.7 palavras por segundo
        normal_duration = words / 2.7
        speed_factor = normal_duration / target_duration
        return max(0.5, min(2.5, speed_factor))

    def synthesize_speech(
        self,
        text: str,
        output_path: Union[str, Path],
        rate: str = "+0%",
        voice: Optional[str] = None,
    ) -> Path:
        """Sintetiza um trecho de texto único diretamente via Edge-TTS."""
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        v = voice or self.voice
        clean_text = re.sub(r"[🚨🔥👀✨]", "", text).strip() or "..."
        communicate = edge_tts.Communicate(clean_text, v, rate=rate)
        asyncio.run(communicate.save(str(out)))
        return out

    def generate_narration_track(
        self,
        segments: List[TranscriptSegment],
        output_audio_path: Union[str, Path],
        target_total_duration: Optional[float] = None,
    ) -> Path:
        """
        Gera uma trilha de áudio contínua e perfeitamente sincronizada com os timestamps dos segmentos.
        """
        output_path = Path(output_audio_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not segments:
            raise ValueError("Lista de segmentos vazia para geração de voz.")

        # Executa síntese assíncrona dos segmentos individuais
        temp_dir = Path(tempfile.mkdtemp(prefix="voice_engine_"))
        try:
            segment_audio_files = asyncio.run(self._synthesize_all_segments(segments, temp_dir))
            # Monta o arquivo de áudio final preenchendo os silêncios exatos
            self._assemble_full_timeline(
                segments=segments,
                segment_files=segment_audio_files,
                output_path=output_path,
                target_total_duration=target_total_duration,
            )
            return output_path
        finally:
            # Limpeza de temporários
            for f in temp_dir.glob("*"):
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                temp_dir.rmdir()
            except Exception:
                pass

    async def _synthesize_all_segments(
        self,
        segments: List[TranscriptSegment],
        temp_dir: Path,
    ) -> List[Path]:
        """Gera o áudio de cada segmento respeitando o tempo disponível."""
        tasks = []
        files = []

        for idx, seg in enumerate(segments):
            seg_file = temp_dir / f"seg_{idx:03d}.mp3"
            files.append(seg_file)
            
            # Limpar texto de caracteres especiais
            clean_text = re.sub(r"[🚨🔥👀✨]", "", seg.text).strip()
            if not clean_text:
                clean_text = "..."

            # Calcular taxa de fala necessária
            available_time = max(0.5, seg.end - seg.start)
            # Regra prática: ~12 caracteres por segundo em fala normal
            est_chars_normal = available_time * 14
            rate_str = "+0%"
            if len(clean_text) > est_chars_normal * 1.3:
                rate_str = "+20%"
            elif len(clean_text) > est_chars_normal * 1.1:
                rate_str = "+10%"

            communicate = edge_tts.Communicate(clean_text, self.voice, rate=rate_str)
            tasks.append(communicate.save(str(seg_file)))

        await asyncio.gather(*tasks)
        return files

    def _get_audio_duration(self, audio_file: Path) -> float:
        """Obtém duração exata do arquivo de áudio via FFmpeg."""
        proc = subprocess.run(
            [self.ffmpeg_exe, "-i", str(audio_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", proc.stderr)
        if match:
            h, m, s = float(match.group(1)), float(match.group(2)), float(match.group(3))
            return h * 3600 + m * 60 + s
        return 0.0

    def _assemble_full_timeline(
        self,
        segments: List[TranscriptSegment],
        segment_files: List[Path],
        output_path: Path,
        target_total_duration: Optional[float] = None,
    ):
        """
        Combina os segmentos de áudio aplicando delay / silêncio nos pontos exatos de tempo (timestamps).
        """
        # Constrói comando com adelay para cada segmento
        filter_complex_parts = []
        mix_inputs = []

        for idx, (seg, audio_file) in enumerate(zip(segments, segment_files)):
            delay_ms = int(max(0.0, seg.start) * 1000)
            mix_inputs.extend(["-i", str(audio_file)])
            filter_complex_parts.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a{idx}]")

        concat_nodes = "".join(f"[a{i}]" for i in range(len(segments)))
        filter_complex_parts.append(
            f"{concat_nodes}amix=inputs={len(segments)}:dropout_transition=0:normalize=0[aout]"
        )

        full_filter = ";".join(filter_complex_parts)

        cmd = [
            self.ffmpeg_exe,
            "-y",
            *mix_inputs,
            "-filter_complex", full_filter,
            "-map", "[aout]",
            "-ac", "2",
            "-ar", "44100",
            str(output_path),
        ]

        # Se houver duração total especificada, limitar
        if target_total_duration and target_total_duration > 0:
            cmd.insert(-1, "-t")
            cmd.insert(-1, str(target_total_duration))

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            # Fallback seguro: concatenação simples se adelay falhar
            self._fallback_simple_concat(segment_files, output_path)

    def _fallback_simple_concat(self, segment_files: List[Path], output_path: Path):
        """Concatenação linear de emergência."""
        concat_txt = output_path.parent / "concat_fallback.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for sf in segment_files:
                f.write(f"file '{sf.as_posix()}'\n")

        cmd = [
            self.ffmpeg_exe,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_txt),
            "-c:a", "libmp3lame",
            "-q:a", "2",
            str(output_path)
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if concat_txt.exists():
            concat_txt.unlink()

    def mix_narration_with_background(
        self,
        original_video: Union[str, Path],
        narration_audio: Union[str, Path],
        output_audio: Union[str, Path],
        bg_volume: float = 0.15,
        voice_volume: float = 1.0,
    ) -> Path:
        """
        Mistura a voz de narração com o áudio de fundo original do vídeo (áudio do vídeo reduzido a 15%).
        """
        out_p = Path(output_audio).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.ffmpeg_exe,
            "-y",
            "-i", str(original_video),
            "-i", str(narration_audio),
            "-filter_complex",
            f"[0:a]volume={bg_volume}[bg];[1:a]volume={voice_volume}[voice];[bg][voice]amix=inputs=2:duration=longest:dropout_transition=0[aout]",
            "-map", "[aout]",
            "-ac", "2",
            "-ar", "44100",
            "-c:a", "aac",
            "-b:a", "192k",
            str(out_p)
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            # Se o vídeo não tiver áudio original, usa apenas a narração
            cmd_voice_only = [
                self.ffmpeg_exe,
                "-y",
                "-i", str(narration_audio),
                "-c:a", "aac",
                "-b:a", "192k",
                str(out_p)
            ]
            subprocess.run(cmd_voice_only, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return out_p
