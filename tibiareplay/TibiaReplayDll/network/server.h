#ifndef SERVER_H_
#define SERVER_H_

#include "ws2_32.h"

template<typename Connection>
class Server
{
 public:
  Server(unsigned short port)
    : port_(port),
      socket_(INVALID_SOCKET)
  {
  }

  virtual ~Server()
  {
    if (socket_ != INVALID_SOCKET)
    {
      WS2_32::closesocket(socket_);
      socket_ = INVALID_SOCKET;
    }
  }

  Connection accept()
  {
    // Setup listen socket if not already setup
    if (socket_ == INVALID_SOCKET)
    {
      // Create and setup listen socket
      socket_ = WS2_32::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
      if (socket_ == INVALID_SOCKET)
      {
        return false;
      }

      sockaddr_in service;
      service.sin_family = AF_INET;
      service.sin_addr.s_addr = WS2_32::inet_addr("127.0.0.1");
      service.sin_port = WS2_32::htons(port_);

      if (WS2_32::bind(socket_, (SOCKADDR*)&service, sizeof(service)) == SOCKET_ERROR)
      {
        WS2_32::closesocket(socket_);
        socket_ = INVALID_SOCKET;
        return false;
      }

      if (WS2_32::listen(socket_, 8) == SOCKET_ERROR)
      {
        WS2_32::closesocket(socket_);
        socket_ = INVALID_SOCKET;
        return false;
      }
    }

    // Accept connection
    SOCKET connectionSocket = WS2_32::accept(socket_, NULL, NULL);
    return Connection(connectionSocket);
  }

 private:
  const unsigned short port_;
  SOCKET socket_;
};

#endif  // SERVER_H_
