#ifndef PACKET_H_
#define PACKET_H_

#include <cstdint>
#include <string>
#include <vector>

class InPacket
{
 public:
  InPacket() : position_(0)
  {
  }

  InPacket(const uint8_t* buffer, int length)
  {
    reset(buffer, length);
  }

  void reset(const uint8_t* buffer, int length)
  {
    buffer_.assign(&buffer[0], &buffer[length]);
    position_ = 0;
  }

  uint8_t getU8()
  {
    auto temp = buffer_[position_];
    position_ += 1;
    return temp;
  }

  uint16_t getU16()
  {
    auto temp =  buffer_[position_] |
                (buffer_[position_ + 1] << 8);
    position_ += 2;
    return temp;
  }

  uint32_t getU32()
  {
    auto temp =  buffer_[position_] |
                (buffer_[position_ + 1] << 8) |
                (buffer_[position_ + 2] << 16) |
                (buffer_[position_ + 3] << 24);
    position_ += 4;
    return temp;
  }

  std::string getString()
  {
    auto length = getU16();
    auto temp = std::string(reinterpret_cast<const char*>(&buffer_[position_]),
                            reinterpret_cast<const char*>(&buffer_[position_ + length]));
    position_ += length;
    return temp;
  }

  std::vector<uint8_t> getRaw(std::size_t num)
  {
    std::vector<uint8_t> raw(&buffer_[position_], &buffer_[position_ + num]);
    position_ += num;
    return raw;
  }

  void skip(std::size_t num)
  {
    position_ += num;
  }

  std::size_t bytesLeft() const { return buffer_.size() - position_; }
  std::size_t getLength() const { return buffer_.size(); }

 private:
  std::vector<uint8_t> buffer_;
  std::size_t position_;
};

class OutPacket
{
 public:
  OutPacket() = default;
  OutPacket(const uint8_t* data, std::size_t num)
    : buffer_(data, data + num)
  {
  }

  void add(const uint8_t* data, std::size_t num)
  {
    buffer_.insert(buffer_.end(), data, data + num);
  }

  void addU8(uint8_t val)
  {
    buffer_.push_back(val);
  }

  void addU16(uint16_t val)
  {
    buffer_.push_back(val & 0xFF);
    buffer_.push_back((val >> 8) & 0xFF);
  }

  void addU32(uint32_t val)
  {
    buffer_.push_back(val & 0xFF);
    buffer_.push_back((val >> 8) & 0xFF);
    buffer_.push_back((val >> 16) & 0xFF);
    buffer_.push_back((val >> 24) & 0xFF);
  }

  void addString(const std::string& str)
  {
    addU16(str.length());
    buffer_.insert(buffer_.end(), str.begin(), str.end());
  }

  void addPadding(std::size_t num)
  {
    buffer_.insert(buffer_.end(), num, 0x33);
  }

  std::size_t getLength() const { return buffer_.size(); }
  const uint8_t* getBuffer() const { return &buffer_[0]; }

  uint8_t* getBuffer() { return &buffer_[0]; }

 private:
  std::vector<uint8_t> buffer_;
};

#endif  // PACKET_H_
