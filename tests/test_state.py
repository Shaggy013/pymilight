import json
import unittest

from pymilight.state import State, BULB_MODE_COLOR, BULB_MODE_SCENE, BULB_MODE_NIGHT, BULB_MODE_WHITE


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
            "_dirty": True,
            "_mqtt_dirty": True,
            "_hue": None,
            "_brightness": None,
            "_white_val": None,
        }, json.loads(dumped))

        state2 = State()
        state2.load(dumped)
        self.assertTrue(state2.state)

    def test_apply_state1(self):
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

    def test_apply_state2(self):
        state = State()
        state.state = True
        state.mode = 2
        state.bulb_mode = BULB_MODE_SCENE

        result = {}
        state.apply_state(result)

        self.assertEqual({
            "state": "ON",
            "color": {"b": 255, "g": 255, "r": 255},
            "bulb_mode": "scene",
            "effect": '2',
            "mode": 2
        }, result)

    def test_apply_night(self):
        state = State()
        state.state = True
        state.bulb_mode = BULB_MODE_NIGHT

        result = {}
        state.apply_state(result)

        self.assertEqual({
            "state": "ON",
            "color": {"b": 255, "g": 255, "r": 255},
            "bulb_mode": "night",
            "effect": 'night_mode',
        }, result)

    def test_apply_white(self):
        state = State()
        state.state = True
        state.bulb_mode = BULB_MODE_WHITE
        state.mireds = 370

        result = {}
        state.apply_state(result)

        self.assertEqual({
            "state": "ON",
            "color": {"b": 255, "g": 255, "r": 255},
            "bulb_mode": "white",
            "effect": 'white_mode',
            "color_temp": 370,
            "kelvin": 2700
        }, result)