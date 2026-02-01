# ========================================
# EkerGallery - AI Fiyat Tahmin Modülü
# ========================================

import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os
import sys
from datetime import datetime

# Üst dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ML_FEATURES, ML_CATEGORICAL, FIRSAT_THRESHOLD
from models.database import db


class PricePredictionModel:
    """Araç fiyat tahmin modeli"""
    
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "price_model.pkl")
    ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "encoders.pkl")
    SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = {}
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """Kaydedilmiş modeli yükle"""
        try:
            if os.path.exists(self.MODEL_PATH):
                with open(self.MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.ENCODERS_PATH, 'rb') as f:
                    self.encoders = pickle.load(f)
                with open(self.SCALER_PATH, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
                print("✅ AI modeli yüklendi")
        except Exception as e:
            print(f"⚠️ Model yüklenemedi: {e}")
    
    def _save_model(self):
        """Modeli kaydet"""
        try:
            with open(self.MODEL_PATH, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.ENCODERS_PATH, 'wb') as f:
                pickle.dump(self.encoders, f)
            with open(self.SCALER_PATH, 'wb') as f:
                pickle.dump(self.scaler, f)
            print("💾 AI modeli kaydedildi")
        except Exception as e:
            print(f"❌ Model kaydedilemedi: {e}")
    
    def _prepare_features(self, vehicle: dict) -> dict:
        """Araç verisinden özellik çıkar"""
        features = {}
        
        # Sayısal özellikler
        for field in ML_FEATURES:
            value = vehicle.get(field, 0)
            if isinstance(value, str):
                # "25.000 km" -> 25000
                value = ''.join(filter(str.isdigit, value))
                value = int(value) if value else 0
            features[field] = value
        
        # Kategorik özellikler
        for field in ML_CATEGORICAL:
            features[field] = str(vehicle.get(field, "Bilinmiyor"))
        
        return features
    
    def _encode_features(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        """Özellikleri encode et"""
        encoded_df = df.copy()
        
        # Kategorik değişkenleri encode et
        for col in ML_CATEGORICAL:
            if col in encoded_df.columns:
                if fit:
                    self.encoders[col] = LabelEncoder()
                    self.encoders[col].fit(encoded_df[col].astype(str))
                
                if col in self.encoders:
                    # Bilinmeyen değerleri handle et
                    encoded_df[col] = encoded_df[col].apply(
                        lambda x: x if x in self.encoders[col].classes_ else "Bilinmiyor"
                    )
                    encoded_df[col] = self.encoders[col].transform(encoded_df[col].astype(str))
        
        # Sayısal değerleri scale et
        if fit:
            self.scaler = StandardScaler()
            return self.scaler.fit_transform(encoded_df.values)
        else:
            return self.scaler.transform(encoded_df.values)
    
    def train(self, min_samples: int = 10):
        """
        Modeli eğit
        
        Args:
            min_samples: Minimum eğitim örneği sayısı
        """
        print("🧠 AI modeli eğitiliyor...")
        
        # Verileri çek
        vehicles = db.get_all_vehicles({"fiyat": {"$gt": 100000}})
        
        if len(vehicles) < min_samples:
            print(f"⚠️ Yetersiz veri: {len(vehicles)} < {min_samples}. Basit tahmin kullanılacak.")
            self.is_trained = False
            return False
        
        # DataFrame oluştur
        data = []
        for v in vehicles:
            try:
                features = self._prepare_features(v)
                features["fiyat"] = v.get("fiyat", 0)
                
                # Geçersiz verileri atla
                if features["yil"] < 1990 or features["fiyat"] < 50000:
                    continue
                    
                data.append(features)
            except:
                continue
        
        if len(data) < min_samples:
            print(f"⚠️ Geçerli veri yetersiz. Basit tahmin kullanılacak.")
            self.is_trained = False
            return False
        
        df = pd.DataFrame(data)
        
        # Özellikler ve hedef
        feature_cols = ML_FEATURES + ML_CATEGORICAL
        X = df[feature_cols]
        y = df["fiyat"]
        
        # Encode et
        X_encoded = self._encode_features(X, fit=True)
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y, test_size=0.2, random_state=42
        )
        
        # Model eğit (Gradient Boosting daha iyi sonuç verir)
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Değerlendirme
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"📊 Eğitim Skoru: {train_score:.3f}")
        print(f"📊 Test Skoru: {test_score:.3f}")
        
        self.is_trained = True
        self._save_model()
        
        return True
    
    def _simple_predict(self, vehicle: dict) -> int:
        """ML modeli yoksa basit kural tabanlı tahmin"""
        try:
            # Benzer araçların ortalamasını bul
            marka = vehicle.get("marka")
            model = vehicle.get("model")
            yil = vehicle.get("yil", 2020)
            km = vehicle.get("km", 100000)
            
            # Veritabanından benzer araçları çek
            similars = db.get_vehicles_by_model(marka, model)
            if not similars:
                return 0
                
            prices = [s.get("fiyat", 0) for s in similars if s.get("fiyat", 0) > 50000]
            if not prices:
                return 0
                
            avg_price = sum(prices) / len(prices)
            
            # KM ve Yıl düzeltmesi (Basit mantık)
            avg_km = sum([s.get("km", 0) for s in similars]) / len(similars)
            
            # Her 10.000 KM farkı için %2 değişim
            km_diff = avg_km - km
            km_factor = (km_diff / 10000) * 0.02
            
            # Hasar puanı düzeltmesi
            # Her 10 puan = yaklaşık %2.5 fiyat düşüşü
            # Boyalı (5 puan) = %1.25 düşüş, Değişen (15 puan) = %3.75 düşüş
            hasar_puani = vehicle.get("hasar_puani", 0)
            hasar_factor = -(hasar_puani / 10) * 0.025  # Negatif (fiyatı düşürür)
            
            final_price = avg_price * (1 + km_factor + hasar_factor)
            return int(max(0, final_price))
        except:
            return 0

    def predict(self, vehicle: dict) -> int:
        """
        Tek araç için fiyat tahmini
        
        Args:
            vehicle: Araç verisi
            
        Returns:
            int: Tahmin edilen fiyat
        """
        # Eğer model eğitilmemişse basit tahmin kullan
        if not self.is_trained:
            return self._simple_predict(vehicle)
        
        try:
            features = self._prepare_features(vehicle)
            feature_cols = ML_FEATURES + ML_CATEGORICAL
            df = pd.DataFrame([features])[feature_cols]
            X_encoded = self._encode_features(df, fit=False)
            
            prediction = self.model.predict(X_encoded)[0]
            return int(max(0, prediction))
        except Exception as e:
            print(f"⚠️ ML Hatası, simple predict deneniyor: {e}")
            return self._simple_predict(vehicle)
    
    def predict_batch(self, vehicles: list) -> list:
        """
        Toplu fiyat tahmini
        
        Args:
            vehicles: Araç listesi
            
        Returns:
            list: Tahmin listesi [{"url": ..., "ai_tahmin": ..., "ai_firsat": ..., "fark": ...}, ...]
        """
        if not self.is_trained:
            print("⚠️ Model henüz eğitilmedi")
            # Even if not trained, simple_predict will be called by predict()
            # So we don't need to return [] here, just let the loop run
        
        results = []
        
        for v in vehicles:
            try:
                fiyat = v.get("fiyat", 0)
                if fiyat < 10000:
                    continue
                
                tahmin = self.predict(v)
                if tahmin <= 0:
                    continue
                
                fark = fiyat - tahmin
                firsat = fiyat < (tahmin * FIRSAT_THRESHOLD)
                
                results.append({
                    "url": v.get("url"),
                    "ai_tahmin": tahmin,
                    "ai_firsat": firsat,
                    "fark": fark
                })
            except:
                continue
        
        return results
    
    def update_all_predictions(self):
        """Tüm araçlar için AI tahminlerini güncelle ve veritabanına kaydet"""
        print("🔄 AI tahminleri güncelleniyor...")
        
        # Önce modeli eğit (varsa güncelle)
        self.train()
        
        # Tüm araçları çek
        vehicles = db.get_all_vehicles({"fiyat": {"$gt": 50000}})
        print(f"📊 {len(vehicles)} araç için tahmin yapılacak")
        
        # Tahminleri yap
        predictions = self.predict_batch(vehicles)
        
        # Veritabanına kaydet
        if predictions:
            db.bulk_update_ai_predictions(predictions)
            # İstatistik
            firsatlar = sum(1 for p in predictions if p["ai_firsat"])
            print(f"✅ Tahmin tamamlandı: {len(predictions)} araç, {firsatlar} fırsat")
        else:
            print("⚠️ Hiçbir tahmin yapılamadı")


# Singleton instance
price_model = PricePredictionModel()


# ========================================
# CRON JOB ENTRY POINT
# ========================================
if __name__ == "__main__":
    """
    Bu script cron job olarak çalıştırılabilir:
    
    Kullanım:
        python ai_model.py train     # Modeli eğit
        python ai_model.py predict   # Tüm tahminleri güncelle
        python ai_model.py           # Varsayılan: tahminleri güncelle
    """
    import sys
    
    action = sys.argv[1] if len(sys.argv) > 1 else "predict"
    
    if action == "train":
        price_model.train()
    else:
        price_model.update_all_predictions()
