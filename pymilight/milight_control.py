"""Main controller to send/receive packets."""
import logging
import math
import queue
import time
from threading import Thread

import RF24

from pymilight.radio import NRF24MiLightRadio, MiLightRadioConfig
from pymilight.packet_formatter import PyRgbCctPacketFormatter


LOGGER = logging.getLogger(__name__)
ON = True
OFF = False


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


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
            return false;
          }

          return currentRadio->available();
        }

        size_t MiLightClient::read(uint8_t packet[]) {
          if (currentRadio == NULL) {
            return 0;
          }

          size_t length;
          currentRadio->read(packet, length);

          return length;
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
        packet = bytearray(self.radios[self.current_radio].formatter._data())
        self.update_resend_count()
        self.write(packet)
        #TODO currently _data() does this...
        #self.radios[self.current_radio].formatter.reset()

    def update(self, msg):
        print(msg)
    """

    void MiLightClient::setHeld(bool held) {
      currentRemote->packetFormatter->setHeld(held);
    }

    void MiLightClient::updateColorRaw(const uint8_t color) {
      currentRemote->packetFormatter->updateColorRaw(color);
      flushPacket();
    }

    void MiLightClient::updateHue(const uint16_t hue) {
      currentRemote->packetFormatter->updateHue(hue);
      flushPacket();
    }

    void MiLightClient::updateBrightness(const uint8_t brightness) {
      currentRemote->packetFormatter->updateBrightness(brightness);
      flushPacket();
    }

    void MiLightClient::updateMode(uint8_t mode) {
      currentRemote->packetFormatter->updateMode(mode);
      flushPacket();
    }

    void MiLightClient::nextMode() {
      currentRemote->packetFormatter->nextMode();
      flushPacket();
    }

    void MiLightClient::previousMode() {
      currentRemote->packetFormatter->previousMode();
      flushPacket();
    }

    void MiLightClient::modeSpeedDown() {
      currentRemote->packetFormatter->modeSpeedDown();
      flushPacket();
    }
    void MiLightClient::modeSpeedUp() {
      currentRemote->packetFormatter->modeSpeedUp();
      flushPacket();
    }
    """

    def update_status(self, status, group_id=1):
        self.radios[self.current_radio].formatter.update_status(status, group_id)
        self.flush_packet()

    """
    void MiLightClient::updateSaturation(const uint8_t value) {
      currentRemote->packetFormatter->updateSaturation(value);
      flushPacket();
    }

    void MiLightClient::updateColorWhite() {
      currentRemote->packetFormatter->updateColorWhite();
      flushPacket();
    }

    void MiLightClient::enableNightMode() {
      currentRemote->packetFormatter->enableNightMode();
      flushPacket();
    }

    void MiLightClient::pair() {
      currentRemote->packetFormatter->pair();
      flushPacket();
    }

    void MiLightClient::unpair() {
      currentRemote->packetFormatter->unpair();
      flushPacket();
    }

    void MiLightClient::increaseBrightness() {
      currentRemote->packetFormatter->increaseBrightness();
      flushPacket();
    }

    void MiLightClient::decreaseBrightness() {
      currentRemote->packetFormatter->decreaseBrightness();
      flushPacket();
    }

    void MiLightClient::increaseTemperature() {
      currentRemote->packetFormatter->increaseTemperature();
      flushPacket();
    }

    void MiLightClient::decreaseTemperature() {
      currentRemote->packetFormatter->decreaseTemperature();
      flushPacket();
    }

    void MiLightClient::updateTemperature(const uint8_t temperature) {
      currentRemote->packetFormatter->updateTemperature(temperature);
      flushPacket();
    }

    void MiLightClient::command(uint8_t command, uint8_t arg) {
      currentRemote->packetFormatter->command(command, arg);
      flushPacket();
    }

    """
    def update(self, request):
        parsed_status = self.parse_status(request)

        # Always turn on first
        if parsed_status == ON:
            self.update_status(ON)

        """
        if (request.containsKey("command")) {
        this->handleCommand(request["command"]);
        }

        if (request.containsKey("commands")) {
        JsonArray& commands = request["commands"];

        if (commands.success()) {
          for (size_t i = 0; i < commands.size(); i++) {
            this->handleCommand(commands.get<String>(i));
          }
        }
        }

        //Homeassistant - Handle effect
        if (request.containsKey("effect")) {
        this->handleEffect(request["effect"]);
        }

        if (request.containsKey("hue")) {
        this->updateHue(request["hue"]);
        }
        if (request.containsKey("saturation")) {
        this->updateSaturation(request["saturation"]);
        }

        // Convert RGB to HSV
        if (request.containsKey("color")) {
        JsonObject& color = request["color"];

        uint8_t r = color["r"];
        uint8_t g = color["g"];
        uint8_t b = color["b"];
        //If close to white
        if( r > 256 - RGB_WHITE_BOUNDARY && g > 256 - RGB_WHITE_BOUNDARY && b > 256 - RGB_WHITE_BOUNDARY) {
            this->updateColorWhite();
        } else {
          double hsv[3];
          RGBConverter converter;
          converter.rgbToHsv(r, g, b, hsv);

          uint16_t hue = round(hsv[0]*360);
          uint8_t saturation = round(hsv[1]*100);

          this->updateHue(hue);
          this->updateSaturation(saturation);
        }
        }

        if (request.containsKey("level")) {
        this->updateBrightness(request["level"]);
        }
        // HomeAssistant
        if (request.containsKey("brightness")) {
        uint8_t scaledBrightness = Units::rescale(request.get<uint8_t>("brightness"), 100, 255);
        this->updateBrightness(scaledBrightness);
        }

        if (request.containsKey("temperature")) {
        this->updateTemperature(request["temperature"]);
        }
        // HomeAssistant
        if (request.containsKey("color_temp")) {
        this->updateTemperature(
          Units::miredsToWhiteVal(request["color_temp"], 100)
        );
        }

        if (request.containsKey("mode")) {
        this->updateMode(request["mode"]);
        }

        // Raw packet command/args
        if (request.containsKey("button_id") && request.containsKey("argument")) {
        this->command(request["button_id"], request["argument"]);
        }
        """

        # Always turn off last
        if parsed_status == OFF:
            self.update_status(OFF)

    """
    void MiLightClient::handleCommand(const String& command) {
      if (command == "unpair") {
        this->unpair();
      } else if (command == "pair") {
        this->pair();
      } else if (command == "set_white") {
        this->updateColorWhite();
      } else if (command == "night_mode") {
        this->enableNightMode();
      } else if (command == "level_up") {
        this->increaseBrightness();
      } else if (command == "level_down") {
        this->decreaseBrightness();
      } else if (command == "temperature_up") {
        this->increaseTemperature();
      } else if (command == "temperature_down") {
        this->decreaseTemperature();
      } else if (command == "next_mode") {
        this->nextMode();
      } else if (command == "previous_mode") {
        this->previousMode();
      } else if (command == "mode_speed_down") {
        this->modeSpeedDown();
      } else if (command == "mode_speed_up") {
        this->modeSpeedUp();
      }
    }

    void MiLightClient::handleEffect(const String& effect) {
      if (effect == "night_mode") {
        this->enableNightMode();
      } else if (effect == "white" || effect == "white_mode") {
        this->updateColorWhite();
      } else { // assume we're trying to set mode
        this->updateMode(effect.toInt());
      }
    }
    """

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
    import queue
    import threading
    import logging
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
