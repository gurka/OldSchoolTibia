#ifndef FILE_UTILS_H_
#define FILE_UTILS_H_

#include <windows.h>

class FileUtils
{
 public:
  static std::string getCurrentWorkingDirectory()
  {
    char cwd[1024];
    DWORD ret = GetCurrentDirectory(sizeof(cwd), cwd);
    if (ret == 0 || ret > sizeof(cwd))
    {
      return "";
    }
    return std::string(cwd);
  }

  static std::vector<std::string> getFilenamesInDirectory(const std::string& dir)
  {
    std::vector<std::string> result;

    WIN32_FIND_DATA findData;
    HANDLE handle = FindFirstFile(std::string(dir + "/*.trp").c_str(), &findData);
    if (handle != INVALID_HANDLE_VALUE)
    {
      do {
        result.emplace_back(findData.cFileName);
      } while (FindNextFile(handle, &findData));
      FindClose(handle);
    }

    return result;
  }
};

#endif  // FILE_UTILS_H_
