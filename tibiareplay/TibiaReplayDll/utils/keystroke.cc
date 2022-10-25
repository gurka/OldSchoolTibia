#include "keystroke.h"

namespace KeyStroke
{

void sendInput(WORD vkCode, bool keyDown)
{
  // Convert to scan code, since certain applications ignores virtual keys
  UINT scanCode = MapVirtualKey(vkCode, MAPVK_VK_TO_VSC);

  INPUT input;
  input.type = INPUT_KEYBOARD;
  input.ki.wVk = 0;
  input.ki.wScan = scanCode;
  input.ki.dwFlags = KEYEVENTF_SCANCODE | (keyDown ? 0 : KEYEVENTF_KEYUP);
  input.ki.time = 0;
  input.ki.dwExtraInfo = 0;
  SendInput(1, &input, sizeof(input));
}

void pressKey(WORD vkCode)
{
  sendInput(vkCode, true);
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
  sendInput(vkCode, false);
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
