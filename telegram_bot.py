import telegram
import os

bot = None


def initialize_bot():
    global bot
    if bot:
        return
    TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    bot = telegram.Bot(token=TOKEN)


def receive_chat_ids(offset, permitted_users):
    initialize_bot()
    all_updates = bot.get_updates(offset=offset)
    chat_ids = set()
    highest_update_id = 0
    for update in all_updates:
        if update.update_id > highest_update_id:
            highest_update_id = update.update_id
        try:
            if update.message.from_user.username in permitted_users:
                chat_ids.add(update.message.chat_id)
        except Exception as e:
            print(e)
    return chat_ids, highest_update_id


def send_message(message, chat_id):
    initialize_bot()
    try:
        return bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Could not send message to chat {chat_id}, got exception {e}")
