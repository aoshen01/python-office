"""Tests for office.excel module."""

import csv
import os
import tempfile

import pytest
from office.excel import Excel


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


SAMPLE_DATA = [
    ["Alice", 30, "Engineer"],
    ["Bob", 25, "Designer"],
    ["Carol", 35, "Manager"],
]
HEADER = ["Name", "Age", "Role"]


def test_create_basic(tmp_dir):
    path = os.path.join(tmp_dir, "test.xlsx")
    result = Excel.create(path, SAMPLE_DATA)
    assert os.path.isfile(result)


def test_create_with_header(tmp_dir):
    path = os.path.join(tmp_dir, "test.xlsx")
    Excel.create(path, SAMPLE_DATA, header=HEADER)
    data = Excel.read(path)
    assert data[0] == HEADER


def test_read(tmp_dir):
    path = os.path.join(tmp_dir, "test.xlsx")
    Excel.create(path, SAMPLE_DATA)
    rows = Excel.read(path)
    assert rows[0] == ["Alice", 30, "Engineer"]


def test_get_sheet_names(tmp_dir):
    path = os.path.join(tmp_dir, "test.xlsx")
    Excel.create(path, SAMPLE_DATA, sheet_name="MySheet")
    names = Excel.get_sheet_names(path)
    assert "MySheet" in names


def test_append_rows(tmp_dir):
    path = os.path.join(tmp_dir, "test.xlsx")
    Excel.create(path, SAMPLE_DATA)
    Excel.append_rows(path, [["Dave", 28, "QA"]])
    rows = Excel.read(path)
    assert any(row == ["Dave", 28, "QA"] for row in rows)


def test_to_csv(tmp_dir):
    xlsx_path = os.path.join(tmp_dir, "test.xlsx")
    csv_path = os.path.join(tmp_dir, "test.csv")
    Excel.create(xlsx_path, SAMPLE_DATA, header=HEADER)
    result = Excel.to_csv(xlsx_path, output_path=csv_path)
    assert os.path.isfile(result)
    with open(result, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    assert rows[0] == HEADER


def test_from_csv(tmp_dir):
    csv_path = os.path.join(tmp_dir, "input.csv")
    xlsx_path = os.path.join(tmp_dir, "output.xlsx")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(SAMPLE_DATA)
    result = Excel.from_csv(csv_path, output_path=xlsx_path)
    assert os.path.isfile(result)
    rows = Excel.read(result)
    assert rows[0] == HEADER
