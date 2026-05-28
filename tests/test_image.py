"""Tests for magnetizer/image.py — resize_image()"""

import pytest
from pathlib import Path
from PIL import Image as PILImage
from magnetizer.image import resize_image


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_image(path, width, height, mode="RGB"):
    img = PILImage.new(mode, (width, height), color=(128, 128, 128))
    img.save(path)
    return path


def open_image(path):
    return PILImage.open(path)


# ---------------------------------------------------------------------------
# Output file
# ---------------------------------------------------------------------------

class TestResizeImageOutput:

    def test_output_file_is_created(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 800, 600)
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        assert dest.exists()

    def test_output_is_valid_image(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 800, 600)
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        img = open_image(dest)
        assert img.size[0] > 0

    def test_png_input_produces_output(self, tmp_path):
        src = make_image(tmp_path / "src.png", 400, 300)
        dest = tmp_path / "dest.png"
        resize_image(src, dest, max_dimension=2000, quality=85)
        assert dest.exists()


# ---------------------------------------------------------------------------
# Resizing — landscape (width is long edge)
# ---------------------------------------------------------------------------

class TestResizeLandscape:

    def test_landscape_long_edge_capped_at_max_dimension(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 4000, 3000)
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        img = open_image(dest)
        assert img.size[0] <= 2000
        assert img.size[1] <= 2000

    def test_landscape_width_equals_max_dimension(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 4000, 3000)
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        assert open_image(dest).size[0] == 2000

    def test_landscape_aspect_ratio_preserved(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 4000, 2000)  # 2:1
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        w, h = open_image(dest).size
        assert abs(w / h - 2.0) < 0.01


# ---------------------------------------------------------------------------
# Resizing — portrait (height is long edge)
# ---------------------------------------------------------------------------

class TestResizePortrait:

    def test_portrait_long_edge_capped_at_max_dimension(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 3000, 4000)
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        img = open_image(dest)
        assert img.size[0] <= 2000
        assert img.size[1] <= 2000

    def test_portrait_height_equals_max_dimension(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 3000, 4000)
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        assert open_image(dest).size[1] == 2000

    def test_portrait_aspect_ratio_preserved(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 1000, 2000)  # 1:2
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        w, h = open_image(dest).size
        assert abs(h / w - 2.0) < 0.01


# ---------------------------------------------------------------------------
# No upscaling
# ---------------------------------------------------------------------------

class TestNoUpscaling:

    def test_small_image_not_upscaled(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 400, 300)
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        assert open_image(dest).size == (400, 300)

    def test_image_exactly_at_max_dimension_not_changed(self, tmp_path):
        src = make_image(tmp_path / "src.jpg", 2000, 1500)
        dest = tmp_path / "dest.jpg"
        resize_image(src, dest, max_dimension=2000, quality=85)
        assert open_image(dest).size == (2000, 1500)
