#ifndef CONSOLE_H_
#define CONSOLE_H_

#include <string>
#include <windows.h>

class Console
{
 public:
  Console() = default;
  Console(const Console&) = delete;
  Console& operator=(const Console&) = delete;
  virtual ~Console();

  bool init(const std::string& title);

  void write(const std::string& message);
  void write(const char* format, ...);

  void progressBar(float percent);

 private:
  bool consoleAllocated_ = false;
  HANDLE consoleHandle_ = INVALID_HANDLE_VALUE;
};

#endif  // CONSOLE_H_
