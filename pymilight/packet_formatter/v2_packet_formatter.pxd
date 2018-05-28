# distutils: language=c++
from .packet_formatter cimport PacketFormatter, MiLightStatus, size_t, uint8_t

cdef extern from "V2PacketFormatter.h":
    cdef cppclass V2PacketFormatter(PacketFormatter):
        V2PacketFormatter(uint8_t protocolId, uint8_t packetLen) except +
        void finalizePacket(uint8_t* packet)
        uint8_t groupCommandArg(MiLightStatus status, uint8_t groupId)
