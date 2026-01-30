from flask import Flask, render_template_string, request, redirect, url_for, session
from pymongo import MongoClient
import certifi
import numpy as np
from sklearn.neural_network import MLPRegressor
import json

app = Flask(__name__)

# --- AYARLAR ---
app.secret_key = "ekergallery_key_ultra"
ADMIN_USER = "ekerard"
ADMIN_PASS = "admin123"
MONGO_URI = "mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?retryWrites=true&w=majority&appName=ekerard"

# --- LOGIN EKRANI (Yeni Tasarım) ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;600;800&display=swap" rel="stylesheet">
</head>
<body style="background:#050505; display:flex; justify-content:center; align-items:center; height:100vh; font-family:'Montserrat', sans-serif; overflow:hidden;">
    
    <div style="position:absolute; width:100%; height:100%; background-image: radial-gradient(#222 1px, transparent 1px); background-size: 30px 30px; opacity:0.2;"></div>

    <div style="background:rgba(20,20,20,0.9); backdrop-filter:blur(10px); padding:50px; border:1px solid #333; width:340px; text-align:center; position:relative; border-radius:15px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
        <h2 style="color:#fff; margin-bottom:10px; letter-spacing:3px; font-weight:300;">EKER<span style="font-weight:800">GALLERY</span></h2>
        <p style="color:#666; font-size:11px; margin-bottom:40px; letter-spacing:1px; text-transform:uppercase;">Premium Araç Veri Merkezi</p>
        
        <form method="POST">
            <input type="text" name="username" placeholder="Kullanıcı Kimliği" style="width:100%; padding:15px; margin-bottom:15px; background:#111; border:1px solid #333; color:white; border-radius:8px; outline:none; transition:0.3s;" required>
            <input type="password" name="password" placeholder="Erişim Şifresi" style="width:100%; padding:15px; margin-bottom:30px; background:#111; border:1px solid #333; color:white; border-radius:8px; outline:none;" required>
            <button type="submit" style="width:100%; padding:15px; background:#fff; color:#000; border:none; border-radius:8px; font-weight:800; letter-spacing:1px; cursor:pointer; transition:0.3s;">SİSTEME GİR</button>
        </form>
    </div>
