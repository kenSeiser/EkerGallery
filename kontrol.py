from pymongo import MongoClient
import urllib.parse
import certifi

# Ayarlar
username = "ekerard_db_user"
password = "Ekerard123"
cluster_url = "ekerard.vthareu.mongodb.net"
safe_password = urllib.parse.quote_plus(password)
mongo_uri = f"mongodb+srv://{username}:{safe_password}@{cluster_url}/?retryWrites=true&w=majority&appName=ekerard"

try:
    print("🔌 Veritabanına bağlanılıyor...")
    client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
    db = client["sahibinden_data"]
    
    # Koleksiyonları listele
    print(f"📂 Bulunan Tablolar: {db.list_collection_names()}")
    
    col_name = db.list_collection_names()[0]
    collection = db[col_name]
    
    # İlk veriyi çek
    ilk_veri = collection.find_one()
    
    print("\n" + "="*30)
    print(f"🔎 TABLO: {col_name}")
    print("👇 İŞTE GERÇEK VERİ YAPISI (Bunu bana kopyala):")
    print("="*30)
    print(ilk_veri)
    print("="*30 + "\n")

except Exception as e:
    print(f"❌ Hata: {e}")
