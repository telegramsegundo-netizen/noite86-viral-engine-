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
        """Constrói uma narrativa de 4 atos 100% dinâmica, personalizada e sem duplicações de texto."""
        title_lower = opp.item.title.lower()
        summary_clean = (opp.item.summary or "").strip()
        if any(w in summary_clean.lower() for w in ["check out", "subscribe", "edition launch", "trailer for", "developed by"]):
            summary_clean = ""

        # ATO 2: Análise central temática adaptada ao assunto real
        if summary_clean and len(summary_clean) > 25:
            act_2 = f"Presta atenção nesse detalhe: {summary_clean}"
        elif any(k in title_lower for k in ["carro", "veículo", "motor", "retro", "custom"]):
            act_2 = "A física dos motores e a customização dos carros anos 80 em Vice City tão simplesmente brutais."
        elif any(k in title_lower for k in ["mapa", "tamanho", "mundo", "colossal"]):
            act_2 = "O mapa de Leonida é colossal, com cidades vizinhas, praias e áreas rurais completamente vivas."
        elif any(k in title_lower for k in ["jason", "lucia", "dupla", "casal"]):
            act_2 = "A relação de Jason e Lucia traz uma mecânica de assaltos cooperativos com química eletrizante."
        elif any(k in title_lower for k in ["água", "chuva", "tempestade", "mar"]):
            act_2 = "A simulação hidrodinâmica das ondas e as tempestades tropicais em Vice Beach redefinem os gráficos dos games."
        elif any(k in title_lower for k in ["polícia", "assalto", "tiroteio", "fuga"]):
            act_2 = "A inteligência artificial das forças táticas cerca cada quarteirão com táticas agressivas de cerco."
        elif any(k in title_lower for k in ["balada", "malibu", "noite", "clube", "som"]):
            act_2 = "O retorno das casas noturnas e a vida underground de Vice City capturam a energia máxima dos anos 80."
        elif any(k in title_lower for k in ["ia", "npc", "pedestre"]):
            act_2 = "Os pedestres reagem às suas roupas, clima e atitudes, criando uma metrópole que respira por conta própria."
        elif any(k in title_lower for k in ["animal", "selvagem", "jacaré", "pântano"]):
            act_2 = "A vida selvagem nos pântanos e canais de Leonida é impiedosa e interage diretamente com o mapa."
        else:
            act_2 = "O nível de detalhes e a densidade visual que a Rockstar construiu em Leonida superam qualquer expectativa."

        # ATO 3: Clímax narrativo de retenção específico
        if any(k in title_lower for k in ["carro", "veículo", "motor", "retro"]):
            act_3 = "O ronco dos motores sob a luz neon faz você sentir a velocidade no asfalto quente."
        elif any(k in title_lower for k in ["mapa", "tamanho", "mundo"]):
            act_3 = "São centenas de interiores exploráveis em alta definição sem nenhuma tela de carregamento."
        elif any(k in title_lower for k in ["jason", "lucia", "dupla"]):
            act_3 = "A lealdade e o perigo entre os dois promete ser a história criminal mais marcante já contada."
        elif any(k in title_lower for k in ["água", "chuva", "tempestade"]):
            act_3 = "Cada gota no para-brisa e cada reflexo nas poças d'água parecem filmagem cinematográfica real."
        elif any(k in title_lower for k in ["balada", "malibu", "noite", "trilha"]):
            act_3 = "A trilha sonora nostálgica com sintetizadores vintage faz você querer viver em 1986 agora mesmo."
        elif any(k in title_lower for k in ["polícia", "assalto", "tiroteio"]):
            act_3 = "A adrenalina da fuga com helicópteros vasculhando vielas coloca o jogador na ponta da cadeira."
        else:
            act_3 = "A Rockstar elevou o padrão para um patamar inalcançável para qualquer outro estúdio."

        act_4 = f"Quer entrar na vibe de Vice City agora? Conheça a {product['name']} da coleção oficial NOITE 86 no link da bio!"

        return [
            ScriptSegment(
                id=1,
                start_sec=0.0,
                end_sec=4.0,
                narration_pt=opp.suggested_hook_pt,
                visual_cue="Corte dinâmico 9:16 com zoom in e banner de alerta no topo",
                on_screen_text="🚨 NOVO DETALHE DE GTA 6!"
            ),
            ScriptSegment(
                id=2,
                start_sec=4.1,
                end_sec=13.0,
                narration_pt=act_2,
                visual_cue="Panorâmica com fundo em boxblur e destaque nos detalhes da cena",
                on_screen_text="DETALHE REVELADO"
            ),
            ScriptSegment(
                id=3,
                start_sec=13.1,
                end_sec=21.5,
                narration_pt=act_3,
                visual_cue="Gameplay e detalhes dos carros clássicos anos 80 sob as luzes neon",
                on_screen_text="ATMOSFERA PURA"
            ),
            ScriptSegment(
                id=4,
                start_sec=21.6,
                end_sec=28.5,
                narration_pt=act_4,
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
