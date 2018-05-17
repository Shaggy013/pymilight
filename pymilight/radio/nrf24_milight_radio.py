"""
Adapated from code from henryk
"""
import logging

from pymilight.radio.pl1167_nrf24 import PL1167_nRF24


LOGGER = logging.getLogger(__name__)


def get_packet_id(packet, packet_length):
    return (packet[1] << 8) | packet[packet_length - 1]


class NRF24MiLightRadio(object):
    def __init__(self, rf, config):
        self._pl1167 = PL1167_nRF24(rf)
        self._config = config
        self._prev_packet_id = None
        self._packet = []
        self._out_packet = []
        self._waiting = False
        self._dupes_received = 0

    def begin(self):
        retval = self._pl1167.open()
        if retval < 0:
            return retval

        retval = self.configure()
        if retval < 0:
            return retval

        self.available()

        return 0

    def configure(self):
        retval = self._pl1167.setCRC(True)
        if retval < 0:
            return retval

        retval = self._pl1167.setPreambleLength(3)
        if retval < 0:
            return retval

        retval = self._pl1167.setTrailerLength(4)
        if retval < 0:
            return retval

        retval = self._pl1167.setSyncword(self._config.syncword0, self._config.syncword3)
        if retval < 0:
            return retval

        # +1 to be able to buffer the length
        retval = self._pl1167.setMaxPacketLength(self._config.packetLength + 1)
        if retval < 0:
            return retval

        return 0

    def available(self):
        if self._waiting:
            LOGGER.info("_waiting")
            return True

        if self._pl1167.receive(self._config.channels[0]) > 0:
            LOGGER.info("NRF24MiLightRadio - received packet!")
            packet_length = len(self._packet)
            if self._pl1167.readFIFO(self._packet, packet_length) < 0:
                return False

            LOGGER.info("NRF24MiLightRadio - Checking packet length (expecting %d, is %d)", self._packet[0] + 1, packet_length)
            if packet_length == 0 or packet_length != self._packet[0] + 1:
                return False

            packet_id = get_packet_id(self._packet, packet_length)
            LOGGER.info("Packet id: %d", packet_id)
            if packet_id == self._prev_packet_id:
                self._dupes_received += 1
            else:
                self._prev_packet_id = packet_id
                self._waiting = True
        return self._waiting

    def read(self, frame_length):
        if not self._waiting:
            frame_length = 0
            return -1

        if frame_length > len(self._packet) - 1:
            frame_length = len(self._packet) - 1

        if frame_length > self._packet[0]:
            frame_length = self._packet[0]

        frame = self._packet[frame_length + 1]
        self._waiting = False

        return frame

    def write(self, frame):
        if len(frame) > len(self._out_packet) - 1:
            return -1

        self._out_packet = [len(frame)] + frame

        retval = self.resend()
        if retval < 0:
            return retval
        return len(frame)

    def resend(self):
        for channel in self._config.channels:
            self._pl1167.writeFIFO(self._out_packet, self._out_packet[0] + 1)
            self._pl1167.transmit(channel)
        return 0
