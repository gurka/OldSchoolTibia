#ifndef TIBIA_CONNECTION_H_
#define TIBIA_CONNECTION_H_

#include "network/connection.h"
#include "packet.h"
#include "utils/xtea.h"

class TibiaConnection : public Connection
{
 public:
  TibiaConnection(SOCKET socket)
    : Connection(socket),
      xteaKeySet_(false)
  {
  }

  bool receive(InPacket* packet);
  bool send(const OutPacket& packet);

  void setXTEAKey(const uint32_t* key);
  void clearXTEAKey() { xteaKeySet_ = false; }

 private:
  bool sendInternal(const OutPacket& packet);

  XTEA xtea_;
  bool xteaKeySet_;
};

#endif  // TIBIA_CONNECTION_H_
