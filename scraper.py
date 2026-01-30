import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
import time
import random
import os
import pickle

# --- AYARLAR ---
MONGO_URI = "mongodb+srv://ekerard_db_user:Ekerard123@ekerard.vthareu.mongodb.net/?appName=ekerard"

TARGET_URLS = [
    {"category": "VW Polo",    "url": "https://www.sahibinden.com/volkswagen-polo"},
    {"category": "Fiat Doblo", "url": "https://www.sahibinden.com/fiat-doblo"},
]

def connect_db():
    try:
        client = MongoClient(MONGO_URI)
        db = client["sahibinden_data"]
        collection = db["tum_araclar"] 
        print("MongoDB connected.")
        return collection
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        return None

def main():
    collection = connect_db()
    if collection is None: return

    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-first-run")
    options.add_argument("--lang=tr-TR") 
    
    # EKRAN HATASINI ÇÖZEN AYAR 👇
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    
    options.page_load_strategy = 'normal' 
    
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")

    print("Launching Undetected Chrome (Version 144 + Fixed Resolution)...")
    
    # Versiyon 144'te sabit kalmaya devam ediyoruz
    driver = uc.Chrome(options=options, version_main=144)
    
    # ❌ driver.maximize_window() <--- BU SATIRI SİLDİK, HATA BURADAYDI

    try:
        print("----------------------------------------------------------------")
        print("🤖 AWS ROBOT BAŞLATILIYOR")
        print("----------------------------------------------------------------")
        
        # 1. ÇEREZ YÜKLEME
        try:
            driver.get("https://www.sahibinden.com/favicon.ico") 
            time.sleep(3)
        except: pass

        cookie_file = "cookies.pkl"
        if os.path.exists(cookie_file):
            print(f"🍪 '{cookie_file}' bulundu, yükleniyor...")
            try:
                with open(cookie_file, "rb") as file:
                    cookies = pickle.load(file)
                    for cookie in cookies:
                        try: driver.add_cookie(cookie)
                        except: pass
                print("✅ Çerezler yüklendi! Sayfa yenileniyor...")
                driver.refresh()
                time.sleep(3)
                driver.get("https://www.sahibinden.com/")
                time.sleep(5)
            except Exception as e:
                print(f"⚠️ Çerez hatası: {e}")
        else:
            print("⚠️ UYARI: cookies.pkl yok!")
            driver.get("https://www.sahibinden.com/")
            time.sleep(10)
        
        # 2. TARAMA DÖNGÜSÜ
        for target in TARGET_URLS:
            kategori_adi = target["category"]
            link = target["url"]
            
            print(f"\n>>> KATEGORİ TARANIYOR: {kategori_adi}")
            driver.get(link)
            time.sleep(random.uniform(5, 8)) 

            page_number = 1
            while True: 
                print(f"--- {kategori_adi} | Sayfa {page_number} ---")
                time.sleep(random.uniform(3, 6))
                
                listings = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
                if len(listings) == 0:
                     print("⚠️ İlan bulunamadı.")
                     if "captcha" in driver.page_source.lower():
                         print("!!! CAPTCHA ÇIKTI !!!")
                         time.sleep(120)
                         driver.refresh()
                         continue
                     else:
                          print("Bitti.")
                          break

                print(f"Bu sayfada {len(listings)} ilan var.")
                for i in range(len(listings)):
                    try:
                        current_listings = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")
                        if i >= len(current_listings): break
                        
                        listing_row = current_listings[i]
                        try: link_tag = listing_row.find_element(By.CSS_SELECTOR, "a.classifiedTitle")
                        except: continue
                        
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link_tag)
                        time.sleep(random.uniform(0.5, 1.0))
                        
                        ActionChains(driver).key_down(Keys.CONTROL).click(link_tag).key_up(Keys.CONTROL).perform()
                        time.sleep(3)
                        
                        if len(driver.window_handles) < 2: continue
                        driver.switch_to.window(driver.window_handles[-1])
                        
                        try: WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "classifiedDetailTitle")))
                        except:
                            if len(driver.window_handles) > 1: driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            continue
                        
                        try: title = driver.find_element(By.CSS_SELECTOR, "div.classifiedDetailTitle h1").text
                        except: title = "Başlık Yok"
                        try: price = driver.find_element(By.CSS_SELECTOR, "div.classifiedInfo > h3").text.strip()
                        except: price = "0"
                        
                        details = {}
                        try:
                            for item in driver.find_elements(By.CSS_SELECTOR, "ul.classifiedInfoList li"):
                                l = item.find_element(By.TAG_NAME, "strong").text.strip()
                                v = item.find_element(By.TAG_NAME, "span").text.strip()
                                details[l] = v
                        except: pass
                        
                        filter_query = {"url": driver.current_url}
                        car_data = {
                            "category": kategori_adi, "title": title, "price": price, 
                            "year": details.get("Yıl", "N/A"), "km": details.get("KM", "0"),
                            "details": details, "url": driver.current_url, "scraped_at": time.time()
                        }
                        collection.update_one(filter_query, {"$set": car_data}, upsert=True)
                        print(f"✅ {title} - {price}")
                        
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(random.uniform(1.5, 3))
                    except:
                        while len(driver.window_handles) > 1:
                            driver.switch_to.window(driver.window_handles[-1])
                            driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    next_btns = driver.find_elements(By.CSS_SELECTOR, "a[title='Sonraki']")
                    if len(next_btns) > 0 and next_btns[0].is_displayed():
                        next_btns[0].click()
                        print(">>> Diğer sayfaya geçiliyor...")
                        time.sleep(random.uniform(6, 10))
                        page_number += 1
                    else:
                        print("Bitti.")
                        break
                except: break
            
    except Exception as e:
        print(f"Genel Hata: {e}")
    finally:
        print("Tarayıcı kapatılıyor.")
        driver.quit()

if __name__ == "__main__":
    main()
