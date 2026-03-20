import datetime
import json
import os
import time
import typing

import redis  # ty: ignore[unresolved-import]
import requests
import telebot  # ty: ignore[unresolved-import]
from alerts import create_report_for_the_region
from get_docker_secret import get_docker_secret
from loguru import logger

REDIS_HOST = "redis"
REDIS_CHANNEL = os.getenv("REDIS_CHANNEL")
API_BASE = os.getenv("API_URL")


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


def make_alert_message(alert: dict) -> str:
    """Make alert message

    Args:
        location (str): Location of the alert
        alert (dict): Alert information

    Returns:
        str: Alert message
    """
    code_to_emoji = {"red": "🔴", "orange": "🟠", "yellow": "🟡"}

    code_color = alert["code"].lower()
    emoji_for_code = code_to_emoji.get(code_color, "⚪")

    message = f"""
🌦️ *Weather Alert* 🌦️

{emoji_for_code} *Phenomenon*: {alert["phenomenon_name"]}
🔢 *Code* {emoji_for_code} {alert["code"].lower()}
⏰ *Start Time*: {pretty_date(alert["start_time"])}
⏳ *End Time*: {pretty_date(alert["end_time"])}

📢 *Description*:
{alert["text"]["EN"]}

*Please click the button below to read more* 👇
    """.strip()

    return message


def pretty_date(date: str) -> str:
    """Convert date to pretty format

    Args:
        date (str): Date in iso format

    Returns:
        str: Pretty date
    """
    dt = datetime.datetime.fromisoformat(date)
    day = dt.day

    if 4 <= day <= 20 or 24 <= day <= 30:  # Special case for 11th-13th, 21st-23rd, 31st
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    return f"{day}{suffix} of {dt.strftime('%B')}, {dt.strftime('%H:%M')}"


def send_alert(bot: telebot.TeleBot, chat_id: str, message: str, location: str) -> bool:
    """Send alert to the user

    Args:
        bot (telebot.TeleBot): Telegram bot client
        chat_id (str): Chat id of the user
        message (str): Alert message
        location (str): Location of the alert

    Returns:
        bool: True if message is sent successfully, False otherwise
    """

    try:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            telebot.types.InlineKeyboardButton(
                "Visit knmi.nl", url=f"https://www.knmi.nl/nederland-nu/weer/waarschuwingen/{location.lower()}"
            )
        )

        bot.send_message(chat_id, message, parse_mode="Markdown", reply_markup=markup)
        return True
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")
        return False


def soft_delete_user(user_id: str) -> bool:
    """Soft delete the user

    Args:
        user_id (str): User id
    """
    logger.info(f"Soft deleting user: {user_id}")
    try:
        r = requests.patch(
            f"{API_BASE}/users",
            params={"telegram_id": f"eq.{user_id}"},
            headers={"Content-Type": "application/json"},
            json={"is_deleted": True},
            timeout=10,
        )
        r.raise_for_status()
        logger.info(f"User {user_id} soft deleted")
        return True
    except Exception as e:
        logger.error(f"Failed to soft delete user {user_id}: {e}")
        return False


def get_on_going_alerts(location: str) -> typing.List[dict]:
    """Get on going alerts

    Args:
        location (str): Location of the alert

    Returns:
        typing.List[dict]: List of on going alerts
    """

    r = requests.get(
        f"{API_BASE}/alerts",
        params={
            "region": f"eq.{location}",
            "end_time": f"gte.{time.strftime('%Y-%m-%d %H:%M:%S')}",
        },
        headers={"Content-Type": "application/json"},
        timeout=10,
    )

    if r.status_code != 200:
        return []

    return r.json()


def create_or_update_alert(old_alert: dict, new_alert: dict) -> None:
    """Update the alert

    Args:
        old_alert (dict): Old alert information
        new_alert (dict): New alert information
    """

    new_alert["description"] = new_alert.pop("text")["EN"]

    r = requests.post(
        f"{API_BASE}/alerts",
        headers={"Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"},
        json=new_alert,
        timeout=10,
    )

    if r.status_code != 204:
        logger.error(f"Failed to update alert: {old_alert}")


def check_alert(location: str, alert: dict) -> str:
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

    # on_going_alets = get_on_going_alerts(location)

    # logger.info(f"on_going_alets: {on_going_alets}")

    # for old_alert in on_going_alets:
    #     if old_alert["phenomenon_name"] == alert["phenomenon_name"]:
    #         if old_alert == alert:
    #             return "unchanged"
    #         else:
    #             create_or_update_alert(old_alert, alert)
    #             return "upadted"

    # create_or_update_alert({}, alert)
    return "new"

    """
    get on_going alerts
    check if alert is in the on_going alerts
    if yes:
        check if the alert is updated
        if yes:
            return updated
        else:
            return unchanged
    else:
        return new
    """


def get_users_interested_in_alert(location: str, alert: dict) -> typing.List[dict]:
    """Get users interested in the alert

    Args:
        location (str): Location of the alert
        alert (dict): Alert information

    Returns:
        typing.List[dict]: List of users interested in the alert
    """

    r = requests.get(
        f"{API_BASE}/users",
        params={"region": f"eq.{location}", "is_deleted": "eq.false", f"notify_{alert['code'].lower()}": "eq.true"},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )

    if r.status_code != 200:
        return []

    return r.json()


def process_message(bot: telebot.TeleBot, record: dict) -> None:
    """Process incoming  messages from the pub/sub

    Args:
        bot (telebot.TeleBot): Telegram bot client
        record (dict): Record from the pub/sub
    """

    logger.info(f"Processing message: {record}")
    for location, alerts in record.items():
        if len(alerts) == 0:
            logger.info(f"No alerts found for {location}")
            continue

        create_report_for_the_region(location, alerts)

        for alert in alerts:
            logger.info(f"Alert: {alert}")
            match check_alert(location, alert):
                case "new":
                    users = get_users_interested_in_alert(location, alert)
                    alert_message = make_alert_message(alert)
                    for user in users:
                        is_sent = send_alert(bot, user["telegram_id"], alert_message, location)
                        if not is_sent:
                            soft_delete_user(user["telegram_id"])
                    logger.info(f"Alert sent to {len(users)} users")
                case "updated":
                    pass
                case "unchanged":
                    logger.info("Alert unchanged. Skipping")
                    continue
                case _:
                    logger.error("Unknown alert status")


def main() -> None:
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
