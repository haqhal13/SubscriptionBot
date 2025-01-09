def notify_admin(bot, message):
    """Sends a notification to the admin."""
    bot.send_message(chat_id=ADMIN_ID, text=message)