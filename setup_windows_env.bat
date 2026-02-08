@echo off
echo ========================================
echo EkerGallery - Windows Ortam Kurulumu
echo ========================================

cd /d "%~dp0"

echo [1/3] Eski sanal ortam kalintilari temizleniyor...
if exist venv_win rmdir /s /q venv_win

echo [2/3] Yeni Windows sanal ortami olusturuluyor (venv_win)...
python -m venv venv_win
if errorlevel 1 (
    echo [HATA] Sanal ortam olusturulamadi! Python yuklu oldugundan emin olun.
    pause
    exit /b 1
)

echo [3/3] Gerekli paketler yukleniyor...
call venv_win\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install undetected-chromedriver selenium pymongo python-dotenv certifi setuptools beautifulsoup4 --quiet



echo.
echo ========================================
echo [BASSARILI] Windows ortami hazirlandi.
echo Artik run_background_low_load.bat calisabilir.
echo ========================================

