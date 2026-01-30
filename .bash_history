sudo apt update && sudo apt install python3-pip nginx -y
pip3 install flask pymongo gunicorn
sudo apt install python3-venv -y
python3 -m venv myenv
source myenv/bin/activate
pip install flask pymongo gunicorn
sudo bash -c 'cat > /etc/nginx/sites-available/sahibinden <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF'
# Ayarları aktifleştir ve Nginx'i yeniden başlat
sudo ln -s /etc/nginx/sites-available/sahibinden /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
python app.py
nano app.py
python app.py
sudo bash -c 'cat > /etc/nginx/sites-available/sahibinden <<EOF
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF'
sudo ln -s /etc/nginx/sites-available/sahibinden /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
nano app.py
python app.py
# Eski olası hatalı ayarları silelim
sudo rm /etc/nginx/sites-enabled/default
sudo rm /etc/nginx/sites-available/sahibinden
sudo rm /etc/nginx/sites-enabled/sahibinden
# Tertemiz ayar dosyasını tekrar oluşturalım
sudo bash -c 'cat > /etc/nginx/sites-available/sahibinden <<EOF
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF'
# Aktif edip Nginx'i tazeleyelim
sudo ln -s /etc/nginx/sites-available/sahibinden /etc/nginx/sites-enabled/
sudo systemctl restart nginx
python3 app.py
sudo ln -s /etc/nginx/sites-available/sahibinden /etc/nginx/sites-enabled/
sudo systemctl reload nginx
python3 app.py
sudo systemctl restart nginx
python3 app.py
[200~python3 app.py~
python3 app.py
nanp app.py
sudo nano app.py
python3 app.py
sudo systemctl status nginx
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo systemctl restart nginx
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
pip install gunicorn
nohup gunicorn --bind 0.0.0.0:5000 app:app &
python3 app.py
sudo nano app.py
python3 app.py
pkill -f gunicorn
pkill -f python3
nohup gunicorn --bind 0.0.0.0:5000 app:app &
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
python3 app.py
sudo nano app.py
sudo python3 app.py
sudo apt update
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install flask pymongo certifi
python3 app.py
nano app.py
sudo apt update
sudo apt install mongo-tools mongodb-server -y
sudo systemctl start mongodb
sudo nano app.py
python3 app.py
nano app.py
python3 app.py
nano app.py
python3 app.py
nano app.py
python3 app.py
nano app.py
python3 app.py
nano app.py
https://eu-north-1.console.aws.amazon.com/ec2-instance-connect/ssh/home?region=eu-north-1&connType=standard&instanceId=i-0faac2c079f4c79ea&osUser=ubuntu&sshPort=22&addressFamily=ipv4
mv app.py app_bozuk_yedek.py
nano app.py
python3 app.py
nano kontrol.py
python3 kontrol.poy
python3 kontrol.py
nano app.py
python3 app.py
nano app.py
python3 app.py
nano app.py
from pymongo import MongoClient
import certifi
# Bağlantı adresini direkt buraya yazıyorum (senin verdiğin bilgilerle)
# Eğer şifreni değiştirdiysen burayı düzelt!
uri = "mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?retryWrites=true&w=majority&appName=ekerard"
try:
except Exception as e:
nano test.py
python3 test.py
nano test.py
python3 test.py
nano app.py
python3 app.py
nano app.py
python3 app.py
rm app.py
nano app.py
python3 app.py
nano app.py
python3 app.py
pip install scikit-learn
nano app.py
python3 app.py
rm app.py
nano app.py
python3 app.py
~source venv/bin/activate
source venv/bin/activate
python3 app.py
nano app.py
python3 app.py
python3 appy.py
python3 app.py
source venv/bin/activate
python3 app.py
sudo nano /etc/systemd/system/ekerard.service
sudo systemctl daemon-reload
sudo systemctl start ekerard
sudo systemctl enable ekerard
sudo systemctl status ekerard
python3 app.py
nano app.py
rm app.py
nano app.py
sudo systemctl restart ekerard
python3 app.py
nano app.py
sudo systemctl restart ekerard
pip install tensorflow
from flask import Flask, render_template_string, request, redirect, url_for, session
from pymongo import MongoClient
import certifi
from sklearn.linear_model import LinearRegression
import numpy as np
app = Flask(__name__)
# --- AYARLAR ---
app.secret_key = "cok_gizli_anahtar_ai_modu"
ADMIN_USER = "ekerard"
ADMIN_PASS = "admin123"
mongo_uri = "mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?retryWrites=true&w=majority&appName=ekerard"
# --- MODERN GİRİŞ SAYFASI (MOBİL UYUMLU) ---
login_html = """
<html lang="tr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Giriş - Ekerard AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
            height: 100vh; display: flex; align-items: center; justify-content: center; 
            font-family: 'Inter', sans-serif; margin: 0; padding: 20px;
        }
        .login-card { 
            background: white; padding: 40px 30px; border-radius: 24px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.08); width: 100%; max-width: 380px; text-align: center; 
        }
        .logo-icon { font-size: 40px; background: linear-gradient(45deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; }
        .title { font-weight: 800; font-size: 22px; color: #1e293b; margin-bottom: 30px; }
        input { 
            width: 100%; padding: 15px; margin-bottom: 15px; border: 2px solid #e2e8f0; 
            border-radius: 12px; font-size: 14px; background: #f8fafc; outline: none; box-sizing: border-box;
        }
        input:focus { border-color: #3b82f6; background: white; }
        .btn-login { 
            width: 100%; padding: 15px; background: linear-gradient(90deg, #3b82f6, #6366f1); 
            border: none; border-radius: 12px; color: white; font-weight: 700; font-size: 15px; 
            cursor: pointer; transition: 0.3s;
        }
        .alert { color: #ef4444; font-size: 13px; margin-bottom: 15px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="login-card">
        <i class="fa-solid fa-robot logo-icon"></i>
        <div class="title">Ekerard AI Analiz</div>
        {% if error %}<div class="alert">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Kullanıcı Adı" required>
            <input type="password" name="password" placeholder="Şifre" required>
            <button type="submit" class="btn-login">Panele Gir <i class="fa-solid fa-arrow-right ms-2"></i></button>
        </form>
    </div>
</body>
</html>
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
@app.route('/logout')
def logout():
@app.route('/')
def home():
if __name__ == '__main__':;     app.run(host="0.0.0.0", port=5000, debug=True)
nano app.py
sudo systemctl restart ekerard
nano app.py
sudo systemctl restart ekerard
python3 app.py
nano app.py
sudo systemctl restart ekerard
nano app.py
sudo systemcl restart ekerard
sudo systemctl restart ekerard
nano birlestir.py
python3 birlestir.py
nzno app.py
sudo nano app.py
sudo systemctl restart ekerard
rm app.py
nano app.py
sudo systemctl restart ekerard
sudo nano app.py
sudo systemctl restart ekerard
sudo nano app.py
sudo systemctl restart ekerard
sudo nano app.py
sudo systemctl restart ekerard
sudo nano app.py
sudo systemctl restart ekerard
sudo nano app.py
sudo systemctl restart ekerard
ls
nano scraper.py
wget "https://limewire.com/d/TzS98#v3ceK20EBO" -O cookies.pkl
cat cookies.pkl
nano sudo scraper.py
/usr/bin/xvfb-run -a python3 scraper.py
nano scraper.py
sudo apt-get update
sudo apt-get install -y xvfb
ls
xvfb-run -a python3 scraper.py
pip3 install undetected-chromedriver selenium pymongo
pip3 install undetected-chromedriver
pip3 install undetected-chromedriver selenium pymongo --break-system-packages
/usr/bin/xvfb-run -a python3 scraper.py
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
llllll
sudo apt install -y ./google-chrome-stable_current_amd64.deb
s
sudo apt install -y ./google-chrome-stable_current_amd64.deb
/usr/bin/xvfb-run -a python3 scraper.py
nano scraper.py
/usr/bin/xvfb-run -a python3 scraper.py
rm scraper.py
nano scraper.py
/usr/bin/xvfb-run -a python3 scraper.py
rm cookies.pkl
nano cookies.pkl
[200~gASV7BEAAAAAAABdlCh9lCiMBmRvbWFpbpSMDy5zYWhpYmluZGVuLmNvbZSMBmV4cGlyeZRKHO18a4wIaHR0cE9ubHmUiYwEbmFtZZSMBl9fZ2Fkc5SMBHBhdGiUjAEvlIwIc2FtZVNpdGWUjAROb25llIwGc2VjdXJllIiMBXZhbHVllIxTSUQ9YjllOWE3NTE5NDkxOGQzZDpUPTE3Njk2NTMyNzY6UlQ9MTc2OTY1MzI3NjpTPUFMTklfTWF3Vnc4TU1fNEUtdkpUYlRkSTh6TUZBYS1RMFGUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKV/dba2gFiWgGjA5PcHRhbm9uQ29uc2VudJRoCGgJaAqMA0xheJRoDIloDViqAgAAaXNHcGNFbmFibGVkPTAmZGF0ZXN0YW1wPVRodStKYW4rMjkrMjAyNiswNSUzQTIwJTNBMDcrR01UJTJCMDMwMCsoR01UJTJCMDMlM0EwMCkmdmVyc2lvbj0yMDI1MDMuMi4wJmJyb3dzZXJHcGNGbGFnPTAmaXNJQUJHbG9iYWw9ZmFsc2UmY29uc2VudElkPWZjOTk3ZGE4LTFiZTMtNGJkZi05NTk4LWM0MjRhNWVjNWQ3OCZpbnRlcmFjdGlvbkNvdW50PTAmaXNBbm9uVXNlcj0xJmxhbmRpbmdQYXRoPWh0dHBzJTNBJTJGJTJGd3d3LnNhaGliaW5kZW4uY29tJTJGJmdyb3Vwcz1DMDAwNCUzQTAlMkNDMDAwMSUzQTElMkNDMDAwMyUzQTAlMkNDMDAwMiUzQTAmaG9zdHM9SDE4MyUzQTAlMkNIMTg2JTNBMCUyQ0gxMzElM0EwJTJDSDc2JTNBMCUyQ0gxMDYlM0EwJTJDSDglM0EwJTJDSDgwJTNBMCUyQ0g2NyUzQTAlMkNIMjclM0EwJTJDSDE0JTNBMCUyQ0gzMSUzQTAlMkNIMTE0JTNBMCUyQ0gxODQlM0EwJTJDSDExNSUzQTAlMkNIMTE3JTNBMCUyQ0g4NyUzQTElMkNIODglM0EwJTJDSDMlM0EwJTJDSDQlM0EwJTJDSDkxJTNBMCUyQ0gxOTQlM0EwJTJDSDUlM0EwJTJDSDE4NSUzQTAlMkNIOTMlM0EwJTJDSDE4MCUzQTAlMkNIMjAxJTNBMCUyQ0gxOTUlM0EwJTJDSDEyJTNBMCUyQ0gxNyUzQTAlMkNIMTIyJTNBMCUyQ0g5NiUzQTAlMkNIMTI0JTNBMCUyQ0g2NCUzQTElMkNIMTk4JTNBMCZnZW5WZW5kb3JzPZR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBErm0XppaAWJaAaMCGdlb2lwSXNwlGgIaAloCowDTGF4lGgMiWgNjAd0dXJrc2F0lHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESubRemloBYloBowJZ2VvaXBDaXR5lGgIaAloCowDTGF4lGgMiWgNjAdhbnRhbHlhlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgEShztfGtoBYloBowFX19ncGmUaAhoCWgKjAROb25llGgMiGgNjFRVSUQ9MDAwMDEwNDJkZDI1ZDA2MzpUPTE3Njk2NTMyNzY6UlQ9MTc2OTY1MzI3NjpTPUFMTklfTVlyOUtnSHpVN3k2QkN1SnExSXA0RDJ4YkdJY0GUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKWsd6aWgFiWgGjAJkcJRoCGgJaAqMA0xheJRoDIloDYwTMTkyMCoxMDgwLWxhbmRzY2FwZZR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEqFIVxraAWJaAaMA01TMZRoCGgJaAqMA0xheJRoDIloDYweaHR0cHM6Ly9zZWN1cmUuc2FoaWJpbmRlbi5jb20vlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgEShwSaGpoBYloBowFX19lb2mUaAhoCWgKjAROb25llGgMiGgNjE1JRD1jOGQ1YjgwNDhjZWU1NDExOlQ9MTc2OTY1MzI3NjpSVD0xNzY5NjUzMjc2OlM9QUEtQWZqWVRtUkxmYnVUVWlNR0hlVmE4S1FqSZR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBErUG4praAWIaAaMA2N3dJRoCGgJaAqMBE5vbmWUaAyIaA2MYkZjYk4xNGhaaXR6M0xydEthX3B6UmlTc2w4bFFsTjV5c29WRHpqbDNyeW04SG9jZnZLbllSdzdqNHU3cXRQRnVhZkJmOUhmcDluVnVKVllkQ0NTcERBVGRrX2d3WkFyMW5RlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgFiWgGjAVweGN0c5RoCGgJaAqMA0xheJRoDIloDYwkMjVhNjdiM2ItZmNiOS0xMWYwLThiMjUtMmE2NzExODlhMDQzlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESkT3W2toBYloBowGX3B4dmlklGgIaAloCowDTGF4lGgMiWgNjCQyM2NhMGY4OS1mY2I5LTExZjAtODgyZi1iODhiNDhkZDJlOTiUdX2UKGgCjBJ3d3cuc2FoaWJpbmRlbi5jb22UaARKz9F6aWgFiGgGjAZfX2NmbGKUaAhoCWgKjAROb25llGgMiGgNjCswSDI4dnVkQ2IxMko2TFZCOXFOdUJDVTNpRG5Cam1MZ1QyZk5QRHpYQ3lalHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESr8bimtoBYloBowEY2RpZJRoCGgJaAqMBE5vbmWUaAyIaA2MGG5FZ0JzbWV1NEN6Z1d5dmk2OTdhYzQwNZR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEpC91traAWIaAaMDGNmX2NsZWFyYW5jZZRoCGgJaAqMBE5vbmWUaAyIaA1YKgEAAFhMUm5UWW1WRWt6OEllMmI1T3NwMThFY1JlQjRhN2RVS2pibXFXcUFGTzQtMTc2OTY1MzI1Ni0xLjIuMS4xLXFWVllVbkdVWVc5REFrVVJrRFNDbDhDMlV6R2ZORlgzOTFOaUcxaWkuQTAyQkc5YldMWGhxRTVUS2F2ZUt3VzZHVVA5SmtEZnNTWm1BS0VHb1lyTi50cjJ0a3lZTXdIeVkyZHNfc3JHT0FMdDdYbVk4S1ZzOWNTWHE3YVBqLjF5NkJMMXNCS0diLnVoV2M3dEM0UjBnX2lvMW1vQ0V3Wk02MVdRQWhKclVxZUd1YzVVaGZUVlJKZG1ESVY1ajdHM0ZKSFl4enA1cW1EY3VYenhyZnVuWEdkWnBRTkpteWFxd3BZQkVqdTh2dVGUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKx8p6aWgFiGgGjAdfX2NmX2JtlGgIaAloCowETm9uZZRoDIhoDYy/LkY2eTU0ejZ0UDQzd1VXX0JfLkdsUDZaZWFTRFg0VU1lSUhnME9DMWVHOC0xNzY5NjUzMjUzLTEuMC4xLjEtQlZ6ZW1zeXFnOFBxdXhaMzJpcmRaaUswZk1zUXBFbXM4ZmltWDBGOHliVklaT0lFRExUbG5PWnlEN250WFVnZGhyUnRlOUVpMzJQYTNYZkQ2YTMyOC5xbW9NU1o3SnFOSWQ0NGtwMy5BbFNEQkRTNW9XQ0dPbC56aGhHV0xqWjGUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKG8V6aWgFiWgGjARfcHgzlGgIaAloCowDTGF4lGgMiWgNWLcCAAA5ODUwOGZhODI4NTVkZDMxM2ZlNTFmMTViOTUyNzJiZDQwMmFkNDVmM2JjODBkMjg1NThhMTc1YzIzMGJhYmJkOlJ0cFNNNzNDcWp3Z0ZWQlV3dmc0RkJpcVZXVy80aEhFV1NMWXhQSC9YYXo0d3lYSll6NWIrK29ISEE4Q0ZmLzl3Q2hQTVdRanEraGsyMWpZbGNZTmxBPT06MTAwMDo0T3B0M2RlRFFhenUyOENxL1JqVDVZUDlnWFdlLzRiOCtQTFpmUXBQOTgrSUNYQUJhenpvSmFydnVOWXFRd3hVbks3RWVwN3dWdXJXWklvS0lLYngzN1lLRWM4UUpaVXJtSDB3T1RiTzd4VVhJaUxnalR5c1RtdGRTS2kzcHF1M3V5bkZjZ3haaTB5UGp0Mkp4djIxOUdaZi9SREZ4czJMMTdmUTV4VHczNW9zTGNlTS9MQTRsMUJDNHpWbGRwNUw1Mkx3UEZBVnA4RlZkY20rdFBOWWtXOVlWOFRudS9icDZmc0tBOFBJWS91Q0dzU2NFU1FCOE4rZU1WYnFucFV5Z0FZck1wR3UraXRVOVNhVFo0TEJvT3E0Q2Ewem9vMVJnQnVhUEM4MFVaaUw5NlB0dW5uR3RLZ3owS2I0OGF5YzlHU0Y5dVpDUUFYL09QaERPVWNzT09zRGRSWGhzajE3eUFHV01ycCtDeUQwWVZNQ3hQeUZUbjVFMWlnWHRiOFZXRHVHTlg2S3hlMGl1SWN6TStsUXVqV3puOWw4MnNCdXl6TGE2SDJPd01ZZldmc0R2bFZ1dXdvcWg4dHArTFppK0J0TWhGNzJGZFVGeUo1djFQNENyMU54VkFXK1ZaZmFpa1Y1TXphZElsa0tsMWRMdFo1RCtrUmVhQlZLcXp2OVdaTEF2V2ZrSnF4ZjVMdXdFN3k0eFE9PZR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEq/G4praAWJaAaMA3ZpZJRoCGgJaAqMBE5vbmWUaAyIaA2MAzczMpR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEpDx3ppaAWIaAaMBGNzaWSUaAhoCWgKjAROb25llGgMiGgNWIABAABhRGd1cDJUTkZuMXhDWGZmV2xDUEFVVDZVd1B2UkhMREJyc1dpSkhjWHpJQWphRVN0TjBkSXNLbTAtMTBnVEUyT2NaV245VlF0YldwVDBfb0wzaFlJdk13bnA2OFRjd0xsUzdHYWhidTVEYmNHUk50dW11bkxyeHFkTkJJcnpnbzhlNFNGdUNLVDNwdTFWczJIUGZYTlFnTk5lQzV5OG1yRzRlQWZlcWRsZ25ULUQ3dG56c2lzM2MwMW93eWVKTHQydXZ0LVV1ZEZRZERZdnRCZkh5QWZsV0VWZkpJQW90VkFuWVctcTVUdVlUbWthSHJKNXlHOUhTYnUwY2ZBNU5tV1lDSmU3X3p2UzhCZWRib25WY3NERklqYm5ZblJ2ckVMVmtRSkIzbFhyTDB1bTFNU3BjdDk5al8yMU1nN1JIc0ZpRDQ3c2xDSFc2QnFIaVFrRG9hWGRWb1VNMWlUNzNzYkUxRDd3T0ljd1ZYWkxNc0VBZFlLeG0xTXNVTWJIVEeUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKP/dba2gFiGgGjARjc2xzlGgIaAloCowETm9uZZRoDIhoDYxWbGJKMkg4YlQ5RUE3TllPZWNmUGo5LXNSMFJQQmM5eGVFTXJpTDlKcW55OGFDeFRzR1NaNFFHYUtVZmRqOUlJUFQwWE1iRko2QXJYeURqUG1lTC00bXeUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARK3Mp6aWgFiGgGjARjc3NzlGgIaAloCowETm9uZZRoDIhoDYxWS1E4U0ZnMWd2U1FrWFZadFUxeWF1QWJmay1oVXdmVVJidUVDVGFacHQwZjBCWk5Cd29uVkJOLUVXMVZianpXWTRyWXlhZGUzcndDcndCN3VDSFc3emeUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARK1xuKa2gFiWgGjAxiYW5uZXJDbG9zZWSUaAhoCWgKjANMYXiUaAyJaA2MBWZhbHNllHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgFiGgGjAJzdJRoCGgJaAqMA0xheJRoDIhoDYxxYTRlYzk3NjM3OGNjOTQxOTI4MmZjMDE5ODc2OTQ0ZTNlMmEwMDE4MTZlZjEzZjIzOWMzY2I2MzQ2YTZjYTMwYjJjOGM3OGIwYmNjMDU3M2Q3M2VmMWU1YTk0N2U5OTBjNDA5ZTdiYTliOTA3YTBlNmKUdWUu~
wget "https://limewire.com/d/QxVvK#X6FS1xN5Gv" -O cookies.pkl
head -n 1 cookies.pkl
wget "https://filebin.net/s6hrkb4rg4mxkix1/cookies.pkl" -O cookies.pkl
head -n 1 cookies.pkl
s

head -n 1 cookies.pkl,
head -n 1 cookies.pkl
ls -l cookies.pkl
/usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 scraper.py
wget "https://filebin.net/apyysktk6bl0upit/cookies.pkl" -O cookies.pkl
ls -l cookies.pkl
/usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 scraper.py
sudo systemctl restart ekerard
echo "gASVWRcAAAAAAABdlCh9lCiMBmRvbWFpbpSMDy5zYWhpYmluZGVuLmNvbZSMBmV4cGlyeZRKbNB6aYwIaHR0cE9ubHmUiYwEbmFtZZSMBF9weDOUjARwYXRolIwBL5SMCHNhbWVTaXRllIwDTGF4lIwGc2VjdXJllImMBXZhbHVllFiLAgAANTNiNzM4MmY3Y2UwMjYxZTZmMGNlZmM3OWIxNjhhN2EwMjM0Mjk3YzI0M2M3MGI5MmNiYzkwNzc0YjdlMjVmYjpGZFFaNGg2WWp0VEc3L3FvcWY5N1YzejFLT0toN0YrVmJtR21zYzJFOFIzTmdoek1EUmJEMTdBRWl1eXl2NHN6REZDRUVrTEtEQ2ZCR0ZvdUtyeFBzUT09OjEwMDA6N2psaVQ5bjU1MHNHbDFIY2trdkhaai9ZSEViWDNkNUMyZVFBVFpVNjdiTVRQakJYUUd2WUdBM1E3a2Y2OTE0K1pKRXhkU2dtZzU5a0ZVVER1T3g2cENaMi9LenF1MTZ6Sm5sQVltMXRLdFl1VlZ4ZGFzR3BBb2FpeTRjZ0l5YTN5TnNJVWtESTVuaEFrWkNJVlA0ekRFVzBTM0tUVzVsci81OXZGc3l2Zm03dHh2YTB3Z0JHN1Q4SmV5VkFDRmtFd0NLMUVLZGRIYzA2NXN1ZWVFVXZUOXpVamlIbGdwSTI2TVhBTlpnZTgwSVpSelVobjI1VkRLK2xlcS9zRXcrN1hmSXNkOWJ0Q2orb1BuLy9Gc0NEQjBaM01QQk9zbUZGZ2UxQ1RrOGY5M3N5cUpnSDIvN2ZyZmpsbkQzZ1o0QjBXbmU0Uk40QUN1Rm1BWkpBVzcvazRCZm5FL2hmMFdKRnBUdTY3aVNkaWs0Y3VHSjZkNVZ3N1dkY2NpWnRmcUJzZERaYzJXUUN6dUJDMktzclRPeFZWUmw5WDJGeFBTaVovbHQ5d1k2N3dKcEEzMzhQUnB0a1lseTlIZk5kNUtlbzQ2QlorenptRG1QVzhLNWk2cFZJTXJhdHhQdStDZUcydWtUZkdUQnVKMm89lHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESqACXGtoBYloBowOT3B0YW5vbkNvbnNlbnSUaAhoCWgKjANMYXiUaAyJaA1YrQIAAGlzR3BjRW5hYmxlZD0wJmRhdGVzdGFtcD1UaHUrSmFuKzI5KzIwMjYrMDYlM0EwOCUzQTE2K0dNVCUyQjAzMDArKEdNVCUyQjAzJTNBMDApJnZlcnNpb249MjAyNTAzLjIuMCZicm93c2VyR3BjRmxhZz0wJmlzSUFCR2xvYmFsPWZhbHNlJmNvbnNlbnRJZD1kOTIwOTQ2YS04MGEyLTQ2MWYtODk5Ny1kZjE4OGEwYWQ3NWUmaW50ZXJhY3Rpb25Db3VudD0xJmlzQW5vblVzZXI9MSZsYW5kaW5nUGF0aD1Ob3RMYW5kaW5nUGFnZSZncm91cHM9QzAwMDQlM0EwJTJDQzAwMDElM0ExJTJDQzAwMDMlM0EwJTJDQzAwMDIlM0EwJmhvc3RzPUgxODMlM0EwJTJDSDE4NiUzQTAlMkNIMTMxJTNBMCUyQ0g3NiUzQTAlMkNIMTA2JTNBMCUyQ0g4JTNBMCUyQ0g4MCUzQTAlMkNINjclM0EwJTJDSDI3JTNBMCUyQ0gxNCUzQTAlMkNIMzElM0EwJTJDSDExNCUzQTAlMkNIMTg0JTNBMCUyQ0gxMTUlM0EwJTJDSDExNyUzQTAlMkNIODclM0ExJTJDSDg4JTNBMCUyQ0gzJTNBMCUyQ0g0JTNBMCUyQ0g5MSUzQTAlMkNIMTk0JTNBMCUyQ0g1JTNBMCUyQ0gxODUlM0EwJTJDSDkzJTNBMCUyQ0gxODAlM0EwJTJDSDIwMSUzQTAlMkNIMTk1JTNBMCUyQ0gxMiUzQTAlMkNIMTclM0EwJTJDSDEyMiUzQTAlMkNIOTYlM0EwJTJDSDEyNCUzQTAlMkNINjQlM0ExJTJDSDE5OCUzQTAmZ2VuVmVuZG9ycz0mQXdhaXRpbmdSZWNvbnNlbnQ9ZmFsc2WUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKHyeKa2gFiWgGjA5fZ2FfQzFYNDRUNVRaOZRoCGgJaAqMA0xheJRoDIloDYwtR1MyLjEuczE3Njk2NTYwMTkkbzEkZzEkdDE3Njk2NTYwOTUkajQ0JGwwJGgwlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESh8nimtoBYloBowOX2dhX0NWUFMzR1hFMVqUaAhoCWgKjANMYXiUaAyJaA2MLUdTMi4xLnMxNzY5NjU2MDE5JG8xJGcxJHQxNzY5NjU2MDk1JGo0NCRsMCRoMJR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEof+HxraAWJaAaMG3R0Y3NpZF9DTUpTVDRCQzc3VTFVRDRBNkk5MJRoCGgJaAqMA0xheJRoDIloDYw1MTc2OTY1NjAyMDA3NDo6WmZNeS1HNmRaVk5ZM0lQbGR2VWEuMS4xNzY5NjU2MDk1MTM3LjGUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKN896aWgFiWgGjAVfZ2FsaZRoCGgJaAqMA0xheJRoDIloDYwSc2VhcmNoUmVzdWx0c1RhYmxllHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESqACXGtoBYloBowEbndzaJRoCGgJaAqMA0xheJRoDIloDYwDc3RklHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESh74fGtoBYloBowRX3R0X2VuYWJsZV9jb29raWWUaAhoCWgKjANMYXiUaAyJaA2MATGUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKddF6aWgFiWgGjARjc2RhlGgIaAloCowDTGF4lGgMiWgNjBQxOTM0OTk2NjU2MC41ODkwNDM3NZR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEpMz3ppaAWJaAaME19kY19ndG1fVUEtMjM1MDcwLTGUaAhoCWgKjANMYXiUaAyJaA1oMXV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESiB28WloBYloBowEX2ZicJRoCGgJaAqMA0xheJRoDIloDYwlZmIuMS4xNzY5NjU2MDE2NjQ3LjM1NjEzODU1MzQ2NzY3MDg4M5R1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBErQJopraAWJaAaMDGJhbm5lckNsb3NlZJRoCGgJaAqMA0xheJRoDIloDYwFZmFsc2WUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKzSaKa2gFiGgGjANjd3SUaAhoCWgKjAROb25llGgMiGgNjGI5dEl1WEd4MEpmZjBXRjZmRjMtRWFpMGJGY1laLUZqeTlpT3IwRk4wQTc2U3QwVXJjem1IaFVoNDZTNTZJQ0JCM0w4MGdOZHpCYkwxUXU5b3phUGk0dmhHM2hYTWg5X1ktQZR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEoW+HxraAWJaAaMBl9fZ2Fkc5RoCGgJaAqMBE5vbmWUaAyIaA2MU0lEPThiZGUzYzg5MzJjMzUyZTU6VD0xNzY5NjU2MDg2OlJUPTE3Njk2NTYwODY6Uz1BTE5JX01aNkhBVFh5TlJwM21XZFBIaDVIUUQ2MVFUM0ZBlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgEStB18WloBYloBowHX2djbF9hdZRoCGgJaAqMA0xheJRoDIloDYwZMS4xLjE4NTY5MjgzNDYuMTc2OTY1NjAxNpR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBErf3HppaAWJaAaMCGdlb2lwSXNwlGgIaAloCowDTGF4lGgMiWgNjAd0dXJrc2F0lHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESt/cemloBYloBowJZ2VvaXBDaXR5lGgIaAloCowDTGF4lGgMiWgNjAdhbnRhbHlhlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESr4mimtoBYloBowEY2RpZJRoCGgJaAqMBE5vbmWUaAyIaA2MGFpWUG9ERUdWcjRRRWVRaWU2OTdhY2YwNJR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEoW+HxraAWJaAaMBV9fZ3BplGgIaAloCowETm9uZZRoDIhoDYxUVUlEPTAwMDAxMzMzNmNhN2U4ZTE6VD0xNzY5NjU2MDg2OlJUPTE3Njk2NTYwODY6Uz1BTE5JX01haG1uT1RJbmpWU3JXaWhsajNtYTRKS3VkdGZ3lHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESlPSemloBYloBowCZHCUaAhoCWgKjANMYXiUaAyJaA2MEzE5MjAqMTA4MC1sYW5kc2NhcGWUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKfixca2gFiWgGjANNUzGUaAhoCWgKjANMYXiUaAyJaA2MHmh0dHBzOi8vc2VjdXJlLnNhaGliaW5kZW4uY29tL5R1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEoWHWhqaAWJaAaMBV9fZW9plGgIaAloCowETm9uZZRoDIhoDYxNSUQ9NGJiMTc1N2M1ZDZiNjhmNjpUPTE3Njk2NTYwODY6UlQ9MTc2OTY1NjA4NjpTPUFBLUFmalpHa2tOd2h5dXN2em5HY1BCak9laneUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaAWJaAaMBXB4Y3RzlGgIaAloCowDTGF4lGgMiWgNjCRiMjgxMjdmYi1mY2JmLTExZjAtYTNiNS0wMTQyZDI5ODg1MjKUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKQQJca2gFiWgGjAZfcHh2aWSUaAhoCWgKjANMYXiUaAyJaA2MJGIxODEwOGNlLWZjYmYtMTFmMC04NGZhLWE2ZDYxN2EzZmFhNpR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEof+HxraAWJaAaMBnR0Y3NpZJRoCGgJaAqMA0xheJRoDIloDYw1MTc2OTY1NjAyMDA3Njo6eTNTUnUzRzByRjdkSDdWV3dLVlkuMS4xNzY5NjU2MDk1MTM3LjCUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKoNJ6aWgFiWgGjApzZWFyY2hUeXBllGgIaAloCowDTGF4lGgMiGgNjBVDQVRFR09SWS9UUkVFL0NMQVNTSUOUdX2UKGgCjBJ3d3cuc2FoaWJpbmRlbi5jb22UaARKztx6aWgFiGgGjAZfX2NmbGKUaAhoCWgKjAROb25llGgMiGgNjCswSDI4dnVkQ2IxMko2TFZCOXFOdUJDVTNpRG5Cam1MZ1NzbzN3WmpDbTVtlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESj4CXGtoBYhoBowEY3Nsc5RoCGgJaAqMBE5vbmWUaAyIaA2MVkdheGU5RURLSTVsVTEtR3loNmxhWkFvdTM1RkZZYmhfNmVIdV9Lc0F3Rnh4QWdGWllCVi1rRUV2NndsbE9ZbmdYYUdPTVNaYmo0LXB3VVVXOVJ4amFBlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESkACXGtoBYhoBowMY2ZfY2xlYXJhbmNllGgIaAloCowETm9uZZRoDIhoDVgqAQAASG9WbENibjk5Z1MwYi4yQS5GM0luMG9reWNXSkFpODdUWEJDcG1PY1V6QS0xNzY5NjU2MDcwLTEuMi4xLjEtbV9oMkp1TWR1SWtMcWU3d1drUnN0OVJhZWVVVHVuRnpHcnlJM00zQkk0ZmI2bjMwNE1EeURQZWxUNnA2RHhYcDRJNVNqRFp2aVNCd21HcDFGQlMyZ21QZ0ouZDVCdmxlTHoxb253WDFjS2tOUzNKelEyaXNOY3d4aGpQUWg0azdFQzFWd19oSkcyVjF6WVQ3SmJJQmdUTm5pLlFUeU1pTGxaYVpQb1pXWG9nSDFvSWVlRWViN2lvaXZSUm8wSkNET05Sdm1uS1QuelZObmdJdUVpdmNjQmR4WkVsTkNhc2kzVGRGYmlYQkNfY5R1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEoe+HxraAWJaAaMBF90dHCUaAhoCWgKjANMYXiUaAyJaA2MIDAxS0czVkZWMzZGQVRQMjAwM1ZGQUhYRUhOXy50dC4xlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESsbVemloBYhoBowHX19jZl9ibZRoCGgJaAqMBE5vbmWUaAyIaA2MvzVyVFV4S00yajhoOE1MX2RSdzBEdHNqdkVNb1BMUmRBYi4wbmJ3TmthNm8tMTc2OTY1NjA2OC0xLjAuMS4xLWJzY1lCLkwuYzlTSVZBODBwQjdyVnlZZjBwaUd3TWk3UGpzeXhtd3R6dnhLM1hncndPajlWNWhDSlg4R1BtZl9QQm56M1pHNU9kOXVkZ1BGLmVMeWxta2JlSzlXRkdXOHlQYkJuY0hNSjdYNDJjUUxURElTYTBPTzZkUlZaM0RulHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESr4mimtoBYloBowDdmlklGgIaAloCowETm9uZZRoDIhoDYwCMziUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKniB8aWgFiWgGjARfZ2lklGgIaAloCowDTGF4lGgMiWgNjBpHQTEuMi43ODYwMTA1MzEuMTc2OTY1NjAxOZR1fZQoaAKMDy5zYWhpYmluZGVuLmNvbZRoBEpC0nppaAWIaAaMBGNzaWSUaAhoCWgKjAROb25llGgMiGgNWIABAAA1bEhTLUxnWEVvQklwQVJlQjAtWjkwWXVSX0p5T1Zodmh2MU1ITG5hZ1QwcHVZMV83d0M5MWdRMGp5b0JzSXA3S3hTZGEtczNFY1BmTmhLR19ybzhsZFM1ZC1zZTI1cFVkUk0xWHgzRlI2MnF3YVRGNm9sNXhOUEdCOWtvaFBfOEVmSjhjb2tGUjVIUWdKTkx0Y29hY2hoem9WRW9IU1JHclhqNS1jbEJ3OGlhMXZqcjFtN2kzRnh0LS1QV05Xb01nSEJlVVU1c0Nydmc2dTFvRTBCSmUxYXlDaUt6NnJ1eW5kU0gtLVNoQkpZdTgtRE1JR2hlWnpIcWYxUEd4d05FX0tsMllNNTA5SWMxc3ZlbmstdEtJVXB0N0RKWFFlWUdVSHF0TlBfYkpsemQzVzRETmhneHNWRmxsVngzc08wa2ZfQkRoYmYzUjllNDZtX19QNDlVMjJXWEdzN3hkVzA1TXBvSHE1dXZUWTU1ZzFwVmZpNURHZTlDVGdILTljUFeUdX2UKGgCjA8uc2FoaWJpbmRlbi5jb22UaARKHieKa2gFiWgGjANfZ2GUaAhoCWgKjANMYXiUaAyJaA2MGkdBMS4yLjczNzUyODMwMC4xNzY5NjU2MDE5lHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgESifWemloBYhoBowEY3Nzc5RoCGgJaAqMBE5vbmWUaAyIaA2MVmRkcV8xakZnZDJ1dTFHaEVvU0V5Y2FzdnRlcWNTNWxjUGJ0d1FPTlF0RFJkeTdkSGtVU2Q1Z1RFenJtVGlYV1c0QzhaLWtubnYzSnlCeDREelNFeWNRlHV9lChoAowPLnNhaGliaW5kZW4uY29tlGgFiGgGjAJzdJRoCGgJaAqMA0xheJRoDIhoDYxxYTdhNDg2ZmVlYmIzYjRmMzk5MjYzYzc4MWMwODlhMGQ4MjZlN2YxYzBmNGNiYWM0MTJiNmVlMzRkZjE4MDZmMTYwNjdkYjY2ZTk1ZmYyMWM3MDhhNWI1YmM0NjQ2ODFkMDQxZDU3MmY0MjRjZmI2YjWUdWUu" | base64 -d > cookies.pkl
nano app.py
nano ~/.ssh/authorized_keys
/usr/bin/google-chrome --no-sandbox --remote-debugging-port=9222 --user-data-dir="/home/ubuntu/chrome_profile" --headless=new
/usr/bin/google-chrome --no-sandbox --remote-debugging-port=9222 --user-data-dir="/home/ubuntu/chrome_profile" --headless=new4
/usr/bin/google-chrome --no-sandbox --remote-debugging-port=9222 --user-data-dir="/home/ubuntu/chrome_profile" --headless=new
sudo systemctl restart ekerard
nan
pip install requests
pip install requests undetected-chromedriver selenium pymongo --break-system-packages
/usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 bedava_robot.py
nano bedava_robot.py
/usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 bedava_robot.py
sudo rm -rf /tmp/*
sudo apt-get clean
df -h
sudo apt-get clean
sudo apt-get autoremove -y
sudo journalctl --vacuum-time=1s
rm -rf ~/.cache/*
sudo rm -rf /var/lib/snapd/cache/*
sudo rm -rf /tmp/*
df -h
/usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 bedava_robot.py
nano bedava_robot.py
/usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 bedava_robot.py
nohup /usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 bedava_robot.py > robot_cikti.log 2>&1 &
tail -f robot_cikti.log
pkill -f bedava_robot.py
nohup /usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 -u bedava_robot.py > robot_cikti.log 2>&1 &
ps aux | grep bedava_robot.py
tail -f robot_cikti.log
nohup /usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 -u bedava_robot.py > robot_cikti.log 2>&1 &
ls
python3 birlestir.py
nano birlestir.py
python3 birlestir.py
ls
python3 birlestir.py
nohup /usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 -u bedava_robot.py > robot_cikti.log 2>&1 &
python3 birlestir.py
nohup /usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 -u bedava_robot.py > robot_cikti.log 2>&1 &
python3 birlestir.py
python birlestir.py
python3 birlestir.py
nano sudo app.py
python3 birlestir.py
nano sudo app.py
sudo app.py
nano sudo app.py
cat app.py
nano sudo app.py
sudo systemctl restart ekerard
pkill -f app.py
nohup python3 app.py > site.log 2>&1 &
tail -f site.log
pip3 install flask scikit-learn pymongo certifi numpy
sudo apt-get update
sudo apt-get install -y python3-flask python3-pymongo python3-certifi python3-numpy python3-sklearn
nohup python3 app.py > site.log 2>&1 &
tail -f site.log
sudo fuser -k 5000/tcp
nohup python3 app.py > site.log 2>&1 &
tail -f site.log
pkill -9 -f app.py
fuser 5000/tcp
sudo kill -9 352718 352721
nohup python3 app.py > site.log 2>&1 &
tail -f site.log
sudo fuser -k 5000/tcp
> site.log
nohup python3 app.py > site.log 2>&1 &
tail -f site.log
sudo reboot
nohup python3 app.py > site.log 2>&1 &
tail -f site.log
sudo pkill -9 python3
sudo fuser -k 5000/tcp
site.log
> site.log
nohup python3 app.py > site.log 2>&1 &
tail -f site.log
sed -i 's/port=5000/port=5001/g' app.py
nohup python3 app.py > site.log 2>&1 &
tail -f site.log
grep "Temizle" app.py
rm app.py
nano app.py
pkill -f app.py; nohup python3 app.py > site.log 2>&1 &
rm app.py
nano app.py
pkill -f app.py; nohup python3 app.py > site.log 2>&1 &
rm app.py
nano app.py
pkill -f app.py; nohup python3 app.py > site.log 2>&1 &
pkill -f bedava_robot.py
nano bedava_robot.py
nano app.py
pkill -f app.py; nohup python3 app.py > site.log 2>&1 &
nohup /usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 -u bedava_robot.py > robot_cikti.log 2>&1 &
python3 birlestir.py
rm app.py
nano app.py
pkill -f app.py; nohup python3 app.py > site.log 2>&1 &
nohup bash -c "while true; do /usr/bin/xvfb-run -a python3 birlestir.py; sleep 30; done" > loop.log 2>&1 &
tail -f loop.log
cat birlestir.py
nohup /usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 -u bedava_robot.py > robot_cikti.log 2>&1 &
nano birlestir.py
nohup bash -c "while true; do /usr/bin/xvfb-run -a python3 birlestir.py; sleep 5; done" > loop.log 2>&1 &
tail -f loop.log
nano birlestir.py
nohup /usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 -u birlestir.py > robot_log.txt 2>&1 &
tail -f loop.log
cat bedava_robot.py
nano bedava_robot.py
pkill -f bedava_robot.py
nano filo_baslat.sh
bash filo_baslat.sh
tail -f log_corsa.txt
nano filo_baslat.py
nano filo_baslat.sh
bash filo_baslat.sh
rm app.py
nano app.py
pkill -f app.py; nohup python3 app.py > site.log 2>&1 &
ls -l *.txt
tail -f log_tesla.txt
nano app.py
pkill -f app.py; nohup python3 app.py > site.log 2>&1 &
sudo apt update
sudo apt install git -y
git config --global user.name "kenSeiser"
git config --global user.email "ekerard@gmail.com"
cat ~/.ssh/id_ed25519.pub
ssh-keygen -t ed25519 -C "github_anahtar"
cat ~/.ssh/id_ed25519.pub
ssh-keygen -t ed25519 -C "github_anahtar"
cat ~/.ssh/id_ed25519.pub
nano .gitignore
git init
git branch -M main
git init
git branch -M main
git add .
git commit -m "EkerGallery ilk yükleme - Full Sistem"
git add
git commit -m "EkerGallery ilk yükleme - Full Sistem"
rm google-chrome-stable_current_amd64.deb
rm *.log
rm nohup.out
rm -rf .cache
rm -rf chrome_profile
git reset
echo "venv/" > .gitignore
echo "*.log" >> .gitignore
echo "*.txt" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "chrome_profile/" >> .gitignore
echo "*.deb" >> .gitignore
echo "nohup.out" >> .gitignore
git add .
git commit -m "EkerGallery Temiz Yedek"
git push -u origin main
git push -u origin main git@github.com:kenSeiser/EkerGallery.git
git push -u origin main
git remote add origin git@github.com:kenSeiser/EkerGallery.git
git push -u origin main
nohup /usr/bin/xvfb-run --server-args="-screen 0 1920x1080x24" -a python3 -u bedava_robot.py > robot_cikti.log 2>&1 &
taif
tail
tail -f 
ssh s
ssh -s
tail -f log_tesla.txt
ls -l *.txt
tail -f log_corsa.txt
