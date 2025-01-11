import io
import json
import logging
import os
import pathlib
import ssl
import typing

import paho.mqtt.client as mqtt_client
import paho.mqtt.properties as properties
import redis
import requests
from get_docker_secret import get_docker_secret
from icecream import ic
from knmi_alerts import get_alerts

BROKER_DOMAIN = "mqtt.dataplatform.knmi.nl"
NOTIFICATION_CLIENT_ID = get_docker_secret("notification_client_id")
NOTIFICATION_TOKEN = get_docker_secret("notification_token")
API_TOKEN = get_docker_secret("open_data_api_token")
TOPIC = "dataplatform/file/v1/waarschuwingen_nederland_48h/1.0/#"
PROTOCOL = mqtt_client.MQTTv5


REDIS_HOST = "redis"
REDIS_CHANNEL = os.getenv("REDIS_CHANNEL")

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

r = redis.Redis(host=REDIS_HOST)


def download_report(url: str) -> io.BytesIO:
    """Download the report

    Args:
        url (str): URL to the report

    Returns:
        io.BytesIO: In-memory report
    """
    resp = requests.get(url, stream=True, timeout=20)
    resp.raise_for_status()

    return io.BytesIO(resp.content)


def write_report(report: io.BytesIO, filename: str, path: pathlib.Path) -> typing.Optional[str]:
    """Write the report to a file

    Args:
        report (io.BytesIO): In-memory report
        filename (str): Name of the file
        path (pathlib.Path): Path to write the file

    Returns:
        typing.Optional[str]: Name of the file
    """
    full_path = path / filename
    with open(full_path, "wb") as fd:
        fd.write(report.read())
        return filename
    return None


def get_temporary_download_url(url: str) -> str:
    """Get the temporary download URL for the report

    Args:
        url (str): URL to the report

    Returns:
        str: Temporary download URL
    """
    resp = requests.get(url, headers={"Authorization": API_TOKEN}, timeout=10)
    resp.raise_for_status()

    return resp.json().get("temporaryDownloadUrl")


def connect_mqtt() -> mqtt_client:
    def on_connect(c: mqtt_client, userdata, flags, reason_code, props=None):
        logger.info(f"Connected using client ID: {str(c._client_id)}")
        logger.info(f"Session present: {str(flags.session_present)}")
        logger.info(f"Connection result: {str(reason_code)}")
        # Subscribe here so it is automatically done after disconnect
        subscribe(c, TOPIC)

    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION2, client_id=NOTIFICATION_CLIENT_ID, protocol=PROTOCOL, transport="websockets"
    )
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    connect_properties = properties.Properties(properties.PacketTypes.CONNECT)
    # Maximum is 3600
    connect_properties.SessionExpiryInterval = 3600

    # The MQTT username is not used for authentication, only the token
    username = "token"
    client.username_pw_set(username, NOTIFICATION_TOKEN)
    client.on_connect = on_connect

    client.connect(host=BROKER_DOMAIN, port=443, keepalive=60, clean_start=False, properties=connect_properties)

    return client


def process_message(message: dict):
    if not message["data"]["filename"].endswith(".xml"):
        return

    download_url = get_temporary_download_url(message["data"]["url"])
    report = download_report(download_url)
    alerts = get_alerts(report)
    ic(alerts)
    r.publish(REDIS_CHANNEL, json.dumps(alerts, default=str))


def subscribe(client: mqtt_client, topic: str):
    def on_message(c: mqtt_client, userdata, message):
        # NOTE: Do NOT do slow processing in this function, as this will interfere with PUBACK messages for QoS=1.
        # A couple of seconds seems fine, a minute is definitely too long.
        logger.info(f"Received message on topic {message.topic}: {str(message.payload)}")
        message = json.loads(message.payload)

        process_message(message)

    def on_subscribe(c: mqtt_client, userdata, mid, reason_codes, properties):
        logger.info(f"Subscribed to topic '{topic}'")

    client.on_subscribe = on_subscribe
    client.on_message = on_message
    # A qos=1 will replay missed events when reconnecting with the same client ID. Use qos=0 to disable
    client.subscribe(topic, qos=1)


def run():
    client = connect_mqtt()
    client.enable_logger(logger=logger)
    client.loop_forever()


if __name__ == "__main__":
    # ic(get_alerts(None))

    message1 = {
        "data": {
            "filename": "knmi_waarschuwingen_202412301245.xml",
            "url": "https://api.dataplatform.knmi.nl/open-data/v1/datasets/waarschuwingen_nederland_48h/versions/1.0/files/knmi_waarschuwingen_202412301245.xml/url",
        }
    }

    message2 = {
        "data": {
            "filename": "knmi_waarschuwingen_202501110807.xml",
            "url": "https://api.dataplatform.knmi.nl/open-data/v1/datasets/waarschuwingen_nederland_48h/versions/1.0/files/knmi_waarschuwingen_202501110807.xml/url",
        }
    }
    # process_message(message2)

    run()
