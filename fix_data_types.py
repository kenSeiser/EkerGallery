#!/usr/bin/env python3
import sys
import re
sys.path.append('/home/ubuntu/EkerGallery')
from models.database import db
from services.ai_model import price_model

def fix_types():
    print("🔧 Veri TİPİ ve ANAHTAR onarımı başlatılıyor...")
    
    vehicles = db.get_all_vehicles({})
    print(f"📊 {len(vehicles)} doğrulama yapılıyor...")
    
    updated_count = 0
    
    for v in vehicles:
        updates = {}
        
        # 1. PRICE -> FIAT
        price_val = v.get("price")
        fiyat_val = v.get("fiyat")
        
        # Eğer fiyat yoksa price'dan üret
        if not fiyat_val and price_val:
            if isinstance(price_val, str):
                try:
                    # "795.000 TL" -> 795000
                    clean = price_val.split('TL')[0].replace('.', '').replace(',', '').strip()
                    updates["fiyat"] = int(clean)
                except:
                    pass
            elif isinstance(price_val, (int, float)):
                updates["fiyat"] = int(price_val)
        
        # 2. YEAR -> YIL
        year_val = v.get("year")
        yil_val = v.get("yil")
        
        if not yil_val and year_val:
            try:
                updates["yil"] = int(str(year_val).strip())
            except:
                pass
                
        # 3. KM (Zaten km key genelde doğru ama tip kontrolü yapalım)
        km_val = v.get("km")
        if isinstance(km_val, str):
            try:
                clean = re.sub(r'\D', '', km_val)
                if clean:
                    updates["km"] = int(clean)
            except:
                pass
                
        if updates:
            db.vehicles.update_one({"_id": v["_id"]}, {"$set": updates})
            updated_count += 1
            
    print(f"✅ {updated_count} araç şeması düzeltildi (Eng -> Tr & Str -> Int).")
    
    # AI Tahminleri Tekrar Dene
    print("🤖 AI Tahminleri (Son Deneme)...")
    price_model.update_all_predictions()

if __name__ == "__main__":
    fix_types()
