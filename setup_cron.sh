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

# Yeni cron job ekle (her 4 saatte bir - 00:00, 04:00, 08:00, 12:00, 16:00, 20:00)
echo "" >> /tmp/clean_cron
echo "# EkerGallery - Otomatik Scraping (4 saatte bir)" >> /tmp/clean_cron
echo "0 */4 * * * /home/ubuntu/EkerGallery/cron_scraper.sh" >> /tmp/clean_cron

# Crontab'ı güncelle
crontab /tmp/clean_cron

# Temizlik
rm /tmp/current_cron /tmp/clean_cron

echo "✅ Cron job kuruldu!"
echo ""
echo "Mevcut cron işleri:"
crontab -l
echo ""
echo "📅 Scraper her 4 saatte bir çalışacak (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)"
