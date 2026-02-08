# ========================================
# EkerGallery - Modern Flask Uygulaması v2.1
# ========================================

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, flash
from werkzeug.security import generate_password_hash, check_password_hash
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



# ========================================
# DEKORATÖRLER
# ========================================


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return render_template('404.html'), 403
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
        
        # 1. Admin Login Attempt
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('dashboard'))
        
        # 2. Db User Login Attempt
        user = db.get_user(username)
        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user.get('role', 'user')
            return redirect(url_for('dashboard'))
        
        error = "Geçersiz kullanıcı adı veya şifre"
    
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Kayıt sayfası"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            return render_template('register.html', error="Tüm alanları doldurun")
            
        if password != confirm_password:
            return render_template('register.html', error="Şifreler eşleşmiyor")
            
        if username == ADMIN_USER:
            return render_template('register.html', error="Bu kullanıcı adı alınamaz")

        # Create user
        hashed_password = generate_password_hash(password)
        if db.create_user(username, hashed_password):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error="Kullanıcı adı zaten kullanımda")
            
    return render_template('register.html')


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
        role=session.get('role', 'user')
    )


# ========================================
# API ROUTES
# ========================================

@app.route('/api/vehicles')
@login_required
def api_vehicles():
    """Araç listesi API"""
    try:
        # Filtre parametrelerini al
        brand = request.args.get('brand') or request.args.get('marka')
        model = request.args.get('model')
        fuel = request.args.get('fuel') or request.args.get('yakit')
        transmission = request.args.get('gear') or request.args.get('vites')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        min_year = request.args.get('min_year')
        
        only_firsatlar = request.args.get('firsatlar') == 'true'
        
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit
        
        filters = {}
        
        if brand and model:
            # Search by marka+model OR category containing both
            category_pattern = f".*{brand}.*{model}.*"
            filters['$or'] = [
                {'marka': brand, 'model': model},
                {'category': {'$regex': category_pattern, '$options': 'i'}}
            ]
        elif brand:
            # Search by marka OR category containing brand
            filters['$or'] = [
                {'marka': brand},
                {'category': {'$regex': f".*{brand}.*", '$options': 'i'}}
            ]
        elif model:
            filters['$or'] = [
                {'model': model},
                {'category': {'$regex': f".*{model}.*", '$options': 'i'}}
            ]
            
        if fuel:
            filters['yakit'] = fuel
        if transmission:
            filters['vites'] = transmission
        if only_firsatlar:
            filters['ai_firsat'] = True
        
        if min_price:
            filters.setdefault('fiyat', {})['$gte'] = int(min_price)
        if max_price:
            filters.setdefault('fiyat', {})['$lte'] = int(max_price)
        if min_year:
            filters['yil'] = {'$gte': int(min_year)}
        
        # Toplam sayıyı al
        total_count = db.vehicles.count_documents(filters)
        print(f"DEBUG: Total count for filters {filters}: {total_count}")
        
        # Verileri çek (Optimize edilmiş Projection ile)
        projection = {
            "marka": 1, "model": 1, "yil": 1, "year": 1, "km": 1, 
            "yakit": 1, "vites": 1, "fiyat": 1, "price": 1,
            "title": 1, "baslik": 1, "category": 1, "url": 1,
            "ai_tahmin": 1, "ai_firsat": 1, "fark": 1,
            "il": 1, "ilce": 1, 
            "hasar_puani": 1, "boyali_parcalar": 1, "degisen_parcalar": 1, "boya_degisen": 1,
            "created_at": 1, "updated_at": 1, "scraped_at": 1, "ai_updated_at": 1,
            "details": 1
        }
        vehicles = db.get_all_vehicles(filters, limit=limit, skip=skip, projection=projection)
        print(f"DEBUG: Fetched {len(vehicles)} vehicles. Skip: {skip}, Limit: {limit}")
        
        for v in vehicles:
            v['_id'] = str(v['_id'])
            for key in ['created_at', 'updated_at', 'scraped_at', 'ai_updated_at']:
                if key in v and v[key]:
                    v[key] = v[key].isoformat() if hasattr(v[key], 'isoformat') else str(v[key])
        
        return jsonify({
            'success': True,
            'count': total_count,
            'data': vehicles,
            'page': page,
            'limit': limit,
            'total_pages': (total_count + limit - 1) // limit if limit > 0 else 1
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
    """İstatistikler API - Filtreye göre istatistik döndürür"""
    try:
        # Filtre parametrelerini al
        brand = request.args.get('brand') or request.args.get('marka')
        model = request.args.get('model')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        min_year = request.args.get('min_year') or request.args.get('yil')
        
        filters = {}
        
        if brand and model:
            # Search by marka+model OR category containing both
            category_pattern = f".*{brand}.*{model}.*"
            filters['$or'] = [
                {'marka': brand, 'model': model},
                {'category': {'$regex': category_pattern, '$options': 'i'}}
            ]
        elif brand:
            # Search by marka OR category containing brand
            filters['$or'] = [
                {'marka': brand},
                {'category': {'$regex': f".*{brand}.*", '$options': 'i'}}
            ]
        elif model:
            filters['$or'] = [
                {'model': model},
                {'category': {'$regex': f".*{model}.*", '$options': 'i'}}
            ]
            
        if min_price:
            filters.setdefault('fiyat', {})['$gte'] = int(min_price)
        if max_price:
            filters.setdefault('fiyat', {})['$lte'] = int(max_price)
            
        if min_year:
            filters['yil'] = {'$gte': int(min_year)}
            
        stats = db.get_stats(filters)
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




# ========================================
# ACTION ROUTES
# ========================================

@app.route('/clean-duplicates', methods=['POST'])
@login_required
@admin_required
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
@admin_required
def update_ai():
    """AI tahminlerini güncelle (Arka Plan İşlemi)"""
    try:
        # Subprocess ile başlat (Fire and forget)
        import subprocess
        subprocess.Popen(['python3', 'run_ai_job.py'], 
                         cwd=os.path.dirname(os.path.abspath(__file__)),
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        
        return jsonify({
            'success': True,
            'message': 'AI güncelleme işlemi arka planda başlatıldı. Bu işlem birkaç dakika sürebilir.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        })



@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    return render_template('admin.html', username=session.get('username'))

@app.route('/api/logs')
@login_required
def api_logs():
    """Son logları getir"""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(log_dir):
            return jsonify({'success': True, 'logs': 'Henüz log dosyası yok.'})
            
        # En yeni log dosyasını bul
        files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith('.log')]
        if not files:
            return jsonify({'success': True, 'logs': 'Log dosyası bulunamadı.'})
            
        latest_file = max(files, key=os.path.getmtime)
        
        # Son 50 satırı oku
        with open(latest_file, 'r', encoding='utf-8', errors='ignore') as f:
            # Tümünü oku, son 2000 karakteri al (basit tail)
            content = f.read()
            tail = content[-4000:] if len(content) > 4000 else content
            
        return jsonify({
            'success': True, 
            'logs': tail,
            'filename': os.path.basename(latest_file)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})




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
