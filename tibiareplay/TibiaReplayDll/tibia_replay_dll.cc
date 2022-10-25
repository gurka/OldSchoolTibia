#include <windows.h>

#include <cstdint>
#include <cstring>
#include <cstdlib>

#include <array>
#include <atomic>
#include <algorithm>
#include <iomanip>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

#include "tibia_connection.h"
#include "packet.h"
#include "replay_reader.h"

#include "network/server.h"

#include "utils/console.h"
#include "utils/fileutils.h"
#include "utils/crc32.h"
#include "utils/rsa.h"
#include "utils/keystroke.h"
#include "utils/obs.h"

void tibiaReplay();
bool writeTibiaServerAddresses();
int getTibiaVersion(HMODULE tibiaHandle);
void handleLoginConnection(TibiaConnection* connection, InPacket* loginPacket);
void handleGameConnection(TibiaConnection* connection, InPacket* loginPacket);

// Tibia version we are injected in
static int tibiaVersion = 0;

// Thread stuff
static std::atomic<bool> quit;

static Console console;

// So that handleGameConnection can continue with next file
static std::vector<std::string> recFilenames;

// RSA instance, only applicable if we are injected in Tibia version 7.70 or newer
static RSA rsa;

// RSA keys (from opentibia/server and otclient)
static const char rsa_private_p[] = "1429962396241639952007017738289889555079540334546615321747051608"
                                    "2934737582776038882967213386204600674145392845853859217990626450"
                                    "972452084065728686565928113";

static const char rsa_private_q[] = "7630979195970404721891201847792002125535401292779123937207447574"
                                    "5966927885136471792353355293072513505707284073737055647088717620"
                                    "33017096809910315212884101";

static const char rsa_public[]    = "1091201329673994292788609605089955415282375029027981291234687579"
                                    "3726629149257644633073969600111060390723088861007265581882535850"
                                    "3429057592827629436413108566029093628212635953836686562675849720"
                                    "6207862794310902180176810615217550567108238764764442605581471797"
                                    "07119674283982419152118103759076030616683978566631413";

// Keystroke mutex
std::mutex keystrokeMutex;

std::string getLengthString(uint32_t length)
{
  // TODO: Use std::ostringstream when Eclipse / GLIBCXX DUAL ABI stops being buggy
  static char buffer[16];

  auto seconds = static_cast<uint32_t>(length / 1000.0f);
  auto hours = seconds / (60 * 60);
  seconds -= (hours * 60 * 60);
  auto minutes = seconds / 60;
  seconds -= (minutes * 60);

  snprintf(buffer, sizeof(buffer), "%2u:%2u:%2u", hours, minutes, seconds);

  return std::string(buffer);
}

uint32_t getFakeTime(int speed)
{
  static auto lastCurrentTime = GetCurrentTime();
  static auto lastFakeTime = lastCurrentTime;

  const auto currentTime = GetCurrentTime();
  const auto elapsedTime = currentTime - lastCurrentTime;

  const auto fakeTime = lastFakeTime + (elapsedTime * speed);

  lastCurrentTime = currentTime;
  lastFakeTime = fakeTime;

  return fakeTime;
}

void tibiaReplay()
{
  if (!writeTibiaServerAddresses())
  {
    return;
  }

  Server<TibiaConnection> server(7171);
  while (!quit)
  {
    // Accept connection
    auto connection = server.accept();
    if (!connection.connected())
    {
      console.write("Could not accept connection!\n");
      continue;
    }

    // Read first packet
    InPacket loginPacket;
    if (!connection.receive(&loginPacket))
    {
      console.write("Could not read packet from connection!\n");
      return;
    }

    auto type = loginPacket.getU8();
    if (type == 0x01)
    {
      handleLoginConnection(&connection, &loginPacket);
    }
    else if (type == 0x0A)
    {
      // Set minimum timer resolution
      if (timeBeginPeriod(1) != TIMERR_NOERROR)
      {
        console.write("Unable to set minimum timer resolution!\n");
        return;
      }

      handleGameConnection(&connection, &loginPacket);

      // Reset minimum timer resolution
      timeEndPeriod(1);
    }
  }
}

