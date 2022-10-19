#include <cstdint>

#include "tibia_connection.h"

bool TibiaConnection::receive(InPacket* packet)
{
  static uint8_t buffer[1024*12];

  if (packet == nullptr)
  {
    return false;
  }

  // Receive packet length
  if (!read(buffer, 2))
  {
    return false;
  }
  uint16_t length = buffer[0] | (buffer[1] << 8);

  // Receive packet
  if (!read(buffer, length))
  {
    return false;
  }

  if (xteaKeySet_)
  {
    // Verify that the packet length is divisible by 8 (required to decrypt)
    if (length % 8 != 0)
    {
      return false;
    }

    // Decrypt packet
    xtea_.decrypt(buffer, length);

    // Read new packet length
    auto newLength = buffer[0] | (buffer[1] << 8);

    packet->reset(buffer + 2, newLength);
  }
  else
  {
    packet->reset(buffer, length);
  }

  return true;
}

bool TibiaConnection::send(const OutPacket& packet)
{
  if (xteaKeySet_)
  {
    // Create a new OutPacket that we can encrypt
    OutPacket encryptedPacket;

    // Add packet length and packet data
    encryptedPacket.addU16(packet.getLength());
    encryptedPacket.add(packet.getBuffer(), packet.getLength());

    // Calculate and add padding, if needed
    if (encryptedPacket.getLength() % 8 != 0)
    {
      encryptedPacket.addPadding(8 - (encryptedPacket.getLength() % 8));
    }

    // Encrypt
    xtea_.encrypt(encryptedPacket.getBuffer(), encryptedPacket.getLength());

    return sendInternal(encryptedPacket);
  }
  else
  {
    return sendInternal(packet);
  }
}

void TibiaConnection::setXTEAKey(const uint32_t* key)
{
  xtea_.setKey(key);
  xteaKeySet_ = true;
}

bool TibiaConnection::sendInternal(const OutPacket& packet)
{
  // Send packet length
  uint16_t length = packet.getLength();

  static uint8_t buffer[2];
  buffer[0] = length & 0xFF;
  buffer[1] = (length >> 8) & 0xFF;

  if (!write(buffer, 2))
  {
    return false;
  }

  // Send packet data
  if (!write(packet.getBuffer(), length))
  {
    return false;
  }

  return true;
}
