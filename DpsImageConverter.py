from __future__ import print_function
import os, sys, math, argparse, configparser
from PIL import Image

class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            print("'{0}' is not a valid path".format(prospective_dir))
            sys.exit(0)
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            print("'{0}' is not a readable path".format(prospective_dir))
            sys.exit(0)

def positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
         raise argparse.ArgumentTypeError(
            "%s is an invalid positive int value" % value)
    return ivalue

parser = argparse.ArgumentParser(
    description = 'Convert images for Dungeon Painter Studio',
    add_help = False
    )

parser.add_argument('-S', '--source', default=os.getcwd(),
    help = 'Directory from which to get the source images',
    action = readable_dir)

args, stuff = parser.parse_known_args()

config = configparser.ConfigParser()

defaults = {"pixels": None, "scale": 5, "optimize": None}

config.read([os.path.join(args.source, 'config.ini')])
if config.has_section("pds_converter"):
    defaults.update(dict(config.items("pds_converter")))

parser = argparse.ArgumentParser(
    parents = [parser]
    )

parser.add_argument('-O', '--output',
    default = os.path.join(os.getcwd(), 'converted'),
    help = 'Directory to which to save the result images',
    action = readable_dir)
parser.add_argument('-p', '--pixels',
    help = 'Number of pixels per unit to use as a measurement for scaling '
    + 'i.e. pixels per foot', type = positive_int)
parser.add_argument('-s', '--scale',
    help = 'Number of units per square i.e. 5 means each square '
    + 'represents 5ft', type = positive_int)
parser.add_argument('-o', '--optimize', help = 'Optimize images for printing '
    + 'for this many pixels per square', type = positive_int)

parser.set_defaults(**defaults)

args = parser.parse_args()

scaled_pixels = 200
if not args.pixels is None and not args.scale is None:
    scaled_pixels = args.pixels * args.scale

preview_pixels = 100
img_pixels = 200

preview_name = "_preview.png"
image_name = "img.png"

for subdir, dirs, files in os.walk(args.source):
    dirs[:] = [d for d in dirs if d not in set(['converted'])]

    for file in files:
        if not file.lower().endswith(".png"):
            continue

        # Get the image to be added
        source_path = os.path.join(subdir, file)
        print("Processing " + source_path)

        source_image = Image.open(source_path)

        # Crop any bounding box
        source_image = source_image.crop(source_image.getbbox())

        # Calculate how many squares this image will need
        source_width_squares = math.ceil(source_image.width / scaled_pixels)
        source_height_squares = math.ceil(source_image.height / scaled_pixels)

        # Create a new canvas with the full size of the padded image
        padded_width_pixels = source_width_squares * scaled_pixels
        padded_height_pixels = source_height_squares * scaled_pixels
        padded_image = Image.new('RGBA',
                                (padded_width_pixels, padded_height_pixels),
                                (0,0,0,0))

        # Paste the original image centered on to the new padded canvas
        offset = (
            (padded_width_pixels - source_image.width) // 2,
            (padded_height_pixels - source_image.height) // 2)
        padded_image.paste(source_image, offset)

        # Resize to create the _perview version for DPS
        # Preview resize = 100px in the widest dimension
        this_preview_pixels = preview_pixels \
            / max([source_width_squares, source_height_squares])

        preview_image = padded_image.resize(
                (round(source_width_squares * this_preview_pixels),
                 round(source_height_squares * this_preview_pixels)),
                Image.ANTIALIAS)

        if (not args.optimize is None):
            # Scale the padded image with antialiasing to the rendering size
            # The image will be already scaled and nicely antialised
            padded_image = padded_image.resize(
                (source_width_squares * args.optimize,
                 source_height_squares * args.optimize),
                Image.ANTIALIAS)

        # Resize to create the img versions that DPS will use
        img_image = padded_image.resize(
            (source_width_squares * img_pixels,
             source_height_squares * img_pixels))

        # Create the path to save the files
        target_path = os.path.join(args.output,
                                  os.path.split(subdir)[1],
                                  os.path.splitext(file)[0])

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        # Save the files
        preview_image.save(os.path.join(target_path, preview_name))
        img_image.save(os.path.join(target_path, image_name))
