"""
PL1167_nRF24.py

Created on: 20 May 2018
Author: dmkent

Port of PL1167_nRF24 by henryk.
 https://github.com/henryk/openmili
 Optimizations by khamann:
 https://github.com/khmann/esp8266_milight_hub/blob/e3600cef75b102ff3be51a7afdb55ab7460fe712/lib/MiLight/PL1167_nRF24.cpp
"""
import logging

import RF24


LOGGER = logging.getLogger(__name__)
CRC_POLY = 0x8408


def calc_crc(data):
    state = 0
    for cur_byte in data:
        for _ in range(8):
            if (cur_byte ^ state) & 0x01:
                state = (state >> 1) ^ CRC_POLY
            else:
                state = state >> 1
        cur_byte = cur_byte >> 1
    return state

def reverse_bits(data):
    result = 0
    for _ in range(8):
        result <<= 1
        result |= data & 1
        data >>= 1
    return result


class PL1167_nRF24(object):
    def __init__(self, radio):
        self._radio = radio
        self._crc = False
        self._preambleLength = 1
        self._syncword0 = 0
        self._syncword3 = 0
        self._syncwordLength = 4
        self._trailerLength = 4
        self._maxPacketLength = 8

        self._channel = 0

        self._nrf_pipe = []

        self._packet_length = 0
        self._receive_length = 0
        self._preamble = 0
        self._packet = []
        self._received = False

    def open(self):
        self._radio.begin()
        self._radio.setAutoAck(False)
        self._radio.setPALevel(RF24.RF24_PA_MAX)
        self._radio.setDataRate(RF24.RF24_1MBPS)
        self._radio.disableCRC()

        self._syncwordLength = 5
        self._radio.setAddressWidth(self._syncwordLength)

        return self.recalc_parameters()

    def recalc_parameters(self):
        packet_length = self._maxPacketLength + 2
        nrf_address_pos = self._syncwordLength

        nrf_address_pos -= 1
        if self._syncword0 & 0x01:
            self._nrf_pipe[nrf_address_pos] = reverse_bits(((self._syncword0 << 4) & 0xf0) + 0x05)
        else:
            self._nrf_pipe[nrf_address_pos] = reverse_bits(((self._syncword0 << 4) & 0xf0) + 0x0a)

        nrf_address_pos -= 1
        self._nrf_pipe[nrf_address_pos] = reverse_bits((self._syncword0 >> 4) & 0xff)
        nrf_address_pos -= 1
        self._nrf_pipe[nrf_address_pos] = reverse_bits(
            ((self._syncword0 >> 12) & 0x0f) +
            ((self._syncword3 << 4) & 0xf0)
        )
        nrf_address_pos -= 1
        self._nrf_pipe[nrf_address_pos] = reverse_bits(
            (self._syncword3 >> 4) & 0xff
        )
        nrf_address_pos -= 1
        # kh: spi says trailer is always "5" ?
        self._nrf_pipe[nrf_address_pos] = reverse_bits(((self._syncword3 >> 12) & 0x0f) + 0x50)

        self._receive_length = packet_length

        self._radio.openWritingPipe(self._nrf_pipe)
        self._radio.openReadingPipe(1, self._nrf_pipe)

        self._radio.setChannel(2 + self._channel)

        self._radio.setPayloadSize(packet_length)
        return 0

    def setPreambleLength(self, preambleLength):
        return 0

    def setSyncword(self, syncword0, syncword3):
        self._syncwordLength = 5
        self._syncword0 = syncword0
        self._syncword3 = syncword3
        return self.recalc_parameters()

    def setTrailerLength(self, trailerLength):
        return 0

    def setCRC(self, crc):
        self._crc = crc
        return self.recalc_parameters()

    def setMaxPacketLength(self, maxPacketLength):
        self._maxPacketLength = maxPacketLength
        return self.recalc_parameters()

    def receive(self, channel):
        if channel != self._channel:
            self._channel = channel
            retval = self.recalc_parameters()
            if retval < 0:
                return retval

        self._radio.startListening()
        if self._radio.available():
            LOGGER.info("Radio is available")
            self.internal_receive()

        if self._received:
            if self._packet_length > 0:
                LOGGER.info("Received packet (len = %d)!", self._packet_length)
            return self._packet_length
        return 0

    def readFIFO(self, data_length):
        if data_length > self._packet_length:
            data_length = self._packet_length
        data = self._packet[:data_length]
        self._packet_length -= data_length
        if self._packet_length:
            self._packet = self._packet[data_length + 1:]
        return data

    def writeFIFO(self, data):
        if len(data) > self._maxPacketLength:
            data = data[:self._maxPacketLength]

        self._packet = data[:]
        self._packet_length = len(data)
        self._received = False

        return len(data)

    def transmit(self, channel):
        if channel != self._channel:
            self._channel = channel
            retval = self.recalc_parameters()
            if retval < 0:
                return retval

        self._radio.stopListening()
        tmp = [''] * self._maxPacketLength
        outp = 0

        if self._crc:
            crc = calc_crc(self._packet)

        for inp in range(len(self._packet) + (self._crc * 2) + 1):
            if inp < len(self._packet):
                tmp[outp] = reverse_bits(self._packet[inp])
                outp += 1
            elif self._crc and inp < len(self._packet) + 2:
                tmp[outp] = reverse_bits((crc >> ((inp - len(self._packet)) * 8)) & 0xff)
                outp += 1

        self._radio.write(tmp, outp)
        return 0

    def internal_receive(self):
        outp = 0

        self._receive_length = self._radio.getDynamicPayloadSize()
        tmp = self._radio.read(self._receive_length)

        # HACK HACK HACK: Reset radio
        self.open()

        LOGGER.info("Packet received: ")
        for i in range(self._receive_length):
            LOGGER.info("%02X", tmp[i])

        for inp in range(self._receive_length):
            tmp[outp] = reverse_bits(tmp[inp])
            outp += 1

        LOGGER.info("Packet transformed: ")
        for i in range(self._receive_length):
            LOGGER.info("%02X", tmp[i])

        if self._crc:
            if outp < 2:
                LOGGER.info("Failed CRC: outp < 2")
                return 0
            crc = calc_crc(tmp[:outp - 2])
            if ((crc & 0xff) != tmp[outp - 2]) or (((crc >> 8) & 0xff) != tmp[outp - 1]):
                recv_crc = ((tmp[outp - 2] & 0xFF) << 8) | (tmp[outp - 1] & 0xFF)
                LOGGER.info("Failed CRC: expected %d, got %d", crc, recv_crc)
                return 0
            outp -= 2

        self._packet = tmp[:outp]
        self._packet_length = outp
        self._received = True

        LOGGER.info("Successfully parsed packet of length %d", self._packet_length)
        return outp
