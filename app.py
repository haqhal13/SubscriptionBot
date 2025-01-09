from flask import Flask, request
import requests
from config import MAKE_WEBHOOK_URL, BOT_TOKEN

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle incoming webhook requests from Telegram.
    Process new member events and send details to Make's webhook.
    """
    data = request.get_json()
    print(f"Received data: {data}")  # Log incoming data for debugging

    # Check if the event is a new member joining
    if "message" in data and "new_chat_member" in data['message']:
        try:
            # Extract new member details
            user = data['message']['new_chat_member']
            username = user.get('username', 'N/A')
            user_id = user['id']
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            chat_id = data['message']['chat']['id']

            # Prepare payload to send to Make
            payload = {
                "username": username,
                "user_id": user_id,
                "full_name": full_name,
                "chat_id": chat_id
            }

            # Send data to Make webhook
            response = requests.post(MAKE_WEBHOOK_URL, json=payload)
            response.raise_for_status()
            print(f"Data sent to Make successfully: {response.status_code}")
        except Exception as e:
            print(f"Error processing new member join: {e}")

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
