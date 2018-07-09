import unittest

from pymilight.milight_control import MiLightController
from pymilight.packet_formatter import PyRgbCctPacketFormatter


class MiLightControllerTestCase(unittest.TestCase):
    def build_mocked_controller(self):
        formatter = PyRgbCctPacketFormatter()
        controller = MiLightController(None, None, None, True)
        controller.radios = {
            "rgb_cct": unittest.mock.MagicMock()
        }
        controller.radios["rgb_cct"].formatter = formatter
        return controller

    def run_packet_compare(self, request, expected):
        controller = self.build_mocked_controller()
        controller.set_bulb("rgb_cct", 0x2, 1)
        packets = list(controller.request_to_packets(request))
        self.assertEqual(len(expected), len(packets))
        for packet, expected_packet in zip(packets, expected):
            self.assertEquals(expected_packet, packet.hex())

    @unittest.mock.patch("pymilight.milight_control.RF24")
    def test_packet_on(self, rf24):
        self.run_packet_compare(
            {"state": "on"},
            ["00dbe12166d1ba66cc"],
        )
    
    @unittest.mock.patch("pymilight.milight_control.RF24")
    def test_packet_white(self, rf24):
        self.run_packet_compare(
            {
                "state": "ON",
                "color_temp": 370,
                "bulb_mode": "white",
                "color":{"r": 255, "g": 255, "b": 255}
            },
            [
                "00dbe12166d1ba66cc",
                "00dbe1216494bb667e",
                "00dbe121643cb86623",
            ]
        )
        
    @unittest.mock.patch("pymilight.milight_control.RF24")
    def test_packet_mode(self, rf24):
        self.run_packet_compare(
            {
                "state": "ON",
                "mode": 3,
                "bulb_mode": "scene",
                "color": {"r": 255, "g": 255, "b": 255}
            },
            [
                "00dbe12166d1ba66cc",
                "00dbe1216494bb667e",
                "00dbe12162cfb866b4",
            ]
        )