"""
tests/helpers.py - Shared test fixtures, path resolvers, and validation helpers
for GTA 6 E-Commerce & Multi-Agent Operations System.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

def skip_test(reason: str):
    """Raise a standard unittest.SkipTest recognized by both pytest and unittest runners."""
    raise unittest.SkipTest(reason)

# Root project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Core path references
CATALOG_DIR = PROJECT_ROOT / "catalog"
CATALOG_JSON_PATH = CATALOG_DIR / "products.json"
CATALOG_SCHEMA_PATH = CATALOG_DIR / "schemas" / "catalog.schema.json"
IP_FILTER_PATH = CATALOG_DIR / "ip_filter.py"
PROMPT_GENERATOR_PATH = CATALOG_DIR / "prompt_generator.py"

VIDEO_PIPELINE_DIR = PROJECT_ROOT / "video_pipeline"
AGENTS_DIR = PROJECT_ROOT / "agents"
STOREFRONT_DIR = PROJECT_ROOT / "storefront"
VALIDATE_SYSTEM_PATH = PROJECT_ROOT / "validate_system.py"

# Banned trademark regex pattern as specified in R1 and PROJECT.md
BANNED_TRADEMARK_PATTERN = re.compile(
    r"\b(GTA|GTA6|GTA\s*VI|Grand\s+Theft\s+Auto|Rockstar|Rockstar\s+Games|Take-Two|Take\s+Two|Lucia|Tommy\s+Vercetti|Vercetti|Ammu-Nation|Ammunation|Sprunk|eCola|Love\s+Fist)\b",
    re.IGNORECASE,
)


def load_json_file(file_path: Path) -> Any:
    """Safely read and parse a JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Required JSON file not found at: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_banned_terms(text: str) -> List[str]:
    """Scan text and return any banned trademark token matches."""
    return [match.group(0) for match in BANNED_TRADEMARK_PATTERN.finditer(text)]


def is_module_available(module_name: str) -> bool:
    """Check if a module or package exists in the project or python path."""
    import importlib.util

    # Check local project directory first
    potential_path = PROJECT_ROOT / module_name.replace(".", "/")
    if potential_path.is_dir() and (potential_path / "__init__.py").exists():
        return True
    if potential_path.with_suffix(".py").exists():
        return True

    # Check python environment
    spec = importlib.util.find_spec(module_name)
    return spec is not None
