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


def send_welcome(message):
    create_or_update_user({"telegram_id": message.from_user.id, "username": message.from_user.username or "undefined"})

    bot.reply_to(
        message,
        """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""",
    )


def set_region(message):
    """Set the region for the user

    Args:
        message (_type_): _description_
    """
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    keyboard.add(*[telebot.types.KeyboardButton(province) for province in LIST_OF_PROVINCES[: len(LIST_OF_PROVINCES) // 2]])
    keyboard.add(*[telebot.types.KeyboardButton(province) for province in LIST_OF_PROVINCES[len(LIST_OF_PROVINCES) // 2 :]])

    # send_message_or_soft_delete_user(bot, message.from_user.id, "Please enter your region", reply_markup=keyboard)

    bot.send_message(message.chat.id, "Please enter your region", reply_markup=keyboard)


def mute_code(message):
    """Mute the alert code

    Args:
        message (_type_): _description_
    """
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    keyboard.add(*[telebot.types.KeyboardButton(code) for code in LIST_OF_CODES])

    # send_message_or_soft_delete_user(
    #     bot, message.from_user.id, "Please enter the alert code you want to mute", reply_markup=keyboard
    # )

    bot.send_message(message.chat.id, "Please enter the alert code you want to mute", reply_markup=keyboard)


def all_messages(message):
    """Echo all messages

    Args:
        message (_type_): _description_
    """
    create_or_update_user({"telegram_id": message.from_user.id, "username": message.from_user.username or "undefined"})

    if message.text in LIST_OF_PROVINCES:
        bot.reply_to(message, f"Region set to {message.text}")
        # reply_to_message_or_soft_delete(message, f"Region set to {message.text}")
        update_user_region(message.from_user.id, message.text)
    elif message.text in LIST_OF_CODES:
        bot.reply_to(message, f"Alert code muted: {message.text}")
        # reply_to_message_or_soft_delete(message, f"Alert code muted: {message.text}")
        update_user_mute_code(message.from_user.id, message.text)
    else:
        # reply_to_message_or_soft_delete(message, message.text)
        bot.reply_to(message, message.text)


if __name__ == "__main__":
    while True:
        try:
            logger.info("Starting bot")

            bot = telebot.TeleBot(get_docker_secret("telegram_bot_token"))

            bot.message_handler(commands=["help", "start"])(send_welcome)
            bot.message_handler(commands=["region"])(set_region)
            bot.message_handler(commands=["mute"])(mute_code)
            bot.message_handler(func=lambda message: True)(all_messages)
            bot.infinity_polling()
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
