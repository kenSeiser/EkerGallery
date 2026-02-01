# ========================================
# EkerGallery - Veritabanı İşlemleri
# ========================================

from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
import certifi
from datetime import datetime
import sys
import os

# Üst dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONGO_URI, DB_NAME, COLLECTION_NAME


class Database:
    """MongoDB veritabanı yönetim sınıfı"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        """Singleton pattern - tek instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None: # Ensure client is initialized only once for the singleton
            try:
                self._client = MongoClient(
                    MONGO_URI,
                    server_api=ServerApi('1'),
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=5000,  # 5 saniye bekle (önceki 30s idi)
                    connectTimeoutMS=5000
                )
                # Bağlantı testi
                self._client.admin.command('ping')
                print("✅ MongoDB bağlantısı başarılı")
            except ConnectionFailure as e:
                print(f"❌ MongoDB bağlantı hatası: {e}")
                raise
            except Exception as e:
                print(f"❌ MongoDB Başlatma Hatası: {e}")
                raise # Re-raise the exception to indicate connection failure
    
    # The connect method is no longer strictly needed as __init__ handles connection
    # but we can keep it for backward compatibility or explicit connection attempts
    def connect(self):
        """Veritabanına bağlan (if not already connected by __init__)"""
        if self._client is None:
            # This block should ideally not be reached if __init__ works correctly
            # but serves as a fallback or explicit connection trigger.
            try:
                self._client = MongoClient(
                    MONGO_URI,
                    server_api=ServerApi('1'), # Ensure ServerApi is also used here
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000
                )
                self._client.admin.command('ping')
                print("✅ MongoDB bağlantısı başarılı (via connect method)")
            except ConnectionFailure as e:
                print(f"❌ MongoDB bağlantı hatası (via connect method): {e}")
                raise
            except Exception as e:
                print(f"❌ MongoDB Başlatma Hatası (via connect method): {e}")
                raise
        return self._client
    
    @property
    def db(self):
        """Veritabanı referansı"""
        return self.connect()[DB_NAME]
    
    @property
    def vehicles(self):
        """Araç koleksiyonu"""
        return self.db[COLLECTION_NAME]
    
    # ========== ARAÇ İŞLEMLERİ ==========
    
    def upsert_vehicle(self, vehicle_data: dict) -> bool:
        """
        Araç verisi ekle veya güncelle (URL'ye göre)
        
        Args:
            vehicle_data: Araç verileri dict
            
        Returns:
            bool: Yeni eklendiyse True, güncellendiyse False
        """
        if "url" not in vehicle_data:
            return False
        
        # Zaman damgası ekle
        vehicle_data["updated_at"] = datetime.utcnow()
        
        result = self.vehicles.update_one(
            {"url": vehicle_data["url"]},
            {
                "$set": vehicle_data,
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        return result.upserted_id is not None
    
    def get_all_vehicles(self, filters: dict = None, limit: int = None) -> list:
        """
        Tüm araçları getir
        
        Args:
            filters: MongoDB filtre sorgusu
            limit: Maksimum kayıt sayısı
            
        Returns:
            list: Araç listesi
        """
        query = filters or {}
        cursor = self.vehicles.find(query).sort("updated_at", DESCENDING)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    def get_vehicles_by_brand(self, brand: str) -> list:
        """Markaya göre araçları getir"""
        return list(self.vehicles.find({"marka": brand}))
    
    def get_vehicles_by_model(self, brand: str, model: str) -> list:
        """Marka ve modele göre araçları getir"""
        return list(self.vehicles.find({"marka": brand, "model": model}))
    
    def get_firsatlar(self) -> list:
        """AI fırsat olarak işaretlenen araçları getir"""
        return list(self.vehicles.find({"ai_firsat": True}).sort("fark", 1))
    
    def get_vehicles_without_ai(self) -> list:
        """AI tahmini yapılmamış araçları getir"""
        return list(self.vehicles.find({
            "$or": [
                {"ai_tahmin": {"$exists": False}},
                {"ai_tahmin": None},
                {"ai_tahmin": 0}
            ]
        }))
    
    def update_ai_prediction(self, url: str, ai_tahmin: int, ai_firsat: bool, fark: int):
        """
        Araç için AI tahminini güncelle
        
        Args:
            url: Araç URL'si
            ai_tahmin: Tahmin edilen fiyat
            ai_firsat: Fırsat mı?
            fark: Gerçek fiyat - tahmin farkı
        """
        self.vehicles.update_one(
            {"url": url},
            {
                "$set": {
                    "ai_tahmin": ai_tahmin,
                    "ai_firsat": ai_firsat,
                    "fark": fark,
                    "ai_updated_at": datetime.utcnow()
                }
            }
        )
    
    def bulk_update_ai_predictions(self, predictions: list):
        """
        Toplu AI tahmin güncellemesi
        
        Args:
            predictions: [{"url": ..., "ai_tahmin": ..., "ai_firsat": ..., "fark": ...}, ...]
        """
        from pymongo import UpdateOne
        
        operations = [
            UpdateOne(
                {"url": p["url"]},
                {"$set": {
                    "ai_tahmin": p["ai_tahmin"],
                    "ai_firsat": p["ai_firsat"],
                    "fark": p["fark"],
                    "ai_updated_at": datetime.utcnow()
                }}
            )
            for p in predictions
        ]
        
        if operations:
            result = self.vehicles.bulk_write(operations)
            print(f"✅ {result.modified_count} araç için AI tahmini güncellendi")
    
    # ========== İSTATİSTİKLER ==========
    
    def get_stats(self) -> dict:
        """Genel istatistikleri getir"""
        total = self.vehicles.count_documents({})
        firsatlar = self.vehicles.count_documents({"ai_firsat": True})
        
        # Marka dağılımı
        brand_pipeline = [
            {"$group": {"_id": "$marka", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        brand_stats = list(self.vehicles.aggregate(brand_pipeline))
        
        # Ortalama fiyat
        avg_pipeline = [
            {"$match": {"fiyat": {"$gt": 0}}},
            {"$group": {"_id": None, "avg_price": {"$avg": "$fiyat"}}}
        ]
        avg_result = list(self.vehicles.aggregate(avg_pipeline))
        avg_price = avg_result[0]["avg_price"] if avg_result else 0
        
        return {
            "total": total,
            "firsatlar": firsatlar,
            "avg_price": int(avg_price),
            "brand_distribution": brand_stats
        }
    
    # ========== TEMİZLİK ==========
    
    def remove_duplicates(self) -> int:
        """Mükerrer kayıtları sil (URL bazlı)"""
        pipeline = [
            {"$group": {
                "_id": "$url",
                "ids": {"$push": "$_id"},
                "count": {"$sum": 1}
            }},
            {"$match": {"count": {"$gt": 1}}}
        ]
        
        duplicates = list(self.vehicles.aggregate(pipeline))
        removed = 0
        
        for doc in duplicates:
            # İlk kaydı tut, diğerlerini sil
            ids_to_remove = doc["ids"][:-1]
            if ids_to_remove:
                result = self.vehicles.delete_many({"_id": {"$in": ids_to_remove}})
                removed += result.deleted_count
        
        print(f"🧹 {removed} mükerrer kayıt silindi")
        return removed
    
    def remove_old_listings(self, days: int = 30) -> int:
        """Eski ilanları sil"""
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = self.vehicles.delete_many({"updated_at": {"$lt": cutoff}})
        
        print(f"🧹 {result.deleted_count} eski ilan silindi ({days} günden eski)")
        return result.deleted_count
    
    def close(self):
        """Bağlantıyı kapat"""
        if self._client:
            self._client.close()
            self._client = None
            print("🔌 MongoDB bağlantısı kapatıldı")


# Singleton instance
db = Database()
