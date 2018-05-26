#include <utils.h>

std::string ParsePacket(PacketFormatter &formatter, const uint8_t *packet) {
    JsonObject jobj = json::object();
    formatter.parsePacket(packet, jobj, nullptr);
    return jobj.dump();
}
