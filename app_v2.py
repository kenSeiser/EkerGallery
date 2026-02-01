# ========================================
# EkerGallery - Modern Flask Uygulaması v2.1
# ========================================

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from functools import wraps
import sys
import os
import json
import threading
import time
from queue import Queue

# Modülleri import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import SECRET_KEY, ADMIN_USER, ADMIN_PASS, VEHICLE_CATEGORIES
from models.database import db


app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = SECRET_KEY

# Global scraping durumu
scraping_status = {
    "active": False,
    "current_brand": "",
    "current_model": "",
    "current_page": 0,
    "total_scraped": 0,
    "new_listings": 0,
    "progress_percent": 0,
    "message": "",
    "errors": []
}

# SSE mesaj kuyruğu
progress_subscribers = []


def broadcast_progress():
    """Tüm abonelere ilerleme durumunu gönder"""
    data = json.dumps(scraping_status)
    for q in progress_subscribers[:]:
        try:
            q.put(data)
        except:
            pass


# ========================================
# DEKORATÖRLER
# ========================================

def login_required(f):
    """Login gerektiren route'lar için dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ========================================
# AUTH ROUTES
# ========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Giriş sayfası"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = "Geçersiz kullanıcı adı veya şifre"
    
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Çıkış"""
    session.clear()
    return redirect(url_for('login'))


# ========================================
# DASHBOARD ROUTES
# ========================================

@app.route('/')
@login_required
def dashboard():
    """Ana dashboard sayfası"""
    try:
        stats = db.get_stats()
    except Exception as e:
        stats = {"total": 0, "firsatlar": 0, "avg_price": 0, "brand_distribution": []}
        print(f"Stats hatası: {e}")
    
    categories = VEHICLE_CATEGORIES
    
    return render_template(
        'dashboard.html',
        stats=stats,
        categories=categories,
        username=session.get('username', 'Kullanıcı'),
        scraping_status=scraping_status
    )


# ========================================
# API ROUTES
# ========================================

@app.route('/api/vehicles')
@login_required
def api_vehicles():
    """Araç listesi API"""
    try:
        brand = request.args.get('brand')
        model = request.args.get('model')
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        min_year = request.args.get('min_year', type=int)
        max_year = request.args.get('max_year', type=int)
        fuel = request.args.get('fuel')
        transmission = request.args.get('transmission')
        only_firsatlar = request.args.get('firsatlar') == 'true'
        limit = request.args.get('limit', default=500, type=int)
        
        filters = {}
        
        if brand:
            filters['marka'] = brand
        if model:
            filters['model'] = model
        if fuel:
            filters['yakit'] = fuel
        if transmission:
            filters['vites'] = transmission
        if only_firsatlar:
            filters['ai_firsat'] = True
        
        if min_price or max_price:
            filters['fiyat'] = {}
            if min_price:
                filters['fiyat']['$gte'] = min_price
            if max_price:
                filters['fiyat']['$lte'] = max_price
        
        if min_year or max_year:
            filters['yil'] = {}
            if min_year:
                filters['yil']['$gte'] = min_year
            if max_year:
                filters['yil']['$lte'] = max_year
        
        vehicles = db.get_all_vehicles(filters, limit=limit)
        
        for v in vehicles:
            v['_id'] = str(v['_id'])
            for key in ['created_at', 'updated_at', 'scraped_at', 'ai_updated_at']:
                if key in v and v[key]:
                    v[key] = v[key].isoformat() if hasattr(v[key], 'isoformat') else str(v[key])
        
        return jsonify({
            'success': True,
            'count': len(vehicles),
            'data': vehicles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        })


@app.route('/api/stats')
@login_required
def api_stats():
    """İstatistikler API"""
    try:
        stats = db.get_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {"total": 0, "firsatlar": 0, "avg_price": 0}
        })


@app.route('/api/firsatlar')
@login_required
def api_firsatlar():
    """Fırsat ilanları API"""
    try:
        firsatlar = db.get_firsatlar()
        
        for v in firsatlar:
            v['_id'] = str(v['_id'])
            for key in ['created_at', 'updated_at', 'scraped_at', 'ai_updated_at']:
                if key in v and v[key]:
                    v[key] = v[key].isoformat() if hasattr(v[key], 'isoformat') else str(v[key])
        
        return jsonify({
            'success': True,
            'count': len(firsatlar),
            'data': firsatlar
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        })


@app.route('/api/brands')
@login_required
def api_brands():
    """Marka listesi API"""
    brands = []
    for key, info in VEHICLE_CATEGORIES.items():
        brands.append({
            'key': key,
            'name': info['display_name'],
            'models': [
                {'key': mk, 'name': mv['name']}
                for mk, mv in info['models'].items()
            ]
        })
    
    return jsonify({
        'success': True,
        'data': brands
    })


