import os
import sys
from PIL import Image, ImageDraw

sprite_file_path = "C:/Program Files/Maxis/SimCity 2000/Data/LARGE.DAT"
#sprite_file_path = "C:/Program Files/Maxis/SimCity 2000/Data/SMALLMED.DAT" # Small versions of the sprites
#sprite_file_path = "C:/Program Files/Maxis/SimCity 2000/Data/SPECIAL.DAT" # Additional small sprites

IMAGE_BACKGROUND_COLOR = (255,255,255,0)
SCRIPT_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))
HEADER_ENTRY_SIZE = 10



# This image is generated by sc2k-make-palette-image.py from a bitmap in the SC2K directory.
palette_path = SCRIPT_PATH + "/simcity-2000-palette.png"
palette_image = Image.open(palette_path)

palette = []

for col in range(16):
    for row in range(16):
        color = palette_image.getpixel((col, row))
        palette.append(color)

def get_palette_color(col, row):
    return palette[col*16 + row]



with open(sprite_file_path, 'rb') as file:
        data = file.read()

        sprite_count = int.from_bytes(data[0:2], byteorder='big', signed=False)

        print("Sprite count: " + str(sprite_count))

        for sprite_index in range(sprite_count):
            entry_start = 2 + sprite_index * HEADER_ENTRY_SIZE

            sprite_id = int.from_bytes(data[entry_start : entry_start+2], byteorder='big', signed=False)
            offset = int.from_bytes(data[entry_start+2 : entry_start+6], byteorder='big', signed=False)
            height = int.from_bytes(data[entry_start+6 : entry_start+8], byteorder='big', signed=False)
            width = int.from_bytes(data[entry_start+8 : entry_start+10], byteorder='big', signed=False)

            #print(str(sprite_index) + " | ID: " + str(sprite_id) + " | OFFSET: " + str(offset) + " | H: " + str(height) + " | W: " + str(width))

            sprite_image = Image.new('RGBA', (width, height), color = IMAGE_BACKGROUND_COLOR)
            sprite_draw = ImageDraw.Draw(sprite_image)

            block_start = offset
            row_index = -1 # All sprites start with a type 1 (new row) block.
            col_index = 0

            while True:
                count = int.from_bytes(data[block_start : block_start+1], byteorder='big', signed=False)
                block_type = int.from_bytes(data[block_start+1 : block_start+2], byteorder='big', signed=False)

                # Do nothing. It's unclear why these blocks exist.
                if block_type == 0:
                    if count != 0:
                        print("Block type 0 with non-zero count: " + str(count)) # Never happens.

                # Go to next row and reset column index.
                elif block_type == 1:
                    row_index += 1
                    col_index = 0

                    # Print all the bytes for this row.
                    #print(" ".join("{:02X}".format(x) for x in data[block_start : block_start + 2 + count]))

                # End of sprite.
                elif block_type == 2:
                    break
                
                # Move insertion point <count> pixels forward in current row.
                elif block_type == 3:
                    col_index += count

                # Pixel data.
                elif block_type == 4:
                    pixel_data_start = block_start + 2

                    for i in range(count):
                            palette_coords = int.from_bytes(data[pixel_data_start + i : pixel_data_start + i + 1], byteorder='big', signed=False)

                            # Two four-bit integers.
                            col = palette_coords & 0b00001111
                            row = (palette_coords >> 4) & 0b00001111 # Technically the bitwise AND here is superfluous since the shift fills the upper bits with zeroes.

                            sprite_draw.point((col_index + i, row_index), fill = get_palette_color(col, row))
                    
                    col_index += count
                
                # Set offset to start of next block.
                if block_type == 4:
                    if count % 2 != 0: # Pixel blocks are padded with an extra null byte if they contain an odd number of pixels.
                            count += 1
                    block_start += 2 + count
                else:
                    block_start += 2
            
            out_path = SCRIPT_PATH + "/sprites/" + str(sprite_index) + "-" + str(sprite_id) + ".png"
            os.makedirs(os.path.dirname(out_path), exist_ok = True)
            sprite_image.save(out_path, "PNG")
