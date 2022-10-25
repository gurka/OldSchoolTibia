#ifndef CRC32_H_
#define CRC32_H_

#include <string>

class Crc32
{
 public:
  static bool checksum(const std::string& filename, unsigned int* crc);

 private:
  static unsigned int reflect(unsigned int reflect, const char cChar);
};

#endif
