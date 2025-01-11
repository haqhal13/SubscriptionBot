from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Fetch the bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

def send_message(chat_id, text):
    """Send a message to a Telegram user."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests."""
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debugging

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            # Handle the /start command
            if text == "/start":
                send_message(chat_id, "Welcome to the bot! How can I help you?")

    except Exception as e:
        print(f"Error in webhook: {e}")

    return "OK"

if __name__ == '__main__':
    # Run the app on the specified port (default: 5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
