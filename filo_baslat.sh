#!/bin/bash

echo "🤖 Robot Filosu (V3 - Final) Hazırlanıyor..."

# --- MEVCUTLAR ---
nohup python3 -u bedava_robot.py "https://www.sahibinden.com/opel-corsa?sorting=date_desc" "opel_corsa" > log_corsa.txt 2>&1 &
echo "✅ Opel Corsa Robotu Gönderildi!"
sleep 2

nohup python3 -u bedava_robot.py "https://www.sahibinden.com/volkswagen-polo?sorting=date_desc" "vw_polo" > log_polo.txt 2>&1 &
echo "✅ VW Polo Robotu Gönderildi!"
sleep 2

nohup python3 -u bedava_robot.py "https://www.sahibinden.com/fiat-doblo?sorting=date_desc" "fiat_doblo" > log_doblo.txt 2>&1 &
echo "✅ Fiat Doblo Robotu Gönderildi!"
sleep 2

# --- YENİ EKLENEN LÜKS ARAÇLAR ---
nohup python3 -u bedava_robot.py "https://www.sahibinden.com/tesla-model-y?sorting=date_desc" "tesla_model_y" > log_tesla.txt 2>&1 &
echo "⚡ Tesla Model Y Robotu Gönderildi!"
sleep 2

nohup python3 -u bedava_robot.py "https://www.sahibinden.com/mercedes-benz-amg-gt?sorting=date_desc" "mercedes_amg" > log_mercedes.txt 2>&1 &
echo "🏎️ Mercedes AMG GT Robotu Gönderildi!"
sleep 2

nohup python3 -u bedava_robot.py "https://www.sahibinden.com/volvo-s90?sorting=date_desc" "volvo_s90" > log_volvo.txt 2>&1 &
echo "🛡️ Volvo S90 Robotu Gönderildi!"

echo "🚀 TÜM FİLO SAHADA! Logları izlemek için: tail -f log_corsa.txt"
