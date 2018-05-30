# distutils: language=c++
# distutils: sources = src/MiLight/utils.cpp src/compat/Arduino.cpp src/MiLight/PacketFormatter.cpp src/MiLight/GroupState.cpp src/MiLight/RgbCctPacketFormatter.cpp src/MiLight/V2PacketFormatter.cpp  src/MiLight/V2RFEncoding.cpp
from cython.operator import dereference
from libcpp cimport bool
from libcpp.string cimport string
from libc.stdio cimport sprintf
import json

from .packet_formatter cimport PacketStream as C_PacketStream
from .packet_formatter cimport MiLightStatus, PacketStream
from .v2_packet_formatter cimport V2PacketFormatter
from .rgb_cct_packet_formatter cimport RgbCctPacketFormatter


cdef extern from "utils.h":
    cdef string ParsePacket(PacketFormatter formatter, unsigned char *packet)


cdef class PyPacketStream:
    cdef C_PacketStream *c_stream

    def __next__(self):
        if self.c_stream[0].hasNext():
            return self.c_stream[0].next()
        raise StopIteration

    def _print_buffer(self):
        for i in range(self.c_stream[0].numPackets):
            print(self.c_stream[0].packetStream[i])


cdef PyPacketStream create(C_PacketStream* stream):
    obj = PyPacketStream()
    obj.c_stream = stream
    return obj


cdef class PyPacketFormatter:
    cdef PacketFormatter *c_pf_obj;

    def reset(self):
        self.c_pf_obj[0].reset()

    def prepare(self, int device_id, int group_id):
        self.c_pf_obj[0].prepare(device_id, group_id)

    def data(self, reset=True):
        cdef PacketStream stream
        stream = self.c_pf_obj[0].buildPackets()
        res = bytearray([stream.packetStream[i] for i in range(stream.numPackets * stream.packetLength)])
        if reset:
            self.c_pf_obj[0].reset()
        return res

    def format(self):
        cdef char response[200]
        cdef char* responseBuffer = response

        responseBuffer += sprintf(
          responseBuffer,
          "\n%s packet received (%d bytes):\n",
          "NAME",
          self.c_pf_obj[0].getPacketLength()
        )
        cdef PacketStream stream
        stream = self.c_pf_obj[0].buildPackets()
        self.c_pf_obj[0].format(stream.packetStream, responseBuffer)
        self.reset()
        return (<bytes>response).decode('ascii')

    def parse(self, bytearray packet):
        cdef unsigned char *packet_array = packet
        cdef string raw_json
        raw_json = ParsePacket(self.c_pf_obj[0], packet)
        return json.loads(raw_json.decode('utf-8'))

    def command(self, int command, int arg):
        self.c_pf_obj[0].command(command, arg)
        return self.data()

    def set_held(self, bool is_held):
        self.c_pf_obj[0].setHeld(is_held)

    # Status
    def update_status(self, bool status, int group_id=-1):
        cdef MiLightStatus milight_status
        if status:
            milight_status = MiLightStatus.ON
        else:
            milight_status = MiLightStatus.OFF
        if group_id >= 0:
            self.c_pf_obj[0].updateStatus(milight_status, group_id)
        else:
            self.c_pf_obj[0].updateStatus(milight_status)
        return self.data()

    def pair(self):
        self.c_pf_obj[0].pair()
        return self.data()

    def unpair(self):
        self.c_pf_obj[0].unpair()
        return self.data()
        
    # Mode
    def update_mode(self, int value):
        self.c_pf_obj[0].updateMode(value)
        return self.data()

    def mode_speed_down(self):
        self.c_pf_obj[0].modeSpeedDown()
        return self.data()

    def mode_speed_up(self):
        self.c_pf_obj[0].modeSpeedUp()
        return self.data()

    def next_mode(self):
        self.c_pf_obj[0].nextMode()
        return self.data()

    def previous_mode(self):
        self.c_pf_obj[0].previousMode()
        return self.data()

    # Color
    def update_hue(self, int value):
        self.c_pf_obj[0].updateHue(value)
        return self.data()

    def update_color_raw(self, int value):
        self.c_pf_obj[0].updateColorRaw(value)
        return self.data()

    def update_color_white(self):
        self.c_pf_obj[0].updateColorWhite()
        return self.data()

    def update_saturation(self, int value):
        self.c_pf_obj[0].updateSaturation(value)
        return self.data()

    # White temperature
    def increase_temperature(self):
        self.c_pf_obj[0].increaseTemperature()
        return self.data()

    def decrease_temperature(self):
        self.c_pf_obj[0].decreaseTemperature()
        return self.data()

    def update_temperature(self, int value):
        self.c_pf_obj[0].updateTemperature(value)
        return self.data()

    # Brightness
    def update_brightness(self, int value):
        self.c_pf_obj[0].updateBrightness(value)
        return self.data()

    def increase_brightness(self):
        self.c_pf_obj[0].increaseBrightness()
        return self.data()

    def decrease_brightness(self):
        self.c_pf_obj[0].decreaseBrightness()
        return self.data()

    def enable_night_mode(self):
        self.c_pf_obj[0].enableNightMode()
        return self.data()


cdef class PyV2PacketFormatter(PyPacketFormatter):
    cdef V2PacketFormatter *c_v2_pf_obj


cdef class PyRgbCctPacketFormatter(PyV2PacketFormatter):
    cdef RgbCctPacketFormatter c_formatter      # hold a C++ instance which we're wrapping

    def __cinit__(self):
        self.c_v2_pf_obj = &self.c_formatter
        self.c_pf_obj = &self.c_formatter

    def on(self):
        self.c_formatter.prepare(0x02, 1)
        self.c_formatter.updateStatus(MiLightStatus.ON, 1)
        return self.data()

    def off(self):
        self.c_formatter.prepare(0x02, 1)
        self.c_formatter.updateStatus(MiLightStatus.OFF, 1)
        return self.data()

