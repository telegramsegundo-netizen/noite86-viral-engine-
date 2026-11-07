"""
video_pipeline/rights_reviewer.py
Agente 05 - Rights & Content Review Engine.

Audits video sources, verifies copyright permissions, ensures compliance with
platform guidelines (YouTube, TikTok, Instagram, Meta), and enforces:
1. Direct processing for authorized/own/licensed material.
2. Mandatory transformative analysis and original script generation for unauthorized third-party material.
"""
from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field


class LicenseType(str, Enum):
    OWN_CONTENT = "own_content"                  # Material próprio do operador
    EXPLICIT_PERMISSION = "explicit_permission"  # Autorização direta do criador parceiro
    PUBLIC_TRAILER_FAIR_USE = "public_trailer"   # Trailer público institucional (análise jornalística)
    PUBLIC_TRAILER = "public_trailer"            # Alias
    UNAUTHORIZED_THIRD_PARTY = "unauthorized"    # Material de terceiro sem autorização direta
    UNAUTHORIZED = "unauthorized"                # Alias


class RightsClearanceReport(BaseModel):
    """Relatório auditável de conformidade de direitos autorais."""
    source_identifier: str
    license_type: LicenseType
    can_republish_direct: bool
    requires_transformative_commentary: bool
    requires_original_script: bool
    watermark_mandatory: bool = True
    disclaimer_text: str
    justification: str

    @property
    def allowed_to_republish_source(self) -> bool:
        return self.can_republish_direct

    @property
    def status(self) -> str:
        if self.can_republish_direct:
            return "approved"
        return "blocked_raw_mirroring"

    @property
    def recommended_action(self) -> str:
        if self.license_type in (LicenseType.OWN_CONTENT, LicenseType.EXPLICIT_PERMISSION):
            return "process_direct"
        elif self.license_type in (LicenseType.PUBLIC_TRAILER_FAIR_USE, LicenseType.PUBLIC_TRAILER):
            return "fair_use_commentary"
        return "original_transformative_analysis_only"

    @property
    def disclaimer(self) -> str:
        return self.disclaimer_text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_identifier": self.source_identifier,
            "license_type": self.license_type.value,
            "can_republish_direct": self.can_republish_direct,
            "allowed_to_republish_source": self.allowed_to_republish_source,
            "status": self.status,
            "recommended_action": self.recommended_action,
            "requires_transformative_commentary": self.requires_transformative_commentary,
            "requires_original_script": self.requires_original_script,
            "watermark_mandatory": self.watermark_mandatory,
            "disclaimer_text": self.disclaimer_text,
            "justification": self.justification,
        }


class RightsReviewer:
    """Motor de análise e compliance de direitos autorais para a Operação Noite 86."""

    DISCLAIMER_TRANSFORMATIVE = (
        "CONTEÚDO ORIGINAL // ANÁLISE JORNALÍSTICA E CRÍTICA INDEPENDENTE. "
        "NÃO POSSUI AFILIAÇÃO COM ESTÚDIOS OU CRIADORES CITADOS. "
        "DIREITOS DE MARCA E IMAGEM PERTENCEM AOS SEUS RESPECTIVOS TITULARES."
    )

    DISCLAIMER_AUTHORIZED = (
        "MATERIAL PRODUZIDO OU LICENCIADO PARA A OPERAÇÃO NOITE 86. "
        "TODOS OS DIREITOS RESERVADOS // ESTÉTICA VICE DISTRICT."
    )

    def evaluate_source(
        self,
        source: Optional[Union[str, Path]] = None,
        declared_license: Optional[Union[str, LicenseType]] = None,
        details: Optional[str] = None,
        source_input: Optional[Union[str, Path]] = None,
        license_type: Optional[Union[str, LicenseType]] = None,
    ) -> RightsClearanceReport:
        """
        Avalia o material de entrada e determina as restrições legais e o modo de operação.
        """
        actual_source = source or source_input or "unknown"
        actual_license = declared_license or license_type
        source_str = str(actual_source).strip()

        # Determinar tipo de licença declarada
        if isinstance(actual_license, str):
            try:
                lic_type = LicenseType(actual_license.lower())
            except ValueError:
                lic_type = LicenseType.PUBLIC_TRAILER_FAIR_USE
        elif isinstance(actual_license, LicenseType):
            lic_type = actual_license
        else:
            # Heurística automática
            if source_str.startswith("mock://") or "synthetic" in source_str or "mock" in source_str:
                lic_type = LicenseType.OWN_CONTENT
            elif "trailer" in source_str.lower() or "rockstar" in source_str.lower() or "official" in source_str.lower():
                lic_type = LicenseType.PUBLIC_TRAILER_FAIR_USE
            elif source_str.startswith("http://") or source_str.startswith("https://"):
                lic_type = LicenseType.UNAUTHORIZED_THIRD_PARTY
            else:
                lic_type = LicenseType.OWN_CONTENT

        if lic_type in (LicenseType.OWN_CONTENT, LicenseType.EXPLICIT_PERMISSION):
            return RightsClearanceReport(
                source_identifier=source_str,
                license_type=lic_type,
                can_republish_direct=True,
                requires_transformative_commentary=False,
                requires_original_script=False,
                disclaimer_text=self.DISCLAIMER_AUTHORIZED,
                justification="Material próprio ou expressamente autorizado para dublagem e comercialização.",
            )

        if lic_type == LicenseType.PUBLIC_TRAILER_FAIR_USE:
            return RightsClearanceReport(
                source_identifier=source_str,
                license_type=lic_type,
                can_republish_direct=True,
                requires_transformative_commentary=True,
                requires_original_script=False,
                disclaimer_text=self.DISCLAIMER_TRANSFORMATIVE,
                justification="Trailer público utilizado sob doutrina de Fair Use / Uso Razoável com comentário e dublagem autoral.",
            )

        # Caso UNAUTHORIZED_THIRD_PARTY
        return RightsClearanceReport(
            source_identifier=source_str,
            license_type=lic_type,
            can_republish_direct=False,
            requires_transformative_commentary=True,
            requires_original_script=True,
            disclaimer_text=self.DISCLAIMER_TRANSFORMATIVE,
            justification=(
                "Vídeo de terceiro sem autorização prévia. É terminantemente proibido redistribuir o material bruto. "
                "O pipeline deve criar roteiro autoral brasileiro de análise factual e aplicar background transformativo."
            ),
        )

    def export_report(self, report: RightsClearanceReport, output_path: Union[str, Path]) -> Path:
        """Salva o relatório em disco em formato auditável JSON."""
        target = Path(output_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return target
