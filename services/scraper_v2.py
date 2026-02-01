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
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--password-store=basic")
        
        # Random window size
        win_size = random.choice(["1920,1080", "1366,768", "1536,864", "1440,900"])
        options.add_argument(f"--window-size={win_size}")
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=tr-TR")
        options.page_load_strategy = 'eager'
        
        # Her instance için benzersiz profil
        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # User Agent - Let uc handle it or random logic
        
        # Proxy
        if self.use_proxy:
            self.proxy = self._get_free_proxy()
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
                print(f"🎭 Proxy: {self.proxy}")
        
        # Driver oluştur
        driver_path = self.DRIVER_PATH if os.path.exists(self.DRIVER_PATH) else None
        
        # Try to use version_main=144 first, if fails, fallback to auto
        try:
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=driver_path,
                version_main=CHROME_VERSION
            )
        except Exception as e:
            print(f"⚠️ Driver init failed with version {CHROME_VERSION}, trying auto... Error: {e}")
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=driver_path
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
    
    def _human_scroll(self):
        """İnsan benzeri sayfa kaydırma simülasyonu"""
        try:
            # Rastgele scroll miktarları
            scroll_amounts = [300, 500, 700, 400, 600]
            for amount in random.sample(scroll_amounts, 3):
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
                time.sleep(random.uniform(0.5, 1.5))
            
            # Bazen yukarı kaydır (gerçek kullanıcı davranışı)
            if random.random() > 0.7:
                self.driver.execute_script("window.scrollBy(0, -200);")
                time.sleep(random.uniform(0.3, 0.8))
        except:
            pass
    

    def _bypass_bot_check(self) -> bool:
        """
        Sahibinden'in bot kontrolünü otomatik geç.
        BRUTE FORCE: Her şeyi tara, logla ve tıkla.
        """
        try:
            page_source = self.driver.page_source.lower()
            bot_keywords = ["basılı tutunuz", "press and hold", "robot", "doğrulama", "captcha", "unusual", "olağandışı"]
            if not any(k in page_source for k in bot_keywords):
                return False
            
            print("🚀 BRUTE FORCE DEBUG Başlatıldı!", flush=True)
            self.driver.save_screenshot("logs/live_1_initial.png")
            
            def scan_and_click_anything(prefix="main"):
                print(f"  🔍 [{prefix}] Tüm interaktif elementler taranıyor...", flush=True)
                
                # Tüm potansiyel butonlar
                elements = self.driver.find_elements(By.CSS_SELECTOR, "button, a, div[role='button'], span[class*='cb'], i[class*='cb']")
                print(f"    - Toplam {len(elements)} aday element bulundu.", flush=True)
                
                candidates = []
                for idx, elem in enumerate(elements):
                    try:
                        if not elem.is_displayed(): continue
                        
                        loc = elem.location
                        size = elem.size
                        aria = (elem.getAttribute('aria-label') or "").lower()
                        text = (elem.text or "").lower()
                        cls = (elem.getAttribute('class') or "").lower()
                        
                        # Sahibinden logosunu ele
                        if "sahibinden" in text or "sahibinden" in aria: continue
                        
                        # Element bilgisini logla
                        print(f"    [{idx}] Pos:({loc['x']},{loc['y']}) Size:{size['width']}x{size['height']} Text:'{text}' Aria:'{aria}' Class:'{cls}'", flush=True)
                        
                        # Puanlama (Sol tarafta ve küçük olanlar accessibility butonu olma adayıdır)
                        score = 0
                        if loc['x'] < 200: score += 50
                        if size['width'] < 100 and size['height'] < 100: score += 30
                        if any(x in aria or x in text or x in cls for x in ['access', 'cb', 'erişi', 'button']): score += 100
                        
                        if score > 0:
                            candidates.append({'elem': elem, 'score': score, 'id': idx})
                    except: continue

                # En yüksek puanlıları dene
                candidates.sort(key=lambda x: x['score'], reverse=True)
                for cand in candidates[:3]:
                    try:
                        print(f"    👉 Aday [{cand['id']}] deneniyor (Puan: {cand['score']})", flush=True)
                        self.driver.save_screenshot(f"logs/live_2_{prefix}_attempt_{cand['id']}.png")
                        actions = ActionChains(self.driver)
                        actions.move_to_element(cand['elem']).click().perform()
                        
                        # Tıkladıktan sonra barın çıkıp çıkmadığını 15sn izle
                        if monitor_bar_live(prefix, cand['id']):
                            return True
                    except: continue
                return False

            def monitor_bar_live(prefix, attempt_id, duration=15):
                print(f"    ⏱️ Bar/Onay bekleniyor...", flush=True)
                for s in range(1, duration + 1):
                    time.sleep(1)
                    if s % 5 == 0:
                        self.driver.save_screenshot(f"logs/live_3_{prefix}_att{attempt_id}_wait_{s}s.png")
                        print(f"      - {s}. saniye...", flush=True)
                
                # Onay barı kontrolü
                confirm_selectors = [".cb-lb", ".cb-lb-t", "#challenge-stage", "[class*='checkbox']", "button[type='submit']"]
                for sel in confirm_selectors:
                    try:
                        btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                        if btn.is_displayed():
                            print(f"    🎯 ONAY BULUNDU! ({sel})", flush=True)
                            self.driver.save_screenshot(f"logs/live_4_{prefix}_success.png")
                            btn.click()
                            time.sleep(5)
                            return True
                    except: continue
                return False

            # Ana sayfa ve Iframe'leri tara
            if scan_and_click_anything("main"): return True
            
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for i, frame in enumerate(iframes):
                try:
                    self.driver.switch_to.frame(i)
                    if scan_and_click_anything(f"iframe_{i}"):
                        self.driver.switch_to.default_content()
                        return True
                    self.driver.switch_to.default_content()
                except:
                    self.driver.switch_to.default_content()
                    continue

            return False
            
        except Exception as e:
            print(f"❌ Brute Force Error: {e}", flush=True)
            self.driver.switch_to.default_content()
            return False
    
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
            
            # Detay listesini parse et (Dinamik - Hepsini al)
            try:
                detail_items = self.driver.find_elements(
                    By.CSS_SELECTOR, "ul.classifiedInfoList li"
                )
                for item in detail_items:
                    try:
                        label = item.find_element(By.TAG_NAME, "strong").text.strip()
                        value = item.find_element(By.TAG_NAME, "span").text.strip()
                        
                        # Config'deki mapping varsa kullan, yoksa olduğu gibi kaydet (slugify ederek)
                        if label in SCRAPE_FIELDS:
                            field_name = SCRAPE_FIELDS[label]
                        else:
                            # "Motor Gücü" -> "motor_gucu"
                            field_name = label.lower().replace(" ", "_").replace("ç", "c").replace("ğ", "g").replace("ı", "i").replace("ö", "o").replace("ş", "s").replace("ü", "u")
                        
                        # Özel parse işlemleri
                        if field_name == "yil":
                            data[field_name] = self._parse_year(value)
                        elif field_name == "km":
                            data[field_name] = self._parse_km(value)
                        elif field_name == "motor_hacmi":
                            data[field_name] = int(''.join(filter(str.isdigit, value)) or 0)
                        elif field_name == "motor_gucu":
                            data[field_name] = int(''.join(filter(str.isdigit, value)) or 0)
                        elif field_name == "fiyat": # Bazen detayda da yazar
                            continue 
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
                data["konum_tam"] = location
                parts = [p.strip() for p in location.split("/")]
                
                if len(parts) >= 1:
                    data["il"] = parts[0]
                if len(parts) >= 2:
                    data["ilce"] = parts[1]
                if len(parts) >= 3:
                    data["mahalle"] = parts[2]
            except:
                pass
            
            # ========== HASAR BİLGİSİ (Boyalı/Değişen) ==========
            data["boyali_parcalar"] = []
            data["degisen_parcalar"] = []
            data["hasar_puani"] = 0
            
            try:
                # Sayfayı aşağı kaydır (hasar bilgisi genelde altta)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(0.5)
                
                # Tramer/Ekspertiz bölümünü bul
                damage_sections = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.classified-expert-report, div.damage-info, div.tramer-section, ul.expertiz-list"
                )
                
                for section in damage_sections:
                    section_text = section.text.lower()
                    
                    # Boyalı parçaları bul
                    if "boyalı" in section_text or "boyali" in section_text:
                        items = section.find_elements(By.CSS_SELECTOR, "li, span.part-name, div.part")
                        for item in items:
                            part_text = item.text.strip()
                            if part_text and "boyalı" in part_text.lower():
                                data["boyali_parcalar"].append(part_text)
                    
                    # Değişen parçaları bul
                    if "değişen" in section_text or "degisen" in section_text:
                        items = section.find_elements(By.CSS_SELECTOR, "li, span.part-name, div.part")
                        for item in items:
                            part_text = item.text.strip()
                            if part_text and "değişen" in part_text.lower():
                                data["degisen_parcalar"].append(part_text)
                
                # Alternatif: Tablo formatında hasar bilgisi
                try:
                    damage_table = self.driver.find_elements(By.CSS_SELECTOR, "table.damage-table tr, div.expertReport div")
                    for row in damage_table:
                        row_text = row.text.lower()
                        if "boyalı" in row_text or "boyali" in row_text:
                            data["boyali_parcalar"].append(row.text.strip())
                        elif "değişen" in row_text or "degisen" in row_text:
                            data["degisen_parcalar"].append(row.text.strip())
                except:
                    pass
                
                # Hasar Puanı Hesapla
                # Boyalı: +5 puan, Değişen: +15 puan (max 100)
                boyali_count = len(data["boyali_parcalar"])
                degisen_count = len(data["degisen_parcalar"])
                data["hasar_puani"] = min(100, (boyali_count * 5) + (degisen_count * 15))
                
                if data["hasar_puani"] > 0:
                    print(f"🔧 Hasar tespit: {boyali_count} boyalı, {degisen_count} değişen = {data['hasar_puani']} puan")
                    
            except Exception as e:
                print(f"⚠️ Hasar bilgisi çekilemedi: {e}")
            
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
        # İnsan benzeri yavaş yükleme bekleme
        time.sleep(random.uniform(8, 15))
        
        # Sayfayı yavaşça kaydır (insan davranışı)
        self._human_scroll()
        
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
            # Sayfa arası bekleme (5-12 saniye rastgele)
            time.sleep(random.uniform(5, 12))
            
            # CAPTCHA veya Engel kontrolü
            page_source = self.driver.page_source.lower()
            if "captcha" in page_source or "olağandışı" in page_source or "unusual" in page_source or "basılı tutunuz" in page_source or "robot" in page_source:
                self._update_status(message="⚠️ Bot tespiti! Bypass deneniyor...")
                print("⚠️ Bot tespiti! Bypass deneniyor...")
                
                # Önce bypass dene
                if self._bypass_bot_check():
                    print("✅ Bot kontrolü geçildi, devam ediliyor...")
                    time.sleep(random.uniform(3, 5))
                else:
                    # Bypass başarısız, bekleme yap
                    print("⚠️ Bypass başarısız, 60-90 saniye bekleniyor...")
                    wait_time = random.uniform(60, 90)
                    time.sleep(wait_time)
                    self.driver.refresh()
                    time.sleep(10)
                continue
            
            # İlan listesi
            listings = self.driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
            
            if len(listings) == 0:
                print("⚠️ İlan bulunamadı, beklenmedik durum!")
                try:
                    debug_time = int(time.time())
                    self.driver.save_screenshot(f"debug_screen_{debug_time}.png")
                    with open(f"debug_source_{debug_time}.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print(f"📸 Debug görüntü kaydedildi: debug_screen_{debug_time}.png")
                except:
                    pass
                print("⚠️ Sonraki kategoriye geçiliyor")
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
                    # Her ilan arası rastgele bekleme (3-8 saniye)
                    time.sleep(random.uniform(3, 8))
                    
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
        
        print(f"DEBUG: run called with brands={brands}")
        
        try:
            self._create_driver()
            self._load_cookies()
            
            target_brands = list(brands) if brands else list(VEHICLE_CATEGORIES.keys())
            print(f"DEBUG: target_brands={target_brands}")
            total_brands = len(target_brands)
            
            for brand_idx, brand_key in enumerate(target_brands):
                if self.should_stop:
                    break
                
                print(f"DEBUG: Checking brand {brand_key}")    
                if brand_key not in VEHICLE_CATEGORIES:
                    print(f"DEBUG: Skipping {brand_key} (not in config)")
                    continue
                
                brand_info = VEHICLE_CATEGORIES[brand_key]
                brand_name = brand_info["display_name"]
                
                # İlerleme yüzdesi hesapla
                base_progress = 15 + int((brand_idx / total_brands) * 70)
                self._update_status(progress_percent=base_progress)
                
                models = list(brand_info["models"].items())
                print(f"DEBUG: Found models for {brand_key}: {models}")
                total_models = len(models)
                
                for model_idx, (model_key, model_info) in enumerate(models):
                    if self.should_stop:
                        break
                        
                    if categories:
                        cat_id = f"{brand_key}_{model_key}"
                        if cat_id not in categories:
                            continue
                    
                    category_name = f"{brand_name} {model_info['name']}"
                    print(f"DEBUG: Processing {brand_key} {model_key} -> URL: {model_info['url']}")
                    
                    # Model bazlı ilerleme
                    model_progress = base_progress + int((model_idx / total_models) * (70 / total_brands))
                    self._update_status(progress_percent=model_progress)
                    
                    try:
                        # Check if method is scrape_category or _scrape_category
                        if hasattr(self, 'scrape_category'):
                            self.scrape_category(
                                category_url=model_info["url"],
                                category_name=category_name,
                                brand=brand_name,
                                model=model_info["name"]
                            )
                        elif hasattr(self, '_scrape_category'):
                            self._scrape_category(
                                category_url=model_info["url"],
                                category_name=category_name,
                                brand=brand_name,
                                model=model_info["name"]
                            )
                        else:
                            print("❌ Error: neither scrape_category nor _scrape_category found")
                            
                    except Exception as e:
                        print(f"❌ Kategori hatası: {e}")
                        import traceback
                        traceback.print_exc()
                        self._update_status(message=f"Hata: {e}")
                        continue
                    
                    time.sleep(random.uniform(10, 20))
            
            self._save_cookies()
            
        except Exception as e:
            print(f"❌ Genel Hata: {e}")
            import traceback
            traceback.print_exc()
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
    
    brands_to_scrape = [b.lower() for b in args.brands] if args.brands else None
    scraper.run(brands=brands_to_scrape)