bool writeTibiaServerAddresses()
{
  // Maps Tibia version to memory addresses where login server addresses are stored
  static std::unordered_map<int, std::vector<DWORD_PTR>> tibiaServerAddresses =
  {
    // For these version it's possible to change login server in the client
    // We change the login server from here anyway, for completeness
    { 700, { 0x115EEC } },
    { 701, { 0x11829C } },
    { 702, { 0x11B2DC } },
    { 710, { 0x11BF64 } },

    // For these version it's not possible to change login server in the client
    { 713, { 0x119BB8, 0x119C28, 0x119C98, 0x119D08, 0x119D78 } },
    { 721, { 0x119C88, 0x119CF8, 0x119D68, 0x119DD8, 0x119E48 } },
    { 723, { 0x11B600, 0x11B670, 0x11B6E0, 0x11B750, 0x11B7C0 } },
    { 724, { 0x11B750, 0x11B7C0, 0x11B830, 0x11B8A0, 0x11B910 } },
    { 726, { 0x11DD98, 0x11DE08, 0x11DE78, 0x11DEE8, 0x11DF58 } },
    { 727, { 0x11F958, 0x11F9C8, 0x11FA38, 0x11FAA8, 0x11FB18 } },
    { 730, { 0x11CDA0, 0x11CE10, 0x11CE80, 0x11CEF0, 0x11CF60 } },
    { 740, { 0x1E8898, 0x1E8908, 0x1E8978, 0x1E89E8, 0x1E8A58 } },
    { 741, { 0x1EB8A8, 0x1EB918, 0x1EB988, 0x1EB9F8, 0x1EBA68 } },
    { 750, { 0x1EB928, 0x1EB998, 0x1EBA08, 0x1EBA78, 0x1EBAE8 } },
    { 755, { 0x1ED930, 0x1ED9A0, 0x1EDA10, 0x1EDA80, 0x1EDAF0 } },
    { 760, { 0x1EFB50, 0x1EFBC0, 0x1EFC30, 0x1EFCA0, 0x1EFD10 } },
    { 770, { 0x2BB2F0, 0x2BB360, 0x2BB3D0, 0x2BB440, 0x2BB4B0 } },
    { 772, { 0x3152F8, 0x315368, 0x3153D8, 0x315448, 0x3154B8 } },
    { 780, { 0x346710, 0x346780, 0x3467F0, 0x346860, 0x3468D0 } },
    { 781, { 0x34A718, 0x34A788, 0x34A7F8, 0x34A868, 0x34A8D8 } },
    { 790, { 0x355E58, 0x355EC8, 0x355F38, 0x355FA8, 0x356018 } },
    { 792, { 0x355E18, 0x355E88, 0x355EF8, 0x355F68, 0x355FD8 } },
  };

  // Maps Tibia version to memory address where RSA key is stored
  static std::unordered_map<int, DWORD_PTR> tibiaRsaKeyAddress =
  {
      { 770, 0x116620 },
      { 772, 0x15B620 },
      { 780, 0x182620 },
      { 781, 0x185620 },
      { 790, 0x18D620 },
      { 792, 0x18D620 },
  };

  // Init console
  if (!console.init("Tibia Replay"))
  {
    OutputDebugString("Could not initialize console, aborting!");
    return false;
  }
  console.write("Tibia Replay DLL injected!\n");

  // Get Tibia handle
  auto tibiaHandle = (DWORD_PTR)GetModuleHandle(NULL);

  // Get Tibia version
  tibiaVersion = getTibiaVersion((HMODULE)tibiaHandle);
  if (tibiaServerAddresses.count(tibiaVersion) == 0)
  {
    console.write("Invalid Tibia.exe version: %d, aborting!\n", tibiaVersion);
    return false;
  }
  console.write("Running Tibia.exe version: %d!\n", tibiaVersion);

  // Replace Tibias server address with 'localhost'
  console.write("Replacing server addresses with 'localhost'... ");
  DWORD dwOldProtect;
  DWORD dwNewProtect;
  for (const auto& address : tibiaServerAddresses[tibiaVersion])
  {
    const auto address_len = strlen("localhost");
    const auto realAddress = tibiaHandle + address;
    VirtualProtect((LPVOID)realAddress, address_len + 1, PAGE_READWRITE, &dwOldProtect);
    strcpy_s(reinterpret_cast<char*>(realAddress), address_len + 1, "localhost");
    VirtualProtect((LPVOID)realAddress, address_len + 1, dwOldProtect, &dwNewProtect);
  }
  console.write("done!\n");

  if (tibiaVersion >= 770)
  {
    if (tibiaRsaKeyAddress.count(tibiaVersion) == 0)
    {
      console.write("No RSA key address for Tibia.exe version: %d, aborting!\n", tibiaVersion);
      return false;
    }

    console.write("Replacing Tibia RSA key with our RSA key... ");

    const auto rsa_public_len = strlen(rsa_public);
    const auto realAddress = tibiaHandle + tibiaRsaKeyAddress[tibiaVersion];
    VirtualProtect((LPVOID)realAddress, rsa_public_len + 1, PAGE_READWRITE, &dwOldProtect);
    strcpy_s(reinterpret_cast<char*>(realAddress), rsa_public_len + 1, rsa_public);
    VirtualProtect((LPVOID)realAddress, rsa_public_len + 1, dwOldProtect, &dwNewProtect);

    console.write("done!\n");

    // Don't forget to set the private key
    rsa.setPrivateKey(rsa_private_p, rsa_private_q);
  }

  return true;
}

