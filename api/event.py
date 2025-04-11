import firebase_admin
from firebase_admin import credentials, messaging
import requests
import os
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

tokens = [
    "fT04LaZzayopUX6gdVRkDi:APA91bH6Wl2Rw0I6aOTnh9aKmJk5FFzjdKJ7ZOKgGWy-b5Uwzp9U9A7RRnXSpM5chGpZa0jLv2Aeyqp_AJ-5fBrhaZGtRoxFBDDf9-1qMXiJQlAtd-lFnrE",
    "dftG_SJkzxP8zgVwSqpsLH:APA91bFiG9Mz8S0xaigCu4cx9HJxJuRJzRtJnx0QwhnOu3b9im2Mx5O6fy7jp5UNle1geweU9UNuU8X6Sh11tVFZX5rlgTC1HAvCoH2cUbAQVG1vVMlHKFQ",
    "eZ6l27Fw9Amw-r0OewG0aN:APA91bErHZ9Dy0Lw51jRvZjaynMno35H-QNwLzQDAUbQsmF9qIScApnXFIJjJQev5F7pAkjCMs5lFL-2hfDVGovDRMYPnVxNwyC7O8GmLIxRZpRPF9KNGM0",
]


def send_push_notifications():
    results = []
    for new_token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title="🔥 Hello from Front!",
                body="Your notification just landed 🛬",
            ),
            token=new_token,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title="🔥 Hello the event is Live!",
                    body="Your notification just landed 🛬",
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
            details = {
                "event_name": event.get("event_Name"),
                "team_1": event.get("team_1"),
                "team_2": event.get("team_2"),
                "event_date": event.get("event_Display_Date"),
                "venue": event.get("venue_Name"),
            }
            event_details.append(details)

        return event_details

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []
