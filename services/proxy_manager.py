# ========================================
# EkerGallery - Proxy Manager
# ========================================
# 
# Free proxy listelerinden proxy çeker ve
# çalışanları bulur
# ========================================

import requests
import random
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ProxyManager:
    """Free proxy yönetim sınıfı"""
    
    # Free proxy kaynakları
    PROXY_SOURCES = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    ]
    
    # Test URL (hızlı yanıt veren site)
    TEST_URL = "https://httpbin.org/ip"
    
    # Sahibinden test URL
    SAHIBINDEN_TEST_URL = "https://www.sahibinden.com/favicon.ico"
    
    def __init__(self):
        self.working_proxies = []
        self.failed_proxies = set()
        self.current_proxy = None
        
    def fetch_proxies(self) -> list:
        """Tüm kaynaklardan proxy listesi çek"""
        all_proxies = set()
        
        logger.info("📥 Proxy listeleri indiriliyor...")
        
        for source_url in self.PROXY_SOURCES:
            try:
                response = requests.get(source_url, timeout=10)
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and ':' in line:
                            # IP:PORT formatını çıkar
                            parts = line.split(':')
                            if len(parts) >= 2:
                                proxy = f"{parts[0]}:{parts[1]}"
                                all_proxies.add(proxy)
            except Exception as e:
                logger.debug(f"Kaynak hatası {source_url}: {e}")
                continue
        
        logger.info(f"📊 Toplam {len(all_proxies)} proxy bulundu")
        return list(all_proxies)
    
    def test_proxy(self, proxy: str, timeout: int = 8) -> bool:
        """Tek bir proxy'yi test et"""
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
        try:
            response = requests.get(
                self.TEST_URL,
                proxies=proxy_dict,
                timeout=timeout
            )
            if response.status_code == 200:
                return True
        except:
            pass
        return False
    
    def test_proxy_for_sahibinden(self, proxy: str, timeout: int = 15) -> bool:
        """Proxy'nin Sahibinden'e erişimini test et"""
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
        try:
            response = requests.get(
                self.SAHIBINDEN_TEST_URL,
                proxies=proxy_dict,
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            if response.status_code == 200:
                return True
        except:
            pass
        return False
    
    def find_working_proxies(self, max_workers: int = 20, max_proxies: int = 10) -> list:
        """Çalışan proxy'leri paralel olarak bul"""
        proxies = self.fetch_proxies()
        
        if not proxies:
            logger.warning("⚠️ Hiç proxy bulunamadı!")
            return []
        
        # Rastgele karıştır
        random.shuffle(proxies)
        
        # Önce hızlı bir pre-test yap
        logger.info(f"🔍 {min(len(proxies), 200)} proxy test ediliyor...")
        
        working = []
        tested = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # İlk 200 proxy'yi test et
            futures = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in proxies[:200]
            }
            
            for future in as_completed(futures):
                proxy = futures[future]
                tested += 1
                
                try:
                    if future.result():
                        # Sahibinden için de test et
                        if self.test_proxy_for_sahibinden(proxy):
                            working.append(proxy)
                            logger.info(f"✅ Çalışan proxy bulundu: {proxy}")
                            
                            if len(working) >= max_proxies:
                                break
                except:
                    pass
        
        logger.info(f"📊 {tested} test edildi, {len(working)} çalışan proxy bulundu")
        
        self.working_proxies = working
        return working
    
    def get_proxy(self) -> str:
        """Çalışan bir proxy döndür"""
        if not self.working_proxies:
            self.find_working_proxies()
        
        if not self.working_proxies:
            logger.warning("⚠️ Kullanılabilir proxy yok!")
            return None
        
        # Daha önce başarısız olmamış birini seç
        available = [p for p in self.working_proxies if p not in self.failed_proxies]
        
        if not available:
            # Hepsini sıfırla ve tekrar dene
            self.failed_proxies.clear()
            available = self.working_proxies
        
        if available:
            self.current_proxy = random.choice(available)
            return self.current_proxy
        
        return None
    
    def mark_failed(self, proxy: str = None):
        """Proxy'yi başarısız olarak işaretle"""
        if proxy is None:
            proxy = self.current_proxy
        
        if proxy:
            self.failed_proxies.add(proxy)
            logger.warning(f"❌ Proxy başarısız: {proxy}")
            
            # Listeden çıkar
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
    
    def get_proxy_for_chrome(self) -> dict:
        """Chrome için proxy ayarları döndür"""
        proxy = self.get_proxy()
        
        if not proxy:
            return None
        
        return {
            "proxy": proxy,
            "chrome_arg": f"--proxy-server=http://{proxy}"
        }
    
    def refresh_proxies(self):
        """Proxy listesini yenile"""
        logger.info("🔄 Proxy listesi yenileniyor...")
        self.failed_proxies.clear()
        self.working_proxies.clear()
        self.find_working_proxies()


# Singleton instance
proxy_manager = ProxyManager()


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    pm = ProxyManager()
    working = pm.find_working_proxies(max_proxies=5)
    
    print("\n" + "="*50)
    print("Çalışan Proxy'ler:")
    for p in working:
        print(f"  - {p}")
    print("="*50)
