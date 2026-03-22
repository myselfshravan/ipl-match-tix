from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from .event import (
    send_push_notifications,
    send_all_notifications,
    fetch_event_details,
    store_event,
    get_last_stored_event,
    compare_events
)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:8080", "https://your-task-organizer.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


@app.route("/")
def home():
    return "Hello from Flask by shravan!"


@app.route("/ping", methods=["GET"])
def ping():
    timestamp = datetime.now().isoformat()
    print(f"[Cron] Ping received at {timestamp}")

    # Fetch latest event
    events = fetch_event_details()
    if not events:
        print("[Cron] No events found in API response")
        return {"status": "error", "message": "No events found", "timestamp": timestamp}, 200

    latest_event = events[0]  # Get the latest (furthest in future) event

    # Log event details
    print(
        f"[Cron] Latest upcoming event: {latest_event['team_1']} vs {latest_event['team_2']} on {latest_event['event_date']}")
    print(f"[Cron] Total upcoming events found: {len(events)}")

    # Get last stored event BEFORE storing new one (fix: was stored first, making comparison useless)
    stored_event = get_last_stored_event()

    # Compare events for notification
    if compare_events(latest_event, stored_event):
        notification_reason = "New event" if not stored_event else "Event change"
        print(f"[Cron] {notification_reason} detected: {latest_event['event_name']}")
        results = send_all_notifications(latest_event, events)

        # Store after comparison and notification
        store_success = store_event(latest_event)
        if not store_success:
            print("[Cron] Failed to store latest event in Firestore")

        return {
            "status": "new_event",
            "event": latest_event,
            "reason": notification_reason,
            "timestamp": timestamp,
            "stored": store_success,
            "notifications": results
        }, 200

    # Store even if no change (updates timestamp)
    store_success = store_event(latest_event)
    print("[Cron] No changes detected requiring notification")
    return {
        "status": "no_change",
        "timestamp": timestamp,
        "stored": store_success
    }, 200


@app.route("/notify", methods=["GET"])
def notify():
    timestamp = datetime.now().isoformat()
    print(f"[Notify] Triggered at {timestamp}")
    events = fetch_event_details()
    latest_event = events[0] if events else None
    results = send_all_notifications(latest_event, events) if latest_event else send_push_notifications()
    return jsonify({"status": "done", "timestamp": timestamp, "results": results}), 200


@app.route("/event", methods=["GET"])
def event():
    timestamp = datetime.now().isoformat()
    print(f"[Event] Triggered at {timestamp}")

    events = fetch_event_details()
    if events:
        # Store the latest event
        latest_event = events[0]
        store_success = store_event(latest_event)
        if not store_success:
            print("[Event] Failed to store event in Firestore")

    return jsonify({
        "status": "done",
        "timestamp": timestamp,
        "results": events,
        "stored": store_success if events else False
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
