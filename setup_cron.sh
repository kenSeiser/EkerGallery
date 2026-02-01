#!/bin/bash
# ========================================
# EkerGallery - Crontab Kurulum Script'i
# ========================================
# 
# AWS EC2 sunucusuna cron job'ları kurar.
# Kullanım: ./setup_cron.sh
#

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/var/log/ekergallery"

echo "📅 EkerGallery Cron Kurulumu Başlıyor..."
echo "=========================================="

# Log dizini oluştur
if [ ! -d "$LOG_DIR" ]; then
    echo "📁 Log dizini oluşturuluyor: $LOG_DIR"
    sudo mkdir -p "$LOG_DIR"
    sudo chown $(whoami):$(whoami) "$LOG_DIR"
fi

# Cron script'ini çalıştırılabilir yap
chmod +x "$PROJECT_DIR/cron_runner.sh"

# Mevcut crontab'ı yedekle
echo "💾 Mevcut crontab yedekleniyor..."
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true

# Yeni crontab oluştur
CRON_CONTENT="
# ========================================
# EkerGallery Zamanlanmış Görevler
# ========================================
# Oluşturulma: $(date)

# Python için PATH ve DISPLAY ayarları
PATH=/usr/local/bin:/usr/bin:/bin
DISPLAY=:0

# ----------------------------------------
# VERİ ÇEKME (Her 4 saatte bir)
# Saatler: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00
# ----------------------------------------
0 */4 * * * cd $PROJECT_DIR && ./cron_runner.sh scrape >> $LOG_DIR/scrape.log 2>&1

# ----------------------------------------
# AI TAHMİN GÜNCELLEME (Scrape'den 30dk sonra)
# Saatler: 00:30, 04:30, 08:30, 12:30, 16:30, 20:30
# ----------------------------------------
30 */4 * * * cd $PROJECT_DIR && ./cron_runner.sh ai >> $LOG_DIR/ai.log 2>&1

# ----------------------------------------
# VERİTABANI TEMİZLİĞİ (Her gece 03:00)
# Mükerrer kayıtları ve eski ilanları siler
# ----------------------------------------
0 3 * * * cd $PROJECT_DIR && ./cron_runner.sh cleanup >> $LOG_DIR/cleanup.log 2>&1

# ----------------------------------------
# LOG ROTASYONU (Her hafta Pazar 04:00)
# Logları sıkıştır ve eski olanları sil
# ----------------------------------------
0 4 * * 0 find $LOG_DIR -name '*.log' -exec gzip {} \; && find $LOG_DIR -name '*.gz' -mtime +30 -delete

# ========================================
"

# Crontab'ı güncelle
echo "$CRON_CONTENT" | crontab -

echo ""
echo "✅ Crontab başarıyla güncellendi!"
echo ""
echo "📋 Aktif Cron Job'lar:"
echo "----------------------------------------"
crontab -l
echo "----------------------------------------"
echo ""
echo "📊 Log dosyaları: $LOG_DIR"
echo ""
echo "🔍 Logları izlemek için:"
echo "   tail -f $LOG_DIR/scrape.log"
echo "   tail -f $LOG_DIR/ai.log"
echo "   tail -f $LOG_DIR/cleanup.log"
