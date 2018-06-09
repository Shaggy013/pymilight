# distutils: language=c++
# distutils: sources = vendor/RGBConverter/RGBConverter.cpp

ctypedef unsigned char byte

cdef extern from "RGBConverter/RGBConverter.h":
    cdef cppclass RGBConverter:
        void rgbToHsl(byte r, byte g, byte b, double hsl[])
        void hslToRgb(double h, double s, double l, byte rgb[])
        void rgbToHsv(byte r, byte g, byte b, double hsv[])
        void hsvToRgb(double h, double s, double v, byte rgb[])

def rgb_to_hsl(int red, int green, int blue):
    cdef double hsl[3]
    cdef RGBConverter converter
    converter.rgbToHsl(red, green, blue, hsl)
    return list(hsl)

def rgb_to_hsv(int red, int green, int blue):
    cdef double hsv[3]
    cdef RGBConverter converter
    converter.rgbToHsv(red, green, blue, hsv)
    return list(hsv)

def hsv_to_rgb(int hue, int saturation, int value):
    cdef byte rgb[3]
    cdef RGBConverter converter
    converter.hsvToRgb(hue, saturation, value, rgb)
    return list(rgb)
