#ifndef REPLAY_READER_H_
#define REPLAY_READER_H_

#include <cstdint>
#include <fstream>
#include <vector>

#include "packet.h"

class ReplayPacket
{
 public:
  ReplayPacket(const OutPacket& packet, uint32_t packetTime)
    : packet_(packet),
      packetTime_(packetTime)
  {
  }

  const OutPacket& getPacket() const { return packet_; }
  uint32_t getPacketTime() const { return packetTime_; }

 private:
  const OutPacket packet_;
  const uint32_t packetTime_;
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
  std::size_t getNumberOfPackets() const { return packets_.size(); }
  std::size_t getNumberOfPacketsLeft() const { return packets_.size() - nextPacketIndex_; }
  const ReplayPacket& getNextPacket();

 private:
  std::string loadError_;

  uint16_t version_;
  uint32_t length_;
  std::vector<ReplayPacket> packets_;
  std::size_t nextPacketIndex_;
};

#endif  // REPLAY_READER_H_
