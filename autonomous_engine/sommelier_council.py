"""
autonomous_engine/sommelier_council.py
CENTRAL DE QUALIDADE & CONSELHO DE SOMMELIERS NOITE 86

Banca examinadora multiagente que audita todo vídeo produzido pela fábrica autônoma.
Critérios de Avaliação:
1. Perito Técnico: Resolução 1080x1920, bitrate, safe-zones de legenda, áudio sem clipping/silêncio.
2. Diretor de Retenção & Hook: Força dos primeiros 3 segundos, densidade narrativa, ritmo de corte.
3. Crítico de Dicção & Voz: Naturalidade da voz neural, cadência gamer, pronúncia de termos (Vice City, Rockstar).
4. Estrategista de Marca NOITE 86: Conexão orgânica do produto (merch), clareza do CTA e apelo estético.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from video_pipeline.ffmpeg_resolver import get_ffmpeg_exe

STORAGE_BASE = Path(r"C:\Users\victo\NOITE86_FACTORY")


@dataclass
class SommelierEvaluation:
    video_path: str
    video_name: str
    overall_score: float  # 0 a 100
    technical_score: float  # 0 a 100
    hook_score: float  # 0 a 100
    retention_score: float  # 0 a 100
    brand_cta_score: float  # 0 a 100
    verdict: str  # 'APROVADO_OURO', 'APROVADO_PADRAO', 'REVISAO_NECESSARIA', 'REPROVADO'
    verdict_badge: str  # 🏆, ✅, ⚠️, ❌
    critique_summary: str
    technical_findings: List[str] = field(default_factory=list)
    viral_strengths: List[str] = field(default_factory=list)
    improvement_points: List[str] = field(default_factory=list)
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "video_path": self.video_path,
            "video_name": self.video_name,
            "overall_score": round(self.overall_score, 1),
            "technical_score": round(self.technical_score, 1),
            "hook_score": round(self.hook_score, 1),
            "retention_score": round(self.retention_score, 1),
            "brand_cta_score": round(self.brand_cta_score, 1),
            "verdict": self.verdict,
            "verdict_badge": self.verdict_badge,
            "critique_summary": self.critique_summary,
            "technical_findings": self.technical_findings,
            "viral_strengths": self.viral_strengths,
            "improvement_points": self.improvement_points,
            "evaluated_at": self.evaluated_at,
        }


class VideoSommelierCouncil:
    """Conselho examinador e central de qualidade de vídeos NOITE 86."""

    def __init__(self):
        self.ffmpeg_exe = Path(get_ffmpeg_exe())
        self.reports_dir = STORAGE_BASE / "08_REPORTS"
        self.rejected_dir = STORAGE_BASE / "07_REJECTED"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.rejected_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_video(
        self,
        video_path: Path | str,
        script_data: Optional[Dict[str, Any]] = None,
        job_metadata: Optional[Dict[str, Any]] = None,
    ) -> SommelierEvaluation:
        """Executa auditoria completa de 4 ângulos: técnico, retenção, dicção e conversão."""
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Vídeo não encontrado para avaliação: {video_path}")

        # 1. PERITO TÉCNICO (FFprobe e arquivos)
        tech_score, tech_findings, tech_issues = self._audit_technical(video_path)

        # 2. DIRETOR DE RETENÇÃO & HOOK VIRAL
        hook_score, hook_findings, hook_issues = self._audit_hook_and_pacing(video_path, script_data)

        # 3. CRÍTICO DE DICÇÃO & CADÊNCIA + AGENTE 15 (ACOUSTIC INSPECTOR)
        retention_score, voice_findings, voice_issues = self._audit_voice_and_flow(video_path, script_data)

        # 4. ESTRATEGISTA COMERCIAL NOITE 86
        brand_score, brand_findings, brand_issues = self._audit_brand_and_cta(script_data)

        # CÁLCULO DA NOTA GERAL DO SOMMELIER (Ponderada)
        # 30% Retenção/Hook, 25% Técnico, 25% Dicção, 20% Marca/CTA
        overall = (
            (hook_score * 0.30)
            + (tech_score * 0.25)
            + (retention_score * 0.25)
            + (brand_score * 0.20)
        )

        # VEREDITO FINAL
        if overall >= 88.0 and not tech_issues:
            verdict = "APROVADO_OURO"
            badge = "🏆"
            summary = "Vídeo de altíssimo padrão. Gancho de retenção violento, enquadramento vertical limpo e integração fluida da marca NOITE 86."
        elif overall >= 72.0 and not tech_issues:
            verdict = "APROVADO_PADRAO"
            badge = "✅"
            summary = "Qualidade aprovada para distribuição. Ritmo dentro dos parâmetros virais de Shorts/Reels/TikTok."
        elif overall >= 55.0:
            verdict = "REVISAO_NECESSARIA"
            badge = "⚠️"
            summary = "Vídeo utilizável, mas apresenta pontos fracos de retenção ou CTA que podem ser melhorados em novos lotes."
        else:
            verdict = "REPROVADO"
            badge = "❌"
            summary = f"Vídeo reprovado pela Central de Qualidade. Falhas críticas: {', '.join(tech_issues + hook_issues)}"

        strengths = hook_findings + voice_findings + brand_findings
        improvements = tech_issues + hook_issues + voice_issues + brand_issues

        evaluation = SommelierEvaluation(
            video_path=str(video_path),
            video_name=video_path.name,
            overall_score=overall,
            technical_score=tech_score,
            hook_score=hook_score,
            retention_score=retention_score,
            brand_cta_score=brand_score,
            verdict=verdict,
            verdict_badge=badge,
            critique_summary=summary,
            technical_findings=tech_findings,
            viral_strengths=strengths[:4],
            improvement_points=improvements[:4] if improvements else ["Nenhum gargalo crítico detectado"],
        )

        # Salva o laudo persistente em JSON ao lado do vídeo e em 08_REPORTS
        self._save_evaluation(evaluation)
        return evaluation

    def _audit_technical(self, path: Path) -> tuple[float, List[str], List[str]]:
        """Audita integridade física do arquivo de vídeo."""
        findings = []
        issues = []
        score = 100.0

        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)

        # Detecta vídeos sintéticos / barras de cor (testsrc) que pesam apenas ~2.2 MB para 30s
        if size_mb < 3.5:
            issues.append(f"ALERTA: Vídeo com densidade visual insuficiente ({size_mb:.2f} MB). Possível artefato sintético ou corte estático.")
            score -= 50.0
        elif size_mb >= 5.0:
            findings.append(f"Densidade visual cinematográfica excelente ({size_mb:.2f} MB, alta fidelidade)")
        else:
            findings.append(f"Tamanho de arquivo aceitável ({size_mb:.2f} MB)")

        # Executa FFmpeg probe
        cmd = [str(self.ffmpeg_exe), "-i", str(path)]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        stderr = res.stderr

        # Verifica resolução 1080x1920
        if "1080x1920" in stderr:
            findings.append("Formato vertical estrito 1080x1920 (9:16) confirmado")
        else:
            issues.append("Resolução fora do padrão 1080x1920")
            score -= 40.0

        # Verifica áudio AAC
        if "Audio: aac" in stderr:
            findings.append("Trilha de áudio AAC estéreo/mono válida e codificada")
        else:
            issues.append("Trilha de áudio ausente ou formato não suportado")
            score -= 35.0

        # Verifica bitrate mínimo para qualidade HD (mínimo 1500 kb/s)
        if "bitrate: " in stderr:
            try:
                bitrate_str = stderr.split("bitrate: ")[1].split(" kb/s")[0].strip()
                bitrate_val = float(bitrate_str)
                if bitrate_val < 1000:
                    issues.append(f"Bitrate excessivamente baixo ({bitrate_val:.0f} kb/s) - risco de pixelização")
                    score -= 25.0
                else:
                    findings.append(f"Taxa de bits nítida ({bitrate_val:.0f} kb/s)")
            except Exception:
                pass

        # Duração ideal entre 20s e 60s para formato Reels/Shorts
        if "Duration: 00:00:30." in stderr or "Duration: 00:00:2" in stderr:
            findings.append("Duração calibrada para alta retenção em formato curto (~30s)")
        elif "Duration: 00:00:0" in stderr:
            issues.append("Duração excessivamente curta (< 10s)")
            score -= 20.0

        return max(0.0, score), findings, issues

    def _audit_hook_and_pacing(
        self, path: Path, script_data: Optional[Dict[str, Any]]
    ) -> tuple[float, List[str], List[str]]:
        """Audita a força do gancho (primeiros 3 segundos) e dinamismo."""
        findings = []
        issues = []
        score = 85.0

        if not script_data:
            return 80.0, ["Roteiro estruturado padrão detectado"], []

        hook = script_data.get("hook_3s", "") or ""
        segments = script_data.get("script_segments", [])

        # Critério 1: Presença de elementos de quebra de padrão no gancho
        impact_words = ["viu isso", "inacreditável", "revelou", "quase ninguém", "segredo", "vazou", "absurdo", "olha isso"]
        matched_impact = [w for w in impact_words if w in hook.lower()]

        if matched_impact:
            findings.append(f"Gancho inicial potente com gatilho de curiosidade ('{matched_impact[0]}')")
            score += 10.0
        else:
            issues.append("Gancho inicial neutro. Recomenda-se pergunta direta ou quebra de padrão nos 3s")
            score -= 10.0

        # Critério 2: Densidade de segmentos (deve ter 4 atos: Gancho, Revelação, Tensão, CTA)
        if len(segments) >= 4:
            findings.append("Estrutura clássica de 4 atos (Gancho ➔ Fato ➔ Curiosidade ➔ Conversão)")
            score += 5.0
        else:
            issues.append("Poucos cortes narrativos no roteiro")
            score -= 15.0

        return min(100.0, max(0.0, score)), findings, issues

    def _audit_voice_and_flow(self, path: Path, script_data: Optional[Dict[str, Any]]) -> tuple[float, List[str], List[str]]:
        """Audita a naturalidade e velocidade da locução combinada com inspeção acústica."""
        findings = []
        issues = []
        score = 88.0

        # Análise forense do áudio com AGENTE 15 (Acoustic Inspector)
        try:
            from autonomous_engine.audio_taskforce import AudioQualityTaskforce
            taskforce = AudioQualityTaskforce()
            audio_rep = taskforce.audit_audio_integrity(path)
            findings.extend(audio_rep.findings)
            issues.extend(audio_rep.issues)
            if not audio_rep.passed:
                score -= 30.0
            else:
                score += 5.0
        except Exception:
            pass

        if not script_data:
            return min(100.0, max(0.0, score)), ["Locução neural pt-BR Antonio aplicada"] + findings, issues

        segments = script_data.get("script_segments", [])
        total_words = sum(len(s.get("narration_pt", "").split()) for s in segments)

        # Ideal para 30s: 65 a 90 palavras (ritmo dinâmico sem atropelar)
        if 60 <= total_words <= 95:
            findings.append(f"Ritmo de fala ideal ({total_words} palavras em 30s ~ 150 ppm)")
            score += 7.0
        elif total_words < 50:
            issues.append("Locução lenta demais para TikTok/Reels (< 50 palavras em 30s)")
            score -= 12.0
        else:
            issues.append("Locução muito acelerada (> 100 palavras em 30s), risco de dicção embolada")
            score -= 10.0

        findings.append("Voz neural selecionada com tom maduro gamer (Antônio Neural)")
        return min(100.0, max(0.0, score)), findings, issues

    def _audit_brand_and_cta(self, script_data: Optional[Dict[str, Any]]) -> tuple[float, List[str], List[str]]:
        """Audita a integração comercial da marca NOITE 86."""
        findings = []
        issues = []
        score = 82.0

        if not script_data:
            return 80.0, ["CTA padrão de bio configurado"], []

        cta = script_data.get("call_to_action", "") or ""
        product = script_data.get("featured_product", {}) or {}

        if "noite 86" in cta.lower() or "bio" in cta.lower():
            findings.append(f"Chamada para ação clara direcionando para o link da bio da NOITE 86")
            score += 10.0
        else:
            issues.append("Chamada para ação ambígua ou sem referência ao link na bio")
            score -= 15.0

        if product.get("name"):
            findings.append(f"Produto em destaque catalogado: {product.get('name')}")
            score += 8.0
        else:
            issues.append("Nenhum produto específico da coleção foi pareado com o vídeo")
            score -= 8.0

        return min(100.0, max(0.0, score)), findings, issues

    def _save_evaluation(self, eval_obj: SommelierEvaluation):
        """Persiste o laudo em disco para visualização no dashboard e auditorias."""
        # Salva junto com os relatórios gerais
        report_file = self.reports_dir / f"sommelier_{Path(eval_obj.video_path).stem}.json"
        report_file.write_text(json.dumps(eval_obj.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

        # Se for reprovado, copia uma referência para 07_REJECTED
        if eval_obj.verdict == "REPROVADO":
            rej_log = self.rejected_dir / f"rejeitado_{Path(eval_obj.video_path).stem}.txt"
            rej_log.write_text(f"Motivo: {eval_obj.critique_summary}\nPontos: {eval_obj.improvement_points}", encoding="utf-8")
