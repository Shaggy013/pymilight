#include <utils.h>


std::string RemoteToString(MiLightRemoteType remote) {
    switch(remote) {
        case REMOTE_TYPE_RGBW:
            return "rgbw";
        case REMOTE_TYPE_CCT:
            return "cct";
        case REMOTE_TYPE_RGB_CCT:
            return "rgb_cct";
        case REMOTE_TYPE_RGB:
            return "rgb";
        case REMOTE_TYPE_FUT089:
            return "fut89";
        case REMOTE_TYPE_UNKNOWN:
        default:
            return "unknown";
    }
}

bool ParsePacket(PacketFormatter &formatter, const uint8_t *packet, std::string *device_type, int *device_id, int *group_id, std::string *message) {
    BulbId bulb;
    JsonObject jobj = json::object();
    bulb = formatter.parsePacket(packet, jobj, nullptr);
    (*device_type) = RemoteToString(bulb.deviceType);
    (*device_id) = bulb.deviceId;
    (*group_id) = bulb.groupId;
    (*message) = jobj.dump();
    return true;
}
