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
  frames_.clear();
  nextFrameIndex_ = 0;

  FileReader fr;

  // Load file
  if (!fr.load(filename))
  {
    loadError_ = "Could not open file";
    return false;
  }

  // Read magic string
  const auto* magic = fr.getBytes(4);
  if (strncmp(magic, "TRP", 4) != 0)
  {
    loadError_ = "Magic string is not correct";
    return false;
  }

  version_ = fr.getU16();
  length_ = fr.getU32();

  // Read number of frames
  auto numberOfFrames = fr.getU32();

  // Read all frames
  for (auto i = 0u; i < numberOfFrames i++)
  {
    auto frameTime = fr.getU32();
    auto frameDataLength = fr.getU16();
    const auto* frameData = fr.getBytes(frameDataLength);

    frames_.emplace_back(frameTime, frameData, frameDataLength);
  }

  return true;
}

const Frame& Replay::getNextFrame()
{
  const auto& frame = frames_[nextFrameIndex_];
  nextFrameIndex_++;
  return frame;
}
