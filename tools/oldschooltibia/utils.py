from datetime import date, datetime
import re

def read_u8(f):
    """Reads an unsigned byte from the file object f.
    """
    temp = f.read(1)
    if not temp:
        raise EOFError("EOF")

    return int.from_bytes(temp, byteorder='little', signed=False)


def read_u16(f):
    """Reads a two byte unsigned value from the file object f.
    """
    temp = f.read(2)
    if not temp:
        raise EOFError("EOF")

    return int.from_bytes(temp, byteorder='little', signed=False)


def read_u32(f):
    """Reads a four byte unsigned value from the file object f.
    """
    temp = f.read(4)
    if not temp:
        raise EOFError("EOF")

    return int.from_bytes(temp, byteorder='little', signed=False)


def read_u64(f):
    """Reads an eight byte unsigned value from the file object f.
    """
    temp = f.read(8)
    if not temp:
        raise EOFError("EOF")

    return int.from_bytes(temp, byteorder='little', signed=False)


def write_u8(f, v):
    """Writes the value v as an unsigned byte to the file object f.
    """
    f.write(v.to_bytes(1, byteorder='little', signed=False))


def write_u16(f, v):
    """Writes the value v as a two byte unsigned value to the file object f.
    """
    f.write(v.to_bytes(2, byteorder='little', signed=False))


def write_u32(f, v):
    """Writes the value v as a four byte unsigned value to the file object f.
    """
    f.write(v.to_bytes(4, byteorder='little', signed=False))


def write_u64(f, v):
    """Writes the value v as an eight byte unsigned value to the file object f.
    """
    f.write(v.to_bytes(8, byteorder='little', signed=False))


def print_bytes(data):
    """Prints the bytes in data formatted to stdout.
    """

    # Generator that returns l in chunks of size n
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

    offset = 0
    for chunk in chunks(data, 16):
        # Lint to be printed
        line = f"{offset:08x}    "

        # Add hex
        str_hex = [f"{byte:02X}" for byte in chunk]
        line += " ".join(str_hex)

        if len(str_hex) < 16:
            # Pad if less than 16 bytes
            line += "   " * (16 - len(str_hex))

        # Add ascii
        line += "    |"
        str_ascii = [f"{byte:c}" if 31 < byte < 127 else "." for byte in chunk]
        line += "".join(str_ascii)

        if len(str_ascii) < 16:
            # Pad if less than 16 bytes
            line += " " * (16 - len(str_ascii))

        line += "|"

        # Print line
        print(line)

        offset += 16


def get_all_strings(frames, min_len, unique, smart):
    strings = []

    def is_latin_1(c):
        return (c >= 32 and c <= 126) or (c >= 160 and c <= 255)


    for frame in frames:
        offset = 0
        while offset < len(frame.data) - 2:
            string_length = (frame.data[offset + 1] << 8) | frame.data[offset]
            if string_length >= min_len and string_length < 1024 and (offset + 2 + string_length - 1 < len(frame.data)):
                string_raw = frame.data[offset + 2:offset + 2 + string_length]
                if all(is_latin_1(char) for char in string_raw):
                    strings.append(string_raw.decode('latin-1'))

                    # note: subtract 1 here because we add 1 below
                    offset += 2 + string_length - 1

            offset += 1

    if smart:
        temp = []
        for string in strings:
            new = re.sub(r'You lose \d+ hitpoint', r'You lose X hitpoint', string)
            new = re.sub(r'You lose \d+ mana', r'You lose X mana', new)
            new = re.sub(r'Using one of \d+ .+\.\.\.', r'Using one of X Y...', new)
            temp.append(new)

        strings = temp

    if unique:
        # nice
        strings = list(set(strings))
        strings.sort()

    return strings


