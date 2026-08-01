# Copyright (c) 2026 Nathan (https://github.com/nathanchankp)
# Licensed under the Demonstration Software License — NOT for production use.
# See LICENSE for full terms.

"""File processor: handles CSV, JSON, and TXT files."""

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def process_csv(file_path: Path) -> dict:
    """Process a CSV file and return summary stats."""
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return {"file": str(file_path.name), "type": "csv", "error": "Empty file"}

    headers = rows[0]
    data_rows = rows[1:]
    return {
        "file": file_path.name,
        "type": "csv",
        "rows": len(data_rows),
        "columns": len(headers),
        "column_names": headers,
        "size_bytes": file_path.stat().st_size,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def process_json(file_path: Path) -> dict:
    """Process a JSON file and return summary info."""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            return {"file": file_path.name, "type": "json", "error": f"Invalid JSON: {e}"}

    if isinstance(data, dict):
        keys = list(data.keys())
        item_count = len(keys)
        structure = "object"
    elif isinstance(data, list):
        keys = list(data[0].keys()) if data and isinstance(data[0], dict) else []
        item_count = len(data)
        structure = "array"
    else:
        keys = []
        item_count = 1
        structure = type(data).__name__

    return {
        "file": file_path.name,
        "type": "json",
        "structure": structure,
        "items": item_count,
        "top_keys": keys[:10],
        "size_bytes": file_path.stat().st_size,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def process_txt(file_path: Path) -> dict:
    """Process a text file and return word/line/char counts."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    words = content.split()

    return {
        "file": file_path.name,
        "type": "txt",
        "lines": len(lines),
        "words": len(words),
        "characters": len(content),
        "size_bytes": file_path.stat().st_size,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


PROCESSORS = {
    ".csv": process_csv,
    ".json": process_json,
    ".txt": process_txt,
}


def process_file(file_path: Path) -> dict:
    """Route a file to the appropriate processor based on extension.

    Args:
        file_path: Path to the file to process.

    Returns:
        Dict with processing results. Includes 'error' key if processing failed
        or file type is unsupported.
    """
    ext = file_path.suffix.lower()
    processor = PROCESSORS.get(ext)

    if processor is None:
        return {
            "file": file_path.name,
            "type": ext or "unknown",
            "error": f"Unsupported file type: {ext}",
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    try:
        result = processor(file_path)
        logger.info("Processed %s (%s)", file_path.name, ext)
        return result
    except Exception as e:
        logger.error("Failed to process %s: %s", file_path.name, e)
        return {
            "file": file_path.name,
            "type": ext,
            "error": str(e),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
