"""
video_pipeline/cli.py
OPERAÇÃO NOITE 86 — Fábrica Inteligente de Vídeos
Pipeline completo de localização, dublagem neural pt-BR, legendas e renderização vertical (1080x1920 9:16)
com auditoria de direitos autorais e CTA da loja NOITE 86.

Uso:
    python -m video_pipeline.cli process --input <arquivo_ou_url> --output-dir ./output --license own_content
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Garante compatibilidade UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from video_pipeline.ingestion import ingest_video
from video_pipeline.renderer import render_vertical_video
from video_pipeline.rights_reviewer import LicenseType, RightsReviewer
from video_pipeline.subtitler import export_subtitles
from video_pipeline.transcriber import Transcriber
from video_pipeline.translator import AITranslator
from video_pipeline.voice_engine import VoiceEngine


def process_video_pipeline(
    input_source: str,
    output_dir: Path,
    license_type: str = "own_content",
    license_details: Optional[str] = None,
    mock: bool = False,
    cta_text: str = "COLEÇÃO NOITE 86 // LINK NA BIO",
    header_text: str = "🚨 NOITE 86 // GTA 6 BRASIL 🚨",
    voice_name: str = "pt-BR-AntonioNeural",
    enable_tts: bool = True,
    mode: str = "blur_padding",
    burn_subtitles: bool = True,
    offline: bool = False,
) -> Dict[str, Any]:
    """
    Executa o pipeline completo da Fábrica de Vídeos NOITE 86:
    [1/7] Auditoria e Revisão de Direitos de Conteúdo (Agente 05)
    [2/7] Ingestão e Validação do Vídeo (Agente 01)
    [3/7] Transcrição de Áudio com Timestamps (Whisper)
    [4/7] Tradução Contextual Gamer pt-BR e Roteirização (Agente 02)
    [5/7] Síntese de Voz Neural Brasileira Edge-TTS R$ 0 (Agente 03)
    [6/7] Geração e Sincronização de Legendas .srt, .vtt, .ass
    [7/7] Renderização Vertical 9:16 (1080x1920) com CTA e Mixagem (Agente 04)
    """
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("🚀 OPERAÇÃO NOITE 86 — INICIANDO FÁBRICA INTELIGENTE DE VÍDEOS")
    print(f"📦 Origem: {input_source}")
    print(f"⚖️  Licença: {license_type.upper()}")
    print("=" * 60)

    # -------------------------------------------------------------
    # [1/7] Auditoria de Direitos & Conteúdo (Agente 05)
    # -------------------------------------------------------------
    print("\n[1/7] ⚖️  Auditando direitos autorais e permissões de uso...")
    rights_reviewer = RightsReviewer()
    clearance = rights_reviewer.evaluate_source(
        source_input=input_source,
        license_type=license_type,
        details=license_details,
    )
    rights_json_path = out_dir / "rights_clearance.json"
    rights_json_path.write_text(
        json.dumps(clearance.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"   Status de autorização: {clearance.status.upper()}")
    print(f"   Ação recomendada: {clearance.recommended_action}")
    if clearance.disclaimer:
        print(f"   Disclaimer: {clearance.disclaimer}")

    # -------------------------------------------------------------
    # [2/7] Ingestão e Validação do Vídeo (Agente 01)
    # -------------------------------------------------------------
    print("\n[2/7] 📥 Ingerindo e validando integridade do vídeo...")
    video_path = ingest_video(input_source, output_dir=out_dir, mock=mock)
    base_name = video_path.stem
    if base_name in ("mock_ingested_video", "synthetic_clip"):
        base_name = "noite86_clip"

    transcript_json_path = out_dir / f"{base_name}_transcript.json"
    localized_json_path = out_dir / f"{base_name}_localized.json"
    narration_audio_path = out_dir / f"{base_name}_narration.mp3"
    rendered_mp4_path = out_dir / f"{base_name}_vertical.mp4"

    # -------------------------------------------------------------
    # [3/7] Transcrição de Áudio com Timestamps
    # -------------------------------------------------------------
    print("\n[3/7] 🎙️  Transcrevendo áudio com timestamps precisos...")
    transcriber = Transcriber(mock_mode=mock)
    raw_segments = transcriber.transcribe(video_path=video_path)
    transcript_data = [seg.to_dict() for seg in raw_segments]
    transcript_json_path.write_text(
        json.dumps(transcript_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"   {len(raw_segments)} segmentos de áudio identificados.")

    # -------------------------------------------------------------
    # [4/7] Tradução Inteligente Gamer pt-BR & Roteirização (Agente 02)
    # -------------------------------------------------------------
    print("\n[4/7] 🧠 Traduzindo com inteligência artificial para pt-BR natural...")
    translator = AITranslator(offline_priority=offline)
    localized_segments = translator.translate_segments(raw_segments, preserve_timing=True)
    
    original_script_analysis = None
    if clearance.license_type == LicenseType.UNAUTHORIZED or not clearance.allowed_to_republish_source:
        print("   ⚠️ Material de terceiro não autorizado: gerando roteiro/análise brasileira 100% original...")
        original_script_analysis = translator.generate_original_script(raw_segments)
        script_path = out_dir / f"{base_name}_original_analysis_script.json"
        script_path.write_text(
            json.dumps(original_script_analysis, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    localized_data = [seg.to_dict() for seg in localized_segments]
    localized_json_path.write_text(
        json.dumps(localized_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"   Tradução concluída. Gírias gamers e hooks virais aplicados.")

    # -------------------------------------------------------------
    # [5/7] Dublagem Neural Brasileira Edge-TTS (Agente 03)
    # -------------------------------------------------------------
    narration_file = None
    if enable_tts:
        print(f"\n[5/7] 🗣️  Sintetizando voz neural brasileira ({voice_name}) via Edge-TTS...")
        try:
            voice_engine = VoiceEngine(default_voice=voice_name)
            narration_file = voice_engine.generate_narration_track(
                segments=localized_segments,
                output_audio_path=narration_audio_path,
            )
            print(f"   Trilha de narração mixada gerada: {narration_file} ({narration_file.stat().st_size} bytes)")
        except Exception as e:
            print(f"   [AVISO] Falha na síntese de voz TTS: {e}. Prosseguindo sem dublagem...")
            narration_file = None
    else:
        print("\n[5/7] ⏩ Dublagem neural desativada (--no-tts).")

    # -------------------------------------------------------------
    # [6/7] Geração de Legendas Sincronizadas
    # -------------------------------------------------------------
    print("\n[6/7] 📝 Gerando legendas sincronizadas (.srt, .vtt, .ass)...")
    sub_files = export_subtitles(
        localized_segments,
        output_prefix=out_dir / f"{base_name}_subtitles",
        formats=("srt", "vtt", "ass"),
    )
    print(f"   Legendas exportadas: {list(sub_files.keys())}")

    # -------------------------------------------------------------
    # [7/7] Renderização Vertical 9:16 (1080x1920) (Agente 04)
    # -------------------------------------------------------------
    print(f"\n[7/7] 🎬 Renderizando vídeo vertical 9:16 (1080x1920) com identidade NOITE 86...")
    subtitle_to_burn = sub_files.get("srt") if burn_subtitles else None
    rendered_output = render_vertical_video(
        input_video=video_path,
        output_video=rendered_mp4_path,
        subtitle_path=subtitle_to_burn,
        cta_text=cta_text,
        header_text=header_text,
        narration_audio=narration_file,
        mode=mode,
    )
    print(f"   Vídeo vertical renderizado com sucesso: {rendered_output} ({rendered_output.stat().st_size} bytes)")

    summary = {
        "status": "success",
        "input_source": input_source,
        "license_clearance": clearance.to_dict(),
        "artifacts": {
            "rights_clearance": str(rights_json_path),
            "transcript_json": str(transcript_json_path),
            "localized_json": str(localized_json_path),
            "narration_audio": str(narration_file) if narration_file else None,
            "subtitles_srt": str(sub_files.get("srt", "")),
            "subtitles_vtt": str(sub_files.get("vtt", "")),
            "subtitles_ass": str(sub_files.get("ass", "")),
            "rendered_video": str(rendered_output),
        },
        "metrics": {
            "segments_count": len(localized_segments),
            "output_size_bytes": rendered_output.stat().st_size,
            "voice_used": voice_name if narration_file else None,
            "rights_authorized": clearance.allowed_to_republish_source,
        },
    }

    report_path = out_dir / f"{base_name}_pipeline_report.json"
    report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n📋 Relatório completo da operação salvo em: {report_path}")
    print("=" * 60)
    return summary


def main():
    parser = argparse.ArgumentParser(
        prog="video_pipeline",
        description="OPERAÇÃO NOITE 86 — Fábrica Inteligente de Vídeos para TikTok, Reels e Shorts",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Comandos disponíveis")

    process_parser = subparsers.add_parser("process", help="Processar e localizar vídeo")
    process_parser.add_argument(
        "--input", "-i",
        dest="input_source",
        default="mock",
        help="Caminho do arquivo local de vídeo (.mp4), URL online ou 'mock'",
    )
    process_parser.add_argument(
        "--output-dir", "-o",
        dest="output_dir",
        default="./output_noite86",
        help="Diretório onde os arquivos gerados serão salvos",
    )
    process_parser.add_argument(
        "--license", "-l",
        dest="license_type",
        choices=["own_content", "explicit_permission", "public_trailer", "unauthorized"],
        default="own_content",
        help="Tipo de licença/autorização do vídeo (Agente 05)",
    )
    process_parser.add_argument(
        "--license-details",
        dest="license_details",
        default=None,
        help="Detalhes ou contrato de licença",
    )
    process_parser.add_argument(
        "--voice",
        dest="voice_name",
        default="pt-BR-AntonioNeural",
        help="Voz neural Edge-TTS (ex: pt-BR-AntonioNeural, pt-BR-FranciscaNeural)",
    )
    process_parser.add_argument(
        "--no-tts",
        dest="enable_tts",
        action="store_false",
        default=True,
        help="Desativar síntese e mixagem de voz neural",
    )
    process_parser.add_argument(
        "--cta",
        dest="cta_text",
        default="COLEÇÃO NOITE 86 // LINK NA BIO",
        help="Texto do CTA comercial exibido no rodapé do vídeo",
    )
    process_parser.add_argument(
        "--header",
        dest="header_text",
        default="🚨 NOITE 86 // GTA 6 BRASIL 🚨",
        help="Texto do banner de topo do vídeo",
    )
    process_parser.add_argument(
        "--mode",
        choices=["blur_padding", "crop_center"],
        default="blur_padding",
        help="Modo de enquadramento vertical 9:16 (padrão: blur_padding)",
    )
    process_parser.add_argument(
        "--no-burn-subtitles",
        dest="burn_subtitles",
        action="store_false",
        default=True,
        help="Não queimar legendas diretamente no vídeo",
    )
    process_parser.add_argument(
        "--mock",
        action="store_true",
        default=False,
        help="Executar em modo mock ultra-rápido com vídeo sintético",
    )
    process_parser.add_argument(
        "--offline",
        action="store_true",
        default=False,
        help="Forçar tradução offline sem chamadas externas",
    )

    args, unknown = parser.parse_known_args()

    if args.subcommand is None:
        args = process_parser.parse_args()

    out_dir = Path(args.output_dir)
    result = process_video_pipeline(
        input_source=args.input_source,
        output_dir=out_dir,
        license_type=args.license_type,
        license_details=args.license_details,
        mock=args.mock or args.input_source == "mock",
        cta_text=args.cta_text,
        header_text=args.header_text,
        voice_name=args.voice_name,
        enable_tts=args.enable_tts,
        mode=args.mode,
        burn_subtitles=args.burn_subtitles,
        offline=args.offline,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
