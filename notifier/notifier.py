import json
import os
import time
import typing

import redis
import requests
import telebot
from get_docker_secret import get_docker_secret
from loguru import logger

REDIS_HOST = "redis"
REDIS_CHANNEL = os.getenv("REDIS_CHANNEL")


def create_bot_client() -> telebot.TeleBot:
    """Create a telegram bot client

    Returns:
        telebot.TeleBot: Telegram bot client
    """
    logger.info("Creating telegram bot client")
    return telebot.TeleBot(get_docker_secret("telegram_bot_token"))


def create_redis_client() -> redis.Redis:
    """Create a redis client

    Returns:
        redis.Redis: Redis client
    """
    logger.info("Creating redis client")
    r = redis.Redis(host=REDIS_HOST, decode_responses=True)
    return r


def make_alert_message(location: str, alert: dict) -> str:
    """Make alert message

    Args:
        location (str): Location of the alert
        alert (dict): Alert information

    Returns:
        str: Alert message
    """

    message = f"""
*Phenomenon*: {alert['phenomenon_name']}
*Code*: {alert['code']}
*Start time*: {alert['start_time']}
*End time*: {alert['end_time']}
*Description*: {alert['text']['EN']}


More info -- https://www.knmi.nl/nederland-nu/weer/waarschuwingen/{location.lower()}
    """.strip()

    return message


def send_alert(bot: telebot.TeleBot, chat_id: str, message: str) -> bool:
    """Send alert to the user

    Args:
        bot (telebot.TeleBot): Telegram bot client
        chat_id (str): Chat id of the user
        message (str): Alert message

    Returns:
        bool: True if message is sent successfully, False otherwise
    """

    try:
        bot.send_message(chat_id, message, parse_mode="Markdown")
        return True
    except telebot.apihelper.ApiTelegramException:
        logger.error(f"Failed to send message to {chat_id}")
        return False


def soft_delete_user(user_id: str) -> None:
    """Soft delete the user

    Args:
        user_id (str): User id
    """
    logger.info(f"Soft deleting user: {user_id}")
    try:
        r = requests.put(
            "http://db_api:3000/users",
            params={"telegram_id": f"eq.{user_id}"},
            headers={"Content-Type": "application/json"},
            json={"is_deleted": True},
            timeout=10,
        )
        r.raise_for_status()
        logger.info(f"User {user_id} soft deleted")
        return True
    except requests.exceptions.RequestException:
        logger.error(f"Failed to soft delete user {user_id}")
        return False


def check_alert(location, alert):
    # r = requests.get(
    #     f"http://db_api:3000/alerts?location=eq.{location}"
    # )

    # alert = {
    #     "phenomenon_name": "Windstoten",
    #     "code": "YELLOW",
    #     "start_time": "2024-12-31 23:00:00+01:00",
    #     "end_time": "2025-01-01 11:00:00+01:00",
    #     "text": {"NL": "Kans op zware windstoten van 75-90 km/u.", "EN": "Risk heavy gusts of 75-90 km/hr."},
    # }

    return "new"


def get_users_interested_in_alert(location: str, alert: dict) -> typing.List[str]:
    """Get users interested in the alert

    Args:
        location (str): Location of the alert
        alert (dict): Alert information

    Returns:
        typing.List[str]: List of users interested in the alert
    """

    r = requests.get(
        "http://db_api:3000/users",
        params={"region": f"eq.{location}", "is_deleted": "eq.false", f"notify_{alert['code'].lower()}": "eq.true"},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )

    if r.status_code != 200:
        return []

    return [user["telegram_id"] for user in r.json()]


def process_message(bot: telebot.TeleBot, record: dict) -> None:
    """Process incoming  messages from the pub/sub

    Args:
        bot (telebot.TeleBot): Telegram bot client
        record (dict): Record from the pub/sub
    """

    logger.info(f"Processing message: {record}")
    for location, alerts in record.items():
        for alert in alerts:
            logger.info(f"Processing alert: {alert}")
            match check_alert(location, alert):
                case "new":
                    users = get_users_interested_in_alert(location, alert)
                    for user in users:
                        is_sent = send_alert(bot, user, make_alert_message(location, alert))
                        if not is_sent:
                            soft_delete_user(user)
                    logger.info(f"Alert sent to {len(users)} users")
                case "updated":
                    pass
                case "unchanged":
                    pass
                case _:
                    logger.error("Unknown alert status")


def main():
    """Main function"""
    logger.info("Starting notifier")

    redis_client = create_redis_client()
    bot = create_bot_client()

    p = redis_client.pubsub(ignore_subscribe_messages=True)
    p.subscribe(REDIS_CHANNEL)

    while True:
        try:
            message = p.get_message()

            if message:
                process_message(bot, json.loads(message["data"]))
            else:
                time.sleep(1)
        except redis.exceptions.ConnectionError:
            logger.error("Redis connection error")
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
