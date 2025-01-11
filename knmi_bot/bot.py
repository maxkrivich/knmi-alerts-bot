import telebot
from get_docker_secret import get_docker_secret
from loguru import logger
from users import create_or_update_user, soft_delete_user, update_user_mute_code, update_user_region

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


def send_message_or_soft_delete(bot: telebot.TeleBot, telegram_id: str, message: str, **kwargs) -> bool:
    """Send message to the user or soft delete the user

    Args:
        bot (telebot.TeleBot): Telegram bot
        user (dict): User information
        message (str): Message to send

    Returns:
        bool: True if message is sent successfully, False otherwise
    """
    try:
        bot.send_message(telegram_id, message, parse_mode="Markdown", **kwargs)
        return True
    except telebot.apihelper.ApiException as e:
        logger.error(f"Error: {e}")
        soft_delete_user(telegram_id)
        return False


def send_reply_or_soft_delete(bot: telebot.TeleBot, message: telebot.types.Message, reply: str, **kwargs) -> bool:
    """Send reply to the user or soft delete the user

    Args:
        bot (telebot.TeleBot): Telegram bot
        message (telebot.types.Message): Telegram message
        reply (str): Reply to send

    Returns:
        bool: True if message is sent successfully, False otherwise
    """
    try:
        bot.reply_to(message, reply, **kwargs)
        return True
    except telebot.apihelper.ApiException as e:
        logger.error(f"Error: {e}")
        soft_delete_user(message.from_user.id)
        return False


def send_reaction_or_soft_delete(bot: telebot.TeleBot, chat_id: str, message_id: str, reactions: list, **kwargs) -> bool:
    """Send reaction to the message or soft delete the user

    Args:
        bot (telebot.TeleBot): Telegram bot
        chat_id (str): Chat id of the user
        message_id (str): Message id
        reactions (list): List of reactions

    Returns:
        bool: True if message is sent successfully, False otherwise
    """
    try:
        bot.set_message_reaction(chat_id, message_id, reactions, **kwargs)
        return True
    except telebot.apihelper.ApiException as e:
        logger.error(f"Error: {e}")
        soft_delete_user(chat_id)
        return False


def send_welcome_command(message: telebot.types.Message):
    """Send welcome message

    Args:
        message (telebot.types.Message): Telegram message
    """
    create_or_update_user(
        {"telegram_id": message.from_user.id, "is_deleted": False, "username": message.from_user.username or "undefined"}
    )

    welcome_message = f"""
Welcome {message.from_user.username}! Please use the following commands:
- /region: Set your region
- /mute: Mute an alert code

This will help me to send alerts based on your preferences.
"""

    send_message_or_soft_delete(bot, message.chat.id, welcome_message)


def send_help_command(message: telebot.types.Message):
    """Send help message

    Args:
        message (telebot.types.Message): Telegram message
    """

    help_message = """
Please use the following commands:
- /region: Set your region
- /mute: Mute an alert code
"""

    send_message_or_soft_delete(bot, message.chat.id, help_message)


def set_region_command(message: telebot.types.Message):
    """Set the region for the user

    Args:
        message (telebot.types.Message): Telegram message
    """
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    keyboard.add(*[telebot.types.KeyboardButton(province) for province in LIST_OF_PROVINCES[: len(LIST_OF_PROVINCES) // 2]])
    keyboard.add(*[telebot.types.KeyboardButton(province) for province in LIST_OF_PROVINCES[len(LIST_OF_PROVINCES) // 2 :]])

    send_message_or_soft_delete(bot, message.chat.id, "Please select your region", reply_markup=keyboard)


def set_mute_code_command(message: telebot.types.Message):
    """Mute the alert code

    Args:
        message (telebot.types.Message): Telegram message
    """
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    keyboard.add(*[telebot.types.KeyboardButton(code) for code in LIST_OF_CODES])

    send_message_or_soft_delete(bot, message.chat.id, "Please select the code you want to mute", reply_markup=keyboard)


def catch_all_messages(message: telebot.types.Message):
    """Echo all messages

    Args:
        message (telebot.types.Message): Telegram message
    """
    create_or_update_user({"telegram_id": message.from_user.id, "username": message.from_user.username or "undefined"})

    if message.text in LIST_OF_PROVINCES:
        send_reaction_or_soft_delete(
            bot, message.chat.id, message.id, [telebot.types.ReactionTypeEmoji("\U0001f44d")], is_big=False
        )

        update_user_region(message.from_user.id, message.text)
    elif message.text in LIST_OF_CODES:
        send_reaction_or_soft_delete(
            bot, message.chat.id, message.id, [telebot.types.ReactionTypeEmoji("\U0001f44d")], is_big=False
        )
        update_user_mute_code(message.from_user.id, message.text)
    else:
        send_reply_or_soft_delete(
            bot, message, "I don't understand this command \U0001f62d. Please use /help to see the list of commands."
        )


if __name__ == "__main__":
    while True:
        try:
            logger.info("Starting bot")

            bot = telebot.TeleBot(get_docker_secret("telegram_bot_token"))

            bot.register_message_handler(send_welcome_command, commands=["start"])
            bot.register_message_handler(send_help_command, commands=["help"])
            bot.register_message_handler(set_region_command, commands=["region"])
            bot.register_message_handler(set_mute_code_command, commands=["mute"])
            bot.register_message_handler(catch_all_messages, func=lambda message: True)

            bot.infinity_polling()
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
