from flask import Flask, request, jsonify
from datetime import datetime
from .event import (
    send_push_notifications,
    fetch_event_details,
    store_event,
    get_last_stored_event,
    compare_events
)

app = Flask(__name__)


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
    print(f"[Cron] Latest upcoming event: {latest_event['team_1']} vs {latest_event['team_2']} on {latest_event['event_date']}")
    print(f"[Cron] Total upcoming events found: {len(events)}")
    
    # Always store the latest event
    store_success = store_event(latest_event)
    if not store_success:
        print("[Cron] Failed to store latest event in Firestore")
    
    # Get last stored event from Firestore for notification check
    stored_event = get_last_stored_event()
    
    # Check specifically for CSK match
    is_csk = latest_event.get('team_2') == "Chennai Super Kings"
    if is_csk:
        print("[Cron] Chennai Super Kings match detected!")
    
    # Compare events for notification
    if compare_events(latest_event, stored_event):
        notification_reason = "CSK match" if is_csk else "New event"
        print(f"[Cron] {notification_reason} detected: {latest_event['event_name']}")
        
        # Send notifications with event data
        send_push_notifications(latest_event)
        
        return {
            "status": "new_event",
            "event": latest_event,
            "reason": notification_reason,
            "timestamp": timestamp,
            "stored": store_success
        }, 200
    
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
    results = send_push_notifications()
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