int getTibiaVersion(HMODULE tibiaHandle)
{
  // Get path to Tibia.exe
  char tibiaFilename[1024];
  if (GetModuleFileName(tibiaHandle, tibiaFilename, sizeof(tibiaFilename)) == 0)
  {
    console.write("Could not get path to Tibia.exe, aborting.\n");
    return 0;
  }

  auto crc = 0u;
  if (!Crc32::checksum(tibiaFilename, &crc))
  {
    console.write("Could not calculate checksum for file: %s\n", tibiaFilename);
    return 0;
  }

  // Maps Tibia.exe checksum to Tibia version
  static std::unordered_map<unsigned int, int> checksumToVersion =
  {
      { 0x8BA5990B, 700 },
      { 0xF6CB58B5, 701 },
      { 0x3F6545D2, 702 },
      { 0x896E66E1, 710 },
      { 0x6E5C7790, 713 },
      { 0x52289E5F, 721 },
      { 0xBC8C3860, 723 },
      { 0xEF044C44, 724 },
      { 0x4A0B0889, 726 },
      { 0xB4B764A3, 727 },
      { 0x6F8FDD9B, 730 },
      { 0x91D70BB9, 740 },
      { 0xCB01B398, 741 },
      { 0xD81EEF24, 750 },
      { 0xBC399D2F, 755 },
      { 0x98E58F34, 760 },
      { 0x640FA2C3, 770 },
      { 0x05415AD2, 772 },
      { 0x5539D1DE, 780 },
      { 0x7B331043, 781 },
      { 0x21ADD79D, 790 },
      { 0x7A4826AE, 792 },
  };

  if (checksumToVersion.count(crc) == 1)
  {
    console.write("Tibia.exe checksum: 0x%08X => Tibia.exe version: %d\n", crc, checksumToVersion[crc]);
    return checksumToVersion[crc];
  }
  else
  {
    console.write("Tibia.exe checksum: 0x%08X => Unknown Tibia.exe version\n", crc);
    return 0;
  }
}

