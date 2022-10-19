#include "crc32.h"

#include <array>
#include <fstream>
#include <iterator>

bool Crc32::checksum(const std::string& filename, unsigned int* crc)
{
  // Create lookup table
  const auto polynomial = 0x04C11DB7u;
  static std::array<unsigned int, 256> table;

  for(auto i = 0; i <= 0xFF; i++)
  {
    table[i] = reflect(i, 8) << 24;

    for (auto pos = 0; pos < 8; pos++)
    {
      table[i] = (table[i] << 1) ^ ((table[i] & (1 << 31)) ? polynomial : 0);
    }

    table[i] = reflect(table[i], 32);
  }

  // Init checksum
  *crc = 0xffffffff;

  // Open file
  std::ifstream fileStream(filename, std::ifstream::binary);
  if (!fileStream)
  {
    return false;
  }

  // Read data
  std::istreambuf_iterator<char> it(fileStream);
  while (it != std::istreambuf_iterator<char>())
  {
    *crc = (*crc >> 8) ^ table[(*crc & 0xFF) ^ static_cast<unsigned char>(*it)];
    ++it;
  }

  // Finalize checksum
  *crc ^= 0xffffffff;

  return true;
}

unsigned int Crc32::reflect(unsigned int reflect, const char c)
{
  auto value = 0u;

  for (auto i = 1; i < (c + 1); i++)
  {
    if (reflect & 1)
    {
      value |= (1 << (c - i));
    }
    reflect >>= 1;
  }

  return value;
}
