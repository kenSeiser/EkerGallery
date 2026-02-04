# ========================================
# EkerGallery - Aggressive Proxy Scraper
# ========================================
# 
# Veri alana kadar proxy'leri sürekli dener
# Proxy çalışmazsa yenisini dener
# ========================================

import time
import random
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proxy_manager import ProxyManager
from scraper_clean import EC2Scraper
from models.database import db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/aggressive_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AggressiveProxyScraper:
    """
    Veri alana kadar proxy'leri sürekli deneyen scraper
    Her başarısız denemede yeni proxy ile tekrar dener
    """
    
    def __init__(self, max_proxy_attempts: int = 50):
        self.max_proxy_attempts = max_proxy_attempts
        self.proxy_manager = ProxyManager()
        self.successful_proxies = []
        self.total_scraped = 0
        
    def find_bulk_proxies(self, target_count: int = 30):
        """Toplu proxy bul"""
        logger.info(f"🔍 {target_count} çalışan proxy aranıyor...")
        return self.proxy_manager.find_working_proxies(max_workers=30, max_proxies=target_count)
    
    def test_proxy_with_sahibinden(self, proxy: str) -> bool:
        """Proxy'nin Sahibinden'de çalışıp çalışmadığını test et"""
        logger.info(f"🧪 Proxy test ediliyor: {proxy}")
        
        try:
            scraper = EC2Scraper(headless=True, use_proxy=False)
            
            # Manuel proxy ayarla
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--lang=tr-TR")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-images")
            options.add_argument(f"--proxy-server=http://{proxy}")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            options.page_load_strategy = 'eager'
            
            driver = uc.Chrome(options=options, version_main=144)
            driver.set_page_load_timeout(60)
            
            # Sahibinden'e git
            driver.get("https://www.sahibinden.com/tesla-model-y?sorting=date_desc")
            time.sleep(random.uniform(5, 10))
            
            # İlan var mı kontrol et
            from selenium.webdriver.common.by import By
            listings = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
            
            driver.quit()
            
            if len(listings) > 0:
                logger.info(f"✅ Proxy çalışıyor! {len(listings)} ilan bulundu")
                return True
            else:
                logger.warning(f"❌ Proxy'de ilan bulunamadı")
                return False
                
        except Exception as e:
            logger.error(f"❌ Proxy test hatası: {e}")
            try:
                driver.quit()
            except:
                pass
            return False
    
    def find_working_proxy_for_sahibinden(self) -> str:
        """Sahibinden'de çalışan proxy bul"""
        logger.info("🔎 Sahibinden'de çalışan proxy aranıyor...")
        
        # Önce toplu proxy al
        proxies = self.find_bulk_proxies(target_count=50)
        
        if not proxies:
            logger.error("❌ Hiç proxy bulunamadı!")
            return None
        
        # Her proxy'yi Sahibinden'de test et
        for i, proxy in enumerate(proxies):
            logger.info(f"📊 Proxy {i+1}/{len(proxies)}: {proxy}")
            
            if self.test_proxy_with_sahibinden(proxy):
                self.successful_proxies.append(proxy)
                return proxy
            
            # Çok hızlı deneme yapma
            time.sleep(random.uniform(2, 5))
        
        return None
    
    def run_with_proxy_rotation(self, max_pages: int = 5, brands: list = None):
        """
        Ana çalıştırma fonksiyonu
        Veri alana kadar proxy'leri sürekli dener
        """
        logger.info("="*60)
        logger.info("🚀 AGGRESSIVE PROXY SCRAPER BAŞLIYOR")
        logger.info(f"📊 Max proxy denemesi: {self.max_proxy_attempts}")
        logger.info("="*60)
        
        # Her kategori için ayrı ayrı dene
        from config import VEHICLE_CATEGORIES
        
        if brands is None:
            brands = list(VEHICLE_CATEGORIES.keys())
        
        for brand_key in brands:
            if brand_key not in VEHICLE_CATEGORIES:
                continue
                
            brand_data = VEHICLE_CATEGORIES[brand_key]
            brand_name = brand_data["display_name"]
            
            for model_key, model_data in brand_data["models"].items():
                category_url = model_data["url"]
                model_name = model_data["name"]
                
                logger.info(f"\n{'='*50}")
                logger.info(f"📂 Kategori: {brand_name} {model_name}")
                logger.info(f"{'='*50}")
                
                # Bu kategori için veri alana kadar dene
                scraped = self._scrape_category_with_retry(
                    category_url=category_url,
                    category_name=f"{brand_name} {model_name}",
                    brand=brand_name,
                    model=model_name,
                    max_pages=max_pages
                )
                
                self.total_scraped += scraped
                
                # Kategoriler arası bekleme
                if scraped > 0:
                    logger.info(f"✅ {scraped} araç çekildi, sonraki kategoriye geçiliyor...")
                    time.sleep(random.uniform(30, 60))
                else:
                    logger.warning(f"⚠️ Bu kategoride veri alınamadı")
                    time.sleep(random.uniform(10, 20))
        
        logger.info("\n" + "="*60)
        logger.info(f"🏁 TAMAMLANDI! Toplam: {self.total_scraped} araç")
        logger.info("="*60)
    
    def _scrape_category_with_retry(self, category_url: str, category_name: str, 
                                     brand: str, model: str, max_pages: int) -> int:
        """
        Tek kategoriyi proxy rotasyonu ile çek
        Veri alana kadar farklı proxy'ler dener
        """
        # Proxy'leri al
        proxies = self.proxy_manager.fetch_proxies()
        random.shuffle(proxies)
        
        attempt = 0
        scraped_count = 0
        
        while attempt < self.max_proxy_attempts and scraped_count == 0:
            attempt += 1
            
            # Rastgele proxy seç
            if len(proxies) > 0:
                proxy = proxies[attempt % len(proxies)]
            else:
                logger.error("Proxy listesi boş!")
                break
            
            logger.info(f"🔄 Deneme {attempt}/{self.max_proxy_attempts} - Proxy: {proxy}")
            
            try:
                scraped_count = self._try_scrape_with_proxy(
                    proxy=proxy,
                    category_url=category_url,
                    category_name=category_name,
                    brand=brand,
                    model=model,
                    max_pages=max_pages
                )
                
                if scraped_count > 0:
                    logger.info(f"✅ Başarılı! {scraped_count} araç çekildi")
                    self.successful_proxies.append(proxy)
                    return scraped_count
                else:
                    logger.warning(f"❌ Bu proxy'de veri yok, başka deneniyor...")
                    
            except Exception as e:
                logger.error(f"❌ Hata: {e}")
            
            # Denemeler arası bekleme
            time.sleep(random.uniform(3, 8))
        
        return scraped_count
    
    def _try_scrape_with_proxy(self, proxy: str, category_url: str, 
                                category_name: str, brand: str, model: str,
                                max_pages: int) -> int:
        """Tek bir proxy ile scrape dene"""
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys
        from datetime import datetime
        
        driver = None
        scraped = 0
        
        try:
            # Chrome başlat
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--lang=tr-TR")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-images")
            options.add_argument("--mute-audio")
            options.add_argument(f"--proxy-server=http://{proxy}")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            options.page_load_strategy = 'eager'
            
            driver = uc.Chrome(options=options, version_main=144)
            driver.set_page_load_timeout(60)
            
            # Sayfaya git
            driver.get(category_url)
            time.sleep(random.uniform(8, 15))
            
            # İlanları bul
            listings = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
            
            if len(listings) == 0:
                driver.quit()
                return 0
            
            logger.info(f"📊 {len(listings)} ilan bulundu!")
            
            # İlanları işle (max 5 sayfa veya belirtilen)
            for page in range(min(max_pages, 3)):  # Hız için 3 sayfa ile sınırla
                listings = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
                
                for i in range(min(len(listings), 10)):  # Sayfa başına max 10 ilan
                    try:
                        current_listings = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
                        if i >= len(current_listings):
                            break
                        
                        listing_row = current_listings[i]
                        
                        try:
                            link_tag = listing_row.find_element(By.CSS_SELECTOR, "a.classifiedTitle")
                        except:
                            continue
                        
                        # Sayfayı elemana kaydır
                        driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                            link_tag
                        )
                        time.sleep(random.uniform(0.5, 1.5))
                        
                        # Yeni sekmede aç
                        ActionChains(driver).key_down(Keys.CONTROL).click(link_tag).key_up(Keys.CONTROL).perform()
                        time.sleep(random.uniform(3, 6))
                        
                        if len(driver.window_handles) < 2:
                            continue
                        
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(random.uniform(2, 4))
                        
                        # Detayları çek
                        vehicle_data = self._extract_details(driver)
                        vehicle_data.update({
                            "marka": brand,
                            "model": model,
                            "category": category_name,
                            "scraped_at": datetime.utcnow(),
                            "proxy_used": proxy
                        })
                        
                        # Kaydet
                        if vehicle_data.get("fiyat", 0) > 0:
                            is_new = db.upsert_vehicle(vehicle_data)
                            scraped += 1
                            status = "🆕" if is_new else "🔄"
                            logger.info(f"  {status} {vehicle_data.get('baslik', '-')[:40]}... - {vehicle_data.get('fiyat', 0):,} ₺")
                        
                        # Sekmeyi kapat
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(random.uniform(1, 3))
                        
                    except Exception as e:
                        logger.debug(f"İlan hatası: {e}")
                        try:
                            driver.switch_to.window(driver.window_handles[0])
                        except:
                            pass
                
                # Sonraki sayfa
                if page < max_pages - 1:
                    try:
                        next_btn = driver.find_element(By.CSS_SELECTOR, "a.prevNextBut[title='Sonraki']")
                        next_btn.click()
                        time.sleep(random.uniform(5, 10))
                    except:
                        break
            
            driver.quit()
            return scraped
            
        except Exception as e:
            logger.error(f"Scrape hatası: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            return 0
    
    def _extract_details(self, driver) -> dict:
        """İlan detaylarını çek"""
        from selenium.webdriver.common.by import By
        from config import SCRAPE_FIELDS
        
        data = {}
        
        try:
            # Başlık
            try:
                data["baslik"] = driver.find_element(
                    By.CSS_SELECTOR, "div.classifiedDetailTitle h1"
                ).text.strip()
            except:
                data["baslik"] = "Başlık Yok"
            
            # Fiyat
            try:
                price_el = driver.find_element(By.CSS_SELECTOR, "div.classifiedInfo > h3")
                price_text = price_el.text
                clean = ''.join(filter(str.isdigit, price_text.split('TL')[0]))
                data["fiyat"] = int(clean) if clean else 0
            except:
                data["fiyat"] = 0
            
            # Detay listesi
            try:
                detail_items = driver.find_elements(By.CSS_SELECTOR, "ul.classifiedInfoList li")
                for item in detail_items:
                    try:
                        label = item.find_element(By.TAG_NAME, "strong").text.strip()
                        value = item.find_element(By.TAG_NAME, "span").text.strip()
                        
                        if label in SCRAPE_FIELDS:
                            field_name = SCRAPE_FIELDS[label]
                        else:
                            field_name = label.lower().replace(" ", "_")
                        
                        if field_name == "yil":
                            clean = ''.join(filter(str.isdigit, str(value)))
                            data[field_name] = int(clean) if clean else 0
                        elif field_name == "km":
                            clean = ''.join(filter(str.isdigit, value))
                            data[field_name] = int(clean) if clean else 0
                        elif field_name != "fiyat":
                            data[field_name] = value
                    except:
                        continue
            except:
                pass
            
            # Konum
            try:
                location = driver.find_element(By.CSS_SELECTOR, "div.classifiedInfo h2").text.strip()
                data["konum_tam"] = location
                parts = [p.strip() for p in location.split("/")]
                if len(parts) >= 1:
                    data["il"] = parts[0]
                if len(parts) >= 2:
                    data["ilce"] = parts[1]
            except:
                pass
            
            data["url"] = driver.current_url
            
        except Exception as e:
            logger.error(f"Detay çekme hatası: {e}")
        
        return data


# Ana çalıştırma
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggressive Proxy Scraper')
    parser.add_argument('--pages', type=int, default=3, help='Kategori başına sayfa')
    parser.add_argument('--attempts', type=int, default=50, help='Max proxy denemesi')
    parser.add_argument('--brands', nargs='+', help='Belirli markalar')
    
    args = parser.parse_args()
    
    os.makedirs("logs", exist_ok=True)
    
    scraper = AggressiveProxyScraper(max_proxy_attempts=args.attempts)
    scraper.run_with_proxy_rotation(max_pages=args.pages, brands=args.brands)
