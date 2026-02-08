#!/bin/bash
# ========================================
# Update Deployment Script
# ========================================

EC2_HOST="ubuntu@13.51.158.83"
SSH_KEY="sonanahtar.pem"
REMOTE_DIR="/home/ubuntu/EkerGallery"

echo "🚀 Starting Deployment..."

# 1. Update Remote Files
echo "📤 Uploading files..."
scp -i "$SSH_KEY" app_v2.py "$EC2_HOST:$REMOTE_DIR/"
scp -i "$SSH_KEY" models/database.py "$EC2_HOST:$REMOTE_DIR/models/"
scp -i "$SSH_KEY" templates/login.html "$EC2_HOST:$REMOTE_DIR/templates/"
scp -i "$SSH_KEY" templates/register.html "$EC2_HOST:$REMOTE_DIR/templates/"
scp -i "$SSH_KEY" templates/dashboard.html "$EC2_HOST:$REMOTE_DIR/templates/"

# 2. Restart Service
echo "🔄 Restarting Service..."
ssh -i "$SSH_KEY" "$EC2_HOST" << 'EOF'
    set -e
    cd /home/ubuntu/EkerGallery
    
    # Activate venv
    if [ -d "myenv" ]; then
        source myenv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Install dependencies (just to be sure)
    pip install werkzeug flask pymongo certifi -q
    
    # Restart Gunicorn
    echo "Killing old process..."
    pkill -f "gunicorn" || true
    pkill -f "python.*app_v2" || true
    sleep 2
    
    echo "Starting Gunicorn..."
    nohup gunicorn -w 4 -b 0.0.0.0:5000 app_v2:app \
        --access-logfile access.log \
        --error-logfile error.log \
        --daemon
        
    echo "✅ Service Restarted!"
EOF

echo "✅ Deployment Complete!"
