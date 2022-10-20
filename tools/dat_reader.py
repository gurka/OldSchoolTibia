from enum import Enum
from libs import utils


class ItemTypeType(Enum):
    ITEM = 0
    OUTFIT = 1
    EFFECT = 2
    MISSILE = 3


class ItemTypeOptions:

    def __init__(self, option, extra):
        self.option = option
        self.extra = extra


class ItemType:

    def __init__(self, type):
        self.type = type
        self.opts = []


def load_dat(filename):
    # BELOW WORKS WITH 7.55 - 7.72
    with open(filename, 'rb') as f:
        # skip checksum
        f.read(4)

        num_items = utils.read_u16(f) - 99
        num_outfits = utils.read_u16(f)
        num_effects = utils.read_u16(f)
        num_missiles = utils.read_u16(f)
        num_total = num_items + num_outfits + num_effects + num_missiles

        print(f"num_items={num_items}, num_outfits={num_outfits}, num_effects={num_effects}, num_missiles={num_missiles}, num_total={num_total}")

        first_id = 100
        next_id = first_id
        item_types = {}
        for _ in range(num_total):
            if next_id - first_id < num_items:
                item_type = ItemType(ItemTypeType.ITEM)
            elif next_id - first_id - num_items < num_outfits:
                item_type = ItemType(ItemTypeType.OUTFIT)
            elif next_id - first_id - num_items - num_outfits < num_effects:
                item_type = ItemType(ItemTypeType.EFFECT)
            else:
                item_type = ItemType(ItemTypeType.MISSILE)

            while True:
                opt_byte = utils.read_u8(f)
                if opt_byte == 0xff:
                    break

                if opt_byte in (0x00, 0x08, 0x09, 0x19, 0x1c, 0x1d):
                    opt_extra = utils.read_u16(f)
                elif opt_byte in (0x15, 0x18):
                    opt_extra = utils.read_u32(f)
                else:
                    opt_extra = None

                item_type.opts.append(ItemTypeOptions(opt_byte, opt_extra))

            sprite_width = utils.read_u8(f)
            sprite_height = utils.read_u8(f)
            if sprite_width > 1 or sprite_height > 1:
                utils.read_u8(f)

            sprite_blend_frames = utils.read_u8(f)
            sprite_xdiv = utils.read_u8(f)
            sprite_ydiv = utils.read_u8(f)
            sprite_zdiv = utils.read_u8(f)
            sprite_num_anims = utils.read_u8(f)

            num_sprites = sprite_width * sprite_height * sprite_blend_frames * sprite_xdiv * sprite_ydiv * sprite_zdiv * sprite_num_anims
            for _ in range(num_sprites):
                utils.read_u16(f)

            item_types[next_id] = item_type
            next_id += 1

        return item_types


if __name__ == '__main__':
    item_types = load_dat('/home/simon/Tibia.dat')
    print(f"Loaded {len(item_types)} item types")

    item_type_id = 3031
    print(f"Item type {item_type_id}")
    for opt in item_types[item_type_id].opts:
        print(f"  {opt.option} {opt.extra}")
