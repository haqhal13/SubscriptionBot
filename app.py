from flask import Flask, request
from telegram import Bot
from handlers import handle_invite_link, handle_member_join, handle_membership_monitoring
from config import BOT_TOKEN

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# Webhook for Invite Link Generation
@app.route('/webhook/invite', methods=['POST'])
def webhook_invite():
    return handle_invite_link(bot)

# Webhook for Member Join
@app.route('/webhook/join', methods=['POST'])
def webhook_join():
    return handle_member_join(request.json, bot)

# Webhook for Membership Monitoring
@app.route('/webhook/monitor', methods=['POST'])
def webhook_monitor():
    return handle_membership_monitoring(bot)

if __name__ == '__main__':
    app.run(port=8443)