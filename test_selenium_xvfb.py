import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By

options = uc.ChromeOptions()
# options.add_argument('--headless') # Headless'i kaldırdık!
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--proxy-server=socks5://127.0.0.1:1080')
options.add_argument('--window-size=1920,1080')

print('Starting Chrome in XVFB (Real Window mode)...')
try:
    driver = uc.Chrome(options=options, version_main=144)
    print('Navigating to Sahibinden...')
    driver.get('https://www.sahibinden.com/tesla')
    time.sleep(15)
    print('Title:', driver.title)
    items = driver.find_elements(By.CLASS_NAME, 'searchResultsItem')
    print(f'Found {len(items)} items!')
    
    if len(items) == 0:
        print('Page Source length:', len(driver.page_source))
        if 'searchResultsItem' not in driver.page_source:
             print('Bot detection still active.')
    
    driver.quit()
except Exception as e:
    print(f'Error: {e}')
