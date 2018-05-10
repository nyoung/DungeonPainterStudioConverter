
# DungeonPainterStudioConverter
Script to convert directories of images for use as Dungeon Painter Studio custom art

## Dependencies
[Python 3](https://www.python.org/downloads/)
[Pillow](https://pillow.readthedocs.io/en/5.1.x/installation.html)

## Basic Use

 1. Populate your images in the directory structure you want them to appear in Dungeon Pager Studio. Note: DPS only allows for a single layer of directories. 
 2. From the root of your image folder, run: py ../path_to_image_converter/dpsimageconverter.py
 3. By default it will create a sub directory named 'converted' with the directory structure used by DPS.
 4. Copy the contents of the converted directory to the data/collections/your_collection/objects folder.
 
