# ========================================
# EkerGallery - EC2 Scraper (Temiz Versiyon)
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
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from bot_bypass import BotBypass
from proxy_manager import proxy_manager

# Üst dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VEHICLE_CATEGORIES, SCRAPE_FIELDS, CHROME_VERSION, MAX_PAGES_PER_CATEGORY
from models.database import db

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EC2Scraper:
    """EC2'de çalışacak Sahibinden scraper"""
    
    COOKIE_FILE = os.path.join(os.path.dirname(__file__), "..", "cookies.pkl")
    
    def __init__(self, headless: bool = True, use_proxy: bool = False):
        self.headless = headless
        self.use_proxy = use_proxy
        self.driver = None
        self.bot_bypass = None
        self.current_proxy = None
        self.total_scraped = 0
        self.new_listings = 0
        
    def _create_driver(self):
        """Chrome driver oluştur - EC2 için optimize edilmiş"""
        logger.info("Chrome başlatılıyor...")
        
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        # EC2 için gerekli ayarlar
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=tr-TR")
        options.add_argument("--window-size=1920,1080")
        
        # Performans ayarları
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-images")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--mute-audio")
        options.add_argument("--no-first-run")
        
        # User Agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        # Proxy ayarı
        if self.use_proxy:
            proxy_info = proxy_manager.get_proxy_for_chrome()
            if proxy_info:
                self.current_proxy = proxy_info["proxy"]
                options.add_argument(proxy_info["chrome_arg"])
                logger.info(f"🌐 Proxy kullanılıyor: {self.current_proxy}")
            else:
                logger.warning("⚠️ Çalışan proxy bulunamadı, direkt bağlantı kullanılacak")
        
        options.page_load_strategy = 'eager'
        
        try:
            self.driver = uc.Chrome(
                options=options,
                version_main=CHROME_VERSION
            )
        except Exception as e:
            logger.warning(f"Chrome {CHROME_VERSION} başlatılamadı, otomatik sürüm deneniyor: {e}")
            self.driver = uc.Chrome(options=options)
        
        self.driver.set_page_load_timeout(120)
        self.bot_bypass = BotBypass(self.driver)
        logger.info("Chrome başlatıldı")
        return self.driver
    
    def _random_delay(self, min_sec=3, max_sec=8):
        """İnsan benzeri rastgele bekleme"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def _human_scroll(self):
        """İnsan benzeri sayfa kaydırma"""
        try:
            scroll_amounts = [300, 500, 700, 400, 600]
            for amount in random.sample(scroll_amounts, 3):
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
                time.sleep(random.uniform(0.5, 1.5))
            
            if random.random() > 0.7:
                self.driver.execute_script("window.scrollBy(0, -200);")
                time.sleep(random.uniform(0.3, 0.8))
        except:
            pass
    
    def _load_cookies(self):
        """Çerezleri yükle"""
        if not os.path.exists(self.COOKIE_FILE):
            logger.warning("Çerez dosyası bulunamadı")
            return False
        
        try:
            self.driver.get("https://www.sahibinden.com/favicon.ico")
            time.sleep(2)
            
            with open(self.COOKIE_FILE, "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
            
            logger.info("Çerezler yüklendi")
            self.driver.refresh()
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"Çerez yükleme hatası: {e}")
            return False
    
    def _save_cookies(self):
        """Çerezleri kaydet"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.COOKIE_FILE, "wb") as f:
                pickle.dump(cookies, f)
            logger.info("Çerezler kaydedildi")
        except:
            pass
    
    def _is_blocked(self) -> bool:
        """Bot engeli kontrolü"""
        if self.bot_bypass:
            return self.bot_bypass.detect_bot_control()
        try:
            page_source = self.driver.page_source.lower()
            blocked_keywords = ["captcha", "robot", "olağandışı", "unusual", "basılı tutunuz", "doğrulama"]
            return any(k in page_source for k in blocked_keywords)
        except:
            return False
    
    def _handle_bot_control(self) -> bool:
        """Bot kontrolü tespit edildiğinde bypass dene"""
        if not self._is_blocked():
            return True
        
        logger.warning("🤖 Bot kontrolü tespit edildi!")
        
        if self.bot_bypass:
            return self.bot_bypass.handle_bot_check(max_attempts=3)
        
        # Fallback: uzun bekle
        logger.info("⏳ 2-3 dakika bekleniyor...")
        time.sleep(random.uniform(120, 180))
        self.driver.refresh()
        self._random_delay(10, 15)
        return not self._is_blocked()
    
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
            
            # Detay listesi
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
                        else:
                            field_name = label.lower().replace(" ", "_").replace("ç", "c").replace("ğ", "g").replace("ı", "i").replace("ö", "o").replace("ş", "s").replace("ü", "u")
                        
                        if field_name == "yil":
                            data[field_name] = self._parse_year(value)
                        elif field_name == "km":
                            data[field_name] = self._parse_km(value)
                        elif field_name in ["motor_hacmi", "motor_gucu"]:
                            data[field_name] = int(''.join(filter(str.isdigit, value)) or 0)
                        elif field_name != "fiyat":
                            data[field_name] = value
                    except:
                        continue
            except:
                pass
            
            # Konum
            try:
                location = self.driver.find_element(
                    By.CSS_SELECTOR, "div.classifiedInfo h2"
                ).text.strip()
                data["konum_tam"] = location
                parts = [p.strip() for p in location.split("/")]
                
                if len(parts) >= 1:
                    data["il"] = parts[0]
                if len(parts) >= 2:
                    data["ilce"] = parts[1]
            except:
                pass
            
            data["url"] = self.driver.current_url
            
        except Exception as e:
            logger.error(f"Detay çekme hatası: {e}")
        
        return data
    
    def scrape_category(self, category_url: str, category_name: str, brand: str, model: str, max_pages: int = None):
        """Kategori sayfasını tara"""
        if max_pages is None:
            max_pages = MAX_PAGES_PER_CATEGORY
        
        logger.info(f"{'='*50}")
        logger.info(f"Kategori: {brand} {model}")
        logger.info(f"URL: {category_url}")
        logger.info(f"{'='*50}")
        
        self.driver.get(category_url)
        self._random_delay(8, 15)
        self._human_scroll()
        
        # Engel kontrolü - bypass mekanizması ile
        if not self._handle_bot_control():
            logger.error("Bot engeli aşılamadı, sonraki kategoriye geçiliyor")
            return
        
        page_number = 1
        while page_number <= max_pages:
            logger.info(f"Sayfa {page_number}/{max_pages}")
            self._random_delay(5, 10)
            
            listings = self.driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
            
            if len(listings) == 0:
                logger.warning("İlan bulunamadı!")
                break
            
            logger.info(f"{len(listings)} ilan bulundu")
            
            for i in range(len(listings)):
                try:
                    current_listings = self.driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
                    if i >= len(current_listings):
                        break
                    
                    listing_row = current_listings[i]
                    
                    try:
                        link_tag = listing_row.find_element(By.CSS_SELECTOR, "a.classifiedTitle")
                    except:
                        continue
                    
                    # Sayfayı o elemana kaydır
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                        link_tag
                    )
                    self._random_delay(0.5, 1)
                    
                    # Yeni sekmede aç
                    ActionChains(self.driver).key_down(Keys.CONTROL).click(link_tag).key_up(Keys.CONTROL).perform()
                    self._random_delay(3, 6)
                    
                    if len(self.driver.window_handles) < 2:
                        continue
                    
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self._random_delay(2, 4)
                    
                    # Detayları çek
                    vehicle_data = self._extract_listing_details()
                    vehicle_data.update({
                        "marka": brand,
                        "model": model,
                        "category": category_name,
                        "scraped_at": datetime.utcnow()
                    })
                    
                    # Kaydet
                    if vehicle_data.get("fiyat", 0) > 0:
                        is_new = db.upsert_vehicle(vehicle_data)
                        self.total_scraped += 1
                        if is_new:
                            self.new_listings += 1
                        
                        status = "🆕" if is_new else "🔄"
                        logger.info(f"  {status} {vehicle_data.get('baslik', '-')[:40]}... - {vehicle_data.get('fiyat', 0):,} ₺")
                    
                    # Sekmeyi kapat
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self._random_delay(2, 5)
                    
                except Exception as e:
                    logger.error(f"İlan hatası: {e}")
                    try:
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    except:
                        pass
            
            # Sonraki sayfa
            page_number += 1
            if page_number <= max_pages:
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.prevNextBut[title='Sonraki']")
                    next_btn.click()
                    self._random_delay(8, 15)
                    self._human_scroll()
                except:
                    logger.info("Sonraki sayfa bulunamadı")
                    break
        
        self._save_cookies()
    
    def run(self, categories: list = None, max_pages: int = None):
        """Tüm kategorileri tara"""
        try:
            self._create_driver()
            self._load_cookies()
            
            if categories is None:
                categories = list(VEHICLE_CATEGORIES.keys())
            
            for brand_key in categories:
                if brand_key not in VEHICLE_CATEGORIES:
                    continue
                
                brand_data = VEHICLE_CATEGORIES[brand_key]
                brand_name = brand_data["display_name"]
                
                for model_key, model_data in brand_data["models"].items():
                    category_url = model_data["url"]
                    model_name = model_data["name"]
                    category_name = f"{brand_name} {model_name}"
                    
                    self.scrape_category(
                        category_url=category_url,
                        category_name=category_name,
                        brand=brand_name,
                        model=model_name,
                        max_pages=max_pages
                    )
                    
                    # Kategoriler arası uzun bekleme
                    self._random_delay(30, 60)
            
            logger.info(f"{'='*50}")
            logger.info(f"TAMAMLANDI!")
            logger.info(f"Toplam: {self.total_scraped} araç")
            logger.info(f"Yeni: {self.new_listings} araç")
            logger.info(f"{'='*50}")
            
        except Exception as e:
            logger.error(f"Scraper hatası: {e}")
        finally:
            if self.driver:
                self.driver.quit()
    
    def close(self):
        if self.driver:
            self.driver.quit()


# Ana çalıştırma
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='EkerGallery Scraper')
    parser.add_argument('--headless', action='store_true', help='Headless modda çalıştır')
    parser.add_argument('--proxy', action='store_true', help='Free proxy kullan (Sahibinden için)')
    parser.add_argument('--pages', type=int, default=5, help='Kategori başına sayfa sayısı')
    parser.add_argument('--brands', nargs='+', help='Sadece belirli markalar (örn: tesla bmw)')
    
    args = parser.parse_args()
    
    # Logs klasörü
    os.makedirs("logs", exist_ok=True)
    
    scraper = EC2Scraper(headless=args.headless, use_proxy=args.proxy)
    scraper.run(categories=args.brands, max_pages=args.pages)

