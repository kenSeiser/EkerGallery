#!/bin/bash
# ========================================
# EkerGallery - Sunucu Güncelleme Scripti
# ========================================
#
# Bu script projeyi GitHub'dan günceller ve servisi yeniden başlatır.
# Sunucuda (EC2) çalıştırılmalıdır.
#

set -e

# Renkli çıktılar
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 EkerGallery Güncellemesi Başlıyor...${NC}"

# 1. Kodları Çek
echo "📥 Git üzerinden güncellemeler alınıyor..."
git pull origin main

# 2. Bağımlılıkları Güncelle
echo "📦 Bağımlılıklar kontrol ediliyor..."
source myenv/bin/activate
pip install -r requirements.txt -q

# 3. İzinleri Ayarla
chmod +x cron_runner.sh setup_cron.sh

# 4. Servisi Yeniden Başlat
echo "🔄 Servis yeniden başlatılıyor..."
pkill -f "gunicorn" || true
pkill -f "python3 app_v2.py" || true

# Gunicorn ile başlat (Daemon modunda)
nohup gunicorn -w 4 -b 0.0.0.0:5000 app_v2:app \
    --access-logfile /var/log/ekergallery/access.log \
    --error-logfile /var/log/ekergallery/error.log \
    --daemon

echo -e "${GREEN}✅ Güncelleme Tamamlandı! Servis 5000 portunda aktif.${NC}"
echo "📝 Logları izlemek için: tail -f /var/log/ekergallery/error.log"
