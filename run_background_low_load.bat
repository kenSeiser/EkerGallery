@echo off
REM ========================================
REM EkerGallery - Arkaplan Çaliştirici (Windows)
REM ========================================

cd /d "%~dp0"

mkdir logs 2>nul
echo [%DATE% %TIME%] Scraper baslatiliyor... >> logs\scraper.log

echo [BILGI] Scraper arkaplanda (Headless) baslatiliyor...
echo [BILGI] Veriler BULUT database'ine aktarilacak.
echo [BILGI] Loglar burada takip edilebilir: logs\scraper.log

REM Venv kontrol (Eger yoksa kurulumu hatirlat)
if not exist venv_win\Scripts\activate.bat (
    echo [UYARI] Windows sanal ortami bulunamadi!
    echo Lutfen once setup_windows_env.bat dosyasini calistirin.
    pause
    exit /b 1
)

call venv_win\Scripts\activate.bat

REM Low priority ve Log yonlendirmesi ile baslat
echo [%DATE% %TIME%] Scraper islemi basladi. >> logs\scraper.log
start /low /min cmd /c "python services/scraper_v2.py >> logs\scraper.log 2>&1"

echo.
echo [BAŞARILI] Scraper düşük öncelikli olarak başlatildi.
echo Veri akisini logs\scraper.log dosyasindan takip edebilirsiniz.
echo.


