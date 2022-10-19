#include <cstdio>
#include <windows.h>
#include <psapi.h>

// Path to the DLL to inject (hint: replace this string to reflect your location of the code/dll)
static char dllName[] = "TibiaReplayDll.dll";

DWORD findTibiaPid()
{
  // Enumerate all processes
  DWORD pids[1024];
  DWORD temp;
  if (!EnumProcesses(pids, sizeof(pids), &temp))
  {
    return 1;
  }

  // Find the first process with the name "Tibia.exe"
  DWORD noPids = temp / sizeof(DWORD);
  for (DWORD i = 0; i < noPids; i++)
  {
    if (pids[i] == 0)
    {
      continue;
    }
    HANDLE tempHandle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pids[i]);
    if (tempHandle == NULL)
    {
      continue;
    }
    HMODULE tempModule;
    if (EnumProcessModules(tempHandle, &tempModule, sizeof(tempModule), &temp))
    {
      char szProcessName[MAX_PATH];
      GetModuleBaseName(tempHandle, tempModule, szProcessName, sizeof(szProcessName) / sizeof(TCHAR));
      if (strcmp("Tibia.exe", szProcessName) == 0)
      {
        return pids[i];
      }
    }
  }
  return 0;
}

bool injectDLL(DWORD pid)
{
  // Get full path of our dll
  char fullDllName[1024];
  if (GetFullPathName(dllName, sizeof(fullDllName), fullDllName, nullptr) == 0)
  {
    return false;
  }

  // Open process using pid
  HANDLE handle = OpenProcess(PROCESS_ALL_ACCESS, false, pid);
  if (handle == NULL)
  {
    return false;
  }

  // Get the address to the function LoadLibraryA in kernel32.dll
  HMODULE kernel32Handle = GetModuleHandle("kernel32.dll");
  if (kernel32Handle == NULL)
  {
    return false;
  }
  FARPROC LoadLibAddr = GetProcAddress(kernel32Handle, "LoadLibraryA");
  if (LoadLibAddr == NULL)
  {
    return false;
  }

  // Allocate memory inside the opened process
  LPVOID dereercomp = VirtualAllocEx(handle, NULL, strlen(fullDllName), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
  if (dereercomp == NULL)
  {
    return false;
  }

  // Write the DLL name to the allocated memory
  if (!WriteProcessMemory(handle, dereercomp, fullDllName, strlen(fullDllName), NULL))
  {
    return false;
  }

  // Create a thread in the opened process
  HANDLE remoteThread = CreateRemoteThread(handle, NULL, 0, (LPTHREAD_START_ROUTINE)LoadLibAddr, dereercomp, 0, NULL);
  if (remoteThread == NULL)
  {
    return false;
  }

  // Wait until thread have started (or stopped?)
  WaitForSingleObject(remoteThread, INFINITE);

  // Free the allocated memory
  VirtualFreeEx(handle, dereercomp, strlen(fullDllName), MEM_RELEASE);

  // Close the handles
  CloseHandle(remoteThread);
  CloseHandle(handle);

  return true;
}

int main(int argc, char* argv[])
{
  printf("Finding Tibia pid\n");
  DWORD tibiaPid = findTibiaPid();
  if (tibiaPid == 0)
  {
    fprintf(stderr, "Could not find Tibia process\n");
    return 1;
  }

  printf("Injecting DLL\n");
  if (!injectDLL(tibiaPid))
  {
    fprintf(stderr, "Could not inject DLL\n");
    return 1;
  }

  printf("Done!\n");

  return 0;
}
