"""Tests for office.file module."""

import os
import tempfile

import pytest

from office.file import File


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def populated_dir(tmp_dir):
    """Create a set of test files in the temp directory."""
    files = [
        "report_2023.txt",
        "report_2024.txt",
        "summary.pdf",
        "notes.txt",
        "image.png",
    ]
    for name in files:
        with open(os.path.join(tmp_dir, name), "w"):
            pass
    return tmp_dir


# ------------------------------------------------------------------
# list_files
# ------------------------------------------------------------------

def test_list_files_all(populated_dir):
    files = File.list_files(populated_dir)
    assert len(files) == 5


def test_list_files_by_extension(populated_dir):
    txts = File.list_files(populated_dir, extensions=[".txt"])
    assert len(txts) == 3
    assert all(f.endswith(".txt") for f in txts)


def test_list_files_recursive(tmp_dir):
    sub = os.path.join(tmp_dir, "sub")
    os.makedirs(sub)
    with open(os.path.join(tmp_dir, "a.txt"), "w"):
        pass
    with open(os.path.join(sub, "b.txt"), "w"):
        pass
    files = File.list_files(tmp_dir, recursive=True)
    assert len(files) == 2


# ------------------------------------------------------------------
# batch_rename
# ------------------------------------------------------------------

def test_batch_rename(populated_dir):
    mapping = File.batch_rename(populated_dir, r"report_(\d+)", r"annual_\1")
    assert len(mapping) == 2
    for new_path in mapping.values():
        assert os.path.isfile(new_path)


def test_batch_rename_dry_run(populated_dir):
    mapping = File.batch_rename(populated_dir, r"report_(\d+)", r"annual_\1", dry_run=True)
    assert len(mapping) == 2
    # Original files should still exist
    for old_path in mapping.keys():
        assert os.path.isfile(old_path)


def test_batch_rename_by_extension(populated_dir):
    mapping = File.batch_rename(populated_dir, r"report_", r"rep_", extensions=[".txt"])
    assert len(mapping) == 2


def test_batch_rename_numbered(populated_dir):
    txts = File.list_files(populated_dir, extensions=[".txt"])
    mapping = File.batch_rename_numbered(populated_dir, prefix="item_", extensions=[".txt"])
    assert len(mapping) == len(txts)
    for new_path in mapping.values():
        assert os.path.isfile(new_path)


# ------------------------------------------------------------------
# copy / move
# ------------------------------------------------------------------

def test_copy_file(tmp_dir):
    src = os.path.join(tmp_dir, "source.txt")
    with open(src, "w") as f:
        f.write("hello")
    dest = os.path.join(tmp_dir, "dest.txt")
    result = File.copy(src, dest)
    assert os.path.isfile(src)
    assert os.path.isfile(result)


def test_move_file(tmp_dir):
    src = os.path.join(tmp_dir, "mover.txt")
    with open(src, "w") as f:
        f.write("data")
    dest = os.path.join(tmp_dir, "moved.txt")
    result = File.move(src, dest)
    assert not os.path.exists(src)
    assert os.path.isfile(result)


# ------------------------------------------------------------------
# get_size
# ------------------------------------------------------------------

def test_get_size_bytes(tmp_dir):
    path = os.path.join(tmp_dir, "sized.txt")
    with open(path, "w") as f:
        f.write("A" * 1000)
    size = File.get_size(path, unit="bytes")
    assert size == 1000


def test_get_size_kb(tmp_dir):
    path = os.path.join(tmp_dir, "sized.txt")
    with open(path, "w") as f:
        f.write("A" * 1024)
    size = File.get_size(path, unit="kb")
    assert abs(size - 1.0) < 0.01
