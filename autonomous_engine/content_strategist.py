"""
autonomous_engine/content_strategist.py
AGENTE 06 — Brazilian Content Strategist
AGENTE 10 — Creative Asset Director
AGENTE 11 — Commercial Content Strategist

Cria o briefing de produção, roteirização autoral brasileira (0-30s),
ganchos virais de retenção, conexão de produto com a loja NOITE 86
e pacote de postagem pronto para TikTok, Reels e Shorts.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from autonomous_engine.rights_clearance import ProductionRoute, RightsVerdict
from autonomous_engine.viral_analyst import ScoredOpportunity

STORAGE_BASE = Path(r"C:\Users\victo\NOITE86_FACTORY")


class ScriptSegment(BaseModel):
    id: int
    start_sec: float
    end_sec: float
    narration_pt: str
    visual_cue: str
    on_screen_text: str


class ProductionBriefing(BaseModel):
    briefing_id: str
    opportunity_id: str
    title_br: str
    viral_score: float
    route: ProductionRoute
    hook_3s: str
    script_segments: List[ScriptSegment]
    featured_product: Dict[str, Any]
    call_to_action: str
    post_caption_social: str
    recommended_audio_mood: str
    hashtags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class BrazilianContentStrategist:
    """Estrategista de narrativa, estética Vice City e conversão da marca NOITE 86."""

    CATALOG_PRODUCTS = [
        {
            "id": "VC-APP-003",
            "name": "Camiseta 'Miami Overdrive 84' Heavyweight",
            "price_str": "R$ 139,90",
            "pitch": "A camiseta vintage streetwear com estética neon que todo fã de Vice City precisa no guarda-roupa."
        },
        {
            "id": "VC-AUD-001",
            "name": "Mini Boombox Cassette 1986 Bluetooth",
            "price_str": "R$ 179,90",
            "pitch": "O som retrô dos anos 80 repaginado com Bluetooth 5.3 para transformar o seu quarto no Vice District."
        },
        {
            "id": "VC-LGT-001",
            "name": "Luminária Neon Laser 'Ocean Drive Nocturne'",
            "price_str": "R$ 149,90",
            "pitch": "A iluminação de acrílico neon que recria a Ocean Drive molhada de chuva na sua mesa gamer."
        }
    ]

    def create_briefing(self, opp: ScoredOpportunity, verdict: RightsVerdict) -> ProductionBriefing:
        """Produz o briefing completo com roteiro autoral de 30 segundos."""
        # Seleciona o produto em rotação baseado nas tags
        product = self._match_product(opp)

        # Monta os segmentos de roteiro sincronizado (0 a 30s)
        segments = self._build_script(opp, verdict, product)

        title_br = f"GTA 6: {opp.item.title[:45]} // Análise Brasil"
        hook = opp.suggested_hook_pt

        cta = f"COLEÇÃO NOITE 86 // {product['name'].upper()} // LINK NA BIO"

        caption = (
            f"🚨 NOVO DETALHE DE GTA 6 REVELADO! 🌴\n\n"
            f"{opp.recommended_angle_br}\n\n"
            f"Você acha que esse vai ser o jogo mais absurdo da história dos games? Deixa nos comentários!\n\n"
            f"🛍️ Camisetas e itens colecionáveis exclusivos da estética Vice City disponíveis na @noite86. Link na bio!\n\n"
            f"#gta6 #vicecity #gta6brasil #rockstargames #noite86 #gamerbr #streetwear"
        )

        briefing = ProductionBriefing(
            briefing_id=f"brief_{opp.item.id}",
            opportunity_id=opp.item.id,
            title_br=title_br,
            viral_score=opp.viral_score,
            route=verdict.route,
            hook_3s=hook,
            script_segments=segments,
            featured_product=product,
            call_to_action=cta,
            post_caption_social=caption,
            recommended_audio_mood="Synthwave retrowave dark electro 110bpm",
            hashtags=["gta6", "vicecity", "gta6brasil", "rockstargames", "noite86"]
        )

        self._save_briefing(briefing)
        return briefing

    def _match_product(self, opp: ScoredOpportunity) -> Dict[str, Any]:
        """Associa inteligentemente o tema da notícia ao produto mais afim do catálogo."""
        tags = [t.lower() for t in opp.item.niche_tags]
        if "car" in tags or "graphics" in tags or "physics" in tags:
            return self.CATALOG_PRODUCTS[0]  # Camiseta Miami Overdrive
        elif "trailer" in tags or "music" in tags or "release date" in tags:
            return self.CATALOG_PRODUCTS[1]  # Boombox Cassette
        else:
            return self.CATALOG_PRODUCTS[2]  # Luminária Ocean Drive

    def _build_script(self, opp: ScoredOpportunity, verdict: RightsVerdict, product: Dict[str, Any]) -> List[ScriptSegment]:
        """Constrói uma narrativa de 4 atos: Gancho (0-4s), Análise (4-14s), Clímax (14-22s), CTA (22-30s)."""
        # Limpa e filtra o contexto para garantir português brasileiro puro e conciso
        facts_raw = opp.item.summary or ""
        is_english_raw = any(w in facts_raw.lower() for w in ["check out", "subscribe", "edition launch", "trailer for", "developed by", "players can", "official trailer"])
        if is_english_raw or len(facts_raw.strip()) < 15:
            facts = "A densidade urbana e a iluminação volumétrica colocam Leonida num patamar nunca antes visto nos videogames."
        else:
            facts = facts_raw[:120].strip()

        return [
            ScriptSegment(
                id=1,
                start_sec=0.0,
                end_sec=4.5,
                narration_pt=opp.suggested_hook_pt,
                visual_cue="Corte dinâmico 9:16 com zoom in e banner de alerta no topo",
                on_screen_text="🚨 NOVO DETALHE DE GTA 6!"
            ),
            ScriptSegment(
                id=2,
                start_sec=4.6,
                end_sec=14.0,
                narration_pt=f"A física da iluminação e os reflexos em Ocean Drive tão batendo de frente com a realidade. {facts}",
                visual_cue="Panorâmica com fundo em boxblur e destaque nos detalhes da cena",
                on_screen_text="FÍSICA & GRÁFICOS SURREAIS"
            ),
            ScriptSegment(
                id=3,
                start_sec=14.1,
                end_sec=22.5,
                narration_pt="A Rockstar elevou a régua pra outro nível. Nenhum jogo de mundo aberto já chegou perto dessa atmosfera noturna.",
                visual_cue="Gameplay e detalhes dos carros clássicos anos 80 sob as luzes neon",
                on_screen_text="O NOVO PADRÃO DA INDÚSTRIA"
            ),
            ScriptSegment(
                id=4,
                start_sec=22.6,
                end_sec=30.0,
                narration_pt=f"Quer entrar na vibe de Vice City agora? Conheça a {product['name']} da coleção oficial NOITE 86 no link da bio!",
                visual_cue="End-card comercial elegante com o mock do produto e botão de link na bio",
                on_screen_text="COLEÇÃO NOITE 86 // LINK NA BIO"
            )
        ]

    def _save_briefing(self, briefing: ProductionBriefing):
        """Salva o roteiro estruturado na pasta 03_SCRIPTS."""
        try:
            scripts_dir = STORAGE_BASE / "03_SCRIPTS"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            f = scripts_dir / f"{briefing.opportunity_id}_script.json"
            f.write_text(json.dumps(briefing.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
