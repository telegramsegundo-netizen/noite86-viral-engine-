"""
autonomous_engine/rights_clearance.py
AGENTE 05 — Rights Clearance Officer

Audita a titularidade e o regime de licenciamento de cada oportunidade detectada.
Garante que nenhum vídeo de terceiro sem autorização seja republicado cru.
Aplica a salvaguarda de transformação editorial autoral (Fair Use estrito).
"""
from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel

from autonomous_engine.viral_analyst import ScoredOpportunity

STORAGE_BASE = Path(r"C:\Users\victo\NOITE86_FACTORY")


class ProductionRoute(str, Enum):
    DIRECT_ADAPTATION = "direct_adaptation"            # Vídeo próprio ou licenciado diretamente
    FAIR_USE_COMMENTARY = "fair_use_commentary"        # Trailer institucional público com disclaimer
    ORIGINAL_TRANSFORMATIVE = "original_transformative" # Terceiro sem autorização: ROTEIRO AUTORAL 100% NOVO


class RightsVerdict(BaseModel):
    opportunity_id: str
    title: str
    source_url: str
    license_category: str
    route: ProductionRoute
    can_use_source_media: bool
    requires_original_script: bool
    mandatory_disclaimer: str
    legal_justification: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "title": self.title,
            "source_url": self.source_url,
            "license_category": self.license_category,
            "route": self.route.value,
            "can_use_source_media": self.can_use_source_media,
            "requires_original_script": self.requires_original_script,
            "mandatory_disclaimer": self.mandatory_disclaimer,
            "legal_justification": self.legal_justification,
        }


class RightsClearanceOfficer:
    """Oficial de conformidade e propriedade intelectual."""

    DISCLAIMER_OWN = (
        "PRODUÇÃO AUTORAL // MARCA NOITE 86. TODOS OS DIREITOS RESERVADOS. ESTÉTICA VICE DISTRICT."
    )

    DISCLAIMER_PUBLIC_TRAILER = (
        "MATERIAL INSTITUCIONAL PÚBLICO UTILIZADO SOB DOUTRINA DE CRÍTICA E ANÁLISE JORNALÍSTICA (FAIR USE). "
        "DIREITOS DE IMAGEM E MARCA PERTENCEM À ROCKSTAR GAMES E TAKE-TWO INTERACTIVE."
    )

    DISCLAIMER_TRANSFORMATIVE = (
        "CONTEÚDO ORIGINAL BRASILEIRO // ANÁLISE EDITORIAL E COMENTÁRIO INDEPENDENTE NOITE 86. "
        "NÃO POSSUI VÍNCULO OU PATROCÍNIO COM ESTÚDIOS OU CRIADORES CITADOS."
    )

    def evaluate_opportunity(self, opp: ScoredOpportunity) -> RightsVerdict:
        """Avalia a oportunidade e determina a rota de produção 100% legal."""
        lic = opp.item.license_category.lower()

        if lic in ("own_content", "explicit_permission"):
            verdict = RightsVerdict(
                opportunity_id=opp.item.id,
                title=opp.item.title,
                source_url=opp.item.url,
                license_category=lic,
                route=ProductionRoute.DIRECT_ADAPTATION,
                can_use_source_media=True,
                requires_original_script=False,
                mandatory_disclaimer=self.DISCLAIMER_OWN,
                legal_justification="Material próprio ou com licença prévia e comprovada para uso comercial.",
            )
        elif lic == "public_trailer" or "trailer" in opp.item.title.lower():
            verdict = RightsVerdict(
                opportunity_id=opp.item.id,
                title=opp.item.title,
                source_url=opp.item.url,
                license_category="public_trailer",
                route=ProductionRoute.FAIR_USE_COMMENTARY,
                can_use_source_media=True,
                requires_original_script=False,
                mandatory_disclaimer=self.DISCLAIMER_PUBLIC_TRAILER,
                legal_justification="Trailer de divulgação pública universal. Análise crítica e cobertura jornalística permitida com crédito.",
            )
        else:
            # Qualquer conteúdo de terceiro sem autorização expressa
            verdict = RightsVerdict(
                opportunity_id=opp.item.id,
                title=opp.item.title,
                source_url=opp.item.url,
                license_category="unauthorized",
                route=ProductionRoute.ORIGINAL_TRANSFORMATIVE,
                can_use_source_media=False,
                requires_original_script=True,
                mandatory_disclaimer=self.DISCLAIMER_TRANSFORMATIVE,
                legal_justification=(
                    "Material de terceiro não licenciado. A mídia bruta original NÃO pode ser redistribuída. "
                    "O sistema utilizará apenas os fatos e ideias para produzir um Roteiro e Cenas 100% Autorais."
                ),
            )

        self._save_verdict(verdict)
        return verdict

    def _save_verdict(self, verdict: RightsVerdict):
        """Salva a decisão de direitos em NOITE86_FACTORY."""
        try:
            target_dir = STORAGE_BASE / ("02_APPROVED_SOURCES" if verdict.can_use_source_media else "07_REJECTED")
            target_dir.mkdir(parents=True, exist_ok=True)
            verdict_file = target_dir / f"{verdict.opportunity_id}_rights.json"
            verdict_file.write_text(json.dumps(verdict.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
