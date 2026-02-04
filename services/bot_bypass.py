# ========================================
# EkerGallery - Bot Bypass Module
# ========================================
# 
# Sahibinden bot kontrolünü atlatmak için
# accessibility button + blue bar yöntemi
#
# Strateji:
# 1. "basılı tutunuz" metni tespit et
# 2. Sol taraftaki accessibility butonunu bul
# 3. Butona tıkla ve basılı tut
# 4. Mavi barın dolmasını bekle
# 5. Mavi bara tıkla
# ========================================

import time
import random
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger(__name__)


class BotBypass:
    """Sahibinden bot kontrolü bypass sınıfı"""
    
    # Bot kontrol anahtar kelimeleri
    BOT_KEYWORDS = [
        "basılı tutunuz",
        "basili tutunuz", 
        "tutunuz",
        "robot değilim",
        "robot degilim",
        "doğrulama",
        "verification",
        "captcha"
    ]
    
    def __init__(self, driver):
        self.driver = driver
        
    def _slow_random_delay(self, min_sec=1.5, max_sec=4.0):
        """Yavaş, insan benzeri rastgele bekleme"""
        delay = random.uniform(min_sec, max_sec)
        # Ekstra mikro-duraklamalar ekle
        delay += random.uniform(0.1, 0.5)
        time.sleep(delay)
        
    def _very_slow_delay(self, min_sec=3.0, max_sec=8.0):
        """Çok yavaş bekleme (kritik işlemler için)"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def detect_bot_control(self) -> bool:
        """Bot kontrol sayfası tespit et"""
        try:
            page_source = self.driver.page_source.lower()
            for keyword in self.BOT_KEYWORDS:
                if keyword.lower() in page_source:
                    logger.warning(f"🤖 Bot kontrolü tespit edildi: '{keyword}'")
                    return True
            return False
        except Exception as e:
            logger.error(f"Bot kontrol tespiti hatası: {e}")
            return False
    
    def _find_accessibility_button(self):
        """
        Sol taraftaki accessibility butonunu bul
        Bu genellikle "basılı tutunuz" yazısının solundaki simge
        """
        try:
            # Farklı olası selector'lar dene
            selectors = [
                # Accessibility icon - genellikle engelli simgesi
                "button[aria-label*='access']",
                "button[class*='access']",
                "div[class*='access'] button",
                "span[class*='access']",
                # Alternatif selector'lar
                ".captcha-accessibility",
                "[data-accessibility]",
                "button.accessibility-btn",
                # Genel buton arama (solda olan)
                ".verification-container button:first-child",
                ".captcha-wrapper button:first-of-type",
                # iframe içinde olabilir
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"✅ Accessibility butonu bulundu: {selector}")
                        return elements[0]
                except:
                    continue
            
            # XPath ile dene - solda olan herhangi bir buton
            try:
                # "basılı tutunuz" metnini içeren elementin yanındaki buton
                xpath_selectors = [
                    "//button[contains(@class, 'access')]",
                    "//*[contains(text(), 'tutunuz')]/preceding-sibling::button",
                    "//*[contains(text(), 'tutunuz')]/..//button",
                    "//div[contains(@class, 'captcha')]//button[1]",
                ]
                
                for xpath in xpath_selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, xpath)
                        if element:
                            logger.info(f"✅ Accessibility butonu XPath ile bulundu")
                            return element
                    except:
                        continue
            except:
                pass
                
            logger.warning("⚠️ Accessibility butonu bulunamadı")
            return None
            
        except Exception as e:
            logger.error(f"Accessibility buton arama hatası: {e}")
            return None
    
    def _find_blue_bar(self):
        """Sağ taraftaki mavi progress barını bul"""
        try:
            selectors = [
                # Progress bar selector'ları
                ".progress-bar",
                "[class*='progress']",
                ".blue-bar",
                "[class*='verification'] [class*='bar']",
                ".captcha-progress",
                "[role='progressbar']",
                # Div tabanlı bar
                "div[style*='background'][style*='blue']",
                "div[class*='fill']",
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"✅ Mavi bar bulundu: {selector}")
                        return elements[-1]  # Sonuncusu (sağdaki)
                except:
                    continue
            
            logger.warning("⚠️ Mavi bar bulunamadı")
            return None
            
        except Exception as e:
            logger.error(f"Mavi bar arama hatası: {e}")
            return None
    
    def _wait_for_bar_fill(self, bar_element, timeout=10):
        """Mavi barın dolmasını bekle"""
        try:
            logger.info("⏳ Mavi barın dolması bekleniyor...")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Bar'ın width değerini kontrol et
                    style = bar_element.get_attribute("style")
                    if style:
                        # width: 100% veya doluluk kontrolü
                        if "100%" in style or "width: 100" in style:
                            logger.info("✅ Bar tamamen doldu!")
                            return True
                    
                    # Alternatif olarak class değişimini kontrol et
                    class_attr = bar_element.get_attribute("class")
                    if class_attr and ("complete" in class_attr or "full" in class_attr):
                        logger.info("✅ Bar tamamlandı!")
                        return True
                        
                except:
                    pass
                
                time.sleep(0.3)  # 300ms aralıklarla kontrol
            
            # Timeout olduysa en azından biraz bekle
            logger.warning("⏱️ Bar dolma timeout, devam ediliyor...")
            return True
            
        except Exception as e:
            logger.error(f"Bar dolma bekleme hatası: {e}")
            return False
    
    def bypass_captcha(self) -> bool:
        """
        Ana bypass fonksiyonu
        Accessibility butonu + mavi bar yöntemi
        """
        logger.info("🔓 Bot bypass başlatılıyor...")
        
        try:
            # Adım 1: Yavaşça bekle
            self._very_slow_delay(2, 4)
            
            # Adım 2: Accessibility butonunu bul
            access_btn = self._find_accessibility_button()
            
            if not access_btn:
                logger.warning("Accessibility butonu bulunamadı, alternatif yöntem deneniyor...")
                # Alternatif: doğrudan "basılı tutunuz" elementine tıkla
                return self._alternative_bypass()
            
            # Adım 3: Butona tıkla (yavaşça)
            self._slow_random_delay(1, 2)
            
            actions = ActionChains(self.driver)
            
            # Mouse'u butona yavaşça götür
            actions.move_to_element(access_btn)
            actions.pause(random.uniform(0.5, 1.0))
            
            # Tıkla ve basılı tut
            logger.info("🖱️ Accessibility butonuna basılı tutuluyor...")
            actions.click_and_hold(access_btn)
            actions.perform()
            
            # Adım 4: Mavi barın dolmasını bekle
            self._slow_random_delay(0.5, 1.0)
            blue_bar = self._find_blue_bar()
            
            if blue_bar:
                self._wait_for_bar_fill(blue_bar, timeout=8)
            else:
                # Bar bulunamazsa sabit süre bekle
                logger.info("⏳ 5 saniye bekleniyor...")
                time.sleep(5)
            
            # Adım 5: Mouse'u bırak
            actions = ActionChains(self.driver)
            actions.release()
            actions.perform()
            
            self._slow_random_delay(0.5, 1.0)
            
            # Adım 6: Mavi bara tıkla
            if blue_bar:
                logger.info("🖱️ Mavi bara tıklanıyor...")
                self._slow_random_delay(0.3, 0.8)
                
                actions = ActionChains(self.driver)
                actions.move_to_element(blue_bar)
                actions.pause(random.uniform(0.2, 0.5))
                actions.click()
                actions.perform()
            
            # Adım 7: Sonucu bekle
            self._very_slow_delay(3, 5)
            
            # Hala bot kontrolü var mı?
            if self.detect_bot_control():
                logger.warning("⚠️ Bypass başarısız olmuş olabilir")
                return False
            
            logger.info("✅ Bot bypass başarılı!")
            return True
            
        except Exception as e:
            logger.error(f"Bypass hatası: {e}")
            return False
    
    def _alternative_bypass(self) -> bool:
        """
        Alternatif bypass yöntemi
        Doğrudan "basılı tutunuz" elementine uzun basma
        """
        logger.info("🔄 Alternatif bypass yöntemi deneniyor...")
        
        try:
            # "basılı tutunuz" veya benzer elementi bul
            selectors = [
                "//*[contains(text(), 'basılı')]",
                "//*[contains(text(), 'tutunuz')]",
                "//*[contains(text(), 'Basılı')]",
                "//button[contains(., 'basılı')]",
                "//div[contains(@class, 'hold')]",
            ]
            
            hold_element = None
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element and element.is_displayed():
                        hold_element = element
                        break
                except:
                    continue
            
            if not hold_element:
                logger.error("Basılı tutunuz elementi bulunamadı")
                return False
            
            # Uzun basma simülasyonu
            self._slow_random_delay(1, 2)
            
            actions = ActionChains(self.driver)
            actions.move_to_element(hold_element)
            actions.pause(random.uniform(0.3, 0.7))
            actions.click_and_hold(hold_element)
            actions.perform()
            
            # 5-7 saniye basılı tut
            hold_time = random.uniform(5, 7)
            logger.info(f"⏳ {hold_time:.1f} saniye basılı tutuluyor...")
            time.sleep(hold_time)
            
            # Bırak
            actions = ActionChains(self.driver)
            actions.release()
            actions.perform()
            
            self._very_slow_delay(3, 5)
            
            if self.detect_bot_control():
                return False
                
            logger.info("✅ Alternatif bypass başarılı!")
            return True
            
        except Exception as e:
            logger.error(f"Alternatif bypass hatası: {e}")
            return False
    
    def handle_bot_check(self, max_attempts=3) -> bool:
        """
        Bot kontrolü varsa bypass etmeye çalış
        max_attempts kadar deneme yapar
        """
        if not self.detect_bot_control():
            return True  # Bot kontrolü yok
        
        logger.warning("🤖 Bot kontrolü tespit edildi, bypass deneniyor...")
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Bypass denemesi {attempt}/{max_attempts}")
            
            if self.bypass_captcha():
                return True
            
            # Başarısızsa uzun bekle
            wait_time = random.uniform(30, 60) * attempt
            logger.info(f"⏳ {wait_time:.0f} saniye bekleniyor...")
            time.sleep(wait_time)
            
            # Sayfayı yenile
            try:
                self.driver.refresh()
                self._very_slow_delay(5, 10)
            except:
                pass
        
        logger.error("❌ Tüm bypass denemeleri başarısız!")
        return False
