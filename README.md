# Old School Tibia
This is a collection of tools and scripts that were used (and still are being used) for creating the videos uploaded to the [Old School Tibia Youtube channel](https://www.youtube.com/channel/UCLvAMwZjm9aUUeJ-wVDMG7A).

## License
See [LICENSE](LICENSE).

### TibiaReplay
TibiaReplay is a tool to play TibiaReplay (.trp) files using the real Tibia client. It has additional features to automate the process of recording the client using a screen recorder such as Open Broadcaster Software (OBS). It currently supports Tibia version 7.00 - 7.92.

To build the tool under Windows you'll need TDM-GCC-32 (GCC 5.1.0), CMake (>= 3.0), GMP (libgmp) and a healthy Bash environment (TDM-GCC and CMake in $PATH). The tool is built as an DLL which are injected to the Tibia client using a DLL injector (which can be built as well).

### Tools
Collection of Python scripts to convert, dump and verify TibiCAM (.rec) and TibiaReplay (.trp) files.

##### convert
[convert.py](tools/convert.py) converts one or multiple TibiCAM files to TibiaReplay files. It can also correct damaged files. This script **does** support encrypted TibiCAM files (thanks to many hours in IDA Pro, sorry how2doit and haktivex). How the encryption (and decryption) of TibiCAM files work is probably what most of you reading this wants to know, so go ahead and read the file [tools/libs/recording.py](tools/libs/recording.py) (line 183 - 241).

##### dump
[dump.py](tools/dump.py) (decrypts) and dumps a TibiCAM or TibiaReplay file. The output is similar to `hexdump -C` but with additional information for each packet. Example output:

    $ ./dump.py -f Beholder.trp | tail
    'Beholder.trp': Packet: 611 Time: 258687 Length: 42
    28 00 AA 0B 00 53 75 6D 6D 65 72 63 6C 75 62 62 |(....Summerclubb|
    01 02 80 07 7D 0A 12 00 49 20 68 6F 70 65 20 79 |....}...I hope y|
    6F 75 20 65 6E 6A 6F 79 65 64                   |ou enjoyed      |
    'Beholder.trp': Packet: 612 Time: 258875 Length: 12
    0A 00 6B 09 80 09 7D 0A 01 AA 05 02             |..k...}.....    |
    'Beholder.trp': Packet: 613 Time: 259093 Length: 39
    25 00 AA 04 00 5A 6F 6E 71 01 FC 7F 03 7D 0A 16 |%....Zonq....}..|
    00 67 6F 3C 3C 3C 3C 3C 3C 3C 3C 3C 3C 3C 3C 3C |.go<<<<<<<<<<<<<|
    3C 3C 3C 3C 3C 3C 3C                            |<<<<<<<         |

##### tstrings
[tstrings.py](tools/tstrings.py) works similar to the POSIX `strings` utility, but for TibiCAM or TibiaReplay files. It simply outputs all strings found in the given TibiCAM or TibiaReplay file.
