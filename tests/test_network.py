"""Tests for office.network module (QR code generation only; web tests mocked)."""

import os
import tempfile
from unittest.mock import patch, MagicMock
from urllib.parse import urlparse

import pytest
from PIL import Image as PILImage

from office.network import Network


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


# ------------------------------------------------------------------
# QR code
# ------------------------------------------------------------------

def test_generate_qrcode_creates_file(tmp_dir):
    path = os.path.join(tmp_dir, "qr.png")
    result = Network.generate_qrcode("https://example.com", output_path=path)
    assert os.path.isfile(result)


def test_generate_qrcode_is_valid_image(tmp_dir):
    path = os.path.join(tmp_dir, "qr.png")
    Network.generate_qrcode("Hello QR", output_path=path)
    with PILImage.open(path) as img:
        assert img.format == "PNG"
        assert img.width > 0
        assert img.height > 0


def test_generate_qrcode_custom_colors(tmp_dir):
    path = os.path.join(tmp_dir, "qr_color.png")
    result = Network.generate_qrcode(
        "color test",
        output_path=path,
        fill_color="blue",
        back_color="yellow",
    )
    assert os.path.isfile(result)


# ------------------------------------------------------------------
# Web scraping (mocked to avoid network calls)
# ------------------------------------------------------------------

SAMPLE_HTML = """
<html>
<head><title>Test</title></head>
<body>
  <p>Hello from the page</p>
  <a href="/page1">Page 1</a>
  <a href="https://other.com/page2">Other</a>
  <table>
    <tr><th>Name</th><th>Value</th></tr>
    <tr><td>Alpha</td><td>1</td></tr>
    <tr><td>Beta</td><td>2</td></tr>
  </table>
</body>
</html>
"""


def _mock_get(*args, **kwargs):
    mock_resp = MagicMock()
    mock_resp.text = SAMPLE_HTML
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@patch("office.network.requests.get", side_effect=_mock_get)
def test_fetch_page(mock_get):
    html = Network.fetch_page("http://example.com")
    assert "Hello from the page" in html


@patch("office.network.requests.get", side_effect=_mock_get)
def test_extract_text_from_url(mock_get):
    text = Network.extract_text_from_url("http://example.com")
    assert "Hello from the page" in text


@patch("office.network.requests.get", side_effect=_mock_get)
def test_extract_links(mock_get):
    links = Network.extract_links("http://example.com")
    assert any("page1" in link for link in links)


@patch("office.network.requests.get", side_effect=_mock_get)
def test_extract_links_same_domain(mock_get):
    links = Network.extract_links("http://example.com", same_domain_only=True)
    assert all(urlparse(link).netloc == "example.com" for link in links)


@patch("office.network.requests.get", side_effect=_mock_get)
def test_scrape_table(mock_get):
    table = Network.scrape_table("http://example.com")
    assert table[0] == ["Name", "Value"]
    assert table[1] == ["Alpha", "1"]
