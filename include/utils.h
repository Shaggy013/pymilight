#ifndef _MIUTILS_H
#define _MIUTILS_H

#include <stdint.h>
#include <string.h>

#include <json.hpp>
#include <PacketFormatter.h>

using json = nlohmann::json;

bool ParsePacket(PacketFormatter &formatter, const uint8_t *packet, std::string *device_type, int *device_id, int *group_id, std::string *message);
#endif
