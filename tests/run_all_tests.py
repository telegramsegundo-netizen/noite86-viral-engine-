#!/usr/bin/env python3
"""
tests/run_all_tests.py - Master Standalone Test Runner
GTA 6 E-Commerce & Multi-Agent Operations System

Executes all opaque-box E2E test tiers (Tiers 1-4) plus unit test suites,
reporting structured tier-by-tier execution logs and returning exit code 0 on pass.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Color formatting helpers for Windows/Unix terminals
USE_COLOR = os.name != "nt" or "WT_SESSION" in os.environ or "ANSICON" in os.environ or True
GREEN = "\033[92m" if USE_COLOR else ""
RED = "\033[91m" if USE_COLOR else ""
YELLOW = "\033[93m" if USE_COLOR else ""
CYAN = "\033[96m" if USE_COLOR else ""
BOLD = "\033[1m" if USE_COLOR else ""
RESET = "\033[0m" if USE_COLOR else ""


TIER_SPECS = {
    1: {
        "name": "Tier 1: Feature Coverage in Isolation",
        "module": "tests.test_e2e_tier1_features",
        "description": "Exercises Features F1-F15 independently (Catalog, AI Prompts, IP Scanner, Video, Agents, Storefront)",
    },
    2: {
        "name": "Tier 2: Boundary, Negative & Adversarial",
        "module": "tests.test_e2e_tier2_boundaries",
        "description": "Adversarial limits: empty inputs, corrupt files, boundary margins, unescaped paths, trademark evasion",
    },
    3: {
        "name": "Tier 3: Cross-Feature Pairwise Integrations",
        "module": "tests.test_e2e_tier3_combinations",
        "description": "Cross-module data contracts: Catalog <-> Store, Video <-> Clipper, Bundles + Coupons + PIX math",
    },
    4: {
        "name": "Tier 4: Real-World End-to-End Scenarios",
        "module": "tests.test_e2e_tier4_scenarios",
        "description": "Complete 24h store launch flow (Catalog -> Video -> Multi-Agent -> Storefront -> PIX Order)",
    },
}


class TierTestResult(unittest.TextTestResult):
    """Custom TestResult collecting detailed execution stats."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.passed_count = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_count += 1


def run_tier(tier_num: int, verbose: bool = False) -> dict:
    """Run tests for a single tier and return statistics."""
    spec = TIER_SPECS[tier_num]
    module_name = spec["module"]

    print(f"\n{BOLD}{CYAN}=== RUNNING {spec['name'].upper()} ==={RESET}")
    print(f"{CYAN}Description: {spec['description']}{RESET}\n")

    loader = unittest.TestLoader()
    try:
        suite = loader.loadTestsFromName(module_name)
    except Exception as e:
        print(f"{RED}Failed to load module {module_name}: {e}{RESET}")
        return {
            "tier": tier_num,
            "name": spec["name"],
            "total": 0,
            "passed": 0,
            "skipped": 0,
            "failed": 1,
            "duration": 0.0,
            "success": False,
        }

    start_time = time.time()
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        resultclass=TierTestResult,
    )
    result = runner.run(suite)
    duration = time.time() - start_time

    total = result.testsRun
    failed = len(result.failures) + len(result.errors)
    skipped = len(result.skipped)
    passed = result.passed_count
    success = result.wasSuccessful()

    return {
        "tier": tier_num,
        "name": spec["name"],
        "total": total,
        "passed": passed,
        "skipped": skipped,
        "failed": failed,
        "duration": duration,
        "success": success,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Master Standalone Test Runner for GTA 6 E-Commerce & Multi-Agent Operations System"
    )
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run only the specified test tier (1, 2, 3, or 4)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose test output listing individual tests",
    )
    args = parser.parse_args()

    print(f"{BOLD}{CYAN}")
    print("=" * 80)
    print("    GTA 6 E-COMMERCE & MULTI-AGENT OPERATIONS SYSTEM")
    print("         OPAQUE-BOX E2E TEST RUNNER (TIERS 1 - 4)    ")
    print("=" * 80)
    print(f"{RESET}")

    selected_tiers = [args.tier] if args.tier else [1, 2, 3, 4]
    tier_results = []
    overall_start = time.time()

    for tier_num in selected_tiers:
        res = run_tier(tier_num, verbose=args.verbose)
        tier_results.append(res)

    overall_duration = time.time() - overall_start

    # Summary Table
    print(f"\n{BOLD}{CYAN}")
    print("=" * 80)
    print("                         TEST EXECUTION SUMMARY MATRIX                         ")
    print("=" * 80)
    print(f"{'Tier':<8}{'Suite Name':<38}{'Total':<8}{'Pass':<8}{'Skip':<8}{'Fail':<8}{'Time':<8}")
    print("-" * 80 + RESET)

    all_passed = True
    total_tests = 0
    total_passed = 0
    total_skipped = 0
    total_failed = 0

    for r in tier_results:
        total_tests += r["total"]
        total_passed += r["passed"]
        total_skipped += r["skipped"]
        total_failed += r["failed"]

        status_color = GREEN if r["success"] else RED
        if not r["success"]:
            all_passed = False

        short_name = r["name"].split(":")[0] + ":" + r["name"].split(":")[1][:28]
        print(
            f"{status_color}Tier {r['tier']:<3} {short_name:<38}{r['total']:<8}{r['passed']:<8}{r['skipped']:<8}{r['failed']:<8}{r['duration']:.2f}s{RESET}"
        )

    print("-" * 80)
    print(
        f"{BOLD}{'TOTAL':<46}{total_tests:<8}{total_passed:<8}{total_skipped:<8}{total_failed:<8}{overall_duration:.2f}s{RESET}"
    )
    print("=" * 80)

    if all_passed:
        print(f"\n{BOLD}{GREEN}>>> [PASS] ALL TEST TIERS EXECUTED SUCCESSFULLY! <<<")
        print(f"Verified {total_passed} passing tests ({total_skipped} clean progressive skips).{RESET}\n")
        return 0
    else:
        print(f"\n{BOLD}{RED}>>> [FAIL] TEST FAILURES DETECTED IN TEST SUITE! <<<{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
