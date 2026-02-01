
import undetected_chromedriver as uc
import time

try:
    print("Initializing Chrome...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    driver = uc.Chrome(options=options, version_main=144)
    print("Driver created.")
    
    driver.get("https://www.google.com")
    print(f"Title: {driver.title}")
    
    driver.quit()
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
