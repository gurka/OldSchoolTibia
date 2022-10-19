#ifndef KEYSTROKE_H_
#define KEYSTROKE_H_

#include <windows.h>
#include <vector>

namespace KeyStroke
{

void pressKey(WORD vkCode);
void pressKey(const std::vector<WORD>& vkCodes);

void releaseKey(WORD vkCode);
void releaseKey(const std::vector<WORD>& vkCodes);

void pressAndRelease(WORD vkCode, DWORD delay = 0);
void pressAndRelease(const std::vector<WORD>& vkCodes, DWORD delay = 0);

}

#endif  // KEYSTROKE_H_
