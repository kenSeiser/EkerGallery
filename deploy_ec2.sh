#!/bin/bash
# ========================================
# EkerGallery - AWS EC2 Deploy Script
# ========================================
#
# Bu script projeyi EC2 sunucusuna deploy eder.
# 
# Kullanım:
#   ./deploy_ec2.sh [ec2-host] [key-file]
#
# Örnek:
#   ./deploy_ec2.sh ubuntu@ec2-xx-xx-xx.compute.amazonaws.com ~/.ssh/mykey.pem
#

set -e

# Renkli çıktılar
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️${NC} $1"; }
error() { echo -e "${RED}[$(date '+%H:%M:%S')] ❌${NC} $1"; }

# Parametreler
EC2_HOST="${1:-ubuntu@your-ec2-host.compute.amazonaws.com}"
SSH_KEY="${2:-~/.ssh/id_rsa}"
PROJECT_NAME="EkerGallery"
REMOTE_DIR="/home/ubuntu/$PROJECT_NAME"

# Proje dizini
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "=========================================="
echo "🚀 EkerGallery EC2 Deploy"
echo "=========================================="
echo ""

# Gerekli dosyaları kontrol et
log "📁 Proje dosyaları kontrol ediliyor..."

REQUIRED_FILES=(
    "app_v2.py"
    "config.py"
    "requirements.txt"
    "models/database.py"
    "services/ai_model.py"
    "services/scraper_v2.py"
    "templates/dashboard.html"
    "templates/login.html"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$PROJECT_DIR/$file" ]; then
        error "Dosya bulunamadı: $file"
        exit 1
    fi
done
log "✅ Tüm dosyalar mevcut"

# SSH bağlantısını test et
log "🔑 SSH bağlantısı test ediliyor..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$EC2_HOST" "echo 'SSH OK'" 2>/dev/null; then
    error "SSH bağlantısı başarısız!"
    echo ""
    echo "Kullanım: $0 [ec2-host] [key-file]"
    echo "Örnek:   $0 ubuntu@ec2-1-2-3-4.compute.amazonaws.com ~/.ssh/mykey.pem"
    exit 1
fi
log "✅ SSH bağlantısı başarılı"

# Geçici dizin oluştur
log "📦 Deploy paketi hazırlanıyor..."
TEMP_DIR=$(mktemp -d)
DEPLOY_DIR="$TEMP_DIR/$PROJECT_NAME"
mkdir -p "$DEPLOY_DIR"

# Dosyaları kopyala
cp -r "$PROJECT_DIR"/app_v2.py "$DEPLOY_DIR/"
cp -r "$PROJECT_DIR"/config.py "$DEPLOY_DIR/"
cp -r "$PROJECT_DIR"/requirements.txt "$DEPLOY_DIR/"
cp -r "$PROJECT_DIR"/.env.example "$DEPLOY_DIR/"
cp -r "$PROJECT_DIR"/cron_runner.sh "$DEPLOY_DIR/"
cp -r "$PROJECT_DIR"/setup_cron.sh "$DEPLOY_DIR/"
cp -r "$PROJECT_DIR"/models "$DEPLOY_DIR/"
cp -r "$PROJECT_DIR"/services "$DEPLOY_DIR/"
cp -r "$PROJECT_DIR"/templates "$DEPLOY_DIR/"

# .env dosyası varsa kopyala
if [ -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env" "$DEPLOY_DIR/"
fi

# cookies.pkl varsa kopyala
if [ -f "$PROJECT_DIR/cookies.pkl" ]; then
    cp "$PROJECT_DIR/cookies.pkl" "$DEPLOY_DIR/"
fi

log "✅ Deploy paketi hazır"

# Sunucuya yükle
log "📤 Dosyalar sunucuya yükleniyor..."
rsync -avz --progress -e "ssh -i $SSH_KEY" \
    "$DEPLOY_DIR/" \
    "$EC2_HOST:$REMOTE_DIR/" \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'myenv' \
    --exclude '.git'

log "✅ Dosyalar yüklendi"

# Sunucuda kurulum yap
log "🔧 Sunucuda kurulum yapılıyor..."
ssh -i "$SSH_KEY" "$EC2_HOST" << 'REMOTE_SCRIPT'
    set -e
    
    cd ~/EkerGallery
    
    echo "📦 Python paketleri kuruluyor..."
    
    # Virtual environment
    if [ ! -d "myenv" ]; then
        python3 -m venv myenv
    fi
    
    source myenv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    
    echo "✅ Paketler kuruldu"
    
    # .env dosyası kontrolü
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo "⚠️ .env dosyası oluşturuldu, lütfen düzenleyin!"
        fi
    fi
    
    # Script izinleri
    chmod +x cron_runner.sh setup_cron.sh 2>/dev/null || true
    
    # Chrome ve ChromeDriver kontrolü
    if ! command -v google-chrome &> /dev/null; then
        echo "🌐 Chrome kuruluyor..."
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update -qq
        sudo apt-get install -y google-chrome-stable -qq
    fi
    
    echo "✅ Kurulum tamamlandı"
REMOTE_SCRIPT

log "✅ Sunucu kurulumu tamamlandı"

# Servisi başlat
log "🚀 Uygulama başlatılıyor..."
ssh -i "$SSH_KEY" "$EC2_HOST" << 'REMOTE_SCRIPT'
    cd ~/EkerGallery
    source myenv/bin/activate
    
    # Eski process'i durdur
    pkill -f "gunicorn.*app_v2" 2>/dev/null || true
    pkill -f "python.*app_v2" 2>/dev/null || true
    
    # Gunicorn ile başlat
    nohup gunicorn -w 4 -b 0.0.0.0:5000 app_v2:app \
        --access-logfile /var/log/ekergallery/access.log \
        --error-logfile /var/log/ekergallery/error.log \
        --daemon
    
    echo "✅ Gunicorn başlatıldı"
REMOTE_SCRIPT

# Temizlik
rm -rf "$TEMP_DIR"

# Sonuç
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Deploy Tamamlandı!${NC}"
echo "=========================================="
echo ""
echo "📍 Uygulama: http://$EC2_HOST:5000"
echo ""
echo "🔧 Sonraki Adımlar:"
echo "   1. .env dosyasını düzenleyin:"
echo "      ssh -i $SSH_KEY $EC2_HOST"
echo "      nano ~/EkerGallery/.env"
echo ""
echo "   2. Cron job'ları kurun:"
echo "      ssh -i $SSH_KEY $EC2_HOST 'cd ~/EkerGallery && ./setup_cron.sh'"
echo ""
echo "   3. Servisi yeniden başlatın:"
echo "      ssh -i $SSH_KEY $EC2_HOST 'cd ~/EkerGallery && source myenv/bin/activate && pkill -f gunicorn && gunicorn -w 4 -b 0.0.0.0:5000 app_v2:app --daemon'"
echo ""
