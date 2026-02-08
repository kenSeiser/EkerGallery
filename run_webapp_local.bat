@echo off
echo Starting Local Web Application...
echo.
cd /d "%~dp0"

if not exist venv_win\Scripts\activate.bat (
    echo Virtual environment not found. Please run scrape_local_v2.bat first to set it up.
    pause
    exit /b
)

call venv_win\Scripts\activate.bat

echo.
echo Installing Flask if needed...
pip install flask pymongo python-dotenv -q

echo.
echo Starting Web Server on http://127.0.0.1:5000
echo (Press Ctrl+C to stop)
python app_v2.py

pause