def guess_version(frames):
    if len(frames) == 0:
        return

    # Updates
    updates = [
        (date(2002,  8, 28), 700),
        (date(2002, 10, 22), 701),
        (date(2002, 11, 21), 702),
        (date(2002, 12, 17), 710),
        (date(2003,  7, 27), 711),
        (date(2003, 12, 16), 720),
        (date(2004,  1, 21), 721),
        (date(2004,  3,  9), 723), # test server client
        (date(2004,  3, 14), 724),
        (date(2004,  5,  4), 726),
        (date(2004,  7, 22), 727),
        (date(2004,  8, 11), 730),
        (date(2004, 12, 10), 735), # test server client
        (date(2004, 12, 14), 740),
        (date(2005,  7,  7), 741),
        (date(2005,  8,  9), 750),
        (date(2005, 11, 16), 755),
        (date(2005, 12, 12), 760),
        (date(2006,  5,  5), 761), # test server client
        (date(2006,  5, 17), 770),
        (date(2006,  5, 31), 771),
        (date(2006,  6,  8), 772),
        (date(2006,  8,  1), 780),
        (date(2006,  8, 29), 781),
        (date(2006, 10, 13), 782),
        (date(2006, 12, 12), 790),
        (date(2007,  1,  8), 792),
        (date(2007,  6, 26), 800),
        (date(2007, 12, 11), 810),
        (date(2008,  4,  8), 811),
        (date(2008,  7,  2), 820),
        (date(2008,  7, 24), 821),
        (date(2008,  8, 12), 822),
        (date(2008,  9, 30), 830),
        (date(2008, 10,  1), 831),
        (date(2008, 12, 10), 840),
        (date(2009,  3, 18), 841),
        (date(2009,  4, 22), 842),
        (date(2009,  7,  1), 850),
        (date(2009, 10,  1), 852),  # 8.51 was released the same day
        (date(2009, 11,  5), 853),
        (date(2009, 12,  9), 854),
        (date(2010,  3, 17), 855),
        (date(2010,  5,  5), 856),
        (date(2010,  5,  6), 857),
        (date(2010,  6, 30), 860),
        (date(2010,  8, 23), 861),
        (date(2010,  9, 22), 862),
        (date(2010, 12,  8), 870),
        (date(2011,  1, 27), 871),
        (date(2011,  4, 20), 872),
        (date(2011,  4,  4), 873),
        (date(2011,  4, 12), 874),
        (date(2011,  6,  9), 900),
    ]

    # Compile regex
    regex = re.compile(r'Your last visit in Tibia: (\d+)\. (\S{3}) (\d{4})')

    # Try to find the login message, which should be in the first frame
    frame = frames[0]
    for i in range(0, len(frame.data) - 4):
        # Version 7.1 has 0xb4 0x11
        # Version 7.2 has 0xb4 0x13
        # Version 7.26 - 8.10 have 0xb4 0x14
        # Version 8.2? - ?.?? have 0xb4 0x16
        if frame.data[i] == 0xb4 and frame.data[i + 1] in (0x11, 0x13, 0x14, 0x16):
            # Possibly a text message
            try:
                text_length = frame.data[i + 2] | frame.data[i + 3] << 8
                if text_length > 255:
                    continue

                # Extract, decode and match against regex
                text = frame.data[i + 4:i + 4 + text_length].decode('ascii')
                m = regex.search(text)
                if m is None:
                    continue
            except:
                # ignore
                continue

            # Parse date
            d = datetime.strptime(f'{m.group(3)}-{m.group(2)}-{m.group(1)}', '%Y-%b-%d').date()

            # Guess version
            for vi in range(1, len(updates)):
                version_date, _ = updates[vi]
                if version_date > d:
                    _, version = updates[vi - 1]
                    return version

    return None


