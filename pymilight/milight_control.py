"""Main controller to send/receive packets."""
import logging
import math
import queue
import time
from threading import Thread

import RF24

from pymilight.radio import NRF24MiLightRadio, MiLightRadioConfig
from pymilight.packet_formatter import PyRgbCctPacketFormatter
from pymilight.rgb_converter import rgb_to_hsv

LOGGER = logging.getLogger(__name__)
ON = True
OFF = False
# MiLight CCT bulbs range from 2700K-6500K, or ~370.3-153.8 mireds.
COLOR_TEMP_MAX_MIREDS = 370
COLOR_TEMP_MIN_MIREDS = 153


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def rescale(val, new_max, old_max):
    return round(val * (new_max / float(old_max)))


def mireds_to_white_val(mireds, max_val=255):
    return rescale(
        constrain(mireds, COLOR_TEMP_MIN_MIREDS, COLOR_TEMP_MAX_MIREDS) - COLOR_TEMP_MIN_MIREDS,
        max_val,
        (COLOR_TEMP_MAX_MIREDS - COLOR_TEMP_MIN_MIREDS)
    )


class MiLightController(Thread):
    DEFAULT_RESEND_COUNT = 10
    RGB_WHITE_BOUNDARY = 40
    def __init__(self, inbound_queue, outbound_queue, shutdown_event, *args, **kwargs):
        super(MiLightController, self).__init__(*args, **kwargs)
        self.inbound_queue = inbound_queue
        self.outbound_queue = outbound_queue
        self.shutdown_event = shutdown_event

        self.base_resend_count = MiLightController.DEFAULT_RESEND_COUNT
        self.current_resend_count = self.base_resend_count
        self.current_radio = None
        self.throttle_threshold = 0.200
        self.throttle_sensitivity = 0
        self.throttle_multiplier = 1
        self.packet_repeat_minimum = 3
        self.last_send = 0

        rf = RF24.RF24(RF24.RPI_V2_GPIO_P1_15, RF24.BCM2835_SPI_CS0, RF24.BCM2835_SPI_SPEED_8MHZ)
        self.radios = {
            name: NRF24MiLightRadio(rf, radio_config)
            for name, radio_config in MiLightRadioConfig.ALL_RADIOS.items()
        }

        formatter = PyRgbCctPacketFormatter()
        for radio in self.radios.values():
            radio.formatter = formatter

    def run(self):
        self.begin()
        while True:
            # Bail if given event to do so.
            if self.shutdown_event.is_set():
                return

            # Handle incoming commands - probably from MQTT.
            try:
                command = self.inbound_queue.get(block=False)
                self.process_command(command)
                self.inbound_queue.task_done()
            except queue.Empty:
                pass
            except Exception as err:
                LOGGER.critical("Failed to process command: %s. Error was %s.", command, err)

            # Handle recieved radio packets.
            try:
                state_message = self.process_radio()
            except Exception as err:
                LOGGER.critical("Error recieveing from radio: %s", err)
            if state_message:
                self.outbound_queue.put(state_message)

            time.sleep(0.5)

    def process_radio(self):
        """TODO
        bool MiLightClient::available() {
          if (currentRadio == NULL) {
            return false
          }

          return currentRadio->available()
        }

        size_t MiLightClient::read(uint8_t packet[]) {
          if (currentRadio == NULL) {
            return 0
          }

          size_t length
          currentRadio->read(packet, length)

          return length
        }
        """
        return None

    def process_command(self, command):
        device_type, device_id, group_id, msg = command

        self.set_bulb(device_type, device_id, group_id)
        self.update(msg)

    def set_bulb(self, device_type, device_id, group_id):
        self.set_current_radio(device_type)
        self.radios[self.current_radio].formatter.prepare(device_id, group_id)

    def begin(self):
        for radio in self.radios.values():
            radio.begin()
        self.set_current_radio(list(self.radios.keys())[0])

    def set_current_radio(self, device_type):
        if device_type not in self.radios:
            raise Exception("Invalid device type")
        if self.current_radio != device_type:
            LOGGER.info("Setting radio for %s.", device_type)
            self.current_radio = device_type
            self.radios[self.current_radio].configure()

    def set_resend_count(self, resend_count):
        self.base_resend_count = resend_count
        self.current_resend_count = resend_count
        self.throttle_multiplier = math.ceil(
            (self.throttle_sensitivity / 1000.0) * self.base_resend_count
        )

    def write(self, packet):
        LOGGER.info("Sending packet (%d repeats): 0x%s", self.current_resend_count, packet.hex())

        for _ in range(self.current_resend_count):
            self.radios[self.current_radio].write(packet)

    def update_resend_count(self):
        now = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        since_last_send = now - self.last_send
        x = (since_last_send - self.throttle_threshold)
        delta = x * self.throttle_multiplier

        self.current_resend_count = constrain(
            self.current_resend_count + delta,
            self.packet_repeat_minimum,
            self.base_resend_count
        )
        self.last_send = now

    def flush_packet(self):
        packet = self.radios[self.current_radio].formatter.data()
        self.update_resend_count()
        self.write(packet)
        #TODO currently _data() does this...
        #self.radios[self.current_radio].formatter.reset()

    def update(self, request):
        formatter = self.radios[self.current_radio].formatter
        parsed_status = self.parse_status(request)

        # Always turn on first
        if parsed_status == ON:
            formatter.update_status(ON)
            self.flush_packet()

        commands = []
        if "command" in request:
            commands = [request["command"]]

        if "commands" in request:
            commands = request["commands"]

        for command in commands:
            self.handle_command(command)

        # /omeassistant - Handle effect
        if "effect" in request:
            self.handle_effect(request["effect"])

        if "hue" in request:
            formatter.update_hue(request["hue"])
            self.flush_packet()

        if "saturation" in request:
            formatter.update_saturation(request["saturation"])
            self.flush_packet()

        # Convert RGB to HSV
        if "color" in request:
            color = request["color"]

            red = color["r"]
            green = color["g"]
            blue = color["b"]
            # If close to white
            if red > 256 - self.RGB_WHITE_BOUNDARY and \
               green > 256 - self.RGB_WHITE_BOUNDARY and \
               blue > 256 - self.RGB_WHITE_BOUNDARY:
                formatter.update_color_white()
                self.flush_packet()
            else:
                hsv = rgb_to_hsv(red, green, blue)

                hue = int(round(hsv[0] * 360, 0))
                saturation = int(round(hsv[1] * 100, 0))

                formatter.update_hue(hue)
                self.flush_packet()
                formatter.update_saturation(saturation)
                self.flush_packet()

        if "level" in request:
            formatter.update_brightness(request["level"])
            self.flush_packet()

        # HomeAssistant
        if "brightness" in request:
            scaled_brightness = rescale(int(request["brightness"]), 100, 255)
            formatter.update_brightness(scaled_brightness)
            self.flush_packet()

        if "temperature" in request:
            formatter.update_temperature(request["temperature"])
            self.flush_packet()

        # HomeAssistant
        if "color_temp" in request:
            formatter.update_temperature(
                mireds_to_white_val(request["color_temp"], 100)
            )
            self.flush_packet()

        if "mode" in request:
            formatter.update_mode(request["mode"])
            self.flush_packet()

        # Raw packet command/args
        if "button_id" in request and "argument" in request:
            formatter.command(request["button_id"], request["argument"])
            self.flush_packet()

        # Always turn off last
        if parsed_status == OFF:
            formatter.update_status(OFF)
            self.flush_packet()

    def handle_command(self, command):
        formatter = self.radios[self.current_radio].formatter
        if command == "unpair":
            formatter.unpair()
        elif command == "pair":
            formatter.pair()
        elif command == "set_white":
            formatter.update_color_white()
        elif command == "night_mode":
            formatter.enable_night_mode()
        elif command == "level_up":
            formatter.increase_brightness()
        elif command == "level_down":
            formatter.decrease_brightness()
        elif command == "temperature_up":
            formatter.increase_temperature()
        elif command == "temperature_down":
            formatter.decrease_temperature()
        elif command == "next_mode":
            formatter.next_mode()
        elif command == "previous_mode":
            formatter.previous_mode()
        elif command == "mode_speed_down":
            formatter.mode_speed_down()
        elif command == "mode_speed_up":
            formatter.mode_speed_up()
        self.flush_packet()

    def handle_effect(self, effect):
        formatter = self.radios[self.current_radio].formatter
        if effect == "night_mode":
            formatter.enable_night_mode()
        elif effect == "white" or effect == "white_mode":
            formatter.update_color_white()
        else: # assume we're trying to set mode
            formatter.update_mode(int(effect))
        self.flush_packet()

    def parse_status(self, request):
        if "status" in request:
            status = request["status"]
        elif "state" in request:
            status = request["state"]
        else:
            return OFF

        if status.lower() == "on" or status.lower() == "true":
            return ON
        return OFF


if __name__ == '__main__':
    import threading
    logging.basicConfig(level=logging.DEBUG)
    inbound = queue.Queue()
    outbound = queue.Queue()
    shutdown = threading.Event()

    controller = MiLightController(inbound, outbound, shutdown)
    controller.start()

    inbound.put(("rgb_cct", 0x1, 1, {"status": "on"}))
    while True:
        if inbound.empty():
            shutdown.set()
            controller.join()
            break
        time.sleep(1)
