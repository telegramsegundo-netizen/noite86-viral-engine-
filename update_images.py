import json
from pathlib import Path

storefront_dir = Path(r"C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\storefront")
config_file = storefront_dir / "data" / "store_config.json"

image_map = {
    "VC-APP-001": "assets/products/vc-app-001.png",
    "VC-APP-002": "assets/products/vc-app-002.png",
    "VC-APP-004": "assets/products/vc-app-004.png",
    "VC-NOQ-001": "assets/products/vc-noq-001.png",
    "VC-DSK-001": "assets/products/vc-dsk-001.png",
    "VC-LGT-001": "assets/products/vc-lgt-001.png",
    "VC-DRK-001": "assets/products/vc-drk-001.png",
    "VC-EDC-001": "assets/products/vc-edc-001.png",
    "VC-AUT-001": "assets/products/vc-aut-001.png",
    "VC-EYE-001": "assets/products/vc-eye-001.png",
}

with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

updated_count = 0
for prod in config.get("products", []):
    sku = prod.get("sku") or prod.get("id")
    if sku in image_map:
        prod["image_placeholder"] = image_map[sku]
        prod["image_url"] = image_map[sku]
        updated_count += 1

with open(config_file, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"Updated {updated_count} products in store_config.json")
