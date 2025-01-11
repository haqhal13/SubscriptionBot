from flask import Flask, request
import requests
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Group ID (VIP Group)
GROUP_ID = os.getenv("GROUP_ID")


def send_message(chat_id, text):
    """Send a message to a Telegram user."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


def create_invite_link():
    """Generate a one-time use invite link."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/createChatInviteLink"
    payload = {"chat_id": GROUP_ID, "member_limit": 1}
    response = requests.post(url, json=payload)
    data = response.json()
    return data.get("result", {}).get("invite_link")


def store_invite_link(invite_link):
    """Store the generated invite link in the database."""
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO invites (invite_link) VALUES (?)", (invite_link,))
    conn.commit()
    conn.close()


def track_user(user_id, username, invite_link):
    """Track the user who joined through the invite link."""
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    join_date = datetime.now()
    kick_date = join_date + timedelta(days=29)
    reminder_date = join_date + timedelta(days=28)

    # Store user and their kick/reminder dates
    cursor.execute("""
    INSERT INTO reminders (user_id, chat_id, reminder_date, kick_date, link_used)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, GROUP_ID, reminder_date, kick_date, invite_link))

    # Update the invite record
    cursor.execute("""
    UPDATE invites
    SET user_id = ?, username = ?, join_date = ?
    WHERE invite_link = ?
    """, (user_id, username, join_date, invite_link))

    conn.commit()
    conn.close()


def send_reminder():
    """Send reminders to users whose subscription is about to expire."""
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()

    today = datetime.now()
    cursor.execute("""
    SELECT user_id, chat_id, reminder_date
    FROM reminders
    WHERE reminder_date <= ?
    """, (today,))
    rows = cursor.fetchall()

    for row in rows:
        user_id, chat_id, reminder_date = row
        send_message(user_id, "Your VIP subscription will end tomorrow. Click this link to renew: google.com")

    conn.close()


def kick_expired_users():
    """Kick users whose subscription has expired."""
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()

    today = datetime.now()
    cursor.execute("""
    SELECT user_id
    FROM reminders
    WHERE kick_date <= ?
    """, (today,))
    rows = cursor.fetchall()

    for row in rows:
        user_id = row[0]
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/kickChatMember"
        payload = {"chat_id": GROUP_ID, "user_id": user_id}
        requests.post(url, json=payload)

    # Remove expired reminders
    cursor.execute("DELETE FROM reminders WHERE kick_date <= ?", (today,))
    conn.commit()
    conn.close()


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming Telegram messages."""
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        user_id = data["message"]["from"]["id"]
        username = data["message"]["from"].get("username", "Unknown")

        if text == "/invite":
            invite_link = create_invite_link()
            store_invite_link(invite_link)
            send_message(chat_id, f"Here is your one-time use invite link: {invite_link}")

        elif text == "/list":
            conn = sqlite3.connect("bot_data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invites")
            rows = cursor.fetchall()

            message = "Invite List:\n"
            for row in rows:
                invite_link, created_at, user_id, username, join_date = row
                message += f"Link: {invite_link}, User: {username}, Join Date: {join_date}\n"

            send_message(chat_id, message)

    if "chat_member" in data:
        new_chat_member = data["chat_member"]["new_chat_member"]
        invite_link = data["chat_member"].get("invite_link", "Unknown")
        if new_chat_member and new_chat_member["status"] == "member":
            track_user(new_chat_member["user"]["id"], new_chat_member["user"]["username"], invite_link)

    return "OK"


if __name__ == "__main__":
    app.run(port=5000)
