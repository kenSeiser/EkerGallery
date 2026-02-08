#!/bin/bash
set -x
echo "Stopping existing services..."
pkill -f gunicorn || true
pkill -f scraper_v2.py || true

echo "Cleaning Chrome driver cache..."
rm -rf ~/.local/share/undetected_chromedriver

cd /home/ubuntu/EkerGallery
source myenv/bin/activate

echo "Starting Web App..."
nohup gunicorn -w 4 -b 0.0.0.0:5000 app_v2:app > logs/webapp.log 2>&1 &

echo "Starting Scraper (Headful with Xvfb)..."
nohup xvfb-run -a --server-args="-screen 0 1920x1080x24" python3 services/scraper_v2.py > logs/scraper.log 2>&1 &

echo "Services started."
ps aux | grep -E "gunicorn|scraper_v2.py" | grep -v grep
