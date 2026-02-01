# 📚 EkerGallery v2.0 - Proje Dokümantasyonu

> **Proje Adı:** EkerGallery - Premium Araç Veri Merkezi  
> **Versiyon:** 2.0  
> **Son Güncelleme:** Şubat 2026

---

## 🚀 Yenilikler (v2.0)

### Mimari İyileştirmeler
- ✅ **AI Tahminleri Veritabanında** - Artık her sorgu için yeniden hesaplanmıyor
- ✅ **Modüler Yapı** - Servisler, modeller ve konfigürasyon ayrıldı
- ✅ **Cron Job Altyapısı** - Otomatik veri çekme ve AI güncelleme
- ✅ **Gelişmiş Veri Çekimi** - Marka, model, yakıt, vites, motor hacmi vb.
- ✅ **Modern UI** - Dropdown menü, responsif tasarım, glassmorphism
- ✅ **RESTful API** - Frontend-Backend ayrımı

### Teknik İyileştirmeler
- ✅ **Singleton Database** - Bağlantı havuzu optimizasyonu
- ✅ **GradientBoosting ML** - Daha iyi fiyat tahmini
- ✅ **Batch AI Updates** - Toplu veritabanı güncellemesi
- ✅ **Environment Variables** - Güvenli konfigürasyon

---

## 📁 Yeni Dosya Yapısı

```
EkerGallery/
├── 📄 app_v2.py              # ⭐ YENİ: Modern Flask uygulaması
├── 📄 config.py              # ⭐ YENİ: Merkezi konfigürasyon
├── 📄 requirements.txt       # Python bağımlılıkları
├── 📄 .env.example           # Ortam değişkenleri örneği
├── 📄 .gitignore             # Git ignore kuralları
│
├── 📁 models/                # ⭐ YENİ: Veritabanı modelleri
│   ├── __init__.py
│   └── database.py           # MongoDB işlemleri
│
├── 📁 services/              # ⭐ YENİ: İş mantığı servisleri
│   ├── __init__.py
│   ├── ai_model.py           # AI fiyat tahmin modülü
│   └── scraper_v2.py         # Gelişmiş web scraper
│
├── 📁 templates/             # ⭐ YENİ: HTML template'leri
│   ├── login.html            # Modern giriş sayfası
│   ├── dashboard.html        # Ana dashboard
│   ├── 404.html              # Hata sayfası
│   └── 500.html              # Hata sayfası
│
├── 📄 cron_runner.sh         # ⭐ YENİ: Cron job scripti
├── 📄 setup_cron.sh          # ⭐ YENİ: Crontab kurulum scripti
│
├── 📄 app.py                 # [ESKİ] Eski Flask uygulaması
├── 📄 scraper.py             # [ESKİ] Eski scraper
└── ...
```

---

## 🗄 Yeni Veritabanı Şeması

### Araç Dokümanı (tum_araclar koleksiyonu)

```json
{
    "_id": ObjectId("..."),
    
    // Temel Bilgiler
    "baslik": "2022 Tesla Model Y Long Range",
    "url": "https://www.sahibinden.com/ilan/...",
    "category": "Tesla Model Y",
    
    // Araç Özellikleri (ML için)
    "marka": "Tesla",
    "model": "Model Y",
    "yil": 2022,
    "km": 25000,
    "fiyat": 2500000,
    "yakit": "Elektrik",
    "vites": "Otomatik",
    "kasa_tipi": "SUV",
    "motor_hacmi": 0,
    "motor_gucu": 346,
    "cekis": "4x4",
    
    // Durum Bilgileri
    "boya_degisen": "Değişen yok",
    "takas": "Hayır",
    "kimden": "Sahibinden",
    "renk": "Beyaz",
    
    // Konum
    "il": "İstanbul",
    "ilce": "Kadıköy",
    
    // AI Tahminleri (artık DB'de saklanıyor!)
    "ai_tahmin": 2750000,
    "ai_firsat": true,
    "fark": -250000,
    "ai_updated_at": ISODate("2026-02-01T16:00:00Z"),
    
    // Zaman Damgaları
    "scraped_at": ISODate("2026-02-01T12:00:00Z"),
    "created_at": ISODate("2026-02-01T12:00:00Z"),
    "updated_at": ISODate("2026-02-01T16:00:00Z")
}
```

---

## 🧠 AI Model Detayları

### Kullanılan Özellikler

| Özellik | Tip | Açıklama |
|---------|-----|----------|
| `yil` | Sayısal | Araç model yılı |
| `km` | Sayısal | Kilometre |
| `motor_hacmi` | Sayısal | Motor hacmi (cc) |
| `motor_gucu` | Sayısal | Motor gücü (hp) |
| `marka` | Kategorik | Araç markası |
| `model` | Kategorik | Araç modeli |
| `yakit` | Kategorik | Yakıt tipi |
| `vites` | Kategorik | Vites tipi |
| `kasa_tipi` | Kategorik | Kasa tipi |
| `renk` | Kategorik | Araç rengi |
| `il` | Kategorik | Konum (il) |

### Model Algoritması

