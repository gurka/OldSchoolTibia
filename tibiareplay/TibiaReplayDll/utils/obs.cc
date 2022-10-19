#include "obs.h"

#include <windows.h>

namespace Obs
{

bool startRecording()
{
  HWND hWndOBS = FindWindow("OBSWindowClass", NULL);
  if (hWndOBS == NULL)
  {
    return false;
  }

  HWND hWndStartRecording = FindWindowEx(hWndOBS, NULL, "Button", "Start Recording");
  if (hWndStartRecording == NULL)
  {
    return false;
  }

  SendMessage(hWndStartRecording, BM_CLICK, 0, 0);
  return true;
}

bool stopRecording()
{
  HWND hWndOBS = FindWindow("OBSWindowClass", NULL);
  if (hWndOBS == NULL)
  {
    return false;
  }

  HWND hWndStopRecording = FindWindowEx(hWndOBS, NULL, "Button", "Stop Recording");
  if (hWndStopRecording == NULL)
  {
    return false;
  }

  SendMessage(hWndStopRecording, BM_CLICK, 0, 0);
  return true;
}

}
