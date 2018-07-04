import json

from pymilight.rgb_converter import hsv_to_rgb
from pymilight.utils import white_val_to_mireds, mireds_to_white_val, rescale


FIELD_NAMES = [
    "unknown",
    "state",
    "status",
    "brightness",
    "level",
    "hue",
    "saturation",
    "color",
    "mode",
    "kelvin",
    "color_temp",
    "bulb_mode",
    "computed_color",
    "effect"
]


BULB_MODE_WHITE = 0
BULB_MODE_COLOR = 1
BULB_MODE_SCENE = 2
BULB_MODE_NIGHT = 3
BULB_MODE_NAMES = {
    BULB_MODE_WHITE: "white",
    BULB_MODE_COLOR: "color",
    BULB_MODE_SCENE: "scene",
    BULB_MODE_NIGHT: "night",
}

class State:
    _instances = {}

    @staticmethod
    def default_state(remote_type):
        state = State._instances[remote_type]

        if remote_type == "rgb_cct":
            state.set_bulb_mode(BULB_MODE_COLOR)
        elif remote_type == "cct":
            state.set_bulb_mode(BULB_MODE_WHITE)

        return state

    def __init__(self):
        self._state = None
        self._brightness = None
        self._brightness_color = None
        self._brightness_mode = None
        self._hue = None
        self._saturation = None
        self._mode = None
        self._bulb_mode = None
        self._kelvin = None
        self._night_mode = None

        self._dirty = 1
        self._mqtt_dirty = 0

        self._data_fields = [
            "_state",
            "_brightness",
            "_brightness_color",
            "_brightness_mode",
            "_hue",
            "_saturation",
            "_mode",
            "_bulb_mode",
            "_kelvin",
            "_night_mode",
            "_dirty",
            "_mqtt_dirty",
        ]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self.set_dirty()
        self._state = value

    @state.deleter
    def state(self):
        self.set_dirty()
        self._state = None

    @property
    def brightness(self):
        if self._bulb_mode is None or self._bulb_mode == BULB_MODE_WHITE:
            return self._brightness
        elif self._bulb_mode == BULB_MODE_COLOR:
            return self._brightness_color
        elif self._bulb_mode == BULB_MODE_SCENE:
            return self._brightness_mode

        return None

    @brightness.setter
    def brightness(self, value):
        if self.brightness is not None and self.brightness == value:
            return

        self.set_dirty()

        if self._bulb_mode is None or self._bulb_mode == BULB_MODE_WHITE:
            self._brightness = value
        elif self._bulb_mode == BULB_MODE_COLOR:
            self._brightness_color = value
        elif self._bulb_mode == BULB_MODE_SCENE:
            self._brightness_mode = value

    @property
    def hue(self):
        if self._hue is None:
            return None
        return rescale(self._hue, 360, 255)

    @hue.setter
    def hue(self, value):
        self.set_dirty()
        self._hue = rescale(value, 255, 360)

    @property
    def saturation(self):
        return self._saturation

    @saturation.setter
    def saturation(self, value):
        self.set_dirty()
        self._saturation = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self.set_dirty()
        self._mode = value

    def has_effect(self):
        # only BULB_MODE_COLOR does not have an effect.
        return self._bulb_mode is not None and self._bulb_mode != BULB_MODE_COLOR

    @property
    def kelvin(self):
        return self._kelvin

    @kelvin.setter
    def kelvin(self, value):
        self.set_dirty()
        self._kelvin = value

    @property
    def mireds(self):
        if self._kelvin is None:
            return None
        return white_val_to_mireds(self._kelvin, 100)

    @mireds.setter
    def mireds(self, value):
        self.set_dirty()
        self._kelvin = mireds_to_white_val(value, 100)

    @property
    def bulb_mode(self):
        # Night mode is a transient state.    When power is toggled, the bulb returns
        # to the state it was last in.    To handle this case, night mode state is
        # stored separately.
        if self._night_mode is not None and self._night_mode:
            return BULB_MODE_NIGHT
        else:
            return self._bulb_mode

    @bulb_mode.setter
    def bulb_mode(self, value):
        if self._bulb_mode is not None and self._bulb_mode == value:
            return

        self.set_dirty()

        # As mentioned in isSetBulbMode, NIGHT_MODE is stored separately.
        if value == BULB_MODE_NIGHT:
            self._night_mode = True
        else:
            self._bulb_mode = value
            self._night_mode = False

    @property
    def night_mode(self):
        return self._night_mode

    @night_mode.setter
    def night_mode(self, value):
        if self._night_mode == value:
            return

        self.set_dirty()
        self._night_mode = value

    @property
    def is_dirty(self):
        return self._dirty

    @property
    def is_mqtt_dirty(self):
        return self._mqtt_dirty

    def set_dirty(self):
        self._dirty = True
        self._mqtt_dirty = True

    def clear_dirty(self):
        self._dirty = False

    def clear_mqtt_dirty(self):
        self._mqtt_dirty = False

    def load(self, json_str):
        data = json.loads(json_str)
        for key in data:
            setattr(self, key, data[key])

        self.clear_dirty()

    def dump(self):
        data = {key: getattr(self, key) for key in self._data_fields}
        return json.dumps(data)

    def patch(self, state):
        if "state" in state:
            self.state = state["state"] == "ON"
        if "brightness" in state:
            brightness = rescale(state["brightness"], 100, 255)
            self.brightness = brightness
        if "hue" in state:
            self.hue = state["hue"]
            self.bulb_mode = BULB_MODE_COLOR
        if "saturation" in state:
            self.saturation = state["saturation"]
            self.bulb_mode = BULB_MODE_COLOR
        if "mode" in state:
            self.mode = state["mode"]
            self.bulb_mode = BULB_MODE_SCENE
        if "color_temp" in state:
            self.mireds = state["color_temp"]
            self.bulb_mode = BULB_MODE_WHITE

        # Any changes other than setting mode to night should take device out of
        # night mode.
        self.night_mode = False

        if "command" in state:
            command = state["command"]

            if command == "white_mode":
                self.bulb_mode = BULB_MODE_WHITE
            elif command == "night_mode":
                self.bulb_mode = BULB_MODE_NIGHT

    def apply_color(self, state):
        if self.saturation is None:
            # Default to fully saturated
            saturation = 1
        else:
            saturation = self.saturation / 100.0
        rgb = hsv_to_rgb(self.hue / 360.0, saturation, 1)
        self.apply_rgb_color(state, rgb[0], rgb[1], rgb[2])

    def apply_rgb_color(self, state, red, green, blue):
        state["color"] = {
            "r": red,
            "g": green,
            "b": blue,
        }

    def apply_field(self, partial_state, field):
        if self.state is not None and field == "state" or field == "status":
            if self.state:
                state = "ON"
            else:
                state = "OFF"
            partial_state["state"] = state
            return

        if self.brightness is not None and field == "brightness":
            partial_state["brightness"] = rescale(self.brightness, 255, 100)
            return

        if self.brightness is not None and field == "level":
            partial_state["level"] = self.brightness
            return

        if self.bulb_mode is not None and field == "bulb_mode":
            partial_state["bulb_mode"] = BULB_MODE_NAMES[self.bulb_mode]
            return

        if field == "color" and self.bulb_mode == BULB_MODE_COLOR:
            self.apply_color(partial_state)
            return

        if field == "computed_color":
            if self.bulb_mode == BULB_MODE_COLOR:
                self.apply_color(partial_state)
            elif self.bulb_mode is not None:
                self.apply_rgb_color(partial_state, 255, 255, 255)
            return

        if self.hue is not None and field == "hue" and self.bulb_mode == BULB_MODE_COLOR:
            partial_state["hue"] = self.hue
            return

        if self.saturation is not None and field == "saturation" and self.bulb_mode == BULB_MODE_COLOR:
            partial_state["saturation"] = self.saturation
            return

        if self.mode is not None and field == "mode" and self.bulb_mode == BULB_MODE_SCENE:
            partial_state["mode"] = self.mode
            return

        if field == "effect":
            if self.bulb_mode == BULB_MODE_SCENE:
                partial_state["effect"] = str(self.mode)
            elif self.bulb_mode == BULB_MODE_WHITE:
                partial_state["effect"] = "white_mode"
            elif self.bulb_mode == BULB_MODE_NIGHT:
                partial_state["effect"] = "night_mode"
            return

        if self.mireds is not None and field == "color_temp" and self.bulb_mode == BULB_MODE_WHITE:
            partial_state["color_temp"] = self.mireds
            return

        if self.kelvin is not None and field == "kelvin" and self.bulb_mode == BULB_MODE_WHITE:
            partial_state["kelvin"] = self.kelvin

    def apply_state(self, partial_state, fields=FIELD_NAMES):
        for field in fields:
            self.apply_field(partial_state, field)