@app.route('/api/scraping-status')
@login_required
def api_scraping_status():
    """Scraping durumu API"""
    return jsonify(scraping_status)


# ========================================
# SSE (Server-Sent Events) PROGRESS STREAM
# ========================================

@app.route('/api/progress-stream')
@login_required
def progress_stream():
    """SSE progress stream"""
    def generate():
        q = Queue()
        progress_subscribers.append(q)
        try:
            yield f"data: {json.dumps(scraping_status)}\n\n"
            
            while True:
                try:
                    data = q.get(timeout=30)
                    yield f"data: {data}\n\n"
                except:
                    yield f"data: {json.dumps({'ping': True})}\n\n"
        finally:
            progress_subscribers.remove(q)
    
    return Response(generate(), mimetype='text/event-stream')


# ========================================
# ACTION ROUTES
# ========================================

@app.route('/clean-duplicates', methods=['POST'])
@login_required
def clean_duplicates():
    """Mükerrer kayıtları temizle"""
    try:
        removed = db.remove_duplicates()
        return jsonify({
            'success': True,
            'message': f'{removed} mükerrer kayıt silindi'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/update-ai', methods=['POST'])
@login_required
def update_ai():
    """AI tahminlerini güncelle"""
    def run_ai_update():
        global scraping_status
        try:
            scraping_status['active'] = True
            scraping_status['message'] = 'AI modeli eğitiliyor...'
            scraping_status['progress_percent'] = 10
            broadcast_progress()
            
            from services.ai_model import price_model
            
            scraping_status['message'] = 'Model eğitimi tamamlandı, tahminler yapılıyor...'
            scraping_status['progress_percent'] = 50
            broadcast_progress()
            
            price_model.update_all_predictions()
            
            scraping_status['message'] = 'AI tahminleri başarıyla güncellendi!'
            scraping_status['progress_percent'] = 100
            broadcast_progress()
            
        except Exception as e:
            scraping_status['errors'].append(str(e))
            scraping_status['message'] = f'Hata: {e}'
        finally:
            time.sleep(2)
            scraping_status['active'] = False
            scraping_status['progress_percent'] = 0
            broadcast_progress()
    
    thread = threading.Thread(target=run_ai_update)
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'AI güncelleme başlatıldı'
    })


@app.route('/start-scraping', methods=['POST'])
@login_required
def start_scraping():
    """Veri çekmeyi başlat (arka planda)"""
    global scraping_status
    
    if scraping_status['active']:
        return jsonify({
            'success': False,
            'error': 'Zaten bir scraping işlemi devam ediyor'
        })
    
    data = request.get_json(silent=True) or {}
    brands = data.get('brands', [])
    
    def run_scraping():
        global scraping_status
        try:
            scraping_status = {
                "active": True,
                "current_brand": "",
                "current_model": "",
                "current_page": 0,
                "total_scraped": 0,
                "new_listings": 0,
                "progress_percent": 0,
                "message": "Scraping başlatılıyor...",
                "errors": []
            }
            broadcast_progress()
            
            from services.scraper_v2 import VehicleScraper
            
            scraper = VehicleScraper(headless=True, use_proxy=False)
            scraper.status_callback = update_scraping_status
            
            scraper.run(brands=brands if brands else None)
            
            scraping_status['message'] = 'Scraping tamamlandı! AI tahminleri güncelleniyor...'
            scraping_status['progress_percent'] = 90
            broadcast_progress()
            
            # AI tahminlerini güncelle
            from services.ai_model import price_model
            price_model.update_all_predictions()
            
            scraping_status['message'] = f'Tamamlandı! {scraping_status["total_scraped"]} ilan çekildi, {scraping_status["new_listings"]} yeni eklendi.'
            scraping_status['progress_percent'] = 100
            broadcast_progress()
            
        except Exception as e:
            scraping_status['errors'].append(str(e))
            scraping_status['message'] = f'Hata: {e}'
            broadcast_progress()
        finally:
            time.sleep(3)
            scraping_status['active'] = False
            scraping_status['progress_percent'] = 0
            broadcast_progress()
    
    thread = threading.Thread(target=run_scraping)
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Scraping başlatıldı'
    })


def update_scraping_status(status_update: dict):
    """Scraper'dan gelen durum güncellemelerini işle"""
    global scraping_status
    scraping_status.update(status_update)
    broadcast_progress()


@app.route('/stop-scraping', methods=['POST'])
@login_required
def stop_scraping():
    """Scraping'i durdur"""
    global scraping_status
    scraping_status['active'] = False
    scraping_status['message'] = 'Durduruldu'
    broadcast_progress()
    
    return jsonify({
        'success': True,
        'message': 'Durdurma sinyali gönderildi'
    })


# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ========================================
# MAIN
# ========================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
