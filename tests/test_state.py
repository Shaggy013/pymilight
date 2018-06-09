import json
import unittest

from pymilight.state import State


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
