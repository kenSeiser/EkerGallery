#!/bin/bash
cd /home/ubuntu/EkerGallery
source myenv/bin/activate
pkill -f app_v2.py
nohup python3 app_v2.py > app.log 2>&1 &
echo "Server started with PID $!"
