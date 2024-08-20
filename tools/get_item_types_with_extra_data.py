#!/usr/bin/env python3
import argparse
import json

from libs import utils


def get_item_types_with_extra_data(filename, version):

    optbytes_u16_700_750 = (0x00, 0x07, 0x08, 0x13, 0x16, 0x1d)
    optbytes_u32_700_750 = (0x10,)
    extra_data_700_750 = (0x04, 0x09, 0x0A)

    optbytes_u16_755_772 = (0x00, 0x08, 0x09, 0x19, 0x1c, 0x1d)
    optbytes_u32_755_772 = (0x15, 0x18)
    extra_data_755_772 = (0x05, 0x0A, 0x0B)

    optbytes_u16_780_850 = (0x00, 0x09, 0x0A, 0x1A, 0x1D, 0x1E)
    optbytes_u32_780_850 = (0x16, 0x19)
    extra_data_780_850 = (0x05, 0x0B, 0x0C)

    if version >= 700 and version <= 750:
        optbytes_u16 = optbytes_u16_700_750
        optbytes_u32 = optbytes_u32_700_750
        extra_data = extra_data_700_750

    elif version > 750 and version <= 772:
        optbytes_u16 = optbytes_u16_755_772
        optbytes_u32 = optbytes_u32_755_772
        extra_data = extra_data_755_772

    elif version > 770 and version <= 850:
        optbytes_u16 = optbytes_u16_780_850
        optbytes_u32 = optbytes_u32_780_850
        extra_data = extra_data_780_850

    else:
        raise Exception(f"Version {version} not supported (700 - 850 is supported)")

    with open(filename, 'rb') as f:
        # skip checksum
        f.read(4)

        num_items = utils.read_u16(f) - 99
        num_outfits = utils.read_u16(f)
        num_effects = utils.read_u16(f)
        num_missiles = utils.read_u16(f)
        num_total = num_items + num_outfits + num_effects + num_missiles

        #print(f"num_items={num_items}, num_outfits={num_outfits}, num_effects={num_effects}, num_missiles={num_missiles}, num_total={num_total}")

        first_id = 100
        next_id = first_id
        item_types_with_extra_data = []
        for _ in range(num_total):
            while True:
                opt_byte = utils.read_u8(f)
                if opt_byte == 0xff:
                    break

                if opt_byte in optbytes_u16:
                    opt_extra = utils.read_u16(f)
                elif opt_byte in optbytes_u32:
                    opt_extra = utils.read_u32(f)

                if opt_byte in extra_data:
                    item_types_with_extra_data.append(next_id)


            sprite_width = utils.read_u8(f)
            sprite_height = utils.read_u8(f)
            if sprite_width > 1 or sprite_height > 1:
                utils.read_u8(f)

            sprite_blend_frames = utils.read_u8(f)
            sprite_xdiv = utils.read_u8(f)
            sprite_ydiv = utils.read_u8(f)
            if version <= 750:
                sprite_zdiv = 1
            else:
                sprite_zdiv = utils.read_u8(f)

            sprite_num_anims = utils.read_u8(f)

            num_sprites = sprite_width * sprite_height * sprite_blend_frames * sprite_xdiv * sprite_ydiv * sprite_zdiv * sprite_num_anims
            for _ in range(num_sprites):
                utils.read_u16(f)

            next_id += 1

        return item_types_with_extra_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("DAT_FILE", help="Tibia.dat file")
    parser.add_argument("VERSION", help="Tibia version (e.g. 700, 750 or 772)")
    args = parser.parse_args()

    item_types_with_extra_data = get_item_types_with_extra_data(args.DAT_FILE, int(args.VERSION))
    print(json.dumps(item_types_with_extra_data))
