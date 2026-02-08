@echo off
REM ========================================
REM EkerGallery - Yerel Scraper Başlatıcı
REM ========================================
REM Bu script scraper'ı kendi bilgisayarınızda çalıştırır
REM Ev IP'niz kullanılacağı için engellenmezsiniz
REM ========================================

echo.
echo =============================================
echo    EkerGallery - Yerel Veri Cekme Araci
echo =============================================
echo.

cd /d "%~dp0"

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi!
    echo Lutfen Python yukleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python bulundu
echo.

REM Gerekli paketleri kontrol et
echo Gerekli paketler kontrol ediliyor...
pip install undetected-chromedriver selenium pymongo python-dotenv --quiet

echo.
echo [BASLIYOR] Scraper baslatiliyor...
echo [BILGI] Ev IP'niz kullanilacak - Engellenmeyeceksiniz
echo [BILGI] Tarayici penceresi acilacak, kapatmayin!
echo.
echo =============================================

REM Scraper'ı çalıştır (headful mod - tarayıcı görünür)
python services/scraper_v2.py --headful

echo.
echo =============================================
echo [TAMAMLANDI] Scraping islemi bitti!
echo Veriler MongoDB'ye kaydedildi.
echo =============================================
echo.
pause
