#!/bin/bash
# ========================================
# EkerGallery - Cron Job Ana Script
# ========================================
# 
# Bu script tüm zamanlanmış görevleri yönetir.
# Kullanım: ./cron_runner.sh [scrape|ai|cleanup|all]
#
# Crontab Örneği (AWS EC2):
# ----------------------------------------
# # Her 4 saatte bir veri çek
# 0 */4 * * * /home/ubuntu/EkerGallery/cron_runner.sh scrape >> /var/log/ekergallery/scrape.log 2>&1
#
# # Scrape'den 30dk sonra AI güncelle
# 30 */4 * * * /home/ubuntu/EkerGallery/cron_runner.sh ai >> /var/log/ekergallery/ai.log 2>&1
#
# # Her gece 03:00'te temizlik
# 0 3 * * * /home/ubuntu/EkerGallery/cron_runner.sh cleanup >> /var/log/ekergallery/cleanup.log 2>&1
# ----------------------------------------

set -e

# Proje dizini
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Python virtual environment
VENV_PATH="$PROJECT_DIR/myenv"
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
fi

# Log fonksiyonu
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# ========================================
# GÖREVLER
# ========================================

run_scrape() {
    log "🤖 SCRAPE GÖREVİ BAŞLIYOR"
    log "----------------------------------------"
    
    python3 -u services/scraper_v2.py
    
    log "----------------------------------------"
    log "✅ SCRAPE GÖREVİ TAMAMLANDI"
}

run_ai() {
    log "🧠 AI GÜNCELLEME GÖREVİ BAŞLIYOR"
    log "----------------------------------------"
    
    python3 -u services/ai_model.py predict
    
    log "----------------------------------------"
    log "✅ AI GÜNCELLEME TAMAMLANDI"
}

run_cleanup() {
    log "🧹 TEMİZLİK GÖREVİ BAŞLIYOR"
    log "----------------------------------------"
    
    python3 -c "
from models.database import db

# Mükerrer kayıtları sil
db.remove_duplicates()

# 30 günden eski ilanları sil
db.remove_old_listings(days=30)

print('Temizlik tamamlandı!')
"
    
    log "----------------------------------------"
    log "✅ TEMİZLİK GÖREVİ TAMAMLANDI"
}

run_all() {
    log "🚀 TÜM GÖREVLER BAŞLIYOR"
    log "========================================"
    
    run_scrape
    echo ""
    run_ai
    echo ""
    run_cleanup
    
    log "========================================"
    log "✅ TÜM GÖREVLER TAMAMLANDI"
}

# ========================================
# ANA MANTIK
# ========================================

TASK="${1:-all}"

case "$TASK" in
    scrape)
        run_scrape
        ;;
    ai)
        run_ai
        ;;
    cleanup)
        run_cleanup
        ;;
    all)
        run_all
        ;;
    *)
        echo "Kullanım: $0 [scrape|ai|cleanup|all]"
        echo ""
        echo "Görevler:"
        echo "  scrape  - Sahibinden'den veri çek"
        echo "  ai      - AI tahminlerini güncelle"
        echo "  cleanup - Veritabanını temizle"
        echo "  all     - Tüm görevleri sırayla çalıştır"
        exit 1
        ;;
esac
