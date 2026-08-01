# Copyright (c) 2026 Nathan (https://github.com/nathanchankp)
# Licensed under the Demonstration Software License — NOT for production use.
# See LICENSE for full terms.

"""Tests for the file processor."""

import json
import tempfile
from pathlib import Path

import pytest

from automation.processor import process_file, process_csv, process_json, process_txt


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file helper."""
    def _create(filename: str, content: str) -> Path:
        path = tmp_path / filename
        path.write_text(content, encoding="utf-8")
        return path
    return _create


def test_process_csv(temp_file):
    content = "name,age,city\nAlice,30,Berlin\nBob,25,Munich\nCharlie,35,Frankfurt\n"
    path = temp_file("test.csv", content)
    result = process_csv(path)

    assert result["type"] == "csv"
    assert result["rows"] == 3
    assert result["columns"] == 3
    assert result["column_names"] == ["name", "age", "city"]
    assert "processed_at" in result


def test_process_csv_empty(temp_file):
    path = temp_file("empty.csv", "")
    result = process_csv(path)
    assert result["error"] == "Empty file"


def test_process_json_object(temp_file):
    data = {"name": "test", "value": 42, "items": [1, 2, 3]}
    path = temp_file("data.json", json.dumps(data))
    result = process_json(path)

    assert result["type"] == "json"
    assert result["structure"] == "object"
    assert result["items"] == 3
    assert "name" in result["top_keys"]


def test_process_json_array(temp_file):
    data = [{"id": 1}, {"id": 2}, {"id": 3}]
    path = temp_file("array.json", json.dumps(data))
    result = process_json(path)

    assert result["structure"] == "array"
    assert result["items"] == 3


def test_process_json_invalid(temp_file):
    path = temp_file("bad.json", "{invalid json}")
    result = process_json(path)
    assert "error" in result
    assert "Invalid JSON" in result["error"]


def test_process_txt(temp_file):
    content = "Hello world\nThis is a test file\nThird line\n"
    path = temp_file("notes.txt", content)
    result = process_txt(path)

    assert result["type"] == "txt"
    assert result["lines"] == 3
    assert result["words"] == 9
    assert result["characters"] == len(content)


def test_process_file_routes_csv(temp_file):
    path = temp_file("data.csv", "a,b\n1,2\n")
    result = process_file(path)
    assert result["type"] == "csv"
    assert "error" not in result


def test_process_file_routes_json(temp_file):
    path = temp_file("data.json", '{"key": "value"}')
    result = process_file(path)
    assert result["type"] == "json"
    assert "error" not in result


def test_process_file_routes_txt(temp_file):
    path = temp_file("readme.txt", "some text")
    result = process_file(path)
    assert result["type"] == "txt"
    assert "error" not in result


def test_process_file_unsupported_type(temp_file):
    path = temp_file("image.xyz", "some data")
    result = process_file(path)
    assert "error" in result
    assert "Unsupported" in result["error"]


def test_process_file_nonexistent():
    result = process_file(Path("nonexistent.csv"))
    assert "error" in result
