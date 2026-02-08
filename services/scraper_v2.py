"""
EkerGallery - Advanced Scraper v3
Features:
- 10-page pagination per category
- Detail page scraping for damage info
- AI price prediction integration
- Robust error handling
"""

import argparse
import time
import random
import os
import sys
import logging
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import MONGO_URI, DB_NAME, COLLECTION_NAME, VEHICLE_CATEGORIES, MAX_PAGES_PER_CATEGORY
except ImportError:
    MONGO_URI = "mongodb://localhost:27017/"
    DB_NAME = "sahibinden_data"
    COLLECTION_NAME = "tum_araclar"
    VEHICLE_CATEGORIES = {}
    MAX_PAGES_PER_CATEGORY = 10

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/scraper.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """MongoDB bağlantısı"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        logger.info(f"Connected to MongoDB: {DB_NAME}")
        return db
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {e}")
        return None


def init_driver():
    """Chrome driver başlat"""
    # User-Agent Rotation
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ]
    options.add_argument(f'--user-agent={random.choice(user_agents)}')
    options.add_argument('--lang=tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7')
    
    try:
        driver = uc.Chrome(options=options)
        logger.info("Chrome driver initialized")
        
        # Stealth
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Warmup
        logger.info("Warming up browser...")
        driver.get("https://www.google.com")
        time.sleep(random.uniform(2, 4))
        
        return driver
    except Exception as e:
        logger.error(f"Failed to init driver: {e}")
        sys.exit(1)


def random_sleep(min_s=2, max_s=5):
    """Rastgele bekleme"""
    time.sleep(random.uniform(min_s, max_s))


def wait_for_manual_intervention(driver):
    """
    Bot kontrolü veya giriş ekranı algılandığında sonsuz döngüde bekler.
    Kullanıcı engeli kaldırdığında otomatik devam eder.
    """
    check_interval = 2
    while True:
        try:
            page_source = driver.page_source
            current_url = driver.current_url
            
            # Daha spesifik öğe kontrolleri
            is_bot = any(x in page_source for x in ["Olağandışı", "Olağan dışı", "robot", "captcha"])
            is_login = any(x in current_url for x in ["UyeGiris", "giris-yap", "secure.sahibinden.com/giris"])
            
            # Eğer ilan tablosu veya detay kutusu gelmişse engel kalkmış demektir
            has_results = len(driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem, .classifiedDetail")) > 0
            
            if not is_bot and not is_login:
                break
            
            if has_results: # İçerik geldiyse uyarıyı geç
                break
                
            if is_bot:
                logger.warning("!!! BOT KONTROLU (CAPTCHA) ALGILANDI !!! Lütfen tarayıcıda işlemi tamamlayın. Scraper bekliyor...")
            elif is_login:
                logger.warning("!!! GIRIS EKRANI ALGILANDI !!! Lütfen giriş yapın. Scraper bekliyor...")
                
            time.sleep(check_interval)
        except Exception as e:
            logger.error(f"Waiting error: {e}")
            break


def random_scroll(driver):
    """Gerçek kullanıcı gibi rastgele scroll yapar"""
    try:
        total_height = driver.execute_script("return document.body.scrollHeight")
        scroll_to = random.randint(100, min(800, total_height))
        driver.execute_script(f"window.scrollTo({{top: {scroll_to}, behavior: 'smooth'}});")
        time.sleep(random.uniform(1, 2))
        driver.execute_script(f"window.scrollTo({{top: 0, behavior: 'smooth'}});")
    except:
        pass


def parse_price(text):
    """Fiyat parse et"""
    if not text:
        return 0
    try:
        clean = text.replace('TL', '').replace('.', '').replace(',', '').strip()
        return int(clean)
    except:
        return 0


def parse_km(text):
    """KM parse et"""
    if not text:
        return 0
    try:
        clean = text.replace('km', '').replace('.', '').replace(',', '').strip()
        return int(clean)
    except:
        return 0


def get_detail_info(driver, url):
    """
    İlan detay sayfasından ek bilgi çek:
    - Yakıt tipi
    - Vites
    - Boyalı parçalar
    - Değişen parçalar
    """
    result = {
        "yakit": "",
        "vites": "",
        "boyali_parcalar": [],
        "degisen_parcalar": [],
        "hasar_puani": 0
    }
    
    try:
        driver.get(url)
        wait_for_manual_intervention(driver)
        random_scroll(driver)
        random_sleep(2, 4)
        
        # Bilgi tablosunu bul
        try:
            info_rows = driver.find_elements(By.CSS_SELECTOR, ".classifiedInfoList li")
            for row in info_rows:
                try:
                    label = row.find_element(By.CSS_SELECTOR, "strong").text.strip()
                    value = row.text.replace(label, "").strip()
                    
                    if "Yakıt" in label:
                        result["yakit"] = value
                    elif "Vites" in label:
                        result["vites"] = value
                except:
                    continue
        except:
            pass
        
        # Tramer / Expertise bilgisi
        try:
            # Boya-Değişen bölümü
            damage_section = driver.find_elements(By.CSS_SELECTOR, ".classified-expertise-list li, .damage-history li")
            for item in damage_section:
                text = item.text.strip().lower()
                if "boyalı" in text or "boyali" in text:
                    result["boyali_parcalar"].append(item.text.strip())
                elif "değişen" in text or "degisen" in text:
                    result["degisen_parcalar"].append(item.text.strip())
        except:
            pass
        
        # Tramer kaydı kontrol
        try:
            page_text = driver.page_source.lower()
            if "tramer kaydı bulunmamaktadır" in page_text or "hasar kaydı yok" in page_text:
                result["hasar_puani"] = 0
            elif "tramer" in page_text or "hasar kaydı" in page_text:
                # Basit skor: boyalı = 5, değişen = 15
                result["hasar_puani"] = len(result["boyali_parcalar"]) * 5 + len(result["degisen_parcalar"]) * 15
        except:
            pass
            
    except Exception as e:
        logger.warning(f"Detail fetch failed for {url}: {e}")
    
    return result


def scrape_listing_page(driver, url):
    """Tek sayfa ilanları çek"""
    listings = []
    
    try:
        driver.get(url)
        wait_for_manual_intervention(driver)
        random_scroll(driver)
        random_sleep(3, 5)
        
        # İlanları bekle
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr.searchResultsItem"))
            )
        except:
            logger.warning(f"No listings found on {url}")
            return []
        
        items = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
        
        for item in items:
            try:
                data_id = item.get_attribute("data-id")
                if not data_id:
                    continue
                
                # Başlık ve link
                title_elem = item.find_element(By.CSS_SELECTOR, ".classifiedTitle")
                title = title_elem.text.strip()
                link = title_elem.get_attribute("href")
                
                # Fiyat
                try:
                    price_elem = item.find_element(By.CSS_SELECTOR, ".searchResultsPriceValue")
                    price = parse_price(price_elem.text)
                except:
                    price = 0
                
                # Tablo hücreleri
                cells = item.find_elements(By.TAG_NAME, "td")
                
                model_name = cells[1].text.strip() if len(cells) > 1 else ""
                year = 0
                if len(cells) > 3:
                    try:
                        year = int(cells[3].text.strip())
                    except:
                        pass
                
                km = parse_km(cells[4].text) if len(cells) > 4 else 0
                color = cells[5].text.strip() if len(cells) > 5 else ""
                location = cells[8].text.replace('\n', ' ').strip() if len(cells) > 8 else ""
                
                listings.append({
                    "ilan_no": data_id,
                    "baslik": title,
                    "url": link,
                    "fiyat": price,
                    "model_detay": model_name,
                    "yil": year,
                    "km": km,
                    "renk": color,
                    "raw_location": location
                })
                
            except Exception as e:
                continue
        
        logger.info(f"Found {len(listings)} listings on page")
        
    except Exception as e:
        logger.error(f"Error scraping page {url}: {e}")
    
    return listings


def scrape_category(driver, db, brand_key, model_key, model_info):
    """Kategori için tüm sayfaları tara"""
    base_url = model_info['url']
    category_name = model_info['name']
    collection = db[COLLECTION_NAME]
    
    logger.info(f"=== Scraping: {brand_key} {category_name} ===")
    
    total_saved = 0
    
    # 10 sayfa tara
    for page in range(MAX_PAGES_PER_CATEGORY):
        offset = page * 20
        
        if "?" in base_url:
            page_url = f"{base_url}&pagingOffset={offset}"
        else:
            page_url = f"{base_url}?pagingOffset={offset}"
        
        logger.info(f"Page {page + 1}/{MAX_PAGES_PER_CATEGORY}: {page_url}")
        
        listings = scrape_listing_page(driver, page_url)
        
        if not listings:
            logger.info(f"No more listings, stopping at page {page + 1}")
            break
        
        # Her ilan için detay sayfasına git
        for listing in listings:
            try:
                # Detay bilgisi çek
                detail = get_detail_info(driver, listing["url"])
                
                # Birleştir
                location_parts = listing["raw_location"].split()
                
                vehicle_doc = {
                    "ilan_no": listing["ilan_no"],
                    "baslik": listing["baslik"],
                    "url": listing["url"],
                    "fiyat": listing["fiyat"],
                    "marka": brand_key,
                    "model": model_key,
                    "model_detay": listing["model_detay"],
                    "yil": listing["yil"],
                    "km": listing["km"],
                    "renk": listing["renk"],
                    "yakit": detail["yakit"],
                    "vites": detail["vites"],
                    "boyali_parcalar": detail["boyali_parcalar"],
                    "degisen_parcalar": detail["degisen_parcalar"],
                    "hasar_puani": detail["hasar_puani"],
                    "il": location_parts[0] if location_parts else "",
                    "ilce": location_parts[1] if len(location_parts) > 1 else "",
                    "category": f"{brand_key} {model_key}",
                    "scraped_at": datetime.now()
                }
                
                # MongoDB'ye kaydet (upsert)
                collection.update_one(
                    {"ilan_no": listing["ilan_no"]},
                    {"$set": vehicle_doc},
                    upsert=True
                )
                total_saved += 1
                
            except Exception as e:
                logger.error(f"Error processing {listing.get('ilan_no', '?')}: {e}")
                continue
            
            # Detay sayfaları arası kısa bekleme
            random_sleep(1, 2)
        
        # Sayfa arası bekleme
        random_sleep(3, 6)
    
    logger.info(f"Saved {total_saved} vehicles for {category_name}")
    return total_saved


def run_ai_predictions(db):
    """AI tahminlerini çalıştır"""
    logger.info("Running AI predictions...")
    try:
        from services.ai_model import price_model
        price_model.update_all_predictions()
        logger.info("AI predictions completed")
    except Exception as e:
        logger.error(f"AI prediction error: {e}")


def main():
    parser = argparse.ArgumentParser(description='Sahibinden Advanced Scraper')
    parser.add_argument('--skip-ai', action='store_true', help='Skip AI predictions')
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("Starting Advanced Scraper v3")
    logger.info("=" * 50)
    
    # IP kontrol
    try:
        resp = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip = resp.json().get('ip')
        logger.info(f"Current IP: {ip}")
    except:
        pass
    
    # DB bağlan
    db = get_db_connection()
    if db is None:
        logger.error("Database connection failed!")
        return
    
    # Driver başlat
    driver = init_driver()
    
    try:
        total = 0
        for brand_key, brand_data in VEHICLE_CATEGORIES.items():
            for model_key, model_info in brand_data.get('models', {}).items():
                saved = scrape_category(driver, db, brand_key, model_key, model_info)
                total += saved
                random_sleep(5, 10)
        
        logger.info(f"Total scraped: {total} vehicles")
        
        # AI tahminleri
        if not args.skip_ai:
            run_ai_predictions(db)
        
    except Exception as e:
        logger.error(f"Scraper error: {e}")
    finally:
        logger.info("Closing driver...")
        driver.quit()
        logger.info("Scraper finished!")


if __name__ == "__main__":
    main()
