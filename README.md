
# USC WebReg Auto

This repository contains simple automation scripts for USC course registration workflows. The scripts can automatically attempt registration and send notifications via ntfy when certain events occur.

## Scripts
- `auto_submit.py`: repeatedly attempts to submit registration (retries every ~40 seconds). Sends an ntfy notification on success.
- `notify_only.py`: monitors whether a `Closed` indicator is present; while `Closed` exists it checks every 5 minutes, and when `Closed` disappears it sends an ntfy notification.

## Requirements
- Python 3.8+
- A browser and matching WebDriver (e.g., Chrome + ChromeDriver)
- Python packages listed in `requirements.txt`

Install packages:
```bash
pip install -r requirements.txt
```

## Environment variables
The scripts read configuration from environment variables (or a `.env` file).

- `USC_USERNAME`, `USC_PASSWORD`: USC login credentials
- `USC_TERM`: target term (default: `Fall 2026`)
- `USC_BROWSER`: browser to use (`Chrome` default)
- `NTFY_TOPIC`: ntfy topic (default: `csci599`)
- `NTFY_URL`: full ntfy URL (overrides `NTFY_TOPIC` if set)

Example (PowerShell, temporary session):
```powershell
$env:USC_USERNAME = 'your_usc_user'
$env:USC_PASSWORD = 'your_usc_pass'
$env:NTFY_TOPIC = 'csci599'
python .\auto_submit.py
```

Or create a `.env` file in the project root (the scripts will auto-load it):
```
USC_USERNAME=your_usc_user
USC_PASSWORD=your_usc_pass
NTFY_TOPIC=csci599
```

## WebDriver (ChromeDriver)
Download the ChromeDriver that matches your Chrome version and place the executable on your system `PATH` or in the same directory as the scripts.

## ntfy mobile setup
1. Android: install the official `ntfy` app from Google Play. Add a subscription with the topic name (for example `csci599`) or use the full URL `https://ntfy.sh/csci599`.
2. iOS: install an ntfy-compatible client from the App Store (or a web push-capable client) and subscribe to the same topic.
3. Test a push locally:
```bash
curl -d "Test message" https://ntfy.sh/csci599
```

When successful, your phone will receive the ntfy notification.

## Run the scripts
```powershell
# Monitor only
python .\notify_only.py

# Automatic submit
python .\auto_submit.py
```

## Notes
- Make sure you comply with USC's terms of service when using automation. These scripts perform simple login and navigation; some pages may require manual handling of multi-factor authentication (Duo) or other interactive steps.
- Keep your credentials secure. Do not commit `.env` or credential files to public repositories.

---
Files: [requirements.txt](requirements.txt) | Scripts: [auto_submit.py](auto_submit.py), [notify_only.py](notify_only.py)