void handleLoginConnection(TibiaConnection* connection, InPacket* loginPacket)
{
  // Skip client OS
  loginPacket->skip(2);
  auto version = loginPacket->getU16();

  if (version != tibiaVersion)
  {
    console.write("handleLoginConnection: Invalid version: %u Expected: %u\n", version, tibiaVersion);
    return;
  }

  if (tibiaVersion >= 770)
  {
    // Skip OS information
    loginPacket->skip(12);

    if (loginPacket->bytesLeft() != 128)
    {
      console.write("Invalid login packet: Cannot decrypt RSA (bytesLeft() = %u)\n", loginPacket->bytesLeft());
      return;
    }

    console.write("Decrypting RSA!\n");
    auto encryptedData = loginPacket->getRaw(128);
    rsa.decrypt(reinterpret_cast<char*>(encryptedData.data()));

    InPacket decryptedPacket(encryptedData.data(), 128);
    if (decryptedPacket.getU8() != 0)
    {
      console.write("Invalid login packet: RSA decryption failed\n");
      return;
    }

    console.write("Reading and setting XTEA key!\n");
    uint32_t xteaKey[4];
    xteaKey[0] = decryptedPacket.getU32();
    xteaKey[1] = decryptedPacket.getU32();
    xteaKey[2] = decryptedPacket.getU32();
    xteaKey[3] = decryptedPacket.getU32();
    connection->setXTEAKey(xteaKey);
  }

  if (recFilenames.empty())
  {
    // Get files in current working directory
    recFilenames = FileUtils::getFilenamesInDirectory(FileUtils::getCurrentWorkingDirectory());

    // Remove files without .trp extension
    const std::string extension = ".trp";
    auto predicate = [&extension](const std::string& filename)
    {
      if (filename.length() > extension.length())
      {
        return filename.compare(filename.length() - extension.length(), extension.length(), extension) != 0;
      }
      return true;
    };
    recFilenames.erase(std::remove_if(recFilenames.begin(), recFilenames.end(), predicate),
                       recFilenames.end());

    // Sort (case insensitive)
    std::sort(recFilenames.begin(), recFilenames.end(), [](const std::string& a, const std::string& b)
    {
      std::string aLower = a;
      std::transform(a.cbegin(), a.cend(), aLower.begin(), ::tolower);

      std::string bLower = b;
      std::transform(b.cbegin(), b.cend(), bLower.begin(), ::tolower);

      return aLower < bLower;
    });

    // Write files to console
    console.write(".trp files in replay directory:\n");
    for (const auto& filename : recFilenames)
    {
      console.write("  %s\n", filename.c_str());
    }

    // Warning if more than 255 replays
    if (recFilenames.size() >= 255)
    {
      console.write("WARNING, CLIENT CAN NOT HANDLE MORE THAN 255 REPLAY FILES\n");

      recFilenames.clear();
      recFilenames.push_back("Too many .trp-files in directory");
    }
  }

  // Loginserver packet => send character / .rec-file list
  OutPacket outPacket;

  // MOTD
  outPacket.addU8(0x14);
  outPacket.addString("0\nWelcome to Tibia Replay");

  // Response
  outPacket.addU8(0x64);

  // Number of characters (.rec files)
  outPacket.addU8(static_cast<uint8_t>(recFilenames.size()));

  // Add real filenames
  for (const auto& filename : recFilenames)
  {
    outPacket.addString(filename);
    outPacket.addString("Tibia Replay");
    outPacket.addU32(0x0100007F);  // 127.0.0.1
    outPacket.addU16(7171);
  }

  // Premium days
  outPacket.addU16(1336);

  // Send packet
  connection->send(outPacket);
}

