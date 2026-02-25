from oldschooltibia import _utils


def guess_version(frames, select_alternative_version=True):
    if len(frames) == 0:
        return


    # Try to find the login message, which _should_ be in the first frame
    # (but not always, so we check the first 10 frames just to be sure)
    for frame in frames[:10]:
        version = _utils.guess_world_from_frame(frame)
        if version is not None:
            break

    if not select_alternative_version:
        return version

    # Some version are not likely to have been used in a recording, e.g.
    # test clients or linux clients
    # There are also some versions with only minor technical changes, which
    # means that the recording can be played in a different version without any issues
    version_alternatives = {
        723: 721, # test client
        735: 730, # test client
        761: 760, # test client
        782: 781, # Linux client
        720: 721, # 7.21 only has minor changes
        771: 772, # 7.70, 7.71 and 7.72 all use the same spr and dat files
        851: 852, # 8.51 and 8.52 was released on the same day
    }

    return version_alternatives.get(version, version)


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
    for string in _utils.get_all_strings(frames, 4, False, True):
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