</body>
</html>
"""

# --- DASHBOARD (EKERGALLERY TASARIMI) ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>EkerGallery - Analytics</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <style>
        :root { 
            --bg-body: #050505; 
            --bg-sidebar: rgba(10, 10, 10, 0.95); 
            --glass-card: rgba(20, 20, 20, 0.7);
            --border-color: rgba(255, 255, 255, 0.1);
            --text-main: #e0e0e0; 
            --text-muted: #6c757d; 
            --accent: #ffffff; 
        }
        
        body { 
            background-color: var(--bg-body); 
            color: var(--text-main); 
            font-family: 'Montserrat', sans-serif; 
            font-size: 13px; 
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 40px 40px; /* Kare desen */
        }
        
        /* SIDEBAR */
        .sidebar { 
            min-height: 100vh; 
            background: var(--bg-sidebar); 
            border-right: 1px solid var(--border-color); 
            padding: 30px 20px; 
            position: fixed; 
            width: 260px; 
            z-index: 1000; 
            backdrop-filter: blur(10px);
        }
        
        .brand { 
            font-size: 22px; 
            color: white; 
            letter-spacing: 2px; 
            margin-bottom: 40px; 
            text-align: center; 
            font-weight: 300;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
        }
        .brand span { font-weight: 800; }
        
        .nav-link { 
            color: var(--text-muted); 
            padding: 12px 15px; 
            margin-bottom: 5px;
            border-radius: 8px;
            transition: 0.3s; 
            cursor: pointer; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
            font-size: 11px; 
            font-weight: 600;
            display: flex;
            align-items: center;
        }
        .nav-link i { width: 25px; text-align: center; margin-right: 10px; }
        .nav-link:hover, .nav-link.active { 
            background: rgba(255,255,255,0.1); 
            color: var(--accent); 
            transform: translateX(5px);
        }
        
        .main-content { margin-left: 260px; padding: 40px; }
        
        /* CARDS (GLASS EFFECT) */
        .stat-card { 
            background: var(--glass-card); 
            backdrop-filter: blur(15px);
            border: 1px solid var(--border-color); 
            padding: 25px; 
            border-radius: 12px;
            text-align: center; 
            transition: 0.3s;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        }
        .stat-card:hover { transform: translateY(-5px); border-color: rgba(255,255,255,0.3); }
        .stat-val { font-size: 28px; font-weight: 600; color: white; margin-bottom: 5px; }
        .stat-label { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: #888; }
        
        /* TABLE */
        .table-container { 
            background: var(--glass-card); 
            backdrop-filter: blur(15px);
            padding: 25px; 
            border: 1px solid var(--border-color); 
            border-radius: 12px;
            margin-top: 30px; 
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        }
        table.dataTable tbody tr { background-color: transparent !important; color: #ccc; border-bottom: 1px solid rgba(255,255,255,0.05); }
        table.dataTable thead th { 
            background-color: transparent; 
            color: #888; 
            border-bottom: 2px solid rgba(255,255,255,0.1); 
            text-transform: uppercase; 
            font-size: 11px; 
            letter-spacing: 1px;
            padding-bottom: 15px;
        }
        
        /* PAGINATION & INPUTS */
        .dataTables_wrapper .dataTables_paginate .paginate_button { 
            color: #fff !important; 
            border: 1px solid rgba(255,255,255,0.2) !important; 
            background: transparent !important; 
            margin: 2px; 
            border-radius: 4px; 
        }
        .dataTables_wrapper .dataTables_paginate .paginate_button:hover,
        .dataTables_wrapper .dataTables_paginate .paginate_button.current { 
            background: #fff !important; 
            color: #000 !important; 
            border-color: #fff !important;
            font-weight: bold;
        }
        input.form-control { 
            background: rgba(0,0,0,0.3); 
            border: 1px solid var(--border-color); 
            color: white; 
            border-radius: 6px; 
            font-size: 12px;
        }
        input.form-control:focus { background: rgba(0,0,0,0.5); color:white; border-color: #666; box-shadow: none; }
        
        .btn-clean { 
            width: 100%; 
            background: rgba(220, 53, 69, 0.1); 
            border: 1px solid rgba(220, 53, 69, 0.3); 
            color: #ff6b6b; 
            padding: 12px; 
            margin-top: 20px; 
            font-size: 11px; 
            border-radius: 8px;
            text-transform: uppercase; 
            transition: 0.3s; 
            letter-spacing: 1px;
        }
        .btn-clean:hover { background: #ff6b6b; color: white; }
    </style>
</head>
<body>

    <div class="sidebar">
        <div class="brand">EKER<span>GALLERY</span></div>
        
        <div class="nav flex-column">
            <div class="nav-link active" onclick="filterTable('')"><i class="fa-solid fa-layer-group"></i> GENEL BAKIŞ</div>
            
            <div class="mt-4 mb-2 text-muted fw-bold ps-2" style="font-size:10px; letter-spacing:1px;">LÜKS KATEGORİ</div>
            <div class="nav-link" onclick="filterTable('Tesla')"><i class="fa-solid fa-bolt"></i> TESLA MODEL Y</div>
            <div class="nav-link" onclick="filterTable('Mercedes')"><i class="fa-solid fa-star"></i> MERCEDES AMG</div>
            <div class="nav-link" onclick="filterTable('Volvo')"><i class="fa-solid fa-shield"></i> VOLVO S90</div>
            
            <div class="mt-4 mb-2 text-muted fw-bold ps-2" style="font-size:10px; letter-spacing:1px;">EKONOMİK SINIF</div>
            <div class="nav-link" onclick="filterTable('Corsa')"><i class="fa-solid fa-car-side"></i> OPEL CORSA</div>
            <div class="nav-link" onclick="filterTable('Polo')"><i class="fa-solid fa-car"></i> VW POLO</div>
            <div class="nav-link" onclick="filterTable('Doblo')"><i class="fa-solid fa-van-shuttle"></i> FIAT DOBLO</div>

            <div class="mt-5">
                <label class="text-muted small ms-1 mb-1">BÜTÇE ARALIĞI</label>
                <div class="d-flex gap-2">
                    <input type="number" id="minPrice" class="form-control" placeholder="Min">
                    <input type="number" id="maxPrice" class="form-control" placeholder="Max">
                </div>
            </div>

            <form action="/clean-duplicates" method="POST" onsubmit="return confirm('Veritabanı optimize edilecek. Onaylıyor musun?');">
                <button type="submit" class="btn-clean"><i class="fa-solid fa-database me-2"></i> VERİLERİ TEMİZLE</button>
            </form>
            
             <a href="/logout" class="nav-link text-danger mt-4"><i class="fa-solid fa-power-off"></i> ÇIKIŞ</a>
        </div>
    </div>

    <div class="main-content">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h3 class="fw-light text-white m-0">Hoşgeldin, <span class="fw-bold">Patron</span></h3>
                <small class="text-muted">Piyasa Analiz Paneli</small>
            </div>
            <div>
                <span class="badge bg-light text-dark px-3 py-2" style="font-weight:600;">CANLI VERİ AKIŞI</span>
            </div>
        </div>

        <div class="row g-4">
            <div class="col-md-4">
                <div class="stat-card">
                    <div class="stat-val" id="totalCount">{{ toplam }}</div>
                    <div class="stat-label">GÖRÜNTÜLENEN İLAN</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card" style="border-color: rgba(40, 167, 69, 0.3);">
                    <div class="stat-val text-success">{{ firsat }}</div>
                    <div class="stat-label">TESPİT EDİLEN FIRSAT</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card">
                    <div class="stat-val" id="dynamicAvg">0 ₺</div>
                    <div class="stat-label">SEÇİLİ ARAÇ ORTALAMASI</div>
                </div>
            </div>
        </div>

        <div class="table-container">
            <table id="mainTable" class="table table-borderless dt-responsive nowrap" style="width:100%">
                <thead>
                    <tr>
                        <th>ANALİZ</th>
                        <th>KATEGORİ</th>
                        <th>BAŞLIK</th>
                        <th>YIL / KM</th>
                        <th>FİYAT</th>
                        <th>AI DEĞERİ</th>
                        <th>KAZANÇ POTANSİYELİ</th>
                        <th>İŞLEM</th>
                    </tr>
                </thead>
                <tbody>
                    {% for a in ilanlar %}
                    <tr>
                        <td>
                            {% if a.ai_firsat %}
                                <span class="badge bg-white text-dark shadow-sm">⚡ FIRSAT</span>
                            {% else %}
                                <span class="badge bg-transparent border border-secondary text-muted">NORMAL</span>
                            {% endif %}
                        </td>
                        <td class="text-white fw-bold">{{ a.category }}</td>
                        <td class="text-light opacity-75">{{ a.baslik[:35] }}...</td>
                        <td class="text-muted">{{ a.yil }} / {{ a.km }}</td>
                        <td class="text-white fw-bold fs-6">{{ "{:,}".format(a.fiyat) }} ₺</td>
                        <td class="text-info opacity-75">{% if a.ai_tahmin > 0 %}{{ "{:,}".format(a.ai_tahmin) }} ₺{% endif %}</td>
                        <td class="{% if a.ai_firsat %}text-success fw-bold{% else %}text-muted{% endif %}">
                            {% if a.fark != 0 %}{{ "{:,}".format(a.fark) }}{% endif %}
                        </td>
                        <td><a href="{{ a.url }}" target="_blank" class="btn btn-sm btn-light rounded-pill px-3" style="font-size:10px; font-weight:700;">İNCELE</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.7.0.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>
    <script src="https://cdn.datatables.net/responsive/2.5.0/js/dataTables.responsive.min.js"></script>

    <script>
        $(document).ready(function() {
            var table = $('#mainTable').DataTable({
                "pageLength": 15,
                "paging": true,
                "info": true,
                "lengthChange": false,
                "responsive": true,
                "language": {"url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/tr.json"},
                "order": [[ 4, "asc" ]],
                
                // --- SİHİRLİ DOKUNUŞ: TABLO HER ÇİZİLDİĞİNDE HESAPLAMA YAP ---
                "drawCallback": function(settings) {
                    var api = this.api();
                    
                    // Ekranda (veya filtrede) kalan satırların fiyatlarını topla
                    var total = 0;
                    var count = 0;
                    
                    api.rows({ search: 'applied' }).data().each(function(row) {
                        // row[4] bizim fiyat sütunu "1.250.000 ₺" şeklinde
                        // Buradan sayıları ayıklıyoruz
                        var priceStr = row[4].replace(/[^\d]/g, ''); // Sadece rakamları al
                        var price = parseInt(priceStr) || 0;
                        
                        if (price > 0) {
                            total += price;
                            count++;
                        }
                    });

                    // Ortalamayı hesapla
                    var avg = count > 0 ? Math.floor(total / count) : 0;
                    
                    // Sağ üstteki kutuya yaz
                    $('#dynamicAvg').text(avg.toLocaleString('tr-TR') + ' ₺');
                    
                    // Toplam sayıyı da güncelle
                    $('#totalCount').text(count);
                }
            });

            // Fiyat Filtresi Mantığı
            $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
                var min = parseInt($('#minPrice').val(), 10);
                var max = parseInt($('#maxPrice').val(), 10);
                var price = parseFloat(data[4].replace(/[^0-9]/g, '')) || 0;
                if ((isNaN(min) && isNaN(max)) || (isNaN(min) && price <= max) || (min <= price && isNaN(max)) || (min <= price && price <= max)) return true;
                return false;
            });

            $('#minPrice, #maxPrice').on('keyup change', function() { table.draw(); });
        });

        function filterTable(val) {
            $('#mainTable').DataTable().search(val).draw();
            
            // Menüdeki aktif sınıfı değiştir
            $('.nav-link').removeClass('active');
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""

# --- BACKEND ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('home'))
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/clean-duplicates', methods=['POST'])
def clean_duplicates():
    if not session.get('logged_in'): return redirect(url_for('login'))
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        col = client["sahibinden_data"]["tum_araclar"]
        pipeline = [{"$group": {"_id": "$url", "ids": {"$push": "$_id"}, "count": {"$sum": 1}}}, {"$match": {"count": {"$gt": 1}}}]
        duplicates = list(col.aggregate(pipeline))
        for doc in duplicates:
            ids_to_remove = doc['ids'][:-1]
            if ids_to_remove: col.delete_many({"_id": {"$in": ids_to_remove}})
    except: pass
    return redirect(url_for('home'))

@app.route('/')
def home():
    if not session.get('logged_in'): return redirect(url_for('login'))
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        col = client["sahibinden_data"]["tum_araclar"]
        data = list(col.find())
        processed = []
        X, y = [], []
        
        for d in data:
            try:
                p_str = str(d.get('price', '0')).split('TL')[0].replace('.', '').strip()
                price = int(p_str) if p_str.isdigit() else 0
                km_raw = str(d.get('details', {}).get('KM', d.get('km', '0')))
                km = int(km_raw.replace('.', '').replace(' km', '').strip()) if km_raw else 0
                year = int(d.get('year', 0))
                category = d.get('category', 'Diğer')
                item = {'category': category, 'baslik': d.get('title', '-'), 'fiyat': price, 'yil': year, 'km': km, 'url': d.get('url', '#'), 'ai_tahmin': 0, 'ai_firsat': False, 'fark': 0}
                if price > 100000 and year > 2000:
                    X.append([year, km])
                    y.append(price)
                    processed.append(item)
            except: continue

        if len(X) > 10:
            model = MLPRegressor(hidden_layer_sizes=(50,50), max_iter=200)
            model.fit(X, y)
            preds = model.predict(X)
            for i, item in enumerate(processed):
                tahmin = int(preds[i])
                item['ai_tahmin'] = tahmin
                item['fark'] = item['fiyat'] - tahmin
                if item['fiyat'] < tahmin * 0.90: item['ai_firsat'] = True
        
        return render_template_string(DASHBOARD_HTML, ilanlar=processed, toplam=len(processed), firsat=sum(1 for x in processed if x['ai_firsat']))
    except Exception as e: return f"Hata: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
