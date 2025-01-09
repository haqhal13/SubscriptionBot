from flask import Flask, request
import requests
from config import MAKE_WEBHOOK_URL, BOT_TOKEN

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Received data: {data}")
    if "message" in data and "new_chat_member" in data['message']:
        user = data['message']['new_chat_member']
        payload = {
            "username": user.get('username', 'N/A'),
            "user_id": user['id'],
            "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
            "chat_id": data['message']['chat']['id']
        }
        response = requests.post(MAKE_WEBHOOK_URL, json=payload)
        print(f"Make webhook response: {response.status_code}, {response.text}")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
