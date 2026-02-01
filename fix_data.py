#!/usr/bin/env python3
import sys
import time
sys.path.append('/home/ubuntu/EkerGallery')
from models.database import db
from services.ai_model import price_model

def fix_missing_fields():
    print("🔧 Veri onarımı başlatılıyor...")
    
    # 1. Marka/Model eksik olanları bul
    incomplete_vehicles = list(db.vehicles.find({
        "$or": [
            {"marka": None},
            {"marka": ""},
            {"model": None},
            {"model": ""}
        ]
    }))
    
    print(f"📊 {len(incomplete_vehicles)} eksik kayıt bulundu.")
    
    updated_count = 0
    
    for v in incomplete_vehicles:
        updates = {}
        
        # Marka/Model bulmaya çalış
        category = v.get("category", "")
        details = v.get("details", {})
        
        marka = details.get("Marka")
        model = details.get("Seri") or details.get("Model")
        
        if not marka and category:
            parts = category.split(" ")
            if len(parts) >= 1:
                marka = parts[0]
                # Normalize
                if marka.lower() in ["vw"]: marka = "Volkswagen"
        
        if not model and category:
            parts = category.split(" ")
            if len(parts) >= 2:
                model = " ".join(parts[1:])
        
        if marka: updates["marka"] = marka
        if model: updates["model"] = model
        
        if updates:
            db.vehicles.update_one({"_id": v["_id"]}, {"$set": updates})
            updated_count += 1
            
    print(f"✅ {updated_count} kayıt onarıldı.")
    
    # 2. AI Tahminleri Güncelle
    print("🤖 AI Tahminleri tetikleniyor...")
    price_model.update_all_predictions()

if __name__ == "__main__":
    fix_data = fix_missing_fields()
