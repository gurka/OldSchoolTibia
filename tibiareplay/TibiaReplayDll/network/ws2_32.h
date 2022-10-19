#ifndef WS2_32_H_
#define WS2_32_H_

#include <windows.h>

class WS2_32
{
 public:
  static int    recv(SOCKET s, char* buf, int len, int flags);
  static int    send(SOCKET s, const char* buf, int len, int flags);
  static int    socket(int af, int type, int protocol);
  static int    htons(u_short hostshort);
  static int    inet_addr(const char* cp);
  static int    connect(SOCKET s, const struct sockaddr* name, int namelen);
  static int    closesocket(SOCKET s);
  static int    bind(SOCKET s, const struct sockaddr* name, int namelen);
  static int    listen(SOCKET s, int backlog);
  static SOCKET accept(SOCKET s, struct sockaddr* addr, int* addrlen);
  static int    WSAGetLastError();
  static void   WSASetLastError(int iError);
  static int    setsockopt(SOCKET s, int level, int optname, const char* optval, int optlen);

 private:
  typedef int    (WINAPI *RECV_PTR)(SOCKET s, char* buf, int len, int flags);
  typedef int    (WINAPI *SEND_PTR)(SOCKET s, const char* buf, int len, int flags);
  typedef int    (WINAPI *SOCKET_PTR)(int af, int type, int protocol);
  typedef int    (WINAPI *HTONS_PTR)(u_short hostshort);
  typedef int    (WINAPI *INET_ADDR_PTR)(const char* cp);
  typedef int    (WINAPI *CONNECT_PTR)(SOCKET s, const struct sockaddr* name, int namelen);
  typedef int    (WINAPI *CLOSESOCKET_PTR)(SOCKET s);
  typedef int    (WINAPI *BIND_PTR)(SOCKET s, const struct sockaddr* name, int namelen);
  typedef int    (WINAPI *LISTEN_PTR)(SOCKET s, int backlog);
  typedef SOCKET (WINAPI *ACCEPT_PTR)(SOCKET s, struct sockaddr* addr, int* addrlen);
  typedef int    (WINAPI *WSAGETLASTERROR_PTR)(void);
  typedef void   (WINAPI *WSASETLASTERROR_PTR)(int);
  typedef int    (WINAPI *SETSOCKOPT_PTR)(SOCKET s, int level, int optname, const char* optval, int optlen);

  static RECV_PTR            recv_ptr;
  static SEND_PTR            send_ptr;
  static SOCKET_PTR          socket_ptr;
  static HTONS_PTR           htons_ptr;
  static INET_ADDR_PTR       inet_addr_ptr;
  static CONNECT_PTR         connect_ptr;
  static CLOSESOCKET_PTR     closesocket_ptr;
  static BIND_PTR            bind_ptr;
  static LISTEN_PTR          listen_ptr;
  static ACCEPT_PTR          accept_ptr;
  static WSAGETLASTERROR_PTR WSAGetLastError_ptr;
  static WSASETLASTERROR_PTR WSASetLastError_ptr;
  static SETSOCKOPT_PTR      setsockopt_ptr;
};

#endif  // WS2_32_H_
