from flask import Flask, request, jsonify
from datetime import datetime
from .event import send_push_notifications, fetch_event_details

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello from Flask by shravan!"


@app.route("/ping", methods=["POST"])
def ping():
    timestamp = datetime.now().isoformat()
    print(f"[Cron] Ping received at {timestamp}")
    return {"status": "pong", "timestamp": timestamp}, 200


@app.route("/notify", methods=["GET"])
def notify():
    timestamp = datetime.now().isoformat()
    print(f"[Notify] Triggered at {timestamp}")
    results = send_push_notifications()
    return jsonify({"status": "done", "timestamp": timestamp, "results": results}), 200


@app.route("/event", methods=["GET"])
def event():
    timestamp = datetime.now().isoformat()
    print(f"[Event] Triggered at {timestamp}")
    results = fetch_event_details()
    return jsonify({"status": "done", "timestamp": timestamp, "results": results}), 200


if __name__ == "__main__":
    app.run(debug=True)
