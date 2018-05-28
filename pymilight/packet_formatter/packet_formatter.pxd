# distutils: language=c++
from libcpp cimport bool

ctypedef unsigned long size_t
ctypedef unsigned char uint8_t
ctypedef unsigned short uint16_t

cdef extern from "MiLightConstants.h":
    cdef enum MiLightStatus:
        ON,
        OFF

cdef extern from "PacketFormatter.h":
    cdef cppclass PacketStream:
        PacketStream()
        uint8_t* next()
        bool hasNext()
        uint8_t* packetStream
        size_t numPackets
        size_t packetLength
        size_t currentPacket

    cdef cppclass PacketFormatter:
        PacketFormatter(const size_t packetLength, const size_t maxPackets) except +
        bool canHandle(const uint8_t *packet, const size_t length)

        void updateStatus(MiLightStatus status)
        void updateStatus(MiLightStatus status, uint8_t groupId)
        void command(uint8_t command, uint8_t arg)

        void setHeld(bool held)

        # Mode
        void updateMode(uint8_t value)
        void modeSpeedDown()
        void modeSpeedUp()
        void nextMode()
        void previousMode()

        void pair()
        void unpair()

        # Color
        void updateHue(uint16_t value)
        void updateColorRaw(uint8_t value)
        void updateColorWhite()

        # White temperature
        void increaseTemperature()
        void decreaseTemperature()
        void updateTemperature(uint8_t value)

        # Brightness
        void updateBrightness(uint8_t value)
        void increaseBrightness()
        void decreaseBrightness()
        void enableNightMode()

        void updateSaturation(uint8_t value)

        void reset()

        PacketStream& buildPackets()
        void prepare(uint16_t deviceId, uint8_t groupId)
        void format(const uint8_t *packet, char *buffer)

        size_t getPacketLength() const
