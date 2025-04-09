from flask import Flask, request
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello from Flask by shravan!"


@app.route("/ping", methods=["POST"])
def ping():
    timestamp = datetime.now().isoformat()
    print(f"[Cron] Ping received at {timestamp}")
    return {"status": "pong", "timestamp": timestamp}, 200


if __name__ == "__main__":
    app.run(debug=True)
