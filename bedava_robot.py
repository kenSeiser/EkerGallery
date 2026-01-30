import sys
import requests
import random
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient

# --- AYARLAR ---
MONGO_URI = "mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?appName=ekerard"

# --- EMİR KOMUTA MERKEZİ (DİNAMİK AYARLAR) ---
# Eğer komutan (sen veya script) özel link verdiyse onu kullan, yoksa varsayılanı kullan.
if len(sys.argv) > 2:
    TARGET_URL = sys.argv[1]       # 1. Argüman: Link
    CATEGORY_NAME = sys.argv[2]    # 2. Argüman: Klasör Adı (Örn: vw_polo)
    print(f"🫡 EMİR ALINDI! Hedef: {CATEGORY_NAME}")
else:
    # Varsayılan (Test için)
    TARGET_URL = "https://www.sahibinden.com/opel-corsa?sorting=date_desc"
    CATEGORY_NAME = "opel_corsa_e"
    print("⚠️ Emir yok, varsayılan (Corsa) modunda çalışılıyor.")

def get_free_proxies():
    print("🌍 Bedava Proxy listesi çekiliyor...")
    try:
        response = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
        if response.status_code == 200:
            proxies = response.text.splitlines()
            print(f"✅ Toplam {len(proxies)} adet proxy bulundu.")
            return proxies
    except Exception as e:
        print(f"❌ Proxy listesi alınamadı: {e}")
    return []

def connect_db():
    try:
        client = MongoClient(MONGO_URI)
        db = client["sahibinden_data"]
        # DİKKAT: Veriler emirle gelen klasör ismine kaydedilecek!
        collection = db[CATEGORY_NAME] 
        return collection
    except: return None

def create_driver(proxy=None):
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--lang=tr-TR") 
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    # Sayfa yüklenmesi uzun sürerse hata vermesin
    options.page_load_strategy = 'eager' 

    if proxy:
        print(f"🎭 Maske Takılıyor: {proxy}")
        options.add_argument(f'--proxy-server={proxy}')
    
    driver = uc.Chrome(options=options, version_main=144)
    driver.set_page_load_timeout(60) 
    return driver

def main():
    proxies = get_free_proxies()
    random.shuffle(proxies)
    collection = connect_db()

    for proxy in proxies:
        driver = None
        try:
            print(f"\n🚀 Denenen IP: {proxy}")
            driver = create_driver(proxy)
            
            # --- 1. SIZMA TESTİ ---
            try:
                driver.get("https://www.sahibinden.com/")
                title = driver.title
                print(f"ℹ️ Sayfa Başlığı: {title}")
                
                if "Olağandışı" in title or "Access Denied" in driver.page_source:
                    raise Exception("IP Engelli")
                if "Sahibinden" not in title:
                    raise Exception("Site Yüklenemedi (Başlık Hatalı)")
                    
            except Exception as e:
                print(f"❌ Giriş Başarısız: {e}")
                driver.quit()
                continue

            print("✅ BAŞARILI! Siteye sızdık. Hedefe gidiliyor...")
            
            # --- 2. HEDEFE GİT VE VERİ ÇEK ---
            driver.get(TARGET_URL)
            
            # Liste yüklenene kadar bekle
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tr.searchResultsItem"))
                )
            except:
                print(f"⚠️ {CATEGORY_NAME} listesi yüklenemedi.")
                driver.quit()
                continue 
            
            listings = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
            print(f"📄 {len(listings)} ilan bulundu.")
            
            count = 0
            for row in listings:
                if count >= 5: break # Her seferde 5 tane çekip bırakır (Hızlı olsun diye)
                try:
                    # İlanın linkini al (DÜZELTME BURADA YAPILDI)
                    link_element = row.find_element(By.CSS_SELECTOR, "a.classifiedTitle")
                    ad_url = link_element.get_attribute("href")
                    title = link_element.text.strip()
                    price = row.find_element(By.CSS_SELECTOR, "div.classifiedInfo > h3").text.strip()
                    
                    # Veritabanı için veri paketi
                    car_data = {
                        "category": CATEGORY_NAME.replace("_", " ").title(), # Örn: vw_polo -> Vw Polo
                        "title": title,
                        "price": price,
                        "url": ad_url, # Artık doğru linki kaydediyor
                        "scraped_at": time.time()
                    }
                    
                    if collection is not None:
                        # Akıllı Kayıt (Varsa Güncelle, Yoksa Ekle)
                        collection.update_one(
                            {"url": ad_url},
                            {"$set": car_data},
                            upsert=True
                        )
                        print(f"💾 Kaydedildi: {title} - {price}")
                        count += 1
                except Exception as e: 
                    print(f"Hata: {e}")
                    pass
            
            print("🏁 Görev Tamamlandı. Robot dinlenmeye çekiliyor.")
            driver.quit()
            break 

        except Exception as e:
            print(f"⚠️ Genel Hata: {e}")
            if driver: driver.quit()
            continue

if __name__ == "__main__":
    main()
