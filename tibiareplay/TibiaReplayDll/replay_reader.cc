#include <iterator>

#include "replay_reader.h"

namespace
{

// Internal class for reading values from a file
class FileReader
{
 public:
  bool load(const std::string& filename)
  {
    // Clear fileBuffer_ in case a file has been opened previously
    fileBuffer_.clear();

    // Open file
    std::ifstream fileStream;
    fileStream.open(filename, std::ifstream::in | std::ifstream::binary);
    fileStream.unsetf(std::ios::skipws);
    if (!fileStream.good())
    {
      return false;
    }

    // Read file
    fileBuffer_.insert(fileBuffer_.begin(),
                       std::istream_iterator<uint8_t>(fileStream),
                       std::istream_iterator<uint8_t>());
    position_ = 0;

    return true;
  }

  std::size_t getFileLength() const { return fileBuffer_.size(); }

  uint8_t getU8()
  {
    auto value = fileBuffer_[position_];
    position_ += 1;
    return value;
  }

  uint16_t getU16()
  {
    auto value =  fileBuffer_[position_] |
                 (fileBuffer_[position_ + 1] << 8);
    position_ += 2;
    return value;
  }

  uint32_t getU32()
  {
    auto value =  fileBuffer_[position_] |
                 (fileBuffer_[position_ + 1] << 8) |
                 (fileBuffer_[position_ + 2] << 16) |
                 (fileBuffer_[position_ + 3] << 24);
    position_ += 4;
    return value;
  }

  const uint8_t* getBytes(std::size_t length)
  {
    const auto* bytes = &fileBuffer_[position_];
    position_ += length;
    return bytes;
  }

 private:
  std::vector<uint8_t> fileBuffer_;
  std::size_t position_;
};

}

bool Replay::load(const std::string& filename)
{
  // Clear information about any previosuly opened Replay
  version_ = 0;
  length_ = 0;
  packets_.clear();
  nextPacketIndex_ = 0;

  FileReader fr;

  // Load file
  if (!fr.load(filename))
  {
    loadError_ = "Could not open file";
    return false;
  }

  // Read magic number
  auto magic = fr.getU16();
  if (magic != 0x1337)  // .trp
  {
    loadError_ = "Magic number is not correct";
    return false;
  }

  version_ = fr.getU16();
  length_ = fr.getU32();

  // Read number of replay packets
  auto numberOfPackets = fr.getU32();

  // Read all replay packets
  for (auto i = 0u; i < numberOfPackets; i++)
  {
    auto packetTime = fr.getU32();
    auto packetDataLength = fr.getU16();
    const auto* packetData = fr.getBytes(packetDataLength);

    if (version_ >= 770) {
      const auto packetLength = packetData[0] | (packetData[1] << 8);
      if (packetLength != packetDataLength) {
        loadError_ = "Packet " + std::to_string(i + 1) + " length does match data length (" + std::to_string(packetLength) + " vs " + std::to_string(packetDataLength) + ")";
        return false;
      }
    }

    packets_.emplace_back(OutPacket(packetData, packetDataLength), packetTime);
  }

  return true;
}

const ReplayPacket& Replay::getNextPacket()
{
  const auto& packet = packets_[nextPacketIndex_];
  nextPacketIndex_++;
  return packet;
}
