#include <cstdio>
#include <cstring>
#include "console.h"

Console::~Console()
{
  if (consoleAllocated_)
  {
    FreeConsole();
  }
}

bool Console::init(const std::string& title)
{
  AllocConsole();
  consoleAllocated_ = true;

  consoleHandle_ = GetStdHandle(STD_OUTPUT_HANDLE);
  if (consoleHandle_ == INVALID_HANDLE_VALUE)
  {
    return false;
  }

  CONSOLE_SCREEN_BUFFER_INFO consoleInfo;
  GetConsoleScreenBufferInfo(consoleHandle_, &consoleInfo);
  consoleInfo.dwSize.X = 80;
  consoleInfo.dwSize.Y = 400;
  SetConsoleScreenBufferSize(consoleHandle_, consoleInfo.dwSize);

  SetConsoleTitleA(title.c_str());

  return true;
}

void Console::write(const std::string& message)
{
  write(message.c_str());
}

void Console::write(const char* format, ...)
{
  if (consoleAllocated_ && consoleHandle_ != INVALID_HANDLE_VALUE)
  {
    char message[1024];

    va_list args;
    va_start(args, format);
    vsnprintf(message, sizeof(message), format, args);
    va_end(args);

    WriteConsoleA(consoleHandle_, message, strlen(message), nullptr, nullptr);
  }
}

void Console::progressBar(float percent)
{
  if (consoleAllocated_ && consoleHandle_ != INVALID_HANDLE_VALUE)
  {
    char message[16];

    snprintf(message, sizeof(message), "\r> %5.2f%% <", percent);

    WriteConsoleA(consoleHandle_, message, strlen(message), nullptr, nullptr);
  }
}
