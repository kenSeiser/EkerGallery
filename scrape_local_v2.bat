@echo off
echo Starting Local Scraper...
echo.
cd /d "%~dp0"

if exist venv_win\Scripts\activate.bat (
    call venv_win\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating...
    python -m venv venv_win
    call venv_win\Scripts\activate.bat
    pip install -r requirements.txt
)

echo.
echo Installing/Verifying dependencies...
pip install undetected-chromedriver pymongo requests selenium colorama -q

echo.
echo Running Scraper...
python services/scraper_v2.py

echo.
echo Scraper finished.
pause
