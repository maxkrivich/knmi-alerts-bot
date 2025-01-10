import requests
import telebot
from get_docker_secret import get_docker_secret
from loguru import logger


def upsert_user_info(message):
    user_props = {"telegram_id": message.from_user.id, "username": message.from_user.username or "undefined"}

    r = requests.post(
        "http://db_api:3000/users",
        headers={"Content-Type": "application/json"},
        json=user_props,
        timeout=5,
    )

    if r.status_code == 409:
        r = requests.put(
            "http://db_api:3000/users",
            params={"telegram_id": f"eq.{user_props['telegram_id']}"},
            headers={"Content-Type": "application/json"},
            json=user_props,
            timeout=5,
        )

    return True


def delete_user(message):
    user_props = {"telegram_id": message.from_user.id}

    r = requests.delete(
        "http://db_api:3000/users",
        params={"telegram_id": f"eq.{user_props['telegram_id']}"},
        headers={"Content-Type": "application/json"},
        timeout=5,
    )

    r.raise_for_status()

    return True


def send_welcome(message):
    upsert_user_info(message)
    # delete_user(message)

    bot.reply_to(
        message,
        """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""",
    )


def echo_message(message):
    upsert_user_info(message)
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
