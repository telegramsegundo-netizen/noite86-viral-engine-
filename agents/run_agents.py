"""
agents/run_agents.py - Unified Master Orchestration Engine CLI
Executes Store Architect Agent and Content Clipper Agent to prepare the entire
storefront configuration and 7-day social marketing campaign in under 2 seconds offline.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.store_architect import StoreArchitectAgent
from agents.content_clipper import ContentClipperAgent


def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(
        description="Unified Master Orchestration Engine for Vice District Agents"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Run in deterministic offline mock mode (default: True)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run in live AI generation mode using Gemini API",
    )
    parser.add_argument(
        "--catalog",
        type=str,
        default=str(PROJECT_ROOT / "catalog" / "products.json"),
        help="Path to catalog products.json",
    )
    parser.add_argument(
        "--clips",
        type=str,
        default=None,
        help="Path to localized clips JSON from video pipeline",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROJECT_ROOT / "storefront" / "data"),
        help="Output directory for generated configs",
    )

    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    mock_mode = not args.live
    start_time = time.time()

    print("\n" + "=" * 70)
    print("  VICE DISTRICT -- AUTONOMOUS MULTI-AGENT ORCHESTRATION ENGINE  ")
    print(f"  Mode: {'DETERMINISTIC OFFLINE MOCK' if mock_mode else 'LIVE AI GENERATION'}")
    print("=" * 70)

    # 1. Store Architect Agent
    print("\n[1/2] Executing Store Architect Agent...")
    architect = StoreArchitectAgent(mock_mode=mock_mode)
    store_config = architect.generate_config(catalog_path=args.catalog)
    products_count = len(store_config.get("products", []))
    bundles_count = len(store_config.get("bundles", []))
    print(f"  [OK] Store Architect completed: {products_count} products loaded, {bundles_count} promotional bundles created.")
    print(f"  [OK] Store configuration written to: storefront/data/store_config.json")

    # 2. Content Clipper & Campaign Agent
    print("\n[2/2] Executing Content Clipper & Campaign Agent...")
    clipper = ContentClipperAgent(mock_mode=mock_mode)

    clips_data = None
    if args.clips and Path(args.clips).exists():
        try:
            with open(args.clips, "r", encoding="utf-8") as f:
                clips_data = json.load(f)
        except Exception as e:
            print(f"  ! Warning: could not load clips file: {e}")

    campaign = clipper.generate_campaign(clips_input=clips_data, catalog_path=args.catalog)
    posts_count = len(campaign.get("schedule", []))
    print(f"  [OK] Content Clipper completed: {posts_count} viral posts scheduled over 7 days.")
    print(f"  [OK] Campaign assets written to: campaigns/social_campaign.json & campaigns/campaign_calendar.md")

    # Also write a copy of store_config to root for convenience
    root_store_config = PROJECT_ROOT / "store_config.json"
    with open(root_store_config, "w", encoding="utf-8") as f:
        json.dump(store_config, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"  [OK] ORCHESTRATION PIPELINE COMPLETE IN {elapsed:.3f} SECONDS (EXIT 0)")
    print("=" * 70 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
