# distutils: language=c++
from libcpp cimport bool

ctypedef unsigned long size_t
ctypedef unsigned char uint8_t

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

    cdef cppclass PacketFormatter:
        PacketFormatter(const size_t packetLength, const size_t maxPackets) except +
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
        void prepare(unsigned short device_id, unsigned char group_id)
        void format(const unsigned char *packet, char* buffer)
        unsigned long getPacketLength() const
        PacketStream &buildPackets()
