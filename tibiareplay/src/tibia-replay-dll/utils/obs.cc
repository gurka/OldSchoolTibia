#include "obs.h"

#include "keystroke.h"
#include <windows.h>

namespace Obs
{

bool startRecording()
{
  KeyStroke::pressAndRelease({ VK_CONTROL, VK_HOME });
  return true;
}

bool stopRecording()
{
  KeyStroke::pressAndRelease({ VK_CONTROL, VK_END });
  return true;
}

}
