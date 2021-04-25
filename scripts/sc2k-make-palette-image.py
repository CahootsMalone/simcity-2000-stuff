import os
import sys
from PIL import Image, ImageDraw

def palette_col_row_to_pixel_coords(col, row):
    # These offsets and scale factors come from the PAL_MSTR.BMP image.
    # It appears to be a scaled-down screenshot of a palette window in a drawing application.
    # Presumably the actual palette is stored somewhere in the SC2K executable.
    x = 2 + (6 * col)
    y = 17 + (5 * row)

    return (x, y)

IMAGE_BACKGROUND_COLOR = (0,0,0)
SCRIPT_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

source_palette_path = "C:/Program Files/Maxis/SimCity 2000/Bitmaps/PAL_MSTR.BMP"
source_palette_image = Image.open(source_palette_path)

# PAL_MSTR.BMP is an indexed-color bitmap.
# If it isn't converted to RGB, getpixel() returns indices.
source_palette_image = source_palette_image.convert('RGB')

new_palette_image = Image.new('RGB', (16, 16), color = IMAGE_BACKGROUND_COLOR)
new_palette_draw = ImageDraw.Draw(new_palette_image)

for col in range(16):
    for row in range(16):
        color = source_palette_image.getpixel(palette_col_row_to_pixel_coords(col, row))

        new_palette_draw.point((col, row), fill = color)

out_path = SCRIPT_PATH + "/simcity-2000-palette.png"
new_palette_image.save(out_path, "PNG")
