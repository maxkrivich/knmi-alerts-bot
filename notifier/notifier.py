import telebot
import os
import redis
import json
import time

from get_docker_secret import get_docker_secret
# from icecream import ic


REDIS_HOST = "redis"
REDIS_CHANNEL = os.getenv("REDIS_CHANNEL")


def create_bot_client():
    return telebot.TeleBot(get_docker_secret("telegram_bot_token"))


def create_redis_client():
    r = redis.Redis(host=REDIS_HOST, decode_responses=True)
    p = r.pubsub(ignore_subscribe_messages=True)
    p.subscribe(REDIS_CHANNEL)

    return p


def send_alert(bot, chat_id, message):
    # TODO: Check if the bot was not blocked by the user
    bot.send_message(chat_id, message)


def check_alert(location, alert):
    return "new"


def get_users_interested_in_alert(location, alert):
    return [get_docker_secret("debug_chat_id")]


def process_message(bot, record):
    # send_alert(bot, get_docker_secret("debug_chat_id"), message["data"])

    for location, alerts in record.items():
        for alert in alerts:
            match check_alert(location, alert):
                case "new":
                    users = get_users_interested_in_alert(location, alert)
                    for user in users:
                        send_alert(bot, user, f"New alert for {location}: {alert}")
                case "updated":
                    pass
                case "unchanged":
                    pass
                case _:
                    pass


def main():
    # listen to pub/sub and wait for alerts
    # get users interested in the alerts (think about muting alerts per user)
    # send alerts to telegram

    pubsub = create_redis_client()
    bot = create_bot_client()
    send_alert(bot, get_docker_secret("debug_chat_id"), "start notifier")

    while True:
        try:
            message = pubsub.get_message()

            if message:
                process_message(bot, json.loads(message["data"]))
            else:
                time.sleep(1)
        except redis.exceptions.ConnectionError:
            pass


if __name__ == "__main__":
    main()
