# ========================================
# EkerGallery - Veritabanı İşlemleri
# ========================================

from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi
import certifi
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONGO_URI, DB_NAME, COLLECTION_NAME


class Database:
    """MongoDB veritabanı yönetim sınıfı"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Lazy connection: MongoDB'ye ilk istekte bağlan (worker'ın boot olması için)
        if Database._client is None:
            try:
                Database._client = MongoClient(
                    MONGO_URI,
                    server_api=ServerApi('1'),
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=10000,
                    connectTimeoutMS=10000
                )
                Database._client.admin.command('ping')
                print("[OK] MongoDB baglantisi basarili")
                # Indeksleri olustur
                self._ensure_indexes()
            except Exception as e:
                print(f"[HATA] MongoDB baglanti hatasi (ilk istekte tekrar denenecek): {e}")
                Database._client = None

    def _ensure_indexes(self):
        """Performans icin gerekli indeksleri olustur"""
        try:
            coll = self.vehicles
            print("[INFO] Indeksler kontrol ediliyor...")
            
            # Filtreleme ve siralama icin temel indeksler
            coll.create_index([("marka", 1)])
            coll.create_index([("model", 1)])
            coll.create_index([("fiyat", 1)])
            coll.create_index([("yil", 1)])
            coll.create_index([("yakit", 1)])
            coll.create_index([("vites", 1)])
            coll.create_index([("ai_firsat", 1)])
            coll.create_index([("updated_at", -1)])
            
            # Bilesik indeksler (Hizli filtreleme icin)
            coll.create_index([("marka", 1), ("model", 1)])
            coll.create_index([("marka", 1), ("fiyat", 1)])
            
            # URL benzersiz olmali
            coll.create_index([("url", 1)], unique=True)
            
            print("[OK] Veritabani indeksleri hazir")
        except Exception as e:
            print(f"[UYARI] Indeks olusturma hatasi: {e}")

    def connect(self):
        if self._client is None:
            try:
                self._client = MongoClient(
                    MONGO_URI,
                    server_api=ServerApi('1'),
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000
                )
                self._client.admin.command('ping')
                print("[OK] MongoDB baglantisi basarili (via connect method)")
            except ConnectionFailure as e:
                print(f"[HATA] MongoDB baglanti hatasi: {e}")
                raise
            except Exception as e:
                print(f"[HATA] MongoDB Baslatma Hatasi: {e}")
                raise
        return self._client

    @property
    def db(self):
        return self.connect()[DB_NAME]

    @property
    def vehicles(self):
        return self.db[COLLECTION_NAME]

    def upsert_vehicle(self, vehicle_data: dict) -> bool:
        if "url" not in vehicle_data:
            return False
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

    def get_all_vehicles(self, filters: dict = None, limit: int = None, skip: int = 0, projection: dict = None) -> list:
        query = filters or {}
        cursor = self.vehicles.find(query, projection).sort("updated_at", DESCENDING)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def get_vehicles_by_brand(self, brand: str) -> list:
        return list(self.vehicles.find({"marka": brand}))

    def get_vehicles_by_model(self, brand: str, model: str) -> list:
        return list(self.vehicles.find({"marka": brand, "model": model}))

    def get_firsatlar(self) -> list:
        return list(self.vehicles.find({"ai_firsat": True}).sort("fark", 1))

    def get_vehicles_without_ai(self) -> list:
        return list(self.vehicles.find({
            "$or": [
                {"ai_tahmin": {"$exists": False}},
                {"ai_tahmin": None},
                {"ai_tahmin": 0}
            ]
        }))

    def update_ai_prediction(self, url: str, ai_tahmin: int, ai_firsat: bool, fark: int):
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
            print(f"[OK] {result.modified_count} arac icin AI tahmini guncellendi")

    def get_stats(self, filters: dict = None) -> dict:
        query = filters or {}
        
        # Toplam araç sayısı (filtreye göre)
        total = self.vehicles.count_documents(query)
        
        # Fırsat sayısı (filtre + ai_firsat)
        firsat_query = query.copy()
        firsat_query["ai_firsat"] = True
        firsatlar = self.vehicles.count_documents(firsat_query)
        
        # Marka dağılımı (filtreye göre)
        brand_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$marka", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        brand_stats = list(self.vehicles.aggregate(brand_pipeline))
        
        # Ortalama fiyat (filtreye göre)
        avg_match = query.copy()
        avg_match["fiyat"] = {"$gt": 0}
        
        avg_pipeline = [
            {"$match": avg_match},
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

    def remove_duplicates(self) -> int:
        pipeline = [
            {"$group": {"_id": "$url", "ids": {"$push": "$_id"}, "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(self.vehicles.aggregate(pipeline))
        removed = 0
        for doc in duplicates:
            ids_to_remove = doc["ids"][:-1]
            if ids_to_remove:
                result = self.vehicles.delete_many({"_id": {"$in": ids_to_remove}})
                removed += result.deleted_count
        print(f"[TEMIZLIK] {removed} mukerrer kayit silindi")
        return removed

    def remove_old_listings(self, days: int = 30) -> int:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = self.vehicles.delete_many({"updated_at": {"$lt": cutoff}})
        print(f"[TEMIZLIK] {result.deleted_count} eski ilan silindi ({days} gunden eski)")
        return result.deleted_count

    @property
    def users(self):
        return self.db['users']

    def create_user(self, username, password_hash, role='user'):
        """Yeni kullanıcısı oluştur"""
        if self.get_user(username):
            return False
        
        user_data = {
            "username": username,
            "password": password_hash,
            "role": role,
            "created_at": datetime.utcnow()
        }
        self.users.insert_one(user_data)
        return True

    def get_user(self, username):
        """Kullanıcıyı getir"""
        return self.users.find_one({"username": username})

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            print("[KAPAT] MongoDB baglantisi kapatildi")


db = Database()
