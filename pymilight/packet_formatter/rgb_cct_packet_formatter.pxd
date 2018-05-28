# distutils: language=c++
from libcpp cimport bool
from libcpp.string cimport string

from .packet_formatter cimport PacketStream, MiLightStatus, size_t
from .v2_packet_formatter cimport V2PacketFormatter

cdef extern from "RgbCctPacketFormatter.h":
    cdef cppclass RgbCctPacketFormatter(V2PacketFormatter):
        RgbCctPacketFormatter() except +
