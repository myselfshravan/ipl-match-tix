# IPL Match Ticket Notifier 🏏

An automated notification system that monitors IPL match ticket availability on TicketGenie and sends push notifications when new matches become available. Special focus on Chennai Super Kings matches!

## Features 🌟

- Real-time monitoring of IPL match tickets on TicketGenie
- Push notifications for new match ticket availability
- Special notifications for Chennai Super Kings matches
- Firebase-powered data storage and notifications
- Serverless deployment on Vercel

## Tech Stack 💻

- **Backend**: Python Flask
- **Database**: Firebase Firestore
- **Notifications**: Firebase Cloud Messaging
- **Deployment**: Vercel
- **CI/CD**: GitHub Actions

## Dependencies 📦

```plaintext
Flask==3.0.3
flask-cors==4.0.0
APScheduler
requests
firebase-admin~=6.7.0
python-dotenv
```

## Environment Variables 🔐

The following environment variables are required:

```plaintext
FIREBASE_TYPE
FIREBASE_PROJECT_ID
FIREBASE_PRIVATE_KEY_ID
FIREBASE_PRIVATE_KEY
FIREBASE_CLIENT_EMAIL
FIREBASE_CLIENT_ID
FIREBASE_AUTH_URI
FIREBASE_TOKEN_URI
FIREBASE_AUTH_PROVIDER_CERT_URL
FIREBASE_CLIENT_CERT_URL
FIREBASE_UNIVERSE_DOMAIN
```

## API Endpoints 🛣️

### GET /ping

Health check endpoint to keep the serverless function active.

### GET /event

Fetches latest IPL match details from TicketGenie and sends notifications if new matches are available.

## Deployment 🚀

This project is deployed on Vercel as a serverless application. The GitHub Actions workflow pings the endpoint every 5 minutes to prevent cold starts.

## Architecture 🏗️

1. The system periodically checks TicketGenie's API for new match listings
2. When a new match is detected (especially CSK matches), it:
   - Stores the match details in Firebase Firestore
   - Sends push notifications via Firebase Cloud Messaging
   - Updates the latest event record
3. A GitHub Actions workflow keeps the serverless function warm

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
