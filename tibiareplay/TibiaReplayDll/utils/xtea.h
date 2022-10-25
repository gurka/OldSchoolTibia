#ifndef XTEA_H_
#define XTEA_H_

#include <cstdint>

class XTEA
{
 public:
  void setKey(const uint32_t* key);

  bool encrypt(uint8_t* buffer, uint16_t length);
  bool decrypt(uint8_t* buffer, uint16_t length);

 private:
  uint32_t key_[4];
};

#endif  // XTEA_H_
