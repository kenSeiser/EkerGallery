#!/bin/bash
# ========================================
# EkerGallery - VPN ile Cron Scraper Script
# ========================================

cd /home/ubuntu/EkerGallery
source myenv/bin/activate

LOG_FILE="/home/ubuntu/EkerGallery/logs/scraper_$(date +%Y%m%d_%H%M%S).log"
mkdir -p /home/ubuntu/EkerGallery/logs

echo "========================================" >> $LOG_FILE
echo "VPN Scraping başlıyor: $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# VPN'i başlat
echo "VPN başlatılıyor..." >> $LOG_FILE
sudo /usr/local/bin/start-vpn.sh >> $LOG_FILE 2>&1
sleep 5

# VPN durumunu kontrol et
if ip addr show tun0 &>/dev/null; then
    echo "VPN aktif - IP: $(curl -s --interface tun0 ifconfig.me)" >> $LOG_FILE
else
    echo "VPN başlatılamadı!" >> $LOG_FILE
    exit 1
fi

# Scraper'ı çalıştır
echo "Scraper çalıştırılıyor..." >> $LOG_FILE
xvfb-run --auto-servernum --server-args="-screen 0 1920x1080x24" python3 -u services/scraper_v2.py >> $LOG_FILE 2>&1

echo "========================================" >> $LOG_FILE
echo "Scraping tamamlandı: $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Eski logları temizle (7 günden eski)
find /home/ubuntu/EkerGallery/logs -name "scraper_*.log" -mtime +7 -delete
