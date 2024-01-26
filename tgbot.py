import telebot
from datetime import datetime
import tgbot_messages

USER_LIST = [370060213,450919685]
# USER_LIST = [370060213,]


TOKEN = '6802517140:AAGXLYQkp37y6ohahBQuM05bmEyxDJBN-Pc'

bot = telebot.TeleBot(token=TOKEN)

@bot.message_handler(commands=['help','start'])
def send_welcome(message):
    bot.send_message(message.chat.id, text=tgbot_messages.MSG_HELLO)

def send_alert_message(text):
    for user_id in USER_LIST:
        chat = bot.get_chat(user_id)
        bot.send_message(chat_id=chat.id, text=f'Ошибочка вылетела:\n{text}')

if __name__ == '__main__':
    print(f'Bot started at {datetime.now()}')
    bot.infinity_polling()
