"""Test the mqtt client."""
import unittest

from pymilight import mqtt_client


class MqttClientTestCase(unittest.TestCase):
    def test_parse_topic(self):
        pat = "root/something/:device_id/:group_id/:device_type"
        regexp = mqtt_client.topic_as_regexp(pat)

        topic = "root/something/0x01/1/rgbcct"
        device_id, group_id, device_type = mqtt_client.parse_topic(regexp, topic)

        self.assertEqual(0x01, device_id)
        self.assertEqual(1, group_id)
        self.assertEqual("rgbcct", device_type)

        topic = "root/something/1330/3/rgt"
        device_id, group_id, device_type = mqtt_client.parse_topic(regexp, topic)

        self.assertEqual(1330, device_id)
        self.assertEqual(3, group_id)
        self.assertEqual("rgt", device_type)
