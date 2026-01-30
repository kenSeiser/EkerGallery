from flask import Flask, render_template_string
from pymongo import MongoClient
import urllib.parse
import certifi

app = Flask(__name__)

# --- AYARLAR ---
username = "ekerard_db_user"
password = "Ekerard123"
cluster_url = "ekerard.vthareu.mongodb.net"

# Şifrede özel karakter varsa bozulmasın diye güvenli hale getiriyoruz
safe_password = urllib.parse.quote_plus(password)

# DÜZELTME: < ve > işaretleri kaldırıldı, f-string ile değişkenler yerleştirildi
mongo_uri = f"mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?appName=ekerard"

@app.route('/')
def home():
    try:
        # SSL sertifika hatası almamak için tlsCAFile eklendi
        client = MongoClient(mongo_uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        
        # Veritabanı adı (Scraper kodunda ne kullandıysan o olmalı, örn: sahibinden_verileri veya opel_corsa_e)
        # Eğer veritabanı adını hatırlamıyorsan burayı kontrol et
        db = client["sahibinden_data"] 

        # Koleksiyon adını otomatik bul
        col_list = db.list_collection_names()
        if not col_list:
            return "<h1>Veritabanı Boş veya Bağlantı Hatalı</h1>"

        # İlk bulduğu tabloyu alır (Örn: volkswagen_polo)
        collection = db[col_list[0]]

        # Verileri çek
        ilanlar = list(collection.find().limit(1000))

        # --- HTML TASARIMI ---
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Ekerard Araç Listesi</title>
            <style>
                body { background-color: #f6f6f6; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }
                .header { background: #ffe800; padding: 20px; text-align: center; border-bottom: 3px solid #333; color: #333; }
                .header h1 { margin: 0; font-size: 24px; text-transform: uppercase; letter-spacing: 1px; }
                .container { max-width: 1100px; margin: 30px auto; background: white; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden; }
                table { width: 100%; border-collapse: collapse; }
                thead { background-color: #f8f9fa; }
                th { padding: 15px; text-align: left; font-size: 13px; font-weight: bold; color: #555; border-bottom: 2px solid #eee; text-transform: uppercase; }
                td { padding: 15px; border-bottom: 1px solid #eee; font-size: 14px; color: #333; vertical-align: middle; }
                tr:hover { background-color: #fff9c4; transition: 0.2s; }
                
                .title-link { color: #003399; text-decoration: none; font-weight: 600; display: block; }
                .title-link:hover { text-decoration: underline; }
                
                .price { color: #d00000; font-weight: bold; font-size: 15px; }
                .badge { background: #333; color: #ffe800; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; vertical-align: middle; margin-left: 10px; }
                
                .tag { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
                .tag-clean { background: #e8f5e9; color: #2e7d32; }
                .tag-damage { background: #ffebee; color: #c62828; }
                .tag-unknown { background: #f5f5f5; color: #757575; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>EKERARD GALERİ <span class="badge">{{ ilanlar|length }} ARAÇ</span></h1>
            </div>
            
            <div class="container">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 45%;">İLAN BAŞLIĞI</th>
                            <th>FİYAT</th>
                            <th>YIL</th>
                            <th>KM</th>
                            <th>HASAR DURUMU</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ilan in ilanlar %}
                        <tr>
                            <td>
                                <a href="{{ ilan.url }}" target="_blank" class="title-link">
                                    {{ ilan.baslik }}
                                </a>
                            </td>
                            <td class="price">{{ "{:,}".format(ilan.fiyat).replace(',', '.') }} TL</td>
                            <td>{{ ilan.yil }}</td>
                            <td>{{ ilan.km }}</td>
                            <td>
                                {% if 'Hatasız' in ilan.hasar_durumu or 'Temiz' in ilan.hasar_durumu %}
                                    <span class="tag tag-clean">HATASIZ</span>
                                {% elif 'Hasarlı' in ilan.hasar_durumu %}
                                    <span class="tag tag-damage">KAYITLI</span>
                                {% else %}
                                    <span class="tag tag-unknown">{{ ilan.hasar_durumu }}</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html, ilanlar=ilanlar)

    except Exception as e:
        return f"""
        <div style='text-align:center; padding:50px; font-family:sans-serif;'>
            <h2 style='color:red'>Bir Hata Oluştu!</h2>
            <p><strong>Hata Detayı:</strong> {e}</p>
            <p>Lütfen MongoDB kullanıcı adı ve şifrenizi kontrol edin.</p>
        </div>
        """

if __name__ == '__main__':
    # AWS veya yerel bilgisayarda herkesin erişebilmesi için 0.0.0.0
    app.run(host="0.0.0.0", port=5000, debug=True)
