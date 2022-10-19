#ifndef CONNECTION_H_
#define CONNECTION_H_

#include <cstdint>

#include "ws2_32.h"

class Connection
{
 public:
  Connection(SOCKET socket) : socket_(socket)
  {
  }

  virtual ~Connection() { close(); }

  bool connected() { return socket_ != INVALID_SOCKET; }
  void close();

  bool read(uint8_t* buffer, int length);
  bool write(const uint8_t* buffer, int length);

 private:
  SOCKET socket_;
};

#endif  // CONNECTION_H_
