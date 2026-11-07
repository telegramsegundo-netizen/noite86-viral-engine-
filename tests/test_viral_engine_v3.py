"""
tests/test_viral_engine_v3.py
Suíte de Testes Automatizados da Operação Autônoma NOITE 86 V3.0 (Testes A a E)
Validação de:
- Radar Internacional (Fontes reais e públicas)
- Ranking com VIRAL_SCORE sem métricas inventadas
- Triagem de direitos autorais e bloqueio de republicação crua
- Roteirização autoral brasileira e briefs de produto
- Fila persistente transacional SQLite com recuperação de falhas
- Execução de ciclo do Comandante Central
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
import pytest

from autonomous_engine.commander import AutonomousCommander
from autonomous_engine.content_strategist import BrazilianContentStrategist
from autonomous_engine.production_queue import JobStatus, ProductionQueue
from autonomous_engine.radar_engine import DiscoveredItem, ViralRadarEngine
from autonomous_engine.rights_clearance import ProductionRoute, RightsClearanceOfficer
from autonomous_engine.viral_analyst import ViralIntelligenceAnalyst


class TesteA_RadarInternacional:
    """TESTE A: Descobrir novas referências em fontes reais permitidas."""

    def test_radar_scans_and_extracts_real_sources(self):
        radar = ViralRadarEngine()
        assert len(radar.sources) >= 4
        
        # Executa varredura real
        items = radar.scan_all_sources()
        assert isinstance(items, list)
        assert len(items) > 0, "Radar deve encontrar pelo menos 1 oportunidade em fontes reais"

        sample = items[0]
        assert sample.id != ""
        assert sample.title != ""
        assert sample.url.startswith("http")
        assert sample.platform in ("youtube", "reddit", "google_trends")


class TesteB_RankingViralScore:
    """TESTE B: Classificar candidatos e gerar ranking sem inventar métricas."""

    def test_analyst_ranks_and_scores_items(self):
        analyst = ViralIntelligenceAnalyst()
        items = [
            DiscoveredItem(
                id="item_01",
                platform="youtube",
                source_name="Rockstar Games",
                author="Rockstar Games",
                title="Grand Theft Auto VI Official Trailer 2 Vice City Launch",
                url="https://youtube.com/watch?v=gta6_real_test",
                published_at="2026-11-07T12:00:00Z",
                discovered_at="2026-11-07T12:30:00Z",
                summary="Exclusive gameplay reveal of Vice City, Lucia and Jason.",
                niche_tags=["gta 6", "vice city", "trailer", "lucia"],
                raw_metrics={"platform_weight": 1.0}
            ),
            DiscoveredItem(
                id="item_02",
                platform="reddit",
                source_name="r/GTA6",
                author="gamer123",
                title="Random discussion about old GTA games",
                url="https://reddit.com/r/GTA6/comments/old_game",
                published_at="2026-10-01T12:00:00Z",
                discovered_at="2026-11-07T12:30:00Z",
                summary="Just reminiscing about GTA 3.",
                niche_tags=[],
                raw_metrics={"platform_weight": 0.5}
            )
        ]

        scored = analyst.analyze_and_rank(items)
        assert len(scored) == 2
        # Item 01 com GTA 6 + Trailer + Rockstar deve ter score muito superior
        assert scored[0].item.id == "item_01"
        assert scored[0].viral_score >= 60.0
        assert scored[0].priority_level in ("HIGH", "MEDIUM")
        assert "🚨" in scored[0].suggested_hook_pt


class TesteC_D_DireitosERoteiroAutoral:
    """TESTE C & D: Triagem de direitos e geração de conteúdo autoral transformativo."""

    def test_unauthorized_content_triggers_original_transformative_route(self):
        officer = RightsClearanceOfficer()
        analyst = ViralIntelligenceAnalyst()
        strategist = BrazilianContentStrategist()

        unauthorized_item = DiscoveredItem(
            id="third_party_leak_01",
            platform="youtube",
            source_name="RandomLeaker",
            author="LeakerChannel",
            title="MASSIVE GTA 6 LEAKED FOOTAGE OF POLICE CHASE",
            url="https://youtube.com/watch?v=unauthorized_clip",
            published_at="2026-11-07T10:00:00Z",
            discovered_at="2026-11-07T10:30:00Z",
            license_category="unauthorized",
            niche_tags=["gta 6", "leak"]
        )

        opp = analyst.analyze_and_rank([unauthorized_item])[0]
        verdict = officer.evaluate_opportunity(opp)

        # Regra inegociável: Não republicar vídeo de terceiro sem autorização!
        assert verdict.can_use_source_media is False
        assert verdict.requires_original_script is True
        assert verdict.route == ProductionRoute.ORIGINAL_TRANSFORMATIVE

        # Gerar roteiro autoral brasileiro com produto da loja
        briefing = strategist.create_briefing(opp, verdict)
        assert len(briefing.script_segments) >= 3
        assert "NOITE 86" in briefing.call_to_action
        assert briefing.featured_product["id"] in ("VC-APP-003", "VC-AUD-001", "VC-LGT-001")


class TesteE_FilaPersistenteERecuperacao:
    """TESTE E: Simulação de interrupção e recuperação de tarefas na fila persistente."""

    def test_queue_enqueue_claim_and_fail_recovery(self, tmp_path):
        db_file = tmp_path / "test_queue.db"
        queue = ProductionQueue(db_path=db_file)

        # 1. Enfileirar
        job_id = queue.enqueue(
            opportunity_id="opp_recover_01",
            title="GTA 6 Physics Breakdown",
            priority=85,
            source_url="https://youtube.com/test",
            route="original_transformative",
            briefing_dict={"test": True}
        )
        assert job_id == "job_opp_recover_01"

        # 2. Reivindicar com lock curto (1 segundo) para simular crash do worker
        claimed = queue.claim_next_job(lock_seconds=1)
        assert claimed is not None
        assert claimed.id == job_id
        assert claimed.status == JobStatus.PROCESSING

        # Nenhum job pendente no momento
        assert queue.claim_next_job() is None

        # 3. Aguarda lock expirar para simular que o trabalhador morreu/PC reiniciou
        time.sleep(1.2)

        # 4. Próxima checagem deve recuperar o job abandonado automaticamente!
        recovered = queue.claim_next_job(lock_seconds=60)
        assert recovered is not None
        assert recovered.id == job_id
        assert recovered.status == JobStatus.PROCESSING

        # 5. Concluir job
        queue.complete_job(job_id, {"rendered_video": "test.mp4"})
        stats = queue.get_stats()
        assert stats["completed"] == 1
        assert stats["processing"] == 0


class TesteF_CicloDoComandante:
    """TESTE F: Execução do ciclo mestre do AutonomousCommander."""

    def test_commander_cycle_runs_without_crashing(self):
        commander = AutonomousCommander()
        summary = commander.run_cycle(max_queue_items=1, process_jobs=False)
        assert summary["radar_findings_count"] > 0
        assert summary["opportunities_ranked_count"] > 0
        assert "queue_stats" in summary
