#include <stddef.h>
#include <inttypes.h>
#include <MiLightConstants.h>

#ifndef _BULB_ID_H
#define _BULB_ID_H

struct BulbId {
  uint16_t deviceId;
  uint8_t groupId;
  MiLightRemoteType deviceType;

  BulbId();
  BulbId(const BulbId& other);
  BulbId(const uint16_t deviceId, const uint8_t groupId, const MiLightRemoteType deviceType);
  bool operator==(const BulbId& other);
  void operator=(const BulbId& other);
};

extern const BulbId DEFAULT_BULB_ID;

struct GroupStateStore {};
#endif
