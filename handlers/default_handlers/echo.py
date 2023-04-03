from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message):
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, f"Команда: {message.text}\n" "не корректна, вот список доступных команд.")
    bot.reply_to(message, "\n".join(text))
