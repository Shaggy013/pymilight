#include <GroupState.h>

const BulbId DEFAULT_BULB_ID;

BulbId::BulbId()
  : deviceId(0),
    groupId(0),
    deviceType(REMOTE_TYPE_UNKNOWN)
{ }

BulbId::BulbId(const BulbId &other)
  : deviceId(other.deviceId),
    groupId(other.groupId),
    deviceType(other.deviceType)
{ }

BulbId::BulbId(
  const uint16_t deviceId, const uint8_t groupId, const MiLightRemoteType deviceType
)
  : deviceId(deviceId),
    groupId(groupId),
    deviceType(deviceType)
{ }

void BulbId::operator=(const BulbId &other) {
  deviceId = other.deviceId;
  groupId = other.groupId;
  deviceType = other.deviceType;
}

bool BulbId::operator==(const BulbId &other) {
  return deviceId == other.deviceId
    && groupId == other.groupId
    && deviceType == other.deviceType;
}
