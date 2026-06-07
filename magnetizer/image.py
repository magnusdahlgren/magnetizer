from pathlib import Path
from PIL import Image


def resize_image(src, dest, max_dimension, quality):
    img = Image.open(src)
    w, h = img.size
    long_edge = max(w, h)
    if long_edge > max_dimension:
        scale = max_dimension / long_edge
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img.save(dest, quality=quality, optimize=True)
