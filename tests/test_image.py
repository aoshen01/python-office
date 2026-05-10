"""Tests for office.image module."""

import os
import tempfile

import pytest
from PIL import Image as PILImage

from office.image import Image


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_image(tmp_dir):
    """Create a simple 400×300 red PNG for testing."""
    path = os.path.join(tmp_dir, "sample.png")
    img = PILImage.new("RGB", (400, 300), color=(255, 0, 0))
    img.save(path)
    return path


def test_resize_exact(tmp_dir, sample_image):
    out = os.path.join(tmp_dir, "resized.png")
    Image.resize(sample_image, 200, 150, output_path=out)
    with PILImage.open(out) as img:
        assert img.size == (200, 150)


def test_resize_keep_aspect(tmp_dir, sample_image):
    out = os.path.join(tmp_dir, "thumb.png")
    Image.resize(sample_image, 100, 100, output_path=out, keep_aspect=True)
    with PILImage.open(out) as img:
        assert img.width <= 100
        assert img.height <= 100


def test_convert_to_jpeg(tmp_dir, sample_image):
    out = os.path.join(tmp_dir, "converted.jpg")
    result = Image.convert(sample_image, "JPEG", output_path=out)
    assert result.endswith(".jpg")
    assert os.path.isfile(result)
    with PILImage.open(result) as img:
        assert img.format == "JPEG"


def test_convert_to_bmp(tmp_dir, sample_image):
    out = os.path.join(tmp_dir, "converted.bmp")
    result = Image.convert(sample_image, "BMP", output_path=out)
    assert os.path.isfile(result)


def test_add_text_watermark(tmp_dir, sample_image):
    out = os.path.join(tmp_dir, "watermarked.png")
    result = Image.add_text_watermark(sample_image, "CONFIDENTIAL", output_path=out)
    assert os.path.isfile(result)


def test_add_text_watermark_positions(tmp_dir, sample_image):
    for pos in ("top-left", "top-right", "bottom-left", "bottom-right"):
        out = os.path.join(tmp_dir, f"wm_{pos}.png")
        result = Image.add_text_watermark(sample_image, "WM", output_path=out, position=pos)
        assert os.path.isfile(result)


def test_thumbnail(tmp_dir, sample_image):
    result = Image.thumbnail(sample_image, max_size=128)
    assert os.path.isfile(result)
    with PILImage.open(result) as img:
        assert img.width <= 128
        assert img.height <= 128


def test_add_image_watermark(tmp_dir, sample_image):
    wm_path = os.path.join(tmp_dir, "watermark.png")
    wm = PILImage.new("RGBA", (50, 50), color=(0, 0, 255, 128))
    wm.save(wm_path)
    out = os.path.join(tmp_dir, "img_wm.png")
    result = Image.add_image_watermark(sample_image, wm_path, output_path=out)
    assert os.path.isfile(result)