def guess_world(frames):

    """
    TODO / improvements:
     - Add release dates to all worlds so that the script can cross-reference
       the Recording (Tibia) version's release date against world release dates
       and remove/skip worlds that can't possibly be correct.

     - Improve the string check to not match on things like 'Jenova' -> 'Nova'
       It should still match if it ends with a dot, comma or other separator (including EOL)
       Example for the world 'Nova':
       'Jenova' -> no match
       'Nova.' -> match
       'Nova$' -> match
       'Novas' -> no match
    """

    WORLDS = [
        # From https://tibia.fandom.com/wiki/Game_Worlds

        # Active worlds
        "Ambra",
        "Antica",
        "Astera",
        "Axera",
        "Belobra",
        "Bombra",
        "Bona",
        "Calmera",
        "Castela",
        "Celebra",
        "Celesta",
        "Collabra",
        "Damora",
        "Descubra",
        # Dia gives a lot of false positives
        # Since it was released in 2023 we simply ignore it
        #"Dia",
        "Epoca",
        "Esmera",
        "Etebra",
        "Ferobra",
        "Firmera",
        "Flamera",
        "Gentebra",
        "Gladera",
        "Gravitera",
        "Guerribra",
        "Harmonia",
        "Havera",
        "Honbra",
        "Impulsa",
        "Inabra",
        "Issobra",
        "Jacabra",
        "Jadebra",
        "Jaguna",
        "Kalibra",
        "Kardera",
        "Kendria",
        "Lobera",
        "Luminera",
        "Lutabra",
        "Menera",
        "Monza",
        "Mykera",
        "Nadora",
        "Nefera",
        "Nevia",
        "Obscubra",
        "Oceanis",
        "Ombra",
        "Ousabra",
        "Pacera",
        "Peloria",
        "Premia",
        "Pulsera",
        "Quelibra",
        "Quintera",
        "Rasteibra",
        "Refugia",
        "Retalia",
        "Runera",
        "Secura",
        "Serdebra",
        "Solidera",
        "Stralis",
        "Syrena",
        "Talera",
        "Thyria",
        "Tornabra",
        "Ulera",
        "Unebra",
        "Ustebra",
        "Utobra",
        "Vandera",
        "Venebra",
        "Victoris",
        "Vitera",
        "Vunira",
        "Wadira",
        "Wildera",
        "Wintera",
        "Yara",
        "Yonabra",
        "Yovera",
        "Yubra",
        "Zephyra",
        "Zuna",
        "Zunera",

        # Old worlds"
        "Adra",
        "Aldora",
        "Alumbra",
        "Amera",
        "Arcania",
        "Ardera",
        "Askara",
        "Assombra",
        "Aurea",
        "Aurera",
        "Aurora",
        "Azura",
        "Balera",
        "Bastia",
        "Batabra",
        "Bellona",
        "Belluma",
        "Beneva",
        "Berylia",
        "Cadebra",
        "Calva",
        "Calvera",
        "Candia",
        "Carnera",
        "Chimera",
        "Chrona",
        "Concorda",
        "Cosera",
        "Danera",
        "Danubia",
        "Dibra",
        "Dolera",
        "Duna",
        "Efidia",
        "Eldera",
        "Elera",
        "Elysia",
        "Emera",
        "Empera",
        "Estela",
        "Eternia",
        "Faluna",
        "Famosa",
        "Fera",
        "Fervora",
        "Fidera",
        "Fortera",
        "Funera",
        "Furia",
        "Furora",
        "Galana",
        "Garnera",
        "Grimera",
        "Guardia",
        "Helera",
        "Hiberna",
        "Honera",
        "Hydera",
        "Illusera",
        "Impera",
        "Inferna",
        "Iona",
        "Iridia",
        "Irmada",
        "Isara",
        "Jamera",
        "Javibra",
        "Jonera",
        "Julera",
        "Justera",
        "Juva",
        "Karna",
        "Keltera",
        "Kenora",
        "Kronera",
        "Kyra",
        "Laudera",
        "Libera",
        "Libertabra",
        "Lucera",
        "Lunara",
        "Macabra",
        "Magera",
        "Malvera",
        "Marbera",
        "Marcia",
        "Mercera",
        "Mitigera",
        "Morgana",
        "Morta",
        "Mortera",
        "Mudabra",
        "Mythera",
        "Nebula",
        "Neptera",
        "Nerana",
        "Nexa",
        "Nika",
        "Noctera",
        "Nossobra",
        "Nova",
        "Obsidia",
        "Ocebra",
        "Ocera",
        "Olera",
        "Olima",
        "Olympa",
        "Optera",
        "Osera",
        "Pacembra",
        "Pandoria",
        "Panthebra",
        "Panthena",
        "Panthera",
        "Pyra",
        "Pythera",
        "Quilia",
        "Ragna",
        "Reinobra",
        "Relania",
        "Relembra",
        "Rowana",
        "Rubera",
        "Samera",
        "Saphira",
        "Seanera",
        "Selena",
        "Serenebra",
        "Shanera",
        "Shivera",
        "Silvera",
        "Solera",
        "Suna",
        "Tavara",
        "Tembra",
        "Tenebra",
        "Thera",
        "Thoria",
        "Titania",
        "Torpera",
        "Tortura",
        "Trimera",
        "Trona",
        "Umera",
        "Unica",
        "Unisera",
        "Unitera",
        "Valoria",
        "Veludera",
        "Verlana",
        "Versa",
        "Vinera",
        "Visabra",
        "Vita",
        "Wizera",
        "Xandebra",
        "Xantera",
        "Xerena",
        "Xylana",
        "Xylona",
        "Yanara",
        "Ysolera",
        "Zanera",
        "Zeluna",
        "Zenobra",
    ]


    points = dict()
    for string in get_all_strings(frames, 4, False, True):
        string_lower = string.lower()
        for world in WORLDS:
            world_lower = world.lower()
            if world_lower in string_lower:

                # This results in many false positives...
                if world_lower == 'vita' and ('exura vita' in string_lower or 'utamo vita' in string_lower or 'adori vita vis' in string_lower):
                    continue

                if world not in points:
                    points[world] = 0
                points[world] += 1

                if ('of ' + world_lower) in string_lower or ('in ' + world_lower) in string_lower or ('de ' + world_lower) in string_lower:
                    points[world] += 10

    return max(points, key=points.get) if len(points) > 0 else None