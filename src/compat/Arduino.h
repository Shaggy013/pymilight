#ifndef _ARDUINO_H
#define _ARDUINO_H

#include <stdint.h>
#include <cstddef>
//#include "WString.h"
#include <time.h>
#include <cstring>

typedef uint8_t byte;

#define min(a,b) ((a)<(b)?(a):(b))
#define max(a,b) ((a)>(b)?(a):(b))
#define constrain(amt,low,high) ((amt)<(low)?(low):((amt)>(high)?(high):(amt)))
//#define round(x)     ((x)>=0?(long)((x)+0.5):(long)((x)-0.5))
//#define millis() (unsigned long)(((float)clock())/CLOCKS_PER_SEC / 1000)
#include <cmath>
#define sprintf_P sprintf
#define strcmp_P strcmp
#define strlen_P strlen

#ifndef PGMSPACE_INCLUDE
#define PGMSPACE_INCLUDE

typedef char __FlashStringHelper;
#define PROGMEM
#define PSTR(s) (s)
#define F(string_literal) (reinterpret_cast<const __FlashStringHelper *>(PSTR(string_literal)))

#define pgm_read_byte(addr) (*(const unsigned char *)(addr))
#define pgm_read_word(addr) (*(const unsigned short *)(addr))
#define pgm_read_dword(addr) (*(const unsigned long *)(addr))
#define pgm_read_float(addr) (*(const float *)(addr))

#define pgm_read_byte_near(addr) pgm_read_byte(addr)
#define pgm_read_word_near(addr) pgm_read_word(addr)
#define pgm_read_dword_near(addr) pgm_read_dword(addr)
#define pgm_read_float_near(addr) pgm_read_float(addr)
#define pgm_read_byte_far(addr) pgm_read_byte(addr)
#define pgm_read_word_far(addr) pgm_read_word(addr)
#define pgm_read_dword_far(addr) pgm_read_dword(addr)
#define pgm_read_float_far(addr) pgm_read_float(addr)

#define memcpy_P(to,from,len) memcpy(to,from,len)
#endif

class Stream {
    public:
        size_t println(const char* val);
        size_t println(char* val);
        size_t println(unsigned int val);
        void begin(uint32_t baud);
        void print(char *val);
};

extern Stream Serial;

#endif
