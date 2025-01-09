from config import ADMIN_ID

def notify_admin(bot, message):
    """Sends a notification to the admin."""
    try:
        bot.send_message(chat_id=ADMIN_ID, text=message)
    except Exception as e:
        print(f"Error notifying admin: {e}")
