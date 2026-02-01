#!/usr/bin/env python3
import sys
import time
sys.path.append('/home/ubuntu/EkerGallery')
from models.database import db

# Count Tesla vehicles
tesla_count = db.vehicles.count_documents({'marka': 'Tesla'})
print(f"Tesla Araç Sayısı: {tesla_count}")

# List first 3 Tesla vehicles if any
if tesla_count > 0:
    print("--- İlk 3 Araç ---")
    vehicles = list(db.vehicles.find({'marka': 'Tesla'}).limit(3))
    for v in vehicles:
        print(f"Model: {v.get('title', 'N/A')} - Fiyat: {v.get('price', 'N/A')}")
else:
    print("Henüz veri yok...")
