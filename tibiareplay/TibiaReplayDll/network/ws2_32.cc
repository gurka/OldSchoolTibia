#include "ws2_32.h"

WS2_32::RECV_PTR            WS2_32::recv_ptr            = (RECV_PTR)            GetProcAddress(GetModuleHandle("WS2_32.dll"), "recv");
WS2_32::SEND_PTR            WS2_32::send_ptr            = (SEND_PTR)            GetProcAddress(GetModuleHandle("WS2_32.dll"), "send");
WS2_32::SOCKET_PTR          WS2_32::socket_ptr          = (SOCKET_PTR)          GetProcAddress(GetModuleHandle("WS2_32.dll"), "socket");
WS2_32::HTONS_PTR           WS2_32::htons_ptr           = (HTONS_PTR)           GetProcAddress(GetModuleHandle("WS2_32.dll"), "htons");
WS2_32::INET_ADDR_PTR       WS2_32::inet_addr_ptr       = (INET_ADDR_PTR)       GetProcAddress(GetModuleHandle("WS2_32.dll"), "inet_addr");
WS2_32::CONNECT_PTR         WS2_32::connect_ptr         = (CONNECT_PTR)         GetProcAddress(GetModuleHandle("WS2_32.dll"), "connect");
WS2_32::BIND_PTR            WS2_32::bind_ptr            = (BIND_PTR)            GetProcAddress(GetModuleHandle("WS2_32.dll"), "bind");
WS2_32::LISTEN_PTR          WS2_32::listen_ptr          = (LISTEN_PTR)          GetProcAddress(GetModuleHandle("WS2_32.dll"), "listen");
WS2_32::ACCEPT_PTR          WS2_32::accept_ptr          = (ACCEPT_PTR)          GetProcAddress(GetModuleHandle("WS2_32.dll"), "accept");
WS2_32::CLOSESOCKET_PTR     WS2_32::closesocket_ptr     = (CLOSESOCKET_PTR)     GetProcAddress(GetModuleHandle("WS2_32.dll"), "closesocket");
WS2_32::WSAGETLASTERROR_PTR WS2_32::WSAGetLastError_ptr = (WSAGETLASTERROR_PTR) GetProcAddress(GetModuleHandle("WS2_32.dll"), "WSAGetLastError");
WS2_32::WSASETLASTERROR_PTR WS2_32::WSASetLastError_ptr = (WSASETLASTERROR_PTR) GetProcAddress(GetModuleHandle("WS2_32.dll"), "WSASetLastError");
WS2_32::SETSOCKOPT_PTR      WS2_32::setsockopt_ptr      = (SETSOCKOPT_PTR)      GetProcAddress(GetModuleHandle("WS2_32.dll"), "setsockopt");

int WS2_32::recv(SOCKET s, char* buf, int len, int flags)
{
  return recv_ptr(s, buf, len, flags);
}

int WS2_32::send(SOCKET s, const char* buf, int len, int flags)
{
  return send_ptr(s, buf, len, flags);
}

int WS2_32::socket(int af, int type, int protocol)
{
  return socket_ptr(af, type, protocol);
}

int WS2_32::htons(u_short hostshort)
{
  return htons_ptr(hostshort);
}

int WS2_32::inet_addr(const char* cp)
{
  return inet_addr_ptr(cp);
}

int WS2_32::connect(SOCKET s, const struct sockaddr* name, int namelen)
{
  return connect_ptr(s, name, namelen);
}

int WS2_32::closesocket(SOCKET s)
{
  return closesocket_ptr(s);
}

int WS2_32::bind(SOCKET s, const struct sockaddr* name, int namelen)
{
  return bind_ptr(s, name, namelen);
}

int WS2_32::listen(SOCKET s, int backlog)
{
  return listen_ptr(s, backlog);
}

SOCKET WS2_32::accept(SOCKET s, struct sockaddr* addr, int* addrlen)
{
  return accept_ptr(s, addr, addrlen);
}

int WS2_32::WSAGetLastError()
{
  return WSAGetLastError_ptr();
}

void WS2_32::WSASetLastError(int iError)
{
  WSASetLastError_ptr(iError);
}

int WS2_32::setsockopt(SOCKET s, int level, int optname, const char* optval, int optlen)
{
  return setsockopt_ptr(s, level, optname, optval, optlen);
}
