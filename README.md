# CS 220 Queue Monitor

Python script that monitors a Google Sheets-based student help queue and sends MacOS notifications when new requests arrive. 

Built this so that I can do other stuff instead of endlessly staring at the queue during office hours.

### Note
For ease of use and ensuring that the notification doesn't disappear when you're not looking:
- go to `System Settings` on your MacBook
- go to `Notifications`
- scroll down until you see `Script Editor`
- change notification type from `Banners` to `Alerts` so that the notification stays there unless closed. 

(Or don't ¯\\_(ツ)_/¯, i just think the notification is more useful as an Alert). 

## Prerequisites
- Python 3.x
- Google Cloud Console account
- Google Sheets API enabled
- MacOS system

## Usage
1. Clone this repository
```bash
git clone https://github.com/Mahir-2003/cs220-queue-monitor.git
python3 queue-monitor.py