void handleGameConnection(TibiaConnection* connection, InPacket* loginPacket)
{
  // Skip client OS
  loginPacket->skip(2);
  auto version = loginPacket->getU16();

  if (version != tibiaVersion)
  {
    console.write("handleLoginConnection: Invalid version: %u Expected: %u\n", version, tibiaVersion);

    OutPacket packet;
    packet.addU8(0x14);
    packet.addString("Invalid Tibia version");
    connection->send(packet);
    connection->close();

    return;
  }

  std::string filename;

  if (version >= 770)
  {
    // Parse encrypted login packet
    if (loginPacket->bytesLeft() != 128)
    {
      console.write("Invalid login packet: Cannot decrypt RSA (bytesLeft() = %u)\n", loginPacket->bytesLeft());
      connection->close();  // We can't send a proper disconnect packet without XTEA keys (?)
      return;
    }

    console.write("Decrypting RSA!\n");
    auto encryptedData = loginPacket->getRaw(128);
    rsa.decrypt(reinterpret_cast<char*>(encryptedData.data()));

    InPacket decryptedPacket(encryptedData.data(), 128);
    if (decryptedPacket.getU8() != 0)
    {
      console.write("Invalid login packet: RSA decryption failed\n");
      connection->close();  // We can't send a proper disconnect packet without XTEA keys (?)
      return;
    }

    console.write("Reading and setting XTEA key!\n");
    uint32_t xteaKey[4];
    xteaKey[0] = decryptedPacket.getU32();
    xteaKey[1] = decryptedPacket.getU32();
    xteaKey[2] = decryptedPacket.getU32();
    xteaKey[3] = decryptedPacket.getU32();
    connection->setXTEAKey(xteaKey);

    // Skip isGM and account number
    decryptedPacket.skip(1 + 4);
    filename = decryptedPacket.getString();
  }
  else
  {
    // Parse unencrypted login packet
    if (version <= 721)
    {
      // Skip isGM
      loginPacket->skip(1);
    }
    else
    {
      // Skip isGM and account number
      loginPacket->skip(1 + 4);
    }

    filename = loginPacket->getString();
  }

  // Find the given filename in the recFilenames vector
  auto it = std::find(recFilenames.begin(), recFilenames.end(), filename);
  if (it == recFilenames.end())
  {
    console.write("Error: could not find filename: '%s' in recFilenames\n", filename.c_str());
    return;
  }

  // Thread to read packets from client, and variables to communicate between threads
  std::atomic<bool> quitReplay(false);
  std::atomic<bool> nextReplay(false);
  std::atomic<uint32_t> newSpeed(1);
  std::thread recvThread = std::thread([&connection, &quitReplay, &nextReplay, &newSpeed]()
  {
    InPacket packet;
    while (connection->receive(&packet))
    {
      // Handle packet
      auto type = packet.getU8();

      //console.write("Received packet: 0x%2X\n", type);

      if (type == 0x14)
      {
        quitReplay = true;
      }
      else if (type == 0x96)
      {
        auto speakType = packet.getU8();

        if (speakType == 0x04 ||  // SPEAK_PRIVATE
            speakType == 0x0B ||  // SPEAK_PRIVATE_RED
            speakType == 0x07)    // SPEAK_RVR_CHANNEL
        {
          packet.getString();  // Receiver
        }
        else if (speakType == 0x05 ||  // SPEAK_CHANNEL_Y
                 speakType == 0x0A ||  // SPEAK_CHANNEL_R1
                 speakType == 0x0E)    // SPEAK_CHANNEL_R2
        {
          packet.getU16();  // Channel ID
        }

        auto message = packet.getString();

        if (message.length() > 0 && message[0] == '/')
        {
          // Tibia Replay command
          auto command = message.substr(1);

          if (command.length() > 6 && command.substr(0, 5) == "speed")
          {
            auto wantedNewSeedString = command.substr(5);
            auto wantedNewSpeed = atoi(wantedNewSeedString.c_str());
            if (wantedNewSpeed >= 0)
            {
              newSpeed = wantedNewSpeed;
            }
          }
          else if (command == "next")
          {
            nextReplay = true;
          }
        }
      }
    }
  });

  std::atomic<bool> escapeClickThreadStop(false);
  std::thread escapeClickThread;
  escapeClickThread = std::thread([&escapeClickThreadStop]()
  {
    // Find Tibia window
    const auto tibiaWindow = FindWindow("TibiaClient", nullptr);
    if (tibiaWindow == 0)
    {
      console.write("\n\nCOULD NOT FIND TIBIA WINDOW, NO KEY-PRESSES WILL BE MADE!!\n\n");
      return;
    }

    Sleep(8000);  // Sleep some time so that the video has time to load, etc

    while (!escapeClickThreadStop)
    {
      if (GetForegroundWindow() == tibiaWindow)
      {
        std::lock_guard<decltype(keystrokeMutex)> lock(keystrokeMutex);
        KeyStroke::pressAndRelease(VK_ESCAPE);
        KeyStroke::pressAndRelease({ VK_CONTROL, 0x44 });  // CTRL + D
      }
      Sleep(2000);
    }
  });

  // Iterate from the given filename until the last filename in recFilenames (auto-play next replay)
  Replay replay;
  while (it != recFilenames.end())
  {
    auto filename = *it;

    quitReplay = false;

    // Open file
    if (!replay.load(filename))
    {
      console.write("Could not open file '%s': %s\n", filename.c_str(), replay.getErrorStr().c_str());
      OutPacket packet;
      packet.addU8(0x14);
      packet.addString(replay.getErrorStr());
      connection->send(packet);
      break;
    }

    // Verify version
    if (replay.getVersion() != tibiaVersion)
    {
      // Allow but warn about different minor version (e.g. 7.70 vs 7.72)
      if (replay.getVersion() / 100 == tibiaVersion / 100)
      {
        console.write("Warning: replay version is %u, Tibia version is %u, continuing...\n", replay.getVersion(), tibiaVersion);
      }
      else
      {
        console.write("Replay file '%s' is version %u, but Tibia is version %u", filename.c_str(), replay.getVersion(), tibiaVersion);
        OutPacket packet;
        packet.addU8(0x14);
        packet.addString("Replay file is version " + std::to_string(replay.getVersion()) + ", but Tibia version is " + std::to_string(tibiaVersion));
        connection->send(packet);
        break;
      }
    }

    // Replay the selected .rec-file
    console.write("Replaying file: '%s'\n", filename.c_str());
    console.write("  Length: %s (%ums)\n", getLengthString(replay.getLength()).c_str(), replay.getLength());
    console.write("  Number of frames: %u\n", replay.getNumberOfFrames());

    // Playback speed, can be changed by user via newSpeed variable
    uint32_t speed = 1;

    // Play recording, send first frame
    const auto& frame = replay.getNextFrame();
    connection->send(frame.getData());

    // Wait for Tibia client to login
    Sleep(1000);

    // Start OBS recording and wait some time to let it start
    if (!Obs::startRecording())
    {
      console.write("WARNING: Could not start recording!\n");
      //break;
    }
    Sleep(1000);

    // Open SkillWindow for 5 seconds
    {
      std::lock_guard<decltype(keystrokeMutex)> lock(keystrokeMutex);
      KeyStroke::pressAndRelease({ VK_CONTROL, 0x53 });  // CTRL + S
    }
    Sleep(5000);
    {
      std::lock_guard<decltype(keystrokeMutex)> lock(keystrokeMutex);
      KeyStroke::pressAndRelease({ VK_CONTROL, 0x53 });  // CTRL + S
    }

    // Set start time here, to avoid problems due to the Sleep()s above
    auto startTime = getFakeTime(speed);

    while (replay.getNumberOfFramesLeft() > 0 && !quitReplay && !nextReplay)
    {
      // Check if replay is paused
      if (speed == 0)
      {
        // Sleep some time
        Sleep(100);

        continue;
      }

      // Get next frame
      const auto& frame = replay.getNextFrame();

      // Calculate when to send this frame to the client
      const auto currentTime = getFakeTime(speed);
      const auto elapsedTime = currentTime - startTime;
      if (elapsedTime < frame.getTime())
      {
        const auto timeUntilNextFrame = frame.getTime() - elapsedTime;

        // Adjust for current speed
        const auto timeToSleep = timeUntilNextFrame / speed;
        Sleep(timeToSleep);
      }

      // Send frame
      connection->send(frame.getData());

      // Check if new speed is wanted
      if (newSpeed != speed)
      {
        speed = newSpeed;
        console.write("Setting new speed: %u\n", speed);
      }

      // Print progress
      float percent = 100.0f - (100.0f * (static_cast<float>(replay.getNumberOfPacketsLeft()) / static_cast<float>(replay.getNumberOfPackets())));
      console.progressBar(percent);
    }

    // End progress bar
    console.progressBar(100.0f);
    console.write("\n");

    if (quitReplay)
    {
      break;
    }
    else if (nextReplay)
    {
      nextReplay = false;
    }

    // Go to next filename
    ++it;
    Sleep(5000);

    // Stop screen recording
    if (!Obs::stopRecording())
    {
      console.write("WARNING: Could not stop recording!\n");
      //break;
    }
    Sleep(5000);
  }

  // Will stop recvThread
  connection->close();
  if (recvThread.joinable())
  {
    recvThread.join();
  }

  // Wait for escapeClickThread
  escapeClickThreadStop = true;
  if (escapeClickThread.joinable())
  {
    escapeClickThread.join();
  }
}

extern "C" __declspec(dllexport) BOOL APIENTRY DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
  static std::thread tibiaReplayThread;

  switch (fdwReason)
  {
    case DLL_PROCESS_ATTACH:
      quit = false;
      tibiaReplayThread = std::thread(tibiaReplay);
      break;

    case DLL_PROCESS_DETACH:
      quit = true;
      if (tibiaReplayThread.joinable())
      {
        tibiaReplayThread.join();
      }
      break;
  }

  return TRUE;
}
