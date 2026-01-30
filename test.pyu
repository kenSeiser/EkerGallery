from pymongo import MongoClient
import certifi

# Bağlantı adresini direkt buraya yazıyorum (senin verdiğin bilgilerle)
# Eğer şifreni değiştirdiysen burayı düzelt!
uri = "mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?retryWrites=true&w=majority&appName=ekerard"

try:
    print("⏳ Bağlanılıyor...")
    client = MongoClient(uri, tlsCAFile=certifi.where())
    
    # Ping atarak testi yap
    client.admin.command('ping')
    print("✅ BAŞARILI! Şifre doğru ve bağlantı çalışıyor.")
except Exception as e:
    print("\n❌ HATA! Bağlantı sağlanamadı.")
    print(f"Hata Sebebi: {e}")
