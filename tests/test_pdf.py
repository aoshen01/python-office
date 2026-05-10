"""Tests for office.pdf module."""

import os
import tempfile

import pytest
from office.pdf import PDF


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_create_basic(tmp_dir):
    path = os.path.join(tmp_dir, "test.pdf")
    result = PDF.create(path, "Hello, World!")
    assert os.path.isfile(result)


def test_create_with_title(tmp_dir):
    path = os.path.join(tmp_dir, "titled.pdf")
    result = PDF.create(path, "Body text here.", title="My Title")
    assert os.path.isfile(result)


def test_get_page_count(tmp_dir):
    path = os.path.join(tmp_dir, "multi.pdf")
    # Long content forces multiple pages
    content = "\n".join(["Line %d" % i for i in range(200)])
    PDF.create(path, content)
    count = PDF.get_page_count(path)
    assert count >= 1


def test_extract_text(tmp_dir):
    path = os.path.join(tmp_dir, "readable.pdf")
    PDF.create(path, "Unique text content 12345")
    text = PDF.extract_text(path)
    assert "Unique text content 12345" in text


def test_extract_text_specific_pages(tmp_dir):
    path = os.path.join(tmp_dir, "multi.pdf")
    content = "\n".join(["Line %d" % i for i in range(200)])
    PDF.create(path, content)
    text = PDF.extract_text(path, pages=[0])
    assert len(text) > 0
