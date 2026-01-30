from pymongo import MongoClient
import certifi

# --- AYARLAR ---
uri = "mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?appName=ekerard"
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["sahibinden_data"]

# Hedef Tablo (Hepsinin toplanacağı yer)
hedef_tablo = db["tum_araclar"]

print(f"--- AKILLI VERİ BİRLEŞTİRME BAŞLADI ---")

# Veritabanındaki tüm klasörleri bul
tum_tablolar = db.list_collection_names()

toplam_islenen = 0
yeni_eklenen = 0

for tablo_adi in tum_tablolar:
    # 1. Hedef tablonun kendisini tekrar kopyalama
    # 2. Sistem dosyalarını (system.indexes vs) atla
    if tablo_adi == "tum_araclar" or tablo_adi.startswith("system."):
        continue
        
    kaynak_tablo = db[tablo_adi]
    veriler = list(kaynak_tablo.find())
    
    # Klasör isminden Kategori Adı Üret (Örn: 'vw_polo' -> 'VW Polo')
    kategori_adi = tablo_adi.replace("_", " ").title()
    # Özel düzeltmeler (İstersen buraya ekleme yapabilirsin)
    if "vw" in tablo_adi: kategori_adi = kategori_adi.replace("Vw", "VW")
    if "bmw" in tablo_adi: kategori_adi = kategori_adi.replace("Bmw", "BMW")
    
    if len(veriler) > 0:
        print(f"🔄 '{tablo_adi}' klasörü taranıyor... ({len(veriler)} ilan)")
        print(f"   🏷️  Bu klasördeki araçlar '{kategori_adi}' olarak etiketlenecek.")
        
        for veri in veriler:
            # URL yoksa bu veriyi atla (Bozuk veri)
            if "url" not in veri:
                continue

            # Eğer veride kategori yazmıyorsa, klasör adından ürettiğimizi kullan
            if "category" not in veri:
                veri["category"] = kategori_adi

            # _id kısmını siliyoruz ki hedef tabloda çakışma olmasın
            if "_id" in veri:
                del veri["_id"]

            # --- SİHİRLİ KISIM (UPSERT) ---
            # URL'ye göre kontrol et: Varsa GÜNCELLE, Yoksa EKLE
            sonuc = hedef_tablo.update_one(
                {"url": veri["url"]},  # Bu link var mı?
                {"$set": veri},        # Varsa verileri güncelle
                upsert=True            # Yoksa yeni oluştur
            )
            
            if sonuc.upserted_id:
                yeni_eklenen += 1
            
            toplam_islenen += 1

print(f"-------------------------------------------")
print(f"✅ İŞLEM TAMAMLANDI!")
print(f"🔎 Toplam İncelenen: {toplam_islenen}")
print(f"🆕 Yeni Eklenen: {yeni_eklenen} (Gerisi güncellendi)")
