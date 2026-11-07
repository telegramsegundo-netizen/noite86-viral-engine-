"""
autonomous_engine/viral_analyst.py
AGENTE 04 — Viral Intelligence Analyst

Processa os dados coletados pelo Radar, elimina duplicatas, avalia relevância
cultural para o público brasileiro e calcula o VIRAL_SCORE matemático (0 a 100)
sem inventar métricas ou falsos números.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from autonomous_engine.radar_engine import DiscoveredItem


class ScoredOpportunity(BaseModel):
    item: DiscoveredItem
    viral_score: float
    score_breakdown: Dict[str, float]
    priority_level: str  # HIGH, MEDIUM, LOW
    recommended_angle_br: str
    suggested_hook_pt: str
    status: str = "analyzed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.item.id,
            "title": self.item.title,
            "url": self.item.url,
            "platform": self.item.platform,
            "author": self.item.author,
            "source_name": getattr(self.item, "source_name", None) or self.item.author or "Fonte Internacional",
            "published_at": self.item.published_at,
            "license_category": self.item.license_category,
            "niche_tags": self.item.niche_tags,
            "viral_score": self.viral_score,
            "score_breakdown": self.score_breakdown,
            "priority_level": self.priority_level,
            "recommended_angle_br": self.recommended_angle_br,
            "suggested_hook_pt": self.suggested_hook_pt,
            "status": self.status,
            "thumbnail": self.item.thumbnail,
        }


class ViralIntelligenceAnalyst:
    """Analista de tendências e calculador de potencial viral."""

    HIGH_IMPACT_TERMS = {
        "gta 6": 15, "gta vi": 15, "vice city": 12, "trailer": 10,
        "lucia": 8, "jason": 8, "leak": 10, "gameplay": 8,
        "release date": 7, "map": 7, "physics": 6, "graphics": 6,
        "leonida": 5, "rockstar": 8, "ps5": 4, "xbox": 4
    }

    def analyze_and_rank(self, items: List[DiscoveredItem]) -> List[ScoredOpportunity]:
        """Deduplica e calcula VIRAL_SCORE para cada oportunidade descoberta."""
        deduped = self._deduplicate(items)
        scored: List[ScoredOpportunity] = []

        for item in deduped:
            opportunity = self._score_item(item)
            scored.append(opportunity)

        # Ordena do maior para o menor VIRAL_SCORE
        scored.sort(key=lambda x: x.viral_score, reverse=True)
        return scored

    def _deduplicate(self, items: List[DiscoveredItem]) -> List[DiscoveredItem]:
        """Elimina URLs repetidas e títulos quase idênticos."""
        seen_urls = set()
        seen_normalized_titles = set()
        unique_items = []

        for it in items:
            if it.url in seen_urls:
                continue

            # Normalização de título simples para detectar clones
            norm = re.sub(r"[^a-zA-Z0-9]", "", it.title.lower())
            if norm in seen_normalized_titles:
                continue

            seen_urls.add(it.url)
            seen_normalized_titles.add(norm)
            unique_items.append(it)

        return unique_items

    def _score_item(self, item: DiscoveredItem) -> ScoredOpportunity:
        """
        Calcula VIRAL_SCORE (0 a 100):
        1. Recency Score (max 25 pts)
        2. Keyword Impact (max 35 pts)
        3. Source Authority & Weight (max 25 pts)
        4. Brazilian Cultural & Commercial Fit (max 15 pts)
        """
        # 1. Recency Score (max 25)
        recency_score = 10.0
        try:
            pub_date = datetime.fromisoformat(item.published_at.replace("Z", "+00:00"))
            hours_ago = (datetime.now(timezone.utc) - pub_date).total_seconds() / 3600.0
            if hours_ago <= 24:
                recency_score = 25.0
            elif hours_ago <= 72:
                recency_score = 20.0
            elif hours_ago <= 168: # 7 dias
                recency_score = 15.0
            elif hours_ago <= 720: # 30 dias
                recency_score = 10.0
            else:
                recency_score = 5.0
        except Exception:
            recency_score = 12.0

        # 2. Keyword Impact (max 35)
        text_lower = f"{item.title} {item.summary}".lower()
        kw_points = 0.0
        for kw, pts in self.HIGH_IMPACT_TERMS.items():
            if kw in text_lower:
                kw_points += pts
        kw_score = min(35.0, kw_points)

        # 3. Source Authority (max 25)
        source_weight = item.raw_metrics.get("platform_weight", 0.8)
        # Bônus para canais oficiais ou grandes hubs
        authority_score = min(25.0, source_weight * 25.0)

        # 4. Brazilian Market Fit (max 15)
        # Temas de mistério, carros, gráficos e gameplay geram maior retenção no público BR
        fit_score = 10.0
        if any(w in text_lower for w in ["trailer", "launch", "leak", "map", "graphics", "car"]):
            fit_score = 15.0

        total_score = round(recency_score + kw_score + authority_score + fit_score, 1)
        total_score = min(100.0, max(0.0, total_score))

        breakdown = {
            "recency": recency_score,
            "keyword_impact": kw_score,
            "source_authority": authority_score,
            "brazilian_fit": fit_score
        }

        # Nível de prioridade
        if total_score >= 70:
            priority = "HIGH"
        elif total_score >= 50:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        # Sugestão de ângulo editorial para o Brasil
        angle, hook = self._generate_editorial_angle(item)

        return ScoredOpportunity(
            item=item,
            viral_score=total_score,
            score_breakdown=breakdown,
            priority_level=priority,
            recommended_angle_br=angle,
            suggested_hook_pt=hook
        )

    def _generate_editorial_angle(self, item: DiscoveredItem) -> tuple[str, str]:
        """Gera direcionamento editorial brasileiro baseado nos fatos identificados."""
        t_low = item.title.lower()
        if "trailer" in t_low or "launch" in t_low:
            angle = "Análise quadro a quadro de novidades e detalhes ocultos no novo material de GTA 6."
            hook = "🚨 VOCÊ VIU ISSO?! Novo material oficial de GTA 6 revelou detalhes inacreditáveis!"
        elif "leak" in t_low:
            angle = "Fato ou rumor: investigação jornalística do que realmente é real no novo vazamento."
            hook = "🔥 VAZOU NOVO DETALHE DE GTA 6! Mas calma: isso é real ou rumor?"
        elif "map" in t_low or "vice city" in t_low:
            angle = "Exploração da geografia de Vice City e tamanho comparado com Los Santos."
            hook = "🗺️ O MAPA DE VICE CITY TÁ SURREAL! Olha essa comparação com o GTA 5!"
        elif "car" in t_low or "vehicle" in t_low:
            angle = "Física automotiva e customização dos carros anos 80 em Vice City."
            hook = "🚗 OS CARROS DE GTA 6 TÃO COM UMA FÍSICA ABSURDA! Se liga nesse detalhe!"
        else:
            angle = "Curiosidade imperdível sobre a ambientação e tecnologia da nova era de Vice City."
            hook = "👀 SE LIGA NESSE DETALHE DE GTA 6 QUE QUASE NINGUÉM PERCEBEU!"

        return angle, hook
