import undetected_chromedriver as uc
import shutil
import os

print("🛠️ TAMİRCİ: Sürücü (Driver) indiriliyor...")

# Sadece indirme yapıp kapatacak
options = uc.ChromeOptions()
options.add_argument("--headless=new")

# Versiyonu 144 olarak ayarladık
driver = uc.Chrome(options=options, version_main=144)

# --- DÜZELTİLEN KISIM ---
# Dosya yolunu standart Selenium komutuyla alıyoruz
driver_path = driver.service.path 

print("✅ Sürücü başarıyla indi!")
print(f"📍 Kaynak Yolu: {driver_path}")

# İndirilen dosyayı çalışma klasörüne 'chromedriver' adıyla kopyala
target_path = "./chromedriver"
shutil.copy(driver_path, target_path)

print(f"📦 Sürücü kopyalandı: {os.path.abspath(target_path)}")

driver.quit()
