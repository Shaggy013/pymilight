import logging
import re

import json
import paho.mqtt.client as mqtt


LOGGER = logging.getLogger(__name__)


def topic_as_regexp(raw_topic):
    raw_topic = raw_topic.replace(":device_id", "(?P<device_id>.+)")
    raw_topic = raw_topic.replace(":group_id", "(?P<group_id>.+)")
    raw_topic = raw_topic.replace(":device_type", "(?P<device_type>.+)")
    return re.compile(raw_topic)


def parse_topic(regexp, topic):
    match = regexp.match(topic)
    if match:
        return int(match.group("device_id"), 0), int(match.group("group_id"), 0), match.group("device_type")
    raise ValueError("Invalid topic")


def bind_topic_string(topic, device_type, device_id, group_id):
    device_id_hex = "0x{:x}".format(device_id)
    topic = topic.replace(":device_id", device_id_hex)
    topic = topic.replace(":hex_device_id", device_id_hex)
    topic = topic.replace(":dec_device_id", str(device_id))
    topic = topic.replace(":group_id", str(group_id))
    topic = topic.replace(":device_type", device_type)
    return topic


class MqttClient(object):
    def __init__(self, config, callback):
        self.mqtt_topic_pattern = config["mqtt_topic_pattern"]
        self.mqtt_update_topic_pattern = config["mqtt_update_topic_pattern"]
        self.mqtt_state_topic_pattern = config["mqtt_state_topic_pattern"]
        self.mqtt_host = config["mqtt_host"]
        self.mqtt_port = config["mqtt_port"]

        self.handle_message = callback
        self._topic_regexp = topic_as_regexp(self.mqtt_topic_pattern)
        self._mqtt = None

        self._connect()

    def __del__(self):
        if self._mqtt:
            self._mqtt.disconnect()

    def _connect(self):
        self._mqtt = mqtt.Client()
        self._mqtt.on_message = self.message_callback
        self._mqtt.on_connect = self.connect_callback
        LOGGER.info("Connecting to: %s", self.mqtt_host)
        self._mqtt.connect_async(self.mqtt_host, self.mqtt_port, 60)
        self._mqtt.loop_start()

    def connect_callback(self, client, userdata, flags, rc):
        topic = self.mqtt_topic_pattern
        topic = topic.replace(":device_id", "+")
        topic = topic.replace(":group_id", "+")
        topic = topic.replace(":device_type", "+")
        LOGGER.info("Subscribing to: %s", topic)
        client.subscribe(topic)

    def message_callback(self, client, userdata, msg):
        LOGGER.info("Got message on topic: %s\n%s", msg.topic, msg.payload)
        try:
            device_id, group_id, device_type = parse_topic(self._topic_regexp, msg.topic)
        except ValueError:
            LOGGER.info("Unable to parse topic.")
            return

        json_msg = json.loads(msg.payload.decode("utf-8"))

        LOGGER.info("Device %04X, group %u", device_id, group_id)

        self.handle_message(device_type, device_id, group_id, json_msg)

    def send_update(self, device_type, device_id, group_id, update):
        self._publish(
            self.mqtt_update_topic_pattern,
            device_type,
            device_id,
            group_id,
            update
        )

    def send_state(self, device_type, device_id, group_id, update):
        self._publish(
            self.mqtt_state_topic_pattern,
            device_type,
            device_id,
            group_id, 
            update,
            True
        )

    def _publish(self, topic, device_type, device_id, group_id, message, retain=False):
        if not topic:
            return

        topic = bind_topic_string(topic, device_type, device_id, group_id)
        LOGGER.info("Publishing update to %s", topic)
        self._mqtt.publish(topic, message, retain=retain)
