# ========================================
# EkerGallery - Gelişmiş Web Scraper v2.1
# ========================================

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import random
import os
import sys
import pickle
import tempfile
import requests
from datetime import datetime

# Üst dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    VEHICLE_CATEGORIES, SCRAPE_FIELDS, CHROME_VERSION,
    MAX_PAGES_PER_CATEGORY
)
from models.database import db


class VehicleScraper:
    """Sahibinden.com araç ilanı scraper"""
    
    COOKIE_FILE = os.path.join(os.path.dirname(__file__), "..", "cookies.pkl")
    DRIVER_PATH = os.path.join(os.path.dirname(__file__), "..", "chromedriver")
    
    def __init__(self, headless: bool = True, use_proxy: bool = False, status_callback=None):
        """
        Args:
            headless: Headless modda çalıştır
            use_proxy: Proxy kullan
            status_callback: İlerleme durumu callback fonksiyonu
        """
        self.headless = headless
        self.use_proxy = use_proxy
        self.driver = None
        self.proxy = None
        self.status_callback = status_callback
        self.should_stop = False
        
        # İlerleme takibi
        self.total_scraped = 0
        self.new_listings = 0
        self.current_brand = ""
        self.current_model = ""
        self.current_page = 0
    
    def _update_status(self, **kwargs):
        """Durum güncellemesi gönder"""
        if self.status_callback:
            status = {
                "current_brand": self.current_brand,
                "current_model": self.current_model,
                "current_page": self.current_page,
                "total_scraped": self.total_scraped,
                "new_listings": self.new_listings,
                **kwargs
            }
            self.status_callback(status)
    
    def _get_free_proxy(self) -> str:
        """Ücretsiz proxy al"""
        self._update_status(message="Proxy aranıyor...")
        try:
            response = requests.get(
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
                timeout=10
            )
            if response.status_code == 200:
                proxies = response.text.strip().split('\n')
                if proxies:
                    proxy = random.choice(proxies)
                    self._update_status(message=f"Proxy bulundu: {proxy}")
                    return proxy
        except:
            pass
        self._update_status(message="Proxy bulunamadı, direkt bağlantı kullanılacak")
        return None
    
    def _create_driver(self):
        """Chrome driver oluştur"""
        self._update_status(message="Chrome başlatılıyor...", progress_percent=5)
        
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        # Temel ayarlar
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=tr-TR")
        options.page_load_strategy = 'eager'
        
        # Her instance için benzersiz profil
        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # User Agent
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Proxy
        if self.use_proxy:
            self.proxy = self._get_free_proxy()
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
                print(f"🎭 Proxy: {self.proxy}")
        
        # Driver oluştur
        driver_path = self.DRIVER_PATH if os.path.exists(self.DRIVER_PATH) else None
        
        self.driver = uc.Chrome(
            options=options,
            driver_executable_path=driver_path,
            version_main=CHROME_VERSION
        )
        self.driver.set_page_load_timeout(120)
        
        self._update_status(message="Chrome başlatıldı", progress_percent=10)
        return self.driver
    
    def _load_cookies(self):
        """Çerezleri yükle"""
        self._update_status(message="Çerezler yükleniyor...")
        
        if not os.path.exists(self.COOKIE_FILE):
            print("⚠️ Çerez dosyası bulunamadı")
            return False
        
        try:
            # Önce siteye git
            self.driver.get("https://www.sahibinden.com/favicon.ico")
            time.sleep(2)
            
            # Çerezleri yükle
            with open(self.COOKIE_FILE, "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
            
            print("✅ Çerezler yüklendi")
            self._update_status(message="Çerezler yüklendi")
            self.driver.refresh()
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ Çerez yükleme hatası: {e}")
            return False
    
    def _save_cookies(self):
        """Çerezleri kaydet"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.COOKIE_FILE, "wb") as f:
                pickle.dump(cookies, f)
            print("💾 Çerezler kaydedildi")
        except:
            pass
    
    def _parse_price(self, price_text: str) -> int:
        """Fiyat metnini sayıya çevir"""
        try:
            clean = ''.join(filter(str.isdigit, price_text.split('TL')[0]))
            return int(clean) if clean else 0
        except:
            return 0
    
    def _parse_km(self, km_text: str) -> int:
        """KM metnini sayıya çevir"""
        try:
            clean = ''.join(filter(str.isdigit, km_text))
            return int(clean) if clean else 0
        except:
            return 0
    
    def _parse_year(self, year_text: str) -> int:
        """Yıl metnini sayıya çevir"""
        try:
            clean = ''.join(filter(str.isdigit, str(year_text)))
            year = int(clean) if clean else 0
            return year if 1950 <= year <= 2030 else 0
        except:
            return 0
    
    def _extract_listing_details(self) -> dict:
        """İlan detay sayfasından verileri çek"""
        data = {}
        
        try:
            # Başlık
            try:
                data["baslik"] = self.driver.find_element(
                    By.CSS_SELECTOR, "div.classifiedDetailTitle h1"
                ).text.strip()
            except:
                data["baslik"] = "Başlık Yok"
            
            # Fiyat
            try:
                price_el = self.driver.find_element(
                    By.CSS_SELECTOR, "div.classifiedInfo > h3"
                )
                data["fiyat"] = self._parse_price(price_el.text)
            except:
                data["fiyat"] = 0
            
            # Detay listesini parse et
            try:
                detail_items = self.driver.find_elements(
                    By.CSS_SELECTOR, "ul.classifiedInfoList li"
                )
                for item in detail_items:
                    try:
                        label = item.find_element(By.TAG_NAME, "strong").text.strip()
                        value = item.find_element(By.TAG_NAME, "span").text.strip()
                        
                        if label in SCRAPE_FIELDS:
                            field_name = SCRAPE_FIELDS[label]
                            
                            if field_name == "yil":
                                data[field_name] = self._parse_year(value)
                            elif field_name == "km":
                                data[field_name] = self._parse_km(value)
                            elif field_name == "motor_hacmi":
                                data[field_name] = int(''.join(filter(str.isdigit, value)) or 0)
                            elif field_name == "motor_gucu":
                                data[field_name] = int(''.join(filter(str.isdigit, value)) or 0)
                            else:
                                data[field_name] = value
                    except:
                        continue
            except:
                pass
            
            # Konum bilgisi
            try:
                location = self.driver.find_element(
                    By.CSS_SELECTOR, "div.classifiedInfo h2"
                ).text.strip()
                parts = location.split(" / ")
                if len(parts) >= 2:
                    data["il"] = parts[0]
                    data["ilce"] = parts[1] if len(parts) > 1 else ""
            except:
                pass
            
            data["url"] = self.driver.current_url
            
        except Exception as e:
            print(f"⚠️ Detay çekme hatası: {e}")
        
        return data
    
    def scrape_category(self, category_url: str, category_name: str, brand: str, model: str, max_pages: int = None):
        """Kategori sayfasını tara"""
        if self.should_stop:
            return
        
        if max_pages is None:
            max_pages = MAX_PAGES_PER_CATEGORY
        
        self.current_brand = brand
        self.current_model = model
        
        print(f"\n{'='*50}")
        print(f"🚗 Kategori: {category_name}")
        print(f"🔗 URL: {category_url}")
        print(f"{'='*50}")
        
        self._update_status(message=f"{brand} {model} taranıyor...")
        
        self.driver.get(category_url)
        time.sleep(random.uniform(5, 8))
        
        page_number = 1
        category_scraped = 0
        category_new = 0
        
        while page_number <= max_pages and not self.should_stop:
            self.current_page = page_number
            self._update_status(
                message=f"{brand} {model} - Sayfa {page_number}/{max_pages}",
                current_page=page_number
            )
            
            print(f"\n📄 Sayfa {page_number}/{max_pages}")
            time.sleep(random.uniform(3, 5))
            
            # CAPTCHA kontrolü
            if "captcha" in self.driver.page_source.lower():
                self._update_status(message="⚠️ CAPTCHA tespit edildi! Bekleniyor...")
                print("⚠️ CAPTCHA tespit edildi! 2 dakika bekleniyor...")
                time.sleep(120)
                self.driver.refresh()
                continue
            
            # İlan listesi
            listings = self.driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
            
            if len(listings) == 0:
                print("⚠️ İlan bulunamadı, sonraki kategoriye geçiliyor")
                break
            
            print(f"📋 {len(listings)} ilan bulundu")
            
            # Her ilanı tara
            for i in range(len(listings)):
                if self.should_stop:
                    break
                    
                try:
                    current_listings = self.driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
                    if i >= len(current_listings):
                        break
                    
                    listing_row = current_listings[i]
                    
                    try:
                        link_tag = listing_row.find_element(By.CSS_SELECTOR, "a.classifiedTitle")
                    except:
                        continue
                    
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                        link_tag
                    )
                    time.sleep(random.uniform(0.3, 0.7))
                    
                    ActionChains(self.driver).key_down(Keys.CONTROL).click(link_tag).key_up(Keys.CONTROL).perform()
                    time.sleep(2)
                    
                    if len(self.driver.window_handles) < 2:
                        continue
                    
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "classifiedDetailTitle"))
                        )
                    except:
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        continue
                    
                    vehicle_data = self._extract_listing_details()
                    vehicle_data["marka"] = brand
                    vehicle_data["model"] = model
                    vehicle_data["category"] = category_name
                    vehicle_data["scraped_at"] = datetime.utcnow()
                    
                    if vehicle_data.get("fiyat", 0) > 0:
                        is_new = db.upsert_vehicle(vehicle_data)
                        self.total_scraped += 1
                        category_scraped += 1
                        if is_new:
                            self.new_listings += 1
                            category_new += 1
                        
                        status = "🆕" if is_new else "🔄"
                        print(f"  {status} {vehicle_data.get('baslik', '-')[:40]}... - {vehicle_data.get('fiyat', 0):,} ₺")
                        
                        self._update_status(
                            message=f"{brand} {model}: {self.total_scraped} ilan çekildi"
                        )
                    
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    while len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            
            # Sonraki sayfa
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                next_buttons = self.driver.find_elements(By.CSS_SELECTOR, "a[title='Sonraki']")
                if next_buttons and next_buttons[0].is_displayed():
                    next_buttons[0].click()
                    print("➡️ Sonraki sayfaya geçiliyor...")
                    time.sleep(random.uniform(5, 8))
                    page_number += 1
                else:
                    print("✅ Son sayfaya ulaşıldı")
                    break
            except:
                break
        
        print(f"\n📊 Kategori Özeti: {category_scraped} ilan tarandı, {category_new} yeni eklendi")
    
    def run(self, categories: list = None, brands: list = None):
        """Scraper'ı çalıştır"""
        print("\n" + "="*60)
        print("🤖 EkerGallery Scraper Başlatılıyor")
        print(f"⏰ Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self._update_status(message="Scraper başlatılıyor...", progress_percent=0)
        
        try:
            self._create_driver()
            self._load_cookies()
            
            target_brands = list(brands) if brands else list(VEHICLE_CATEGORIES.keys())
            total_brands = len(target_brands)
            
            for brand_idx, brand_key in enumerate(target_brands):
                if self.should_stop:
                    break
                    
                if brand_key not in VEHICLE_CATEGORIES:
                    continue
                
                brand_info = VEHICLE_CATEGORIES[brand_key]
                brand_name = brand_info["display_name"]
                
                # İlerleme yüzdesi hesapla
                base_progress = 15 + int((brand_idx / total_brands) * 70)
                self._update_status(progress_percent=base_progress)
                
                models = list(brand_info["models"].items())
                total_models = len(models)
                
                for model_idx, (model_key, model_info) in enumerate(models):
                    if self.should_stop:
                        break
                        
                    if categories:
                        cat_id = f"{brand_key}_{model_key}"
                        if cat_id not in categories:
                            continue
                    
                    category_name = f"{brand_name} {model_info['name']}"
                    
                    # Model bazlı ilerleme
                    model_progress = base_progress + int((model_idx / total_models) * (70 / total_brands))
                    self._update_status(progress_percent=model_progress)
                    
                    try:
                        self.scrape_category(
                            category_url=model_info["url"],
                            category_name=category_name,
                            brand=brand_name,
                            model=model_info["name"]
                        )
                    except Exception as e:
                        print(f"❌ Kategori hatası: {e}")
                        self._update_status(message=f"Hata: {e}")
                        continue
                    
                    time.sleep(random.uniform(10, 20))
            
            self._save_cookies()
            
        except Exception as e:
            print(f"❌ Genel Hata: {e}")
            self._update_status(message=f"Hata: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🔌 Tarayıcı kapatıldı")
        
        self._update_status(
            message=f"Tamamlandı! {self.total_scraped} ilan, {self.new_listings} yeni",
            progress_percent=85
        )
        
        print("\n" + "="*60)
        print("✅ Scraping Tamamlandı!")
        print(f"📊 Toplam: {self.total_scraped} ilan, {self.new_listings} yeni eklendi")
        print("="*60)
    
    def stop(self):
        """Scraping'i durdur"""
        self.should_stop = True
        self._update_status(message="Durduruluyor...")


# ========================================
# CRON JOB ENTRY POINT
# ========================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='EkerGallery Scraper')
    parser.add_argument('--brands', nargs='+', help='Taranacak markalar')
    parser.add_argument('--headful', action='store_true', help='Görünür modda çalıştır')
    parser.add_argument('--proxy', action='store_true', help='Proxy kullan')
    
    args = parser.parse_args()
    
    scraper = VehicleScraper(
        headless=not args.headful,
        use_proxy=args.proxy
    )
    
    scraper.run(brands=args.brands)
