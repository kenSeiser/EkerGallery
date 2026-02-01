#!/bin/bash
# ========================================
# EkerGallery - Cron Scraper Script
# EC2'de 4 saatte bir çalışır
# ========================================

# Dizine git
cd /home/ubuntu/EkerGallery

# Virtual environment'ı aktive et
source myenv/bin/activate

# Log dosyası
LOG_FILE="/home/ubuntu/EkerGallery/logs/scraper_$(date +%Y%m%d_%H%M%S).log"
mkdir -p /home/ubuntu/EkerGallery/logs

echo "========================================" >> $LOG_FILE
echo "Scraping başlıyor: $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Scraper'ı çalıştır (Xvfb ile Headful Stealth Modunda)
# --headful: Scraper'a headless olmadığını söyler
# xvfb-run: Sanal ekran oluşturur
xvfb-run --auto-servernum --server-args="-screen 0 1920x1080x24" python3 -u services/scraper_v2.py --headful >> $LOG_FILE 2>&1

# Sonuç
echo "========================================" >> $LOG_FILE
echo "Scraping tamamlandı: $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Eski logları temizle (7 günden eski)
find /home/ubuntu/EkerGallery/logs -name "scraper_*.log" -mtime +7 -delete
