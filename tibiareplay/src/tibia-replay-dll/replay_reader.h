#ifndef REPLAY_READER_H_
#define REPLAY_READER_H_

#include <cstdint>
#include <fstream>
#include <vector>

#include "packet.h"

class Frame
{
 public:
  Frame(uint32_t time, const std::uint8_t* data, std::size_t dataLength)
    : time_(time),
      data_(data, dataLength)
  {
  }

  uint32_t getTime() const { return time_; }
  const OutPacket& getData() const { return data_; }

 private:
  const uint32_t time_;
  const OutPacket data_;
};

class Replay
{
 public:
  // File loading functions
  bool load(const std::string& filename);
  const std::string& getErrorStr() const { return loadError_; }

  // Replay functions
  uint16_t getVersion() const { return version_; }
  uint32_t getLength() const { return length_; }
  std::size_t getNumberOfFrames() const { return frames_.size(); }
  std::size_t getNumberOfFramesLeft() const { return frames_.size() - nextFrameIndex_; }
  const Frame& getNextFrame();

 private:
  std::string loadError_;

  uint16_t version_;
  uint32_t length_;
  std::vector<Frame> frames_;
  std::size_t nextFrameIndex_;
};

#endif  // REPLAY_READER_H_
