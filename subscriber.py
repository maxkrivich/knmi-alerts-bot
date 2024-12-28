import logging
import ssl
import os

import paho.mqtt.client as mqtt_client
import paho.mqtt.properties as properties

BROKER_DOMAIN = "mqtt.dataplatform.knmi.nl"
# Client ID should be made static, it is used to identify your session, so that
# missed events can be replayed after a disconnect
# https://www.uuidgenerator.net/version4
CLIENT_ID = os.environ.get("KNMI_NOTIFICATION_CLIENT_ID")
# Obtain your token at: https://developer.dataplatform.knmi.nl/notification-service
TOKEN = os.environ.get("KNMI_NOTIFICATION_TOKEN")
# This will listen to both file creation and update events of this dataset:
# https://dataplatform.knmi.nl/dataset/radar-echotopheight-5min-1-0
# This topic should have one event every 5 minutes
TOPIC = "dataplatform/file/v1/waarschuwingen_nederland_48h/1.0/#"
# Version 3.1.1 also supported
PROTOCOL = mqtt_client.MQTTv5

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def connect_mqtt() -> mqtt_client:
    def on_connect(c: mqtt_client, userdata, flags, reason_code, props=None):
        logger.info(f"Connected using client ID: {str(c._client_id)}")
        logger.info(f"Session present: {str(flags.session_present)}")
        logger.info(f"Connection result: {str(reason_code)}")
        # Subscribe here so it is automatically done after disconnect
        subscribe(c, TOPIC)

    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, protocol=PROTOCOL, transport="websockets"
    )
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    connect_properties = properties.Properties(properties.PacketTypes.CONNECT)
    # Maximum is 3600
    connect_properties.SessionExpiryInterval = 3600

    # The MQTT username is not used for authentication, only the token
    username = "token"
    client.username_pw_set(username, TOKEN)
    client.on_connect = on_connect

    client.connect(host=BROKER_DOMAIN, port=443, keepalive=60, clean_start=False, properties=connect_properties)

    return client


def subscribe(client: mqtt_client, topic: str):
    def on_message(c: mqtt_client, userdata, message):
        # NOTE: Do NOT do slow processing in this function, as this will interfere with PUBACK messages for QoS=1.
        # A couple of seconds seems fine, a minute is definitely too long.
        logger.info(f"Received message on topic {message.topic}: {str(message.payload)}")

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
    run()
