import sys
import requests
import random
import time
import os
import shutil
import tempfile # <-- YENİ SİLAHIMIZ (Her robota özel oda)
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient

# --- AYARLAR ---
MONGO_URI = "mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?appName=ekerard"
DRIVER_PATH = "./chromedriver" # <-- Tamirci ile indirdiğimiz dosya

if len(sys.argv) > 2:
    TARGET_URL = sys.argv[1]
    CATEGORY_NAME = sys.argv[2]
else:
    TARGET_URL = "https://www.sahibinden.com/opel-corsa?sorting=date_desc"
    CATEGORY_NAME = "opel_corsa_e"

def get_free_proxies():
    try:
        response = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
        if response.status_code == 200:
            return response.text.splitlines()
    except: pass
    return []

def connect_db():
    try:
        client = MongoClient(MONGO_URI)
        db = client["sahibinden_data"]
        return db[CATEGORY_NAME] 
    except: return None

def create_driver(proxy=None):
    options = uc.ChromeOptions()
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # --- KRİTİK ÇÖZÜM: HER ROBOTA ÖZEL PROFİL ---
    # Bu satır sayesinde robotlar birbirinin Chrome'unu çökertmez.
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    # ---------------------------------------------
    
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument("--lang=tr-TR") 
    options.page_load_strategy = 'eager' 

    if proxy:
        print(f"🎭 Maske Takılıyor: {proxy}")
        options.add_argument(f'--proxy-server={proxy}')
     
    # Tamirci'nin indirdiği dosyayı kullanıyoruz
    driver = uc.Chrome(
        options=options,
        driver_executable_path=DRIVER_PATH,
        version_main=144
    )
    
    driver.set_page_load_timeout(120) 
    return driver

def main():
    proxies = get_free_proxies()
    random.shuffle(proxies)
    collection = connect_db()
    if not proxies: proxies = [None]

    for proxy in proxies:
        driver = None
        try:
            print(f"\n🚀 Denenen IP: {proxy if proxy else 'Proxy Yok'}")
            driver = create_driver(proxy)
             
            # Sızma Testi
            try:
                driver.get("https://www.sahibinden.com/")
                time.sleep(5) 
                if "Just a moment" in driver.title: time.sleep(20)
                
                title = driver.title
                print(f"ℹ️ Başlık: {title}")
                 
                if "sahibinden" not in title.lower() and "www.sahibinden.com" not in title:
                    raise Exception("Giriş Başarısız")
            except Exception as e:
                print(f"❌ {e}")
                if driver: driver.quit()
                continue

            print("✅ BAŞARILI! Veri Çekiliyor...")
            driver.get(TARGET_URL)
            
            time.sleep(5)
            listings = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
            print(f"📄 {len(listings)} ilan bulundu.")
            
            for row in listings:
                try:
                    link = row.find_element(By.CSS_SELECTOR, "a.classifiedTitle").get_attribute("href")
                    if collection is not None:
                         collection.update_one({"url": link}, {"$set": {"url": link, "tarih": time.time()}}, upsert=True)
                         print(f"💾 Kaydedildi: {link}")
                except: pass
             
            if driver: driver.quit()
            break 

        except Exception as e:
            print(f"⚠️ Hata: {e}")
            if driver: driver.quit()
            continue

if __name__ == "__main__":
    main()
