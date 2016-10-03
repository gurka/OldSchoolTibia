#ifndef FILE_UTILS_H_
#define FILE_UTILS_H_

#include <sys/types.h>
#include <unistd.h>
#include <dirent.h>

class FileUtils
{
 public:
  static std::string getCurrentWorkingDirectory()
  {
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    return std::string(cwd);
  }

  static std::vector<std::string> getFilenamesInDirectory(const std::string& dir)
  {
    std::vector<std::string> result;

    DIR *dp;
    struct dirent* ep;
    dp = opendir(dir.c_str());

    if (dp)
    {
      while ((ep = readdir(dp)))
      {
        result.push_back(std::string(ep->d_name));
      }

      closedir(dp);
    }

    return result;
  }
};

#endif  // FILE_UTILS_H_
