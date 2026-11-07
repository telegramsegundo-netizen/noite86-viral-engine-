import json
from pathlib import Path

config_file = Path(r"C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\storefront\data\store_config.json")
with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

for prod in config.get("products", []):
    sku = prod.get("sku") or prod.get("id")
    if sku == "VC-AUD-001":
        prod["image_placeholder"] = "assets/products/vc-aud-001.png"
        prod["image_url"] = "assets/products/vc-aud-001.png"

with open(config_file, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("VC-AUD-001 updated in store_config.json")
