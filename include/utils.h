#ifndef _MIUTILS_H
#define _MIUTILS_H

#include <stdint.h>
#include <string.h>

#include <json.hpp>
#include <PacketFormatter.h>

using json = nlohmann::json;

std::string ParsePacket(PacketFormatter &formatter, const uint8_t *packet);
#endif
