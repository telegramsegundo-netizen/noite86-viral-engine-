"""
autonomous_engine/commander.py
AGENTE 00 — Autonomous Commander (Comandante Central de Operações)

Coordena todo o fluxo de ponta a ponta:
Radar -> Análise Viral -> Auditoria de Direitos -> Roteirização -> Fila -> Produção -> QA -> Relatórios.
Opera 24/7 de forma contínua com tolerância a falhas e recuperação automática.
"""
from __future__ import annotations

import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from autonomous_engine.content_strategist import BrazilianContentStrategist
from autonomous_engine.local_worker import LocalProductionWorker
from autonomous_engine.production_queue import ProductionQueue
from autonomous_engine.radar_engine import ViralRadarEngine
from autonomous_engine.rights_clearance import RightsClearanceOfficer
from autonomous_engine.viral_analyst import ViralIntelligenceAnalyst

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
STORAGE_BASE = Path(r"C:\Users\victo\NOITE86_FACTORY")


class AutonomousCommander:
    """Comandante Geral da Operação Noite 86."""

    def __init__(self):
        self.radar = ViralRadarEngine()
        self.analyst = ViralIntelligenceAnalyst()
        self.rights_officer = RightsClearanceOfficer()
        self.strategist = BrazilianContentStrategist()
        self.queue = ProductionQueue()
        self.worker = LocalProductionWorker(queue=self.queue)
        self.is_running = False

    def run_cycle(self, max_queue_items: int = 3, process_jobs: bool = True) -> Dict[str, Any]:
        """
        Executa 1 ciclo operacional completo:
        1. Varre fontes com o Radar.
        2. Analisa relevância e pontua VIRAL_SCORE.
        3. Triagem de direitos autorais.
        4. Cria briefings e roteiros em PT-BR.
        5. Enfileira as oportunidades mais quentes.
        6. Processa a fila e renderiza o vídeo se process_jobs=True.
        """
        cycle_start = time.time()
        print("\n" + "=" * 65)
        print("👑 [COMMANDER-00] INICIANDO CICLO OPERACIONAL NOITE 86")
        print("=" * 65)

        # 1. RADAR INTERNACIONAL
        discovered_items = self.radar.scan_all_sources()
        print(f"[Commander] Itens encontrados pelo radar: {len(discovered_items)}")

        # 2. ANÁLISE DE TENDÊNCIAS & VIRAL_SCORE
        ranked_opportunities = self.analyst.analyze_and_rank(discovered_items)
        print(f"[Commander] Oportunidades deduplicadas e ranqueadas: {len(ranked_opportunities)}")

        # 3, 4 & 5. TRIAGEM DE DIREITOS, BRIEFING E ENFILEIRAMENTO
        enqueued_count = 0
        briefings_created = []

        # Seleciona as melhores oportunidades para enfileirar
        for opp in ranked_opportunities[:max_queue_items]:
            verdict = self.rights_officer.evaluate_opportunity(opp)
            briefing = self.strategist.create_briefing(opp, verdict)
            briefings_created.append(briefing)

            # Prioridade baseada no VIRAL_SCORE (arredondado para inteiro)
            priority_int = int(round(opp.viral_score))
            job_id = self.queue.enqueue(
                opportunity_id=opp.item.id,
                title=opp.item.title,
                priority=priority_int,
                source_url=opp.item.url,
                route=verdict.route.value,
                briefing_dict=briefing.to_dict()
            )
            if job_id:
                enqueued_count += 1
                print(f"[Commander] 📥 Enfileirado: {opp.item.title[:45]}... (Score: {opp.viral_score}) => {job_id}")

        # 6. PRODUÇÃO EXECUTIVA (Heavy Worker)
        processed_artifacts = []
        if process_jobs:
            print("\n[Commander] ⚙️ Disparando Local Heavy Worker para produzir jobs pendentes...")
            # Processa até o limite de jobs enfileirados
            for _ in range(max(1, enqueued_count)):
                art = self.worker.process_next_job()
                if art:
                    processed_artifacts.append(art)
                else:
                    break

        # 7. RELATÓRIO OPERACIONAL
        cycle_duration = round(time.time() - cycle_start, 2)
        queue_stats = self.queue.get_stats()

        summary = {
            "cycle_timestamp": datetime.now(timezone.utc).isoformat(),
            "cycle_duration_seconds": cycle_duration,
            "radar_findings_count": len(discovered_items),
            "opportunities_ranked_count": len(ranked_opportunities),
            "top_viral_score": ranked_opportunities[0].viral_score if ranked_opportunities else 0.0,
            "newly_enqueued": enqueued_count,
            "jobs_rendered": len(processed_artifacts),
            "queue_stats": queue_stats,
            "top_candidates": [o.to_dict() for o in ranked_opportunities[:5]],
            "rendered_videos": [a.get("rendered_video") for a in processed_artifacts if a.get("rendered_video")],
        }

        self._save_daily_report(summary)
        print("=" * 65)
        print(f"🏁 [COMMANDER-00] CICLO CONCLUÍDO EM {cycle_duration}s!")
        print(f"📊 Fila total: {queue_stats.get('total')} | Concluídos: {queue_stats.get('completed')} | Pendentes: {queue_stats.get('queued')}")
        print("=" * 65)
        return summary

    def _save_daily_report(self, summary: Dict[str, Any]):
        """Grava relatório na pasta 08_REPORTS em NOITE86_FACTORY."""
        try:
            rep_dir = STORAGE_BASE / "08_REPORTS"
            rep_dir.mkdir(parents=True, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            rep_file = rep_dir / f"daily_operations_report_{today}.json"
            rep_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass


if __name__ == "__main__":
    commander = AutonomousCommander()
    commander.run_cycle(max_queue_items=1, process_jobs=True)
