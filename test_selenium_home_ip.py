import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By

options = uc.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--proxy-server=socks5://127.0.0.1:1080')

print('Starting Chrome...')
try:
    driver = uc.Chrome(options=options, version_main=144)
    
    print('Testing Proxy...')
    driver.get('https://ifconfig.me')
    print('Internal IP via Selenium:', driver.find_element(By.TAG_NAME, 'body').text.strip())
    
    print('Navigating to Sahibinden...')
    driver.get('https://www.sahibinden.com/tesla')
    time.sleep(15)
    print('Title:', driver.title)
    items = driver.find_elements(By.CLASS_NAME, 'searchResultsItem')
    print(f'Found {len(items)} items!')
    
    if len(items) == 0:
        print('Page Source Snippet:', driver.page_source[:1000])
        driver.save_screenshot('error.png')
        print('Screenshot saved to error.png')
        
    driver.quit()
except Exception as e:
    print(f'Error: {e}')
