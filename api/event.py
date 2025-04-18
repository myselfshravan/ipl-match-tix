import firebase_admin
from firebase_admin import credentials, messaging, firestore
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

service_account_info = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
}

# Initialize Firebase App (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

tokens = [
    "fT04LaZzayopUX6gdVRkDi:APA91bH6Wl2Rw0I6aOTnh9aKmJk5FFzjdKJ7ZOKgGWy-b5Uwzp9U9A7RRnXSpM5chGpZa0jLv2Aeyqp_AJ-5fBrhaZGtRoxFBDDf9-1qMXiJQlAtd-lFnrE",
    "dftG_SJkzxP8zgVwSqpsLH:APA91bFiG9Mz8S0xaigCu4cx9HJxJuRJzRtJnx0QwhnOu3b9im2Mx5O6fy7jp5UNle1geweU9UNuU8X6Sh11tVFZX5rlgTC1HAvCoH2cUbAQVG1vVMlHKFQ",
    "eZ6l27Fw9Amw-r0OewG0aN:APA91bErHZ9Dy0Lw51jRvZjaynMno35H-QNwLzQDAUbQsmF9qIScApnXFIJjJQev5F7pAkjCMs5lFL-2hfDVGovDRMYPnVxNwyC7O8GmLIxRZpRPF9KNGM0",
    "f17IYE3SbSR8FsZ2_eshEL:APA91bGHVa7m1ATN9zMccyTc55MBsgC7KDyRzFVhtThgmZRC6YRD_CtVYsM7dRaEIFDJu5GGr7C-fGgDIO4m5_UqJcGcPqKHl3eEMy_vxFq8YhaNiYyPYp0",
    "foX0_uMYimJtMV8wJ4Fehq:APA91bEHnrlGbcY8HBoV9ItT5TU_nuEqd69dKCbC-XhKM9ovrNNovD-Zwodh1xUoijZLpYVMv7YpfVgxfFPS08FPkmuG-fmA6j3Vr7Npw-w24gMKeOdd6WY",
    "eHSm0QsG3C52uaMUBlWjvv:APA91bHCTEuE9dPxHy-3SecQjf2N-IEGc38mPjpsuFt6uJ2JFin0-c93oRYPeIdiH2JA8ia-ofMnnKI40lVJEMfiU55fsP3cemB-YlhK6lI78d7sDJ5bgPg"
]


def send_push_notifications(event_data=None):
    results = []
    for new_token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title="🎫 New IPL Match Available! (Test)",
                body=f"{event_data['team_1']} vs {event_data['team_2']} at {event_data['venue']}" if event_data else "New event available! (Test)",
            ),
            token=new_token,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title="🏏 IPL Match Tickets Alert!",
                    body=f"Tickets for {event_data['team_1']} vs {event_data['team_2']} on {event_data['event_date']}" if event_data else "New match tickets available!",
                    icon="https://github.com/user-attachments/assets/d4d3382b-e981-4391-afa7-d99332c5ebed",
                    badge="https://github.com/user-attachments/assets/d4d3382b-e981-4391-afa7-d99332c5ebed",
                    require_interaction=True,
                )
            )
        )
        try:
            response = messaging.send(message)
            print("✅ Successfully sent message:", response)
            results.append({"token": new_token, "status": "success", "response": response})
        except Exception as e:
            print("❌ Error sending message:", e)
            results.append({"token": new_token, "status": "error", "error": str(e)})
    return results


def store_event(event_data):
    try:
        # Store in Firestore with timestamp
        doc_ref = db.collection('events').document('latest')
        doc_ref.set({
            **event_data,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        print(f"Error storing event: {e}")
        return False


def get_last_stored_event():
    try:
        doc_ref = db.collection('events').document('latest')
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Error fetching last event: {e}")
        return None


def compare_events(new_event, stored_event):
    # Check for Chennai Super Kings match
    if new_event.get('team_2') == "Chennai Super Kings":
        return True

    if not stored_event:
        return True

    # Compare using ISO date if available, otherwise use display date
    date_changed = False
    if 'event_iso_date' in new_event and 'event_iso_date' in stored_event:
        date_changed = new_event['event_iso_date'] != stored_event['event_iso_date']
    else:
        date_changed = new_event['event_date'] != stored_event['event_date']

    # Compare relevant fields
    return (new_event['event_name'] != stored_event['event_name'] or
            date_changed or
            new_event['team_1'] != stored_event['team_1'] or
            new_event['team_2'] != stored_event['team_2'])


def is_csk_match(event_data):
    return event_data.get('team_2') == "Chennai Super Kings"


def fetch_event_details():
    url = "https://rcbmpapi.ticketgenie.in/ticket/eventlist/O"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.ticketgenie.in/",
        "Origin": "https://www.ticketgenie.in",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "Success":
            print("Failed to fetch data.")
            return []

        events = data.get("result", [])
        event_details = []

        for event in events:
            # Use the precise ISO format for date parsing if available
            try:
                event_date = datetime.fromisoformat(event.get("event_Date"))
            except (ValueError, TypeError):
                try:
                    # Fallback to display date format
                    event_date = datetime.strptime(event.get("event_Display_Date"), "%a, %b %d, %Y %I:%M %p")
                except (ValueError, TypeError):
                    print(
                        f"Failed to parse date for event: {event.get('event_Name')} - Display Date: {event.get('event_Display_Date')} - ISO Date: {event.get('event_Date')}")
                    continue
            details = {
                "event_name": event.get("event_Name"),
                "team_1": event.get("team_1"),
                "team_2": event.get("team_2"),
                "event_date": event.get("event_Display_Date"),  # Keep display format for UI
                "event_iso_date": event.get("event_Date"),  # Keep ISO format for reference
                "venue": event.get("venue_Name"),
                "_date_obj": event_date  # Add temporary field for sorting
            }
            event_details.append(details)

        # Sort events by date, latest (furthest in future) first
        current_date = datetime.now()
        # Filter out past events and sort by date in descending order
        upcoming_events = [e for e in event_details if e["_date_obj"] >= current_date]
        upcoming_events.sort(key=lambda x: x["_date_obj"], reverse=True)
        event_details = upcoming_events

        # Remove temporary sorting field
        for event in event_details:
            del event["_date_obj"]

        return event_details

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []
