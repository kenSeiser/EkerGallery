import subprocess
import sys
import time
import os

# Brand groups for parallel execution
groups = [
    ["tesla", "mercedes", "bmw"],
    ["volvo", "volkswagen", "opel"],
    ["fiat", "renault", "toyota", "honda"]
]

def run_scraper(brands):
    # Use the current python interpreter (from venv)
    cmd = [sys.executable, "-u", "services/scraper_v2.py", "--brands"] + brands + ["--headful"]
    print(f"🚀 Başlatılıyor: {brands}")
    # Using xvfb-run for each process might be needed if they don't share display
    # But we set up Xvfb on :99 globally? 
    # Let's verify if we need separate displays or shared.
    # Shared :99 usually works for multiple windows.
    return subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

procs = []
print(f"🤖 Paralel Scraping Başlatılıyor (3 Grup)...")

for i, group in enumerate(groups):
    p = run_scraper(group)
    procs.append(p)
    print(f"⏳ Grup {i+1} başladı, 10 saniye bekleniyor...")
    time.sleep(10)  # Start staggered to avoid CPU spike

print("✅ Tüm grupler başlatıldı. İşlemler devam ediyor...")

try:
    for p in procs:
        p.wait()
except KeyboardInterrupt:
    print("\n🛑 Durduruluyor...")
    for p in procs:
        p.terminate()
