# Turtle Tracker Auto - GitHub Actions

Auto-update Google Sheets tiap jam 08:05 WIB (01:05 UTC) untuk 12 core saham Turtle BEI.

## Setup 1x:

1. Buat repo baru di GitHub, upload 2 file ini:
   - `turtle_tracker_daily.py`
   - `.github/workflows/turtle-tracker.yml`

2. Di repo > Settings > Secrets and variables > Actions > New repository secret:
   - Name: `GSHEETS_SERVICE_ACCOUNT_JSON`
     Value: paste isi file JSON service account kamu (copy semua isi file turtle-tracker-key.json)
   - Name: `GSHEETS_SHEET_ID`
     Value: ID Google Sheets kamu (dari URL)

3. Di Google Sheets, Share ke email service account (Editor)

4. Done! Tiap Senin-Jumat jam 08:05 WIB akan auto-run.
   Bisa juga run manual: Actions > Turtle Tracker Auto Update > Run workflow

## File:
- `turtle_tracker_daily.py` - script utama
- `signals_today.csv` - auto-generated tiap run (backup)
- Google Sheets LIVE_SIGNALS - auto-update

## Core 12 saham:
CUAN, BRPT, BRMS, PTRO, TPIA, DSSA, MAPA, WIFI, ISAT, MDKA, ESSA, INCO
Total return backtest v3: +845%, 61 trades, 92.3% ticker profit, avg +13.87% per trade