# ========================================
# EkerGallery - Merkezi Konfigürasyon
# ========================================

import os
from dotenv import load_dotenv

# .env dosyasını yükle (varsa)
load_dotenv()

# --- VERİTABANI AYARLARI ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?retryWrites=true&w=majority&appName=ekerard")
DB_NAME = "sahibinden_data"
COLLECTION_NAME = "tum_araclar"

# --- FLASK AYARLARI ---
SECRET_KEY = os.getenv("SECRET_KEY", "ekergallery_secret_2026")
ADMIN_USER = os.getenv("ADMIN_USER", "ekerard")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

# --- SCRAPER AYARLARI ---
CHROME_VERSION = 144
SCRAPE_INTERVAL_HOURS = 4  # Kaç saatte bir veri çekilecek
MAX_PAGES_PER_CATEGORY = 10  # Kategori başına maksimum sayfa

# Scraper'ın ATLAMASI gereken modeller (verisi zaten çekilmiş)
SKIP_MODELS = ["model-y", "model-3"]

# --- ARAÇ KATEGORİLERİ ---
# Sahibinden URL yapısı ve kategori tanımları
VEHICLE_CATEGORIES = {
    # Lüks Segment
    "tesla": {
        "display_name": "Tesla",
        "models": {
            "model-y": {"url": "https://www.sahibinden.com/tesla-model-y?sorting=date_desc", "name": "Model Y"},
            "model-3": {"url": "https://www.sahibinden.com/tesla-model-3?sorting=date_desc", "name": "Model 3"},
            "model-s": {"url": "https://www.sahibinden.com/tesla-model-s?sorting=date_desc", "name": "Model S"},
        }
    },
    "mercedes": {
        "display_name": "Mercedes-Benz",
        "models": {
            "amg-gt": {"url": "https://www.sahibinden.com/mercedes-benz-amg-gt?sorting=date_desc", "name": "AMG GT"},
            "c-serisi": {"url": "https://www.sahibinden.com/mercedes-benz-c-serisi?sorting=date_desc", "name": "C Serisi"},
            "e-serisi": {"url": "https://www.sahibinden.com/mercedes-benz-e-serisi?sorting=date_desc", "name": "E Serisi"},
        }
    },
    "bmw": {
        "display_name": "BMW",
        "models": {
            "3-serisi": {"url": "https://www.sahibinden.com/bmw-3-serisi?sorting=date_desc", "name": "3 Serisi"},
            "5-serisi": {"url": "https://www.sahibinden.com/bmw-5-serisi?sorting=date_desc", "name": "5 Serisi"},
            "x5": {"url": "https://www.sahibinden.com/bmw-x5?sorting=date_desc", "name": "X5"},
        }
    },
    "volvo": {
        "display_name": "Volvo",
        "models": {
            "s90": {"url": "https://www.sahibinden.com/otomobil-volvo-s90?sorting=date_desc", "name": "S90"},
            "xc60": {"url": "https://www.sahibinden.com/otomobil-volvo-xc60?sorting=date_desc", "name": "XC60"},
            "xc90": {"url": "https://www.sahibinden.com/otomobil-volvo-xc90?sorting=date_desc", "name": "XC90"},
        }
    },
    # Ekonomik Segment
    "volkswagen": {
        "display_name": "Volkswagen",
        "models": {
            "polo": {"url": "https://www.sahibinden.com/volkswagen-polo?sorting=date_desc", "name": "Polo"},
            "golf": {"url": "https://www.sahibinden.com/volkswagen-golf?sorting=date_desc", "name": "Golf"},
            "passat": {"url": "https://www.sahibinden.com/volkswagen-passat?sorting=date_desc", "name": "Passat"},
        }
    },
    "opel": {
        "display_name": "Opel",
        "models": {
            "corsa": {"url": "https://www.sahibinden.com/opel-corsa?sorting=date_desc", "name": "Corsa"},
            "astra": {"url": "https://www.sahibinden.com/opel-astra?sorting=date_desc", "name": "Astra"},
        }
    },
    "fiat": {
        "display_name": "Fiat",
        "models": {
            "egea": {"url": "https://www.sahibinden.com/fiat-egea?sorting=date_desc", "name": "Egea"},
            "doblo": {"url": "https://www.sahibinden.com/fiat-doblo?sorting=date_desc", "name": "Doblo"},
        }
    },
    "renault": {
        "display_name": "Renault",
        "models": {
            "clio": {"url": "https://www.sahibinden.com/renault-clio?sorting=date_desc", "name": "Clio"},
            "megane": {"url": "https://www.sahibinden.com/renault-megane?sorting=date_desc", "name": "Megane"},
        }
    },
    "toyota": {
        "display_name": "Toyota",
        "models": {
            "corolla": {"url": "https://www.sahibinden.com/toyota-corolla?sorting=date_desc", "name": "Corolla"},
            "c-hr": {"url": "https://www.sahibinden.com/toyota-c-hr?sorting=date_desc", "name": "C-HR"},
        }
    },
    "honda": {
        "display_name": "Honda",
        "models": {
            "civic": {"url": "https://www.sahibinden.com/honda-civic?sorting=date_desc", "name": "Civic"},
        }
    }
}

# --- SAHİBİNDEN VERİ ALANLARI ---
# ML modeli için önemli özellikler
SCRAPE_FIELDS = {
    # Temel Bilgiler
    "İlan No": "ilan_no",
    "İlan Tarihi": "ilan_tarihi",
    
    # Araç Özellikleri (ML için kritik)
    "Marka": "marka",
    "Seri": "seri",
    "Model": "model",
    "Yıl": "yil",
    "Yakıt": "yakit",
    "Vites": "vites",
    "KM": "km",
    "Kasa Tipi": "kasa_tipi",
    "Motor Hacmi": "motor_hacmi",
    "Motor Gücü": "motor_gucu",
    "Çekiş": "cekis",
    
    # Durum Bilgileri
    "Boya-değişen": "boya_degisen",
    "Takasa Uygun": "takas",
    "Kimden": "kimden",
    
    # Renk
    "Renk": "renk",
    
    # Konum
    "İl": "il",
    "İlçe": "ilce",
    "Mahalle": "mahalle",
    "Ülke": "ulke",
}

# --- ML MODEL AYARLARI ---
ML_FEATURES = ["yil", "km", "motor_hacmi", "motor_gucu", "hasar_puani"]  # Sayısal özellikler (hasar puanı dahil)
ML_CATEGORICAL = ["marka", "model", "yakit", "vites", "kasa_tipi", "renk", "il"]  # Kategorik özellikler
FIRSAT_THRESHOLD = 0.85  # Tahmin edilen değerin %85'inden düşükse fırsat

# --- CRON ZAMANLARI ---
# AWS EC2 için crontab formatı
CRON_SCHEDULES = {
    "scrape": "0 */4 * * *",      # Her 4 saatte bir (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)
    "ai_update": "30 */4 * * *",  # Scrape'den 30 dk sonra AI güncelle
    "cleanup": "0 3 * * *",        # Her gece 03:00'te temizlik
}
