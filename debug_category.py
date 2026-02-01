#!/usr/bin/env python3
import sys
import json
from bson import json_util
sys.path.append('/home/ubuntu/EkerGallery')
from models.database import db

# Find Fiat by Category Regex
print("\n--- FIAT ARAÇLARI (Regex ile) ---")
category_regex = ".*Fiat.*Doblo.*"
cat_fiats = list(db.vehicles.find({"category": {"$regex": category_regex, "$options": "i"}}).limit(5))
print(f"Regex '{category_regex}' ile bulunan: {len(cat_fiats)}")

for v in cat_fiats:
    print("\nAraç:")
    print(f"Marka Field: '{v.get('marka')}' (Type: {type(v.get('marka'))})")
    print(f"Model Field: '{v.get('model')}'")
    print(f"Category: '{v.get('category')}'")
    print(f"Details Marka: {v.get('details', {}).get('Marka')}")
    print(f"AI Tahmin: {v.get('ai_tahmin')}")