```python
# GradientBoostingRegressor kullanılıyor
model = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
```

### Fırsat Tespiti

```python
FIRSAT_THRESHOLD = 0.85  # %85

# Fiyat, tahmin edilen değerin %85'inden düşükse fırsat
if fiyat < (ai_tahmin * 0.85):
    ai_firsat = True
```

---

## ⏰ Cron Job Zamanlaması

### Zamanlanmış Görevler

| Görev | Zamanlama | Açıklama |
|-------|-----------|----------|
| **Scrape** | Her 4 saatte | 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 |
| **AI Update** | Scrape + 30dk | 00:30, 04:30, 08:30, 12:30, 16:30, 20:30 |
| **Cleanup** | Her gece 03:00 | Mükerrer ve eski kayıtları sil |
| **Log Rotation** | Pazar 04:00 | Logları sıkıştır |

### Neden 4 Saat?

1. **Sahibinden Güncellemesi**: İlanlar genellikle günde birkaç kez güncellenir
2. **Sunucu Yükü**: Çok sık çekme sunucu yükünü artırır
3. **Bot Algılama**: Sık istekler bot algılamayı tetikleyebilir
4. **Veri Kalitesi**: 4 saat yeni ilanları yakalamak için yeterli

### Kurulum (AWS EC2)

```bash
# 1. Script'leri çalıştırılabilir yap
chmod +x cron_runner.sh setup_cron.sh

# 2. Cron job'ları kur
./setup_cron.sh

# 3. Cron durumunu kontrol et
crontab -l

# 4. Logları izle
tail -f /var/log/ekergallery/scrape.log
```

---

## 🖥 Modern UI Özellikleri

### Sidebar (Sol Menü)
- ✅ Collapsible dropdown menüler
- ✅ Marka > Model hiyerarşisi
- ✅ AI Fırsatları kısayolu
- ✅ Yönetim araçları

### Dashboard
- ✅ Canlı istatistik kartları
- ✅ Dinamik ortalama hesaplama
- ✅ Gelişmiş filtreler (Marka, Model, Fiyat, Yıl)
- ✅ DataTables entegrasyonu
- ✅ CSV Export

### Responsive Tasarım
- ✅ Desktop optimizasyonu
- ✅ Tablet desteği
- ✅ Mobil uyumluluk

---

## 🔌 API Endpoints

### Araç Listesi
```
GET /api/vehicles?brand=Tesla&model=Model%20Y&min_price=1000000
```

**Query Parametreleri:**
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `brand` | string | Marka filtresi |
| `model` | string | Model filtresi |
| `min_price` | int | Minimum fiyat |
| `max_price` | int | Maksimum fiyat |
| `min_year` | int | Minimum yıl |
| `max_year` | int | Maksimum yıl |
| `fuel` | string | Yakıt tipi |
| `transmission` | string | Vites tipi |
| `firsatlar` | bool | Sadece fırsatlar |
| `limit` | int | Kayıt limiti |

### Fırsat Listesi
```
GET /api/firsatlar
```

### İstatistikler
```
GET /api/stats
```

### Marka Listesi
```
GET /api/brands
```

### AI Güncelleme
```
POST /update-ai
```

### Veri Temizleme
```
POST /clean-duplicates
```

---

## 🚀 Kurulum ve Çalıştırma

### 1. Bağımlılıkları Kur
```bash
cd EkerGallery
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

### 2. Ortam Değişkenlerini Ayarla
```bash
cp .env.example .env
nano .env  # Değerleri düzenle
```

### 3. ChromeDriver İndir
```bash
python3 tamirci.py
```

### 4. Uygulamayı Başlat

**Geliştirme:**
```bash
python3 app_v2.py
```

**Üretim (Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app_v2:app
```

### 5. Cron Job'ları Kur (AWS EC2)
```bash
./setup_cron.sh
```

---

## 📊 Performans Karşılaştırması

| Metrik | v1.0 (Eski) | v2.0 (Yeni) |
|--------|------------|-------------|
| Sayfa Yükleme | ~5 saniye | ~0.3 saniye |
| AI Hesaplama | Her istekte | Önceden hesaplanmış |
| Veri Çekimi | Manuel | Otomatik (4 saat) |
| ML Özellikleri | 2 (yıl, km) | 11+ |
| API Desteği | Yok | RESTful |
| Mobile UI | Kısmi | Tam responsive |

---

## 🔐 Güvenlik

⚠️ **Üretim için yapılması gerekenler:**

1. ✅ `.env` dosyası kullan (kod içinde şifre yok)
2. ✅ `.gitignore` güncel
3. ⏳ HTTPS sertifikası (Cloudflare/Let's Encrypt)
4. ⏳ Rate limiting
5. ⏳ Input validation

---

## 📝 Sonraki Adımlar

1. [ ] Kullanıcı yönetimi (multi-tenant)
2. [ ] Email/SMS bildirimleri (fırsat bulunduğunda)
3. [ ] Fiyat geçmişi grafikleri
4. [ ] Daha fazla araç kategorisi
5. [ ] Mobil uygulama (React Native)

---

*Dokümantasyon v2.0 - Şubat 2026*
