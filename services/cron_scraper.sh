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

# Aggressive Scraper'ı çalıştır (Proxy rotasyonu ile veri alana kadar dener)
# --attempts: Kategori başına max proxy denemesi
# --pages: Kategori başına sayfa sayısı
xvfb-run --auto-servernum --server-args="-screen 0 1920x1080x24" python3 -u services/aggressive_scraper.py --attempts 50 --pages 3 >> $LOG_FILE 2>&1

# Sonuç
echo "========================================" >> $LOG_FILE
echo "Scraping tamamlandı: $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Eski logları temizle (7 günden eski)
find /home/ubuntu/EkerGallery/logs -name "scraper_*.log" -mtime +7 -delete
