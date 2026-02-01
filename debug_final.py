#!/usr/bin/env python3
import sys
import json
sys.path.append('/home/ubuntu/EkerGallery')
from models.database import db

# 1. Fiyat Kontrolü
print("\n--- FİYAT KONTROLÜ ---")
expensive_cars = list(db.vehicles.find({"fiyat": {"$gt": 50000}}).limit(5))
print(f"Fiyat > 50000 olan araç sayısı: {db.vehicles.count_documents({'fiyat': {'$gt': 50000}})}")

if expensive_cars:
    print("Örnek Araç:")
    v = expensive_cars[0]
    print(f"Fiyat: {v.get('fiyat')} (Type: {type(v.get('fiyat'))})")
    print(f"Marka: {v.get('marka')}")
else:
    print("⚠️ Fiyatı > 50000 olan araç bulunamadı!")
    # Rastgele bir araç çekip fiyat tipine bak
    sample = db.vehicles.find_one({})
    if sample:
        print(f"Rastgele Araç Fiyat: {sample.get('fiyat')} (Type: {type(sample.get('fiyat'))})")

# 2. Fiat Kontrolü (Marka Düzeltilmiş mi?)
print("\n--- FIAT KONTROLÜ ---")
fiats = list(db.vehicles.find({"marka": "Fiat"}).limit(5))
print(f"Marka='Fiat' olan araç sayısı: {len(fiats)} (Limitli)")

if fiats:
    v = fiats[0]
    print(f"Marka: {v.get('marka')}")
    print(f"Model: {v.get('model')}")
