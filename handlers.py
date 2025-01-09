import requests
from utils import notify_admin
from config import WEBHOOK_REGISTER, WEBHOOK_MEMBER_JOIN

def handle_invite_link(bot):
    """Generates and registers a one-time invite link."""
    try:
        # Generate one-time-use invite link
        invite_link = bot.create_chat_invite_link(chat_id=GROUP_ID, member_limit=1).invite_link

        # Register invite link via webhook
        response = requests.post(WEBHOOK_REGISTER, json={"invite_link": invite_link})
        if response.status_code == 200:
            print("Invite link registered successfully.")

        return "OK", 200
    except Exception as e:
        print(f"Error generating invite link: {e}")
        return "Error", 500

def handle_member_join(data, bot):
    """Handles new member join event."""
    try:
        user = data['message']['new_chat_participant']
        username = user.get('username', 'N/A')
        user_id = user['id']
        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        invite_link = data.get('invite_link', 'Unknown')

        # Send member details to Make webhook for logging
        response = requests.post(WEBHOOK_MEMBER_JOIN, json={
            "username": username,
            "user_id": user_id,
            "full_name": full_name,
            "invite_link": invite_link
        })

        if response.status_code == 200:
            print("Member details sent to Make webhook.")

        # Notify admin about new member
        notify_admin(bot, f"New Member: @{username} ({full_name}), ID: {user_id}, Invite Link: {invite_link}")

        return "OK", 200
    except Exception as e:
        print(f"Error handling member join: {e}")
        return "Error", 500

def handle_membership_monitoring(bot):
    """Handles membership expiration monitoring."""
    try:
        # This functionality remains the same as it doesn't rely on Google Sheets
        # For example, Make could periodically send HTTP requests to this endpoint with membership data.
        pass
    except Exception as e:
        print(f"Error in membership monitoring: {e}")
        return "Error", 500