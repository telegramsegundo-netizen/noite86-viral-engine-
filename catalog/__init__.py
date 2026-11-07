"""
Vice City E-Commerce Catalog Package

Provides catalog loading, strict JSON schema validation, IP non-infringement scanner,
and generative AI prompt builders for high-margin 1980s/1990s retro Miami products.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema

from catalog.ip_filter import (
    IPFilter,
    IPScanResult,
    IPViolation,
    sanitize_text,
    scan_catalog,
    scan_product,
    scan_text,
)
from catalog.prompt_generator import (
    PromptGenerator,
    PromptSpecification,
    generate_prompt,
    generate_prompts_for_product,
)

__version__ = "1.0.0"

_CURRENT_DIR = Path(__file__).resolve().parent
_PRODUCTS_FILE = _CURRENT_DIR / "products.json"
_SCHEMA_FILE = _CURRENT_DIR / "schemas" / "catalog.schema.json"


def load_catalog(path: Optional[Path | str] = None) -> Dict[str, Any]:
    """
    Load the master catalog JSON dataset.
    """
    target_path = Path(path) if path else _PRODUCTS_FILE
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_schema(path: Optional[Path | str] = None) -> Dict[str, Any]:
    """
    Load the JSON Schema Draft-07 for catalog validation.
    """
    target_path = Path(path) if path else _SCHEMA_FILE
    with open(target_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema


def get_products(catalog_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Return the list of products from the catalog.
    """
    data = catalog_data or load_catalog()
    return data.get("products", [])


def get_product_by_id(product_id: str, catalog_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve a product by its ID or SKU.
    """
    products = get_products(catalog_data)
    norm_id = product_id.strip().upper()
    for product in products:
        if product.get("id", "").upper() == norm_id or product.get("sku", "").upper() == norm_id:
            return product
    return None


def validate_catalog(catalog_data: Optional[Dict[str, Any]] = None) -> bool:
    """
    Strictly validate catalog dataset against JSON Schema Draft-07.
    Raises jsonschema.ValidationError on failure.
    """
    data = catalog_data or load_catalog()
    schema = load_schema()
    jsonschema.validate(instance=data, schema=schema)
    return True


__all__ = [
    "__version__",
    "load_catalog",
    "load_schema",
    "get_products",
    "get_product_by_id",
    "validate_catalog",
    "IPFilter",
    "IPScanResult",
    "IPViolation",
    "scan_text",
    "sanitize_text",
    "scan_product",
    "scan_catalog",
    "PromptGenerator",
    "PromptSpecification",
    "generate_prompt",
    "generate_prompts_for_product",
]
