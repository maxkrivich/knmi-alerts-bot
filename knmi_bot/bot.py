import telebot
from get_docker_secret import get_docker_secret
from loguru import logger


def send_welcome(message):
    bot.reply_to(
        message,
        """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""",
    )


def echo_message(message):
    bot.reply_to(message, message.text)


if __name__ == "__main__":
    while True:
        try:
            logger.info("Starting bot")

            bot = telebot.TeleBot(get_docker_secret("telegram_bot_token"))

            bot.message_handler(commands=["help", "start"])(send_welcome)
            bot.message_handler(func=lambda message: True)(echo_message)
            bot.infinity_polling()
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
