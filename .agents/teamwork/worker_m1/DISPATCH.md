## 2026-11-07T00:42:04Z
You are Worker M1 (Catalog, AI Prompts & Legal Boundaries Engine Worker).
Your identity: teamwork_worker
Your working directory: C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.agents\teamwork\worker_m1\
Parent Orchestrator Conversation ID: a5e87fb8-1970-4caf-809e-c3fe935bfa92

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Mandatory instructions:
1. First, read the authoritative user request at:
   C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\ORIGINAL_REQUEST.md
2. Read the master project architecture at:
   C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\PROJECT.md
3. Read Explorer 1's detailed survey and specifications at:
   C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.agents\teamwork\explorer_survey_1\analysis.md
   and C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.agents\teamwork\explorer_survey_1\handoff.md

Your Scope and Write Ownership:
You exclusively own and must implement the following files in C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\:
- `pyproject.toml`: Project configuration using standard uv/python tools, defining dependencies (pydantic, jsonschema, pytest, etc.).
- `catalog/__init__.py`: Package init.
- `catalog/products.json`: Complete dataset with 12 out-of-the-box conceptual & physical high-margin products (>67%-86% margins, dual BRL and USD pricing, AI prompt metadata, tags, specifications).
- `catalog/schemas/catalog.schema.json`: JSON Schema Draft-07 strictly validating the catalog format.
- `catalog/ip_filter.py`: Automated trademark non-infringement scanner and IP defense matrix (detects and blocks any Rockstar Games / Take-Two trademarks like GTA, Grand Theft Auto, Rockstar, Lucia, Jason, Tommy Vercetti, etc., while approving lawful 80s/90s Miami Vice City retro aesthetics).
- `catalog/prompt_generator.py`: Generative AI prompt builder parameterizing camera optics, volumetric neon lighting, 300 DPI print vectors for Midjourney v6.1 and Flux.1 Pro.
- `tests/test_catalog.py`: Unit and validation test suite verifying schema conformance, margin calculations (>65%), IP filter accuracy, and prompt generation.

Verification:
Run the tests using `uv run pytest tests/test_catalog.py` (or Python directly).
Ensure all tests pass cleanly. Document test commands and results in your report.

Deliverables:
- Write your completion report in C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.agents\teamwork\worker_m1\handoff.md
- Update your progress.md and send a message back to the orchestrator (conversation ID a5e87fb8-1970-4caf-809e-c3fe935bfa92) using send_message.
