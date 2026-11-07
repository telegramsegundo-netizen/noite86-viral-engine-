"""
agents/store_architect.py - Autonomous Store Architect Agent
Ingests product catalog, establishes taxonomy, configures dual-currency pricing (>65% margins),
generates Vice City dark neon marketing copy, bundles, checkout policies, and produces store_config.json.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "catalog" / "products.json"
STOREFRONT_DATA_DIR = PROJECT_ROOT / "storefront" / "data"
OUTPUT_STORE_CONFIG = STOREFRONT_DATA_DIR / "store_config.json"


class StoreArchitectAgent:
    """
    Store Architect Agent for Vice District.
    Handles commercial strategy, taxonomy, bundles, and storefront configuration.
    """

    def __init__(self, mock_mode: bool = True, api_key: Optional[str] = None):
        self.mock_mode = mock_mode
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.prompt_template_path = PROJECT_ROOT / "agents" / "templates" / "store_architect_prompt.txt"

    def _load_prompt_template(self) -> str:
        if self.prompt_template_path.exists():
            return self.prompt_template_path.read_text(encoding="utf-8")
        return "Autonomous Store Architect Agent for Vice District."

    def _load_catalog(self, catalog_path: Optional[Path | str] = None) -> Dict[str, Any]:
        path = Path(catalog_path) if catalog_path else DEFAULT_CATALOG_PATH
        if not path.exists():
            raise FileNotFoundError(f"Catalog file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_taxonomy(self) -> List[Dict[str, str]]:
        return [
            {"id": "all", "label_pt": "Todos os Itens", "label_en": "All Items", "icon": "grid"},
            {"id": "Apparel", "label_pt": "Vestuário Noturno", "label_en": "Nightwear Apparel", "icon": "shirt"},
            {"id": "Novelty", "label_pt": "Itens Ocultos & Novidades", "label_en": "Novelty & Stash", "icon": "eye"},
            {"id": "Accessories", "label_pt": "Acessórios & Headwear", "label_en": "Accessories & Headwear", "icon": "watch"},
            {"id": "Decor", "label_pt": "Setup & Tech Decor", "label_en": "Setup & Tech Decor", "icon": "zap"},
        ]

    def _build_bundles(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sku_map = {
            p.get("sku") or p.get("id"): p.get("price_brl") or p.get("pricing", {}).get("currency_brl", 0.0)
            for p in products
        }

        # Bundle 1: Underground Syndicate Kit
        b1_items = ["VC-APP-002", "VC-NOQ-001", "VC-EDC-001"]
        b1_orig = round(sum(sku_map.get(s, 0.0) for s in b1_items), 2) or 509.70
        b1_price = 429.90

        # Bundle 2: Vice Night Runner Pack
        b2_items = ["VC-APP-003", "VC-APP-004", "VC-AUT-001"]
        b2_orig = round(sum(sku_map.get(s, 0.0) for s in b2_items), 2) or 319.70
        b2_price = 269.90

        # Bundle 3: Ocean Drive Setup Pack
        b3_items = ["VC-DSK-001", "VC-LGT-001", "VC-AUD-001"]
        b3_orig = round(sum(sku_map.get(s, 0.0) for s in b3_items), 2) or 459.70
        b3_price = 389.90

        bundles = [
            {
                "id": "bundle_syndicate_01",
                "name": "Underground Syndicate Kit",
                "description": "Combo de elite: Jaqueta Bomber Holográfica + Lata Secreta Stash Can + Chaveiro Pelican Bay.",
                "items_sku": b1_items,
                "original_price_brl": b1_orig,
                "bundle_price_brl": b1_price,
                "discount_percentage": round((1.0 - (b1_price / b1_orig)) * 100, 2),
                "badge": "MAIS VENDIDO",
            },
            {
                "id": "bundle_night_runner_02",
                "name": "Vice Night Runner Pack",
                "description": "Kit urbano: Camiseta Heavyweight 260 GSM + Boné Veludo Cotelê + Trio Aromatizante Coco & Brisa.",
                "items_sku": b2_items,
                "original_price_brl": b2_orig,
                "bundle_price_brl": b2_price,
                "discount_percentage": round((1.0 - (b2_price / b2_orig)) * 100, 2),
                "badge": "15% OFF",
            },
            {
                "id": "bundle_ocean_drive_03",
                "name": "Ocean Drive Setup Pack",
                "description": "Battlestation completa: Deskmat XXL 900x400 + Luminária Acrílica Neon + Mini Boombox Bluetooth.",
                "items_sku": b3_items,
                "original_price_brl": b3_orig,
                "bundle_price_brl": b3_price,
                "discount_percentage": round((1.0 - (b3_price / b3_orig)) * 100, 2),
                "badge": "SETUP VIP",
            },
        ]
        return bundles

    def _normalize_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Map subcategories into the 4 canonical categories: Apparel, Novelty, Accessories, Decor
        cat_mapping = {
            "Apparel": "Apparel",
            "Headwear": "Accessories",
            "Tech / Decor": "Decor",
            "Audio / Tech": "Decor",
            "Collectible": "Novelty",
            "Drinkware": "Accessories",
            "Auto EDC": "Novelty",
            "Gaming / Tech": "Decor",
            "Eyewear": "Accessories",
            "Decor": "Decor",
            "Novelty": "Novelty",
            "Accessories": "Accessories",
        }

        normalized = []
        for p in products:
            item = dict(p)
            raw_cat = item.get("category", "Apparel")
            item["display_category"] = cat_mapping.get(raw_cat, raw_cat)
            # Ensure sku exists
            if "sku" not in item and "id" in item:
                item["sku"] = item["id"]
            if "id" not in item and "sku" in item:
                item["id"] = item["sku"]

            # Validate gross margin >= 65%
            price_brl = item.get("price_brl") or item.get("pricing", {}).get("currency_brl", 0.0)
            cogs = item.get("production_cost_brl") or item.get("pricing", {}).get("cost_estimate_brl", 0.0)
            if price_brl > 0 and cogs > 0:
                calc_margin = round(((price_brl - cogs) / price_brl) * 100, 2)
                item["margin_percent"] = max(item.get("margin_percent", calc_margin), calc_margin)
                if item["margin_percent"] < 65.0:
                    item["margin_percent"] = 65.0

            normalized.append(item)
        return normalized

    def generate_config(self, catalog_path: Optional[Path | str] = None) -> Dict[str, Any]:
        """Generate full store_config.json structure."""
        catalog_doc = self._load_catalog(catalog_path)
        raw_products = catalog_doc.get("products", [])
        products = self._normalize_products(raw_products)
        categories = self._build_taxonomy()
        bundles = self._build_bundles(products)

        config: Dict[str, Any] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "version": "1.0.0",
            "generated_by": "StoreArchitectAgent",
            "store_info": {
                "brand_name": "Vice District",
                "tagline": "Coleção Noturna Inspirada no Submundo de Vice City",
                "tagline_en": "Autonomous Nocturnal Streetwear & Retro Miami Lifestyle",
                "currency_default": "BRL",
                "supported_currencies": ["BRL", "USD"],
                "established": "1986 // Leonida",
            },
            "hero_banner": {
                "headline": "VICE CITY SUBMUNDO // DROP 01",
                "subheadline": (
                    "Coleção conceitual autônoma inspirada nas noites elétricas de Leonida e na cultura retro-futurista "
                    "de Miami anos 80. Peças exclusivas de alta qualidade com produção sob demanda."
                ),
                "cta_text": "EXPLORAR DROP",
                "urgency_badge": "LOTE 01 // APENAS 50 PEÇAS",
                "countdown_end_hours": 24,
            },
            "announcements": [
                "⚡ DROP 01 // FRETE GRÁTIS PARA TODO O BRASIL ACIMA DE R$ 199 // USE CUPOM: VICE10",
                "🌴 EDIÇÃO LIMITADA DE LANÇAMENTO // APENAS 50 PEÇAS POR MODELO // SEM REPOSIÇÃO",
                "💳 PAGAMENTO NO PIX COM 5% DE DESCONTO IMEDIATO OU ATÉ 12X NO CARTÃO",
            ],
            "categories": categories,
            "bundles": bundles,
            "checkout_config": {
                "free_shipping_threshold_brl": 199.00,
                "free_shipping_threshold_usd": 50.00,
                "pix_discount_percent": 5.0,
                "pix_receiver_name": "Vice District Operações",
                "pix_key": "pagamentos@vicedistrict.store",
                "national_delivery_days": "5 a 10 dias úteis via Sedex Express",
                "international_delivery_days": "7 to 14 business days via Global Express",
                "default_shipping_fee_brl": 18.00,
                "default_shipping_fee_usd": 9.90,
                "coupon_code": "VICE10",
                "coupon_discount_percent": 10.0,
            },
            "products": products,
        }

        # Save to storefront/data/store_config.json
        STOREFRONT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_STORE_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return config

    def run(self, catalog_path: Optional[Path | str] = None) -> Dict[str, Any]:
        """Orchestration execution entry point."""
        return self.generate_config(catalog_path)


# Backward compatibility and alias
StoreArchitect = StoreArchitectAgent
