#!/bin/bash
# ========================================
# EkerGallery - Cron Setup Script
# EC2'de cron job'ları kurar
# ========================================

echo "🚀 EkerGallery Cron Job Kurulumu"
echo "================================"

# Cron scraper script'ini çalıştırılabilir yap
chmod +x /home/ubuntu/EkerGallery/cron_scraper.sh

# Mevcut crontab'ı al
crontab -l > /tmp/current_cron 2>/dev/null || echo "" > /tmp/current_cron

# EkerGallery job'larını kaldır (varsa)
grep -v "EkerGallery" /tmp/current_cron > /tmp/clean_cron

# Yeni cron job ekle (her gece 03:00'te)
echo "" >> /tmp/clean_cron
echo "# EkerGallery - Otomatik Scraping (her gece 03:00)" >> /tmp/clean_cron
echo "0 3 * * * /home/ubuntu/EkerGallery/cron_scraper.sh" >> /tmp/clean_cron

# Crontab'ı güncelle
crontab /tmp/clean_cron

# Temizlik
rm /tmp/current_cron /tmp/clean_cron

echo "✅ Cron job kuruldu!"
echo ""
echo "Mevcut cron işleri:"
crontab -l
echo ""
echo "📅 Scraper her gece 03:00'te çalışacak (UTC)"
