import telebot
from get_docker_secret import get_docker_secret
from loguru import logger
from users import create_or_update_user, update_user_mute_code, update_user_region

LIST_OF_PROVINCES = [
    "Drenthe",
    "Flevoland",
    "Friesland",
    "Gelderland",
    "Groningen",
    "Limburg",
    "Noord-Brabant",
    "Noord-Holland",
    "Overijssel",
    "Utrecht",
    "Zeeland",
    "Zuid-Holland",
    "Waddenzee",
    "IJsselmeergebied",
    "Waddeneilanden",
]

LIST_OF_CODES = [
    "Red",
    "Orange",
    "Yellow",
]


def send_welcome(message: telebot.types.Message):
    """Send welcome message

    Args:
        message (telebot.types.Message): Telegram message
    """
    create_or_update_user({"telegram_id": message.from_user.id, "username": message.from_user.username or "undefined"})

    welcome_message = f"""
Welcome {message.from_user.username}! Please use the following commands:
- /region: Set your region
- /mute: Mute an alert code

This will help me to send alerts based on your preferences.
"""

    bot.send_message(message.chat.id, welcome_message)


def send_help(message: telebot.types.Message):
    """Send help message

    Args:
        message (telebot.types.Message): Telegram message
    """

    help_message = """
Please use the following commands:
- /region: Set your region
- /mute: Mute an alert code
"""

    bot.send_message(message.chat.id, help_message)


def set_region(message: telebot.types.Message):
    """Set the region for the user

    Args:
        message (telebot.types.Message): Telegram message
    """
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    keyboard.add(*[telebot.types.KeyboardButton(province) for province in LIST_OF_PROVINCES[: len(LIST_OF_PROVINCES) // 2]])
    keyboard.add(*[telebot.types.KeyboardButton(province) for province in LIST_OF_PROVINCES[len(LIST_OF_PROVINCES) // 2 :]])

    bot.send_message(message.chat.id, "Please select your region", reply_markup=keyboard)


def mute_code(message: telebot.types.Message):
    """Mute the alert code

    Args:
        message (telebot.types.Message): Telegram message
    """
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    keyboard.add(*[telebot.types.KeyboardButton(code) for code in LIST_OF_CODES])

    bot.send_message(message.chat.id, "Please select the code you want to mute", reply_markup=keyboard)


def all_messages(message: telebot.types.Message):
    """Echo all messages

    Args:
        message (telebot.types.Message): Telegram message
    """
    create_or_update_user({"telegram_id": message.from_user.id, "username": message.from_user.username or "undefined"})

    if message.text in LIST_OF_PROVINCES:
        bot.set_message_reaction(message.chat.id, message.id, [telebot.types.ReactionTypeEmoji("\U0001f44d")], is_big=False)
        update_user_region(message.from_user.id, message.text)
    elif message.text in LIST_OF_CODES:
        bot.set_message_reaction(message.chat.id, message.id, [telebot.types.ReactionTypeEmoji("\U0001f44d")], is_big=False)
        update_user_mute_code(message.from_user.id, message.text)
    else:
        bot.reply_to(message, message.text)


if __name__ == "__main__":
    while True:
        try:
            logger.info("Starting bot")

            bot = telebot.TeleBot(get_docker_secret("telegram_bot_token"))

            bot.register_message_handler(send_welcome, commands=["start"])
            bot.register_message_handler(send_help, commands=["help"])
            bot.register_message_handler(set_region, commands=["region"])
            bot.register_message_handler(mute_code, commands=["mute"])
            bot.register_message_handler(all_messages, func=lambda message: True)

            bot.infinity_polling()
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
