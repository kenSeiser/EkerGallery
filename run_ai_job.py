#!/usr/bin/env python3
import sys
import time
import os

# Set up environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db
from services.ai_model import price_model

def run_job():
    print("🚀 AI Güncelleme İşlemi Başlatıldı...")
    start_time = time.time()
    
    try:
        # Update all predictions
        price_model.update_all_predictions()
        
        duration = time.time() - start_time
        print(f"✅ İşlem tamamlandı. Süre: {duration:.2f} saniye")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_job()
