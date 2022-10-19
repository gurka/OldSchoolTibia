#include "XTEA.h"

#include <algorithm>

void XTEA::setKey(const uint32_t* key)
{
  std::copy(key, key + 4, key_);
}

bool XTEA::encrypt(uint8_t* buffer, uint16_t length)
{
  if (length % 8 != 0)
  {
    return false;
  }

  // TODO: This breaks GCC's strict aliasing (use -fno-strict-aliasing)
  auto* temp = (uint32_t*)(buffer);

  std::size_t pos = 0;
  while (pos < (length / 4u))
  {
    uint32_t v0 = temp[pos];
    uint32_t v1 = temp[pos + 1];

    const uint32_t delta = 0x61C88647;
    uint32_t sum = 0;

    for (int i = 0; i < 32; i++)
    {
      v0 += ((v1 << 4 ^ v1 >> 5) + v1) ^ (sum + key_[sum & 3]);
      sum -= delta;
      v1 += ((v0 << 4 ^ v0 >> 5) + v0) ^ (sum + key_[(sum >> 11) & 3]);
    }

    temp[pos] = v0;
    temp[pos + 1] = v1;

    pos += 2;
  }

  return true;
}

bool XTEA::decrypt(uint8_t* buffer, uint16_t length)
{
  if (length % 8 != 0)
  {
    return false;
  }

  // TODO: This breaks GCC's strict aliasing (use -fno-strict-aliasing)
  auto* temp = (uint32_t*)(buffer);

  std::size_t pos = 0;
  while (pos < (length / 4u))
  {
    uint32_t v0 = temp[pos];
    uint32_t v1 = temp[pos + 1];

    const uint32_t delta = 0x61C88647;
    uint32_t sum = 0xC6EF3720;

    for (int i = 0; i < 32; i++)
    {
      v1 -= ((v0 << 4 ^ v0 >> 5) + v0) ^ (sum + key_[(sum >> 11) & 3]);
      sum += delta;
      v0 -= ((v1 << 4 ^ v1 >> 5) + v1) ^ (sum + key_[sum & 3]);
    }

    temp[pos] = v0;
    temp[pos + 1] = v1;

    pos += 2;
  }

  return true;
}
