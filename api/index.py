from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests

app = Flask(__name__)

# Your webhook URL
WEBHOOK_URL = "https://webhook.site/d9417f71-3d2a-4a31-96c7-e8d03a78e1c9"

# Function to be triggered by cron
def cron_job():
    timestamp = datetime.now().isoformat()
    print(f"[Cron] Hitting webhook at {timestamp}")
    try:
        res = requests.post(WEBHOOK_URL, json={"message": "Cron triggered", "time": timestamp})
        print(f"[Cron] Webhook response: {res.status_code}")
    except Exception as e:
        print(f"[Cron] Error: {e}")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(cron_job, 'interval', minutes=5)
scheduler.start()

@app.route('/')
def home():
    return 'Flask with cron is running!'

if __name__ == '__main__':
    app.run(debug=True)
