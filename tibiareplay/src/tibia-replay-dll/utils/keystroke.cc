#include "keystroke.h"

namespace KeyStroke
{

void pressKey(WORD vkCode)
{
  INPUT input;
  input.type = INPUT_KEYBOARD;
  input.ki.wVk = vkCode;
  input.ki.wScan = 0;
  input.ki.dwFlags = 0;
  input.ki.time = 0;
  input.ki.dwExtraInfo = 0;
  SendInput(1, &input, sizeof(input));
}

void pressKey(const std::vector<WORD>& vkCodes)
{
  for (auto vkCode : vkCodes)
  {
    pressKey(vkCode);
  }
}

void releaseKey(WORD vkCode)
{
  INPUT input;
  input.type = INPUT_KEYBOARD;
  input.ki.wVk = vkCode;
  input.ki.wScan = 0;
  input.ki.dwFlags = KEYEVENTF_KEYUP;
  input.ki.time = 0;
  input.ki.dwExtraInfo = 0;
  SendInput(1, &input, sizeof(input));
}

void releaseKey(const std::vector<WORD>& vkCodes)
{
  for (auto vkCode : vkCodes)
  {
    releaseKey(vkCode);
  }
}

void pressAndRelease(WORD vkCode, DWORD delay)
{
  pressKey(vkCode);
  if (delay > 0)
  {
    Sleep(delay);
  }
  releaseKey(vkCode);
}

void pressAndRelease(const std::vector<WORD>& vkCodes, DWORD delay)
{
  for (auto it = vkCodes.cbegin(); it != vkCodes.cend(); ++it)
  {
    pressKey(*it);
  }
  if (delay > 0)
  {
    Sleep(delay);
  }
  for (auto it = vkCodes.crbegin(); it != vkCodes.crend(); ++it)
  {
    releaseKey(*it);
  }
}

}
