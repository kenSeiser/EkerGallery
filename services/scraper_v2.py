# ========================================
# EkerGallery - Geli??mi?? Web Scraper v2.1
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
from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging
import re

# ??st dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    VEHICLE_CATEGORIES, SCRAPE_FIELDS, CHROME_VERSION,
    MAX_PAGES_PER_CATEGORY
)
from models.database import db


class VehicleScraper:
    """Sahibinden.com ara?? ilan?? scraper"""
    
    COOKIE_FILE = os.path.join(os.path.dirname(__file__), "..", "cookies.pkl")
    DRIVER_PATH = os.path.join(os.path.dirname(__file__), "..", "chromedriver")
    
    def __init__(self, headless: bool = True, use_proxy: bool = False, status_callback=None):
        """
        Args:
            headless: Headless modda ??al????t??r
            use_proxy: Proxy kullan
            status_callback: ??lerleme durumu callback fonksiyonu
        """
        self.headless = headless
        self.use_proxy = use_proxy
        self.driver = None
        self.proxy = None
        self.status_callback = status_callback
        self.should_stop = False
        
        # ZenRows API Key
        self.zenrows_api_key = os.getenv("ZENROWS_API_KEY")
        # ScraperAPI Key
        self.scraperapi_key = os.getenv("SCRAPERAPI_KEY")
        
        if self.zenrows_api_key:
            print("???? ZenRows API Key bulundu, bulut modu aktif.")
        if self.scraperapi_key:
            print("???? ScraperAPI Key bulundu, bulut modu aktif.")
        
        # ??lerleme takibi
        self.total_scraped = 0
        self.new_listings = 0
        self.current_brand = ""
        self.current_model = ""
        self.current_page = 0
    
    def _update_status(self, **kwargs):
        """Durum g??ncellemesi g??nder"""
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
    
    def _get_page_source_api(self, url: str) -> str:
        """Bulut Servisleri veya Ev IP'si (SOCKS5) ??zerinden sayfa kayna????n?? al"""
        
        # 0. EV IP'S?? (SOCKS5) - EN G??VENL?? VE ??CRETS??Z Y??NTEM
        # Laptop ??zerinden a????lan t??nel (localhost:1080) varsa bunu kullan
        try:
            self._update_status(message=f"Ev IP'si ??zerinden indiriliyor: {url[:30]}...")
            print(f"???? Ev IP'si K??pr??s?? (SOCKS5) deneniyor: {url}")
            proxies = {
                'http': 'socks5h://127.0.0.1:1080',
                'https': 'socks5h://127.0.0.1:1080'
            }
            # Ev IP'sinde genelde JS Render gerekmez ama Sahibinden i??in User-Agent ??nemlidir
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/'
            }
            response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
            if response.status_code == 200 and "searchResultsItem" in response.text:
                print("??? Ev IP'si ile ba??ar??yla indirildi!")
                return response.text
            else:
                print(f"?????? Ev IP'si ba??ar??s??z oldu (Status: {response.status_code}), bulut servislerine ge??iliyor...")
        except Exception as e:
            print(f"?????? Ev IP'si k??pr??s?? aktif de??il veya hata olu??tu: {e}")

        # 1. ScraperAPI Denemesi
        if self.scraperapi_key:
            # ... (mevcut ScraperAPI kodu buraya gelecek - zaten a??a????da var, sadece ak?????? bozmamak i??in ??zetledim)
            pass

        # ... (mevcut ZenRows kodu fallback olarak devam eder)
        
        # Orijinal mant?????? korumak i??in a??a????dakini ScraperAPI/ZenRows blo??u olarak kals??n
        # (ReplacementChunk i??inde hepsini tek seferde g??ncelleyelim)
        
        if self.scraperapi_key:
            try:
                params = {'api_key': self.scraperapi_key, 'url': url, 'render': 'true', 'country_code': 'tr'}
                print(f"???? ScraperAPI deneniyor...")
                response = requests.get('http://api.scraperapi.com', params=params, timeout=120)
                if response.status_code == 200: return response.text
            except: pass

        if self.zenrows_api_key:
            try:
                params = {'apikey': self.zenrows_api_key, 'url': url, 'js_render': 'true', 'proxy_country': 'tr'}
                print(f"???? ZenRows deneniyor...")
                response = requests.get('https://api.zenrows.com/v1/', params=params, timeout=120)
                if response.status_code == 200: return response.text
            except: pass
                
        return None

    def _get_free_proxy(self) -> str:
        """??cretsiz proxy al"""
        self._update_status(message="Proxy aran??yor...")
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
        self._update_status(message="Proxy bulunamad??, direkt ba??lant?? kullan??lacak")
        return None
    
    def _create_driver(self):
        """Chrome driver olu??tur"""
        self._update_status(message="Chrome ba??lat??l??yor...", progress_percent=5)
        
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
        
        # Her instance i??in benzersiz profil
        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # User Agent - Let uc handle it or random logic
        
        # Proxy
        if self.use_proxy:
            self.proxy = self._get_free_proxy()
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
                print(f"???? Proxy: {self.proxy}")
        
        # Driver olu??tur
        driver_path = self.DRIVER_PATH if os.path.exists(self.DRIVER_PATH) else None
        
        # Try to use version_main=144 first, if fails, fallback to auto
        try:
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=driver_path,
                version_main=CHROME_VERSION
            )
        except Exception as e:
            print(f"?????? Driver init failed with version {CHROME_VERSION}, trying auto... Error: {e}")
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=driver_path
            )

        self.driver.set_page_load_timeout(120)
        
        self._update_status(message="Chrome ba??lat??ld??", progress_percent=10)
        return self.driver
    
    def _load_cookies(self):
        """??erezleri y??kle"""
        self._update_status(message="??erezler y??kleniyor...")
        
        if not os.path.exists(self.COOKIE_FILE):
            print("?????? ??erez dosyas?? bulunamad??")
            return False
        
        try:
            # ??nce siteye git
            self.driver.get("https://www.sahibinden.com/favicon.ico")
            time.sleep(2)
            
            # ??erezleri y??kle
            with open(self.COOKIE_FILE, "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
            
            print("??? ??erezler y??klendi")
            self._update_status(message="??erezler y??klendi")
            self.driver.refresh()
            time.sleep(3)
            return True
        except Exception as e:
            print(f"??? ??erez y??kleme hatas??: {e}")
            return False
    
    def _save_cookies(self):
        """??erezleri kaydet"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.COOKIE_FILE, "wb") as f:
                pickle.dump(cookies, f)
            print("???? ??erezler kaydedildi")
        except:
            pass
    
    def _parse_price(self, price_text: str) -> int:
        """Fiyat metnini say??ya ??evir"""
        try:
            clean = ''.join(filter(str.isdigit, price_text.split('TL')[0]))
            return int(clean) if clean else 0
        except:
            return 0
    
    def _parse_km(self, km_text: str) -> int:
        """KM metnini say??ya ??evir"""
        try:
            clean = ''.join(filter(str.isdigit, km_text))
            return int(clean) if clean else 0
        except:
            return 0
    
    def _parse_year(self, year_text: str) -> int:
        """Y??l metnini say??ya ??evir"""
        try:
            clean = ''.join(filter(str.isdigit, str(year_text)))
            year = int(clean) if clean else 0
            return year if 1950 <= year <= 2030 else 0
        except:
            return 0
    
    def _human_scroll(self):
        """??nsan benzeri sayfa kayd??rma sim??lasyonu"""
        try:
            # Rastgele scroll miktarlar??
            scroll_amounts = [300, 500, 700, 400, 600]
            for amount in random.sample(scroll_amounts, 3):
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
                time.sleep(random.uniform(0.5, 1.5))
            
            # Bazen yukar?? kayd??r (ger??ek kullan??c?? davran??????)
            if random.random() > 0.7:
                self.driver.execute_script("window.scrollBy(0, -200);")
                time.sleep(random.uniform(0.3, 0.8))
        except:
            pass
    

    def _bypass_bot_check(self) -> bool:
        """
        Sahibinden'in bot kontrol??n?? otomatik ge??.
        BRUTE FORCE: Her ??eyi tara, logla ve t??kla.
        """
        try:
            page_source = self.driver.page_source.lower()
            bot_keywords = ["bas??l?? tutunuz", "press and hold", "robot", "do??rulama", "captcha", "unusual", "ola??and??????"]
            if not any(k in page_source for k in bot_keywords):
                return False
            
            print("???? BRUTE FORCE DEBUG Ba??lat??ld??!", flush=True)
            self.driver.save_screenshot("logs/live_1_initial.png")
            
            def scan_and_click_anything(prefix="main"):
                print(f"  ???? [{prefix}] T??m interaktif elementler taran??yor...", flush=True)
                
                # T??m potansiyel butonlar
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
                        
                        # Puanlama (Sol tarafta ve k??????k olanlar accessibility butonu olma aday??d??r)
                        score = 0
                        if loc['x'] < 200: score += 50
                        if size['width'] < 100 and size['height'] < 100: score += 30
                        if any(x in aria or x in text or x in cls for x in ['access', 'cb', 'eri??i', 'button']): score += 100
                        
                        if score > 0:
                            candidates.append({'elem': elem, 'score': score, 'id': idx})
                    except: continue

                # En y??ksek puanl??lar?? dene
                candidates.sort(key=lambda x: x['score'], reverse=True)
                for cand in candidates[:3]:
                    try:
                        print(f"    ???? Aday [{cand['id']}] deneniyor (Puan: {cand['score']})", flush=True)
                        self.driver.save_screenshot(f"logs/live_2_{prefix}_attempt_{cand['id']}.png")
                        actions = ActionChains(self.driver)
                        actions.move_to_element(cand['elem']).click().perform()
                        
                        # T??klad??ktan sonra bar??n ????k??p ????kmad??????n?? 15sn izle
                        if monitor_bar_live(prefix, cand['id']):
                            return True
                    except: continue
                return False

            def monitor_bar_live(prefix, attempt_id, duration=15):
                print(f"    ?????? Bar/Onay bekleniyor...", flush=True)
                for s in range(1, duration + 1):
                    time.sleep(1)
                    if s % 5 == 0:
                        self.driver.save_screenshot(f"logs/live_3_{prefix}_att{attempt_id}_wait_{s}s.png")
                        print(f"      - {s}. saniye...", flush=True)
                
                # Onay bar?? kontrol??
                confirm_selectors = [".cb-lb", ".cb-lb-t", "#challenge-stage", "[class*='checkbox']", "button[type='submit']"]
                for sel in confirm_selectors:
                    try:
                        btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                        if btn.is_displayed():
                            print(f"    ???? ONAY BULUNDU! ({sel})", flush=True)
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
            print(f"??? Brute Force Error: {e}", flush=True)
            self.driver.switch_to.default_content()
            return False
    
    def _extract_listing_details_soup(self, soup: BeautifulSoup, url: str) -> dict:
        """BeautifulSoup kullanarak ilan detaylar??n?? ??ek"""
        data = {"url": url}
        
        try:
            # Ba??l??k
            title_tag = soup.select_one("div.classifiedDetailTitle h1")
            data["baslik"] = title_tag.text.strip() if title_tag else "Ba??l??k Yok"
            
            # Fiyat
            price_tag = soup.select_one("div.classifiedInfo > h3")
            data["fiyat"] = self._parse_price(price_tag.text) if price_tag else 0
            
            # Detay listesi
            info_list = soup.select("ul.classifiedInfoList li")
            for item in info_list:
                try:
                    label_tag = item.find("strong")
                    value_tag = item.find("span")
                    if not label_tag or not value_tag: continue
                    
                    label = label_tag.text.strip()
                    value = value_tag.text.strip()
                    
                    if label in SCRAPE_FIELDS:
                        field_name = SCRAPE_FIELDS[label]
                    else:
                        field_name = label.lower().replace(" ", "_").replace("??", "c").replace("??", "g").replace("??", "i").replace("??", "o").replace("??", "s").replace("??", "u")
                    
                    if field_name == "yil":
                        data[field_name] = self._parse_year(value)
                    elif field_name == "km":
                        data[field_name] = self._parse_km(value)
                    elif field_name == "motor_hacmi" or field_name == "motor_gucu":
                        data[field_name] = int(''.join(filter(str.isdigit, value)) or 0)
                    else:
                        data[field_name] = value
                except: continue

            # Konum
            loc_tag = soup.select_one("div.classifiedInfo h2")
            if loc_tag:
                location = loc_tag.text.strip()
                data["konum_tam"] = location
                parts = [p.strip() for p in location.split("/")]
                if len(parts) >= 1: data["il"] = parts[0]
                if len(parts) >= 2: data["ilce"] = parts[1]
                if len(parts) >= 3: data["mahalle"] = parts[2]
            
            # Hasar Bilgisi (??zet)
            data["boyali_parcalar"] = []
            data["degisen_parcalar"] = []
            expert_text = soup.get_text().lower()
            if "boyal??" in expert_text or "de??i??en" in expert_text:
                # Basit bir puanlama (Soup ile detayl?? tabla parse etmek zor olabilir ama anahtar kelimelerden gidelim)
                data["hasar_puani"] = 10 if "boyal??" in expert_text else 0
                data["hasar_puani"] += 20 if "de??i??en" in expert_text else 0
            else:
                data["hasar_puani"] = 0
                
        except Exception as e:
            print(f"?????? Soup parsing hatas??: {e}")
            
        return data

    def _scrape_category_api(self, category_url: str, category_name: str, brand: str, model: str, max_pages: int = None):
        """ZenRows API ile kategori tara"""
        if self.should_stop: return
        if max_pages is None: max_pages = MAX_PAGES_PER_CATEGORY
        
        self.current_brand = brand
        self.current_model = model
        print(f"\n???? [API MODU] {category_name} taran??yor...")
        
        page_number = 1
        while page_number <= max_pages and not self.should_stop:
            url = f"{category_url}&pagingOffset={(page_number-1)*20}" if page_number > 1 else category_url
            html = self._get_page_source_api(url)
            if not html: break
            
            soup = BeautifulSoup(html, 'html.parser')
            listings = soup.select("tr.searchResultsItem")
            print(f"???? Sayfa {page_number}: {len(listings)} ilan bulundu")
            
            for item in listings:
                if self.should_stop: break
                try:
                    link_tag = item.select_one("a.classifiedTitle")
                    if not link_tag: continue
                    link = "https://www.sahibinden.com" + link_tag['href']
                    
                    # Detay sayfas??n?? ??ek
                    detail_html = self._get_page_source_api(link)
                    if not detail_html: continue
                    
                    detail_soup = BeautifulSoup(detail_html, 'html.parser')
                    vehicle_data = self._extract_listing_details_soup(detail_soup, link)
                    vehicle_data.update({
                        "marka": brand, "model": model, "category": category_name,
                        "scraped_at": datetime.utcnow()
                    })
                    
                    if vehicle_data.get("fiyat", 0) > 0:
                        is_new = db.upsert_vehicle(vehicle_data)
                        self.total_scraped += 1
                        if is_new: self.new_listings += 1
                        print(f"  {'????' if is_new else '????'} {vehicle_data.get('baslik', '-')[:40]}... - {vehicle_data.get('fiyat', 0):,} ???")
                except Exception as e:
                    print(f"?????? ??lan hatas??: {e}")
            
            page_number += 1
            time.sleep(1) # API modunda fazla beklemeye gerek yok, proxy rotasyonu var

    def _extract_listing_details(self) -> dict:
        """??lan detay sayfas??ndan verileri ??ek"""
        data = {}
        
        try:
            # Ba??l??k
            try:
                data["baslik"] = self.driver.find_element(
                    By.CSS_SELECTOR, "div.classifiedDetailTitle h1"
                ).text.strip()
            except:
                data["baslik"] = "Ba??l??k Yok"
            
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
                        
                        # Config'deki mapping varsa kullan, yoksa oldu??u gibi kaydet (slugify ederek)
                        if label in SCRAPE_FIELDS:
                            field_name = SCRAPE_FIELDS[label]
                        else:
                            # "Motor G??c??" -> "motor_gucu"
                            field_name = label.lower().replace(" ", "_").replace("??", "c").replace("??", "g").replace("??", "i").replace("??", "o").replace("??", "s").replace("??", "u")
                        
                        # ??zel parse i??lemleri
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
            
            # ========== HASAR B??LG??S?? (Boyal??/De??i??en) ==========
            data["boyali_parcalar"] = []
            data["degisen_parcalar"] = []
            data["hasar_puani"] = 0
            
            try:
                # Sayfay?? a??a???? kayd??r (hasar bilgisi genelde altta)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(0.5)
                
                # Tramer/Ekspertiz b??l??m??n?? bul
                damage_sections = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.classified-expert-report, div.damage-info, div.tramer-section, ul.expertiz-list"
                )
                
                for section in damage_sections:
                    section_text = section.text.lower()
                    
                    # Boyal?? par??alar?? bul
                    if "boyal??" in section_text or "boyali" in section_text:
                        items = section.find_elements(By.CSS_SELECTOR, "li, span.part-name, div.part")
                        for item in items:
                            part_text = item.text.strip()
                            if part_text and "boyal??" in part_text.lower():
                                data["boyali_parcalar"].append(part_text)
                    
                    # De??i??en par??alar?? bul
                    if "de??i??en" in section_text or "degisen" in section_text:
                        items = section.find_elements(By.CSS_SELECTOR, "li, span.part-name, div.part")
                        for item in items:
                            part_text = item.text.strip()
                            if part_text and "de??i??en" in part_text.lower():
                                data["degisen_parcalar"].append(part_text)
                
                # Alternatif: Tablo format??nda hasar bilgisi
                try:
                    damage_table = self.driver.find_elements(By.CSS_SELECTOR, "table.damage-table tr, div.expertReport div")
                    for row in damage_table:
                        row_text = row.text.lower()
                        if "boyal??" in row_text or "boyali" in row_text:
                            data["boyali_parcalar"].append(row.text.strip())
                        elif "de??i??en" in row_text or "degisen" in row_text:
                            data["degisen_parcalar"].append(row.text.strip())
                except:
                    pass
                
                # Hasar Puan?? Hesapla
                # Boyal??: +5 puan, De??i??en: +15 puan (max 100)
                boyali_count = len(data["boyali_parcalar"])
                degisen_count = len(data["degisen_parcalar"])
                data["hasar_puani"] = min(100, (boyali_count * 5) + (degisen_count * 15))
                
                if data["hasar_puani"] > 0:
                    print(f"???? Hasar tespit: {boyali_count} boyal??, {degisen_count} de??i??en = {data['hasar_puani']} puan")
                    
            except Exception as e:
                print(f"?????? Hasar bilgisi ??ekilemedi: {e}")
            
            data["url"] = self.driver.current_url
            
        except Exception as e:
            print(f"?????? Detay ??ekme hatas??: {e}")
        
        return data
    
    def scrape_category(self, category_url: str, category_name: str, brand: str, model: str, max_pages: int = None):
        """Kategori sayfas??n?? tara"""
        if self.should_stop:
            return
        
        if max_pages is None:
            max_pages = MAX_PAGES_PER_CATEGORY
        
        self.current_brand = brand
        self.current_model = model
        
        print(f"\n{'='*50}")
        print(f"???? Kategori: {category_name}")
        print(f"???? URL: {category_url}")
        print(f"{'='*50}")
        
        self._update_status(message=f"{brand} {model} taran??yor...")
        
        self.driver.get(category_url)
        # ??nsan benzeri yava?? y??kleme bekleme
        time.sleep(random.uniform(8, 15))
        
        # Sayfay?? yava????a kayd??r (insan davran??????)
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
            
            print(f"\n???? Sayfa {page_number}/{max_pages}")
            # Sayfa aras?? bekleme (5-12 saniye rastgele)
            time.sleep(random.uniform(5, 12))
            
            # CAPTCHA veya Engel kontrol??
            page_source = self.driver.page_source.lower()
            if "captcha" in page_source or "ola??and??????" in page_source or "unusual" in page_source or "bas??l?? tutunuz" in page_source or "robot" in page_source:
                self._update_status(message="?????? Bot tespiti! Bypass deneniyor...")
                print("?????? Bot tespiti! Bypass deneniyor...")
                
                # ??nce bypass dene
                if self._bypass_bot_check():
                    print("??? Bot kontrol?? ge??ildi, devam ediliyor...")
                    time.sleep(random.uniform(3, 5))
                else:
                    # Bypass ba??ar??s??z, bekleme yap
                    print("?????? Bypass ba??ar??s??z, 60-90 saniye bekleniyor...")
                    wait_time = random.uniform(60, 90)
                    time.sleep(wait_time)
                    self.driver.refresh()
                    time.sleep(10)
                continue
            
            # ??lan listesi
            listings = self.driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
            
            if len(listings) == 0:
                print("?????? ??lan bulunamad??, beklenmedik durum!")
                try:
                    debug_time = int(time.time())
                    self.driver.save_screenshot(f"debug_screen_{debug_time}.png")
                    with open(f"debug_source_{debug_time}.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print(f"???? Debug g??r??nt?? kaydedildi: debug_screen_{debug_time}.png")
                except:
                    pass
                print("?????? Sonraki kategoriye ge??iliyor")
                break
            
            print(f"???? {len(listings)} ilan bulundu")
            
            # Her ilan?? tara
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
                    # Her ilan aras?? rastgele bekleme (3-8 saniye)
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
                        
                        status = "????" if is_new else "????"
                        print(f"  {status} {vehicle_data.get('baslik', '-')[:40]}... - {vehicle_data.get('fiyat', 0):,} ???")
                        
                        self._update_status(
                            message=f"{brand} {model}: {self.total_scraped} ilan ??ekildi"
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
                    print("?????? Sonraki sayfaya ge??iliyor...")
                    time.sleep(random.uniform(5, 8))
                    page_number += 1
                else:
                    print("??? Son sayfaya ula????ld??")
                    break
            except:
                break
        
        print(f"\n???? Kategori ??zeti: {category_scraped} ilan tarand??, {category_new} yeni eklendi")
    
    def run(self, categories: list = None, brands: list = None):
        """Scraper'?? ??al????t??r"""
        print("\n" + "="*60)
        print("???? EkerGallery Scraper Ba??lat??l??yor")
        print(f"??? Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self._update_status(message="Scraper ba??lat??l??yor...", progress_percent=0)
        
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
                
                # ??lerleme y??zdesi hesapla
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
                    
                    # Model bazl?? ilerleme
                    model_progress = base_progress + int((model_idx / total_models) * (70 / total_brands))
                    self._update_status(progress_percent=model_progress)
                    
                    try:
                        # API Modu veya Selenium Modu se??imi
                        if self.zenrows_api_key:
                            self._scrape_category_api(
                                category_url=model_info["url"],
                                category_name=category_name,
                                brand=brand_name,
                                model=model_info["name"]
                            )
                        else:
                            # Eski Selenium Mant??????
                            self.scrape_category(
                                category_url=model_info["url"],
                                category_name=category_name,
                                brand=brand_name,
                                model=model_info["name"]
                            )
                            
                    except Exception as e:
                        print(f"??? Kategori hatas??: {e}")
                        import traceback
                        traceback.print_exc()
                        self._update_status(message=f"Hata: {e}")
                        continue
                    
                    time.sleep(random.uniform(10, 20))
            
            self._save_cookies()
            
        except Exception as e:
            print(f"??? Genel Hata: {e}")
            import traceback
            traceback.print_exc()
            self._update_status(message=f"Hata: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                print("\n???? Taray??c?? kapat??ld??")
        
        self._update_status(
            message=f"Tamamland??! {self.total_scraped} ilan, {self.new_listings} yeni",
            progress_percent=85
        )
        
        print("\n" + "="*60)
        print("??? Scraping Tamamland??!")
        print(f"???? Toplam: {self.total_scraped} ilan, {self.new_listings} yeni eklendi")
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
    parser.add_argument('--headful', action='store_true', help='G??r??n??r modda ??al????t??r')
    parser.add_argument('--proxy', action='store_true', help='Proxy kullan')
    
    args = parser.parse_args()
    
    scraper = VehicleScraper(
        headless=not args.headful,
        use_proxy=args.proxy
    )
    
    brands_to_scrape = [b.lower() for b in args.brands] if args.brands else None
    scraper.run(brands=brands_to_scrape)
