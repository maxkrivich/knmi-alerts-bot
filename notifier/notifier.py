import telebot
import os
import redis
import time

from get_docker_secret import get_docker_secret
from icecream import ic


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
    bot.send_message(chat_id, message)


def main():
    # listen to pub/sub and wait for alerts
    # get users interested in the alerts (think about muting alerts per user)
    # send alerts to telegram
    pubsub = create_redis_client()
    # bot = create_bot_client()

    while True:
        try:
            message = pubsub.get_message()

            if message:
                ic("Got message")
                ic(message)
                # send_alert(bot, message["data"]["chat_id"], message["data"]["message"])
            else:
                time.sleep(1)
        except redis.exceptions.ConnectionError:
            pass


if __name__ == "__main__":
    main()
