#include "connection.h"

void Connection::close()
{
  if (connected())
  {
    WS2_32::closesocket(socket_);
    socket_ = INVALID_SOCKET;
  }
}


bool Connection::read(uint8_t* buffer, int length)
{
  if (socket_ == INVALID_SOCKET)
  {
    return false;
  }

  int bytesLeft = length;
  while (bytesLeft > 0)
  {
    int ret = WS2_32::recv(socket_,
                           reinterpret_cast<char*>(buffer + (length - bytesLeft)),
                           bytesLeft,
                           0);

    if (ret == SOCKET_ERROR || ret == 0)
    {
      WS2_32::closesocket(socket_);
      return false;
    }

    bytesLeft -= ret;
  }

  return true;
}

bool Connection::write(const uint8_t* buffer, int length)
{
  if (socket_ == INVALID_SOCKET)
  {
    return false;
  }

  int bytesLeft = length;
  while (bytesLeft > 0)
  {
    int ret = WS2_32::send(socket_,
                           reinterpret_cast<const char*>(buffer + (length - bytesLeft)),
                           bytesLeft,
                           0);

    if (ret == SOCKET_ERROR)
    {
      WS2_32::closesocket(socket_);
      return false;
    }

    bytesLeft -= ret;
  }

  return true;
}
