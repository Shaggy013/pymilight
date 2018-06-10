import json
import unittest

from pymilight.state import State, BULB_MODE_COLOR


class MiLightStateTestCase(unittest.TestCase):
    def test_dump_load(self):
        state = State()
        state.state = True
        dumped = state.dump()
        self.assertEqual({
            "_saturation": None,
            "_mode": None,
            "_brightness_mode": None,
            "_brightness_color": None,
            "_night_mode": None,
            "_bulb_mode": None,
            "_state": True,
            "_kelvin": None,
            "_dirty": True,
            "_mqtt_dirty": True,
            "_hue": None,
            "_brightness": None,
        }, json.loads(dumped))

        state2 = State()
        state2.load(dumped)
        self.assertTrue(state2.state)

    def test_apply_state(self):
        state = State()
        state.state = True
        state.bulb_mode = BULB_MODE_COLOR
        state.brightness = 67
        state.hue = 200
        state.saturation = 100

        result = {}
        state.apply_state(result)

        self.assertEqual({
            "brightness": 171,
            "level": 67,
            "state": "ON",
            "color": {"b": 255, "g": 169, "r": 0},
            "hue": 200,
            "saturation": 100,
            "bulb_mode": "color"
        }, result)