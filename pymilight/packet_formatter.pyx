# distutils: language=c++
# distutils: sources = src/MiLight/PacketFormatter.cpp src/MiLight/RgbCctPacketFormatter.cpp src/MiLight/V2RFEncoding.cpp src/MiLight/V2PacketFormatter.cpp src/compat/Arduino.cpp
from cython.operator import dereference
from libcpp cimport bool
from libc.stdio cimport sprintf

cdef extern from "MiLightConstants.h":
    cdef enum MiLightStatus:
        ON,
        OFF

cdef extern from "PacketFormatter.h":
    cdef cppclass PacketStream:
        PacketStream()
        unsigned char* next()
        bool hasNext()
        unsigned char* packetStream
        unsigned long numPackets
        unsigned long packetLength
        unsigned long currentPacket

cdef extern from "RgbCctPacketFormatter.h":
    cdef cppclass RgbCctPacketFormatter:
        RgbCctPacketFormatter() except +
        void updateStatus(MiLightStatus status, unsigned char group);
        void updateBrightness(unsigned char value)
        void updateHue(unsigned short value)
        void updateColorRaw(unsigned char value)
        void updateColorWhite()
        void updateTemperature(unsigned char value)
        void updateSaturation(unsigned char value)
        void enableNightMode()

        void modeSpeedDown()
        void modeSpeedUp()
        void updateMode(unsigned char mode)
        void nextMode()
        void previousMode()
        void reset()
        void format(const unsigned char *packet, char* buffer)
        unsigned long getPacketLength() const
        PacketStream &buildPackets()

cdef class PyPacketStream:
    cdef PacketStream *c_stream

    def __next__(self):
        if self.c_stream[0].hasNext():
            return self.c_stream[0].next()
        raise StopIteration

    def _print_buffer(self):
        for i in range(self.c_stream[0].numPackets):
            print(self.c_stream[0].packetStream[i])


cdef PyPacketStream create(PacketStream* stream):
    obj = PyPacketStream()
    obj.c_stream = stream
    return obj

cdef class PyRgbCctPacketFormatter:
    cdef RgbCctPacketFormatter c_formatter      # hold a C++ instance which we're wrapping

    def updateColorWhite(self):
        self.c_formatter.updateColorWhite()
        return self._data()

    def on(self):
        self.c_formatter.updateStatus(MiLightStatus.ON, 1)
        return self._data()

    def off(self):
        self.c_formatter.updateStatus(MiLightStatus.OFF, 1)
        return self._data()

    def _data(self, reset=True):
        cdef PacketStream stream
        stream = self.c_formatter.buildPackets()
        res = [stream.packetStream[i] for i in range(stream.numPackets * stream.packetLength)]
        if reset:
            self.c_formatter.reset()
        return res

    def format(self):
        cdef char response[200]
        cdef char* responseBuffer = response

        responseBuffer += sprintf(
          responseBuffer,
          "\n%s packet received (%d bytes):\n",
          "NAME",
          self.c_formatter.getPacketLength()
        )
        cdef PacketStream stream
        stream = self.c_formatter.buildPackets()
        self.c_formatter.format(stream.packetStream, responseBuffer)
        return (<bytes>response).decode('ascii')